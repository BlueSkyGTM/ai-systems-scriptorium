"""
kafka_sim.py
Offline, in-process Kafka simulation.

Preserves Kafka semantics without a broker:
  - Topic(name, num_partitions): append-only partitions, monotonic offsets.
  - Producer: publishes records to a Topic keyed by a routing key.
  - ConsumerGroup: round-robin partition assignment, committed-offset
    tracking, at-least-once delivery (replay from last committed offset).

Vocabulary contract (must match the real Kafka mental model):
  topic       — named, ordered channel split into partitions
  partition   — append-only log; ordering guaranteed within a partition
  offset      — monotonic int position within a partition (0-based)
  producer    — entity that appends records to a topic
  consumer    — entity that reads records from its assigned partitions
  consumer group — set of consumers that jointly cover all partitions;
                   each partition is owned by exactly one consumer
  at-least-once  — a record is redelivered if its offset is not committed
                   before a crash/reset; consumers must be idempotent
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Record: the unit of data on a partition
# ---------------------------------------------------------------------------

@dataclass
class Record:
    """A single message stored on a partition."""
    key: str          # routing key (e.g. doc_id)
    value: dict       # payload (the CDC event dict)
    partition: int    # which partition it landed on
    offset: int       # monotonic offset within that partition


# ---------------------------------------------------------------------------
# Topic: the named, partitioned log
# ---------------------------------------------------------------------------

class Topic:
    """
    Append-only, partitioned log.

    Partition assignment is deterministic: key -> MD5 hash % num_partitions.
    Offsets are per-partition monotonic ints starting at 0.
    """

    def __init__(self, name: str, num_partitions: int = 4) -> None:
        if num_partitions < 1:
            raise ValueError("num_partitions must be >= 1")
        self.name = name
        self.num_partitions = num_partitions
        # Each partition is an ordered list of Record
        self._partitions: list[list[Record]] = [[] for _ in range(num_partitions)]

    def _partition_for_key(self, key: str) -> int:
        """Deterministic key -> partition mapping (stable across runs)."""
        digest = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
        return digest % self.num_partitions

    def append(self, value: dict, key: str) -> tuple[int, int]:
        """
        Append a record to the partition determined by key.

        Returns (partition, offset) — the address of the new record.
        """
        part = self._partition_for_key(key)
        offset = len(self._partitions[part])
        record = Record(key=key, value=value, partition=part, offset=offset)
        self._partitions[part].append(record)
        return part, offset

    def read_from(self, partition: int, from_offset: int) -> list[Record]:
        """
        Return all records in *partition* at offset >= from_offset.
        This is what a consumer calls after seeking to its committed offset.
        """
        if partition < 0 or partition >= self.num_partitions:
            raise IndexError(f"Partition {partition} out of range for topic '{self.name}'")
        return self._partitions[partition][from_offset:]

    def end_offset(self, partition: int) -> int:
        """Next offset that would be assigned (i.e. current length)."""
        return len(self._partitions[partition])

    def total_records(self) -> int:
        return sum(len(p) for p in self._partitions)


# ---------------------------------------------------------------------------
# Producer
# ---------------------------------------------------------------------------

class Producer:
    """Publishes records to a Topic."""

    def __init__(self, topic: Topic) -> None:
        self.topic = topic

    def produce(self, value: dict, key: str) -> tuple[int, int]:
        """
        Publish value to the topic keyed by key.
        Returns (partition, offset).
        """
        return self.topic.append(value, key)


# ---------------------------------------------------------------------------
# ConsumerGroup
# ---------------------------------------------------------------------------

class ConsumerGroup:
    """
    A group of N consumers that jointly consume all partitions of a topic.

    Assignment:
      consumer_id (0-indexed) owns partition p if: p % num_consumers == consumer_id
      (round-robin, deterministic).

    Committed offsets:
      Each partition tracks the offset of the *next* record to deliver.
      Commit advances this pointer. Without commit, re-poll redelivers
      (at-least-once semantics).
    """

    def __init__(self, topic: Topic, num_consumers: int) -> None:
        if num_consumers < 1:
            raise ValueError("num_consumers must be >= 1")
        self.topic = topic
        self.num_consumers = num_consumers
        # committed_offset[partition] = next offset to read (starts at 0)
        self._committed: list[int] = [0] * topic.num_partitions

    def assignment(self, consumer_id: int) -> list[int]:
        """Return the list of partition indices owned by consumer_id."""
        return [
            p for p in range(self.topic.num_partitions)
            if p % self.num_consumers == consumer_id
        ]

    def poll(self, consumer_id: int) -> list[Record]:
        """
        Fetch all undelivered records for consumer_id's partitions
        (from committed offset onward).  Does NOT advance the committed
        offset — caller must call commit() after successful processing
        for at-least-once guarantee.
        """
        records = []
        for part in self.assignment(consumer_id):
            records.extend(self.topic.read_from(part, self._committed[part]))
        return records

    def commit(self, consumer_id: int) -> None:
        """
        Advance committed offset for all of consumer_id's partitions
        to the current end offset (marking all polled records as processed).
        """
        for part in self.assignment(consumer_id):
            self._committed[part] = self.topic.end_offset(part)

    def seek(self, partition: int, offset: int) -> None:
        """
        Reset the committed offset for a specific partition.
        Used to simulate at-least-once redelivery (roll back to an earlier
        offset to replay uncommitted records).
        """
        self._committed[partition] = offset

    def committed_offset(self, partition: int) -> int:
        """Return the committed offset for a partition."""
        return self._committed[partition]

    def lag(self) -> dict[int, int]:
        """
        Per-partition consumer lag = end_offset - committed_offset.
        A lag of 0 means the consumer is fully caught up.
        """
        return {
            p: self.topic.end_offset(p) - self._committed[p]
            for p in range(self.topic.num_partitions)
        }

    def all_partitions_covered(self) -> bool:
        """True if every partition is assigned to exactly one consumer."""
        covered = set()
        for cid in range(self.num_consumers):
            for p in self.assignment(cid):
                if p in covered:
                    return False   # overlap — should never happen with round-robin
                covered.add(p)
        return covered == set(range(self.topic.num_partitions))
