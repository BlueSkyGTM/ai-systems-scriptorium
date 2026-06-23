"""
tests/test_kafka_sim.py
pytest suite for the in-process Kafka simulation (kafka_sim.py).

Covers:
  - Topic: append, partition assignment, offsets, read_from, end_offset
  - Producer: produce records, returns correct (partition, offset)
  - ConsumerGroup: assignment coverage, poll, commit, seek, lag
  - At-least-once: seek-and-replay semantics
  - Edge cases: single partition, num_consumers > num_partitions

All tests are offline, deterministic, no I/O.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kafka_sim import Topic, Producer, ConsumerGroup, Record


# ---------------------------------------------------------------------------
# Topic tests
# ---------------------------------------------------------------------------

class TestTopic:
    def test_append_returns_partition_and_offset(self):
        t = Topic("t", num_partitions=4)
        part, offset = t.append({"x": 1}, key="k1")
        assert 0 <= part < 4
        assert offset == 0

    def test_offsets_monotonic_within_partition(self):
        t = Topic("t", num_partitions=1)
        _, off1 = t.append({"a": 1}, key="k")
        _, off2 = t.append({"a": 2}, key="k")
        _, off3 = t.append({"a": 3}, key="k")
        assert off1 == 0
        assert off2 == 1
        assert off3 == 2

    def test_same_key_always_same_partition(self):
        t = Topic("t", num_partitions=8)
        parts = set()
        for i in range(20):
            p, _ = t.append({"i": i}, key="stable_key")
            parts.add(p)
        assert len(parts) == 1, "Same key must always route to same partition"

    def test_different_keys_can_go_to_different_partitions(self):
        t = Topic("t", num_partitions=4)
        parts = set()
        for key in [f"doc_{i:04d}" for i in range(20)]:
            p, _ = t.append({}, key=key)
            parts.add(p)
        # With 20 distinct keys and 4 partitions we expect multiple partitions hit
        assert len(parts) > 1

    def test_read_from_returns_records_from_offset(self):
        t = Topic("t", num_partitions=1)
        t.append({"n": 0}, key="k")
        t.append({"n": 1}, key="k")
        t.append({"n": 2}, key="k")
        records = t.read_from(0, from_offset=1)
        assert len(records) == 2
        assert records[0].value["n"] == 1
        assert records[1].value["n"] == 2

    def test_read_from_empty_when_at_end(self):
        t = Topic("t", num_partitions=1)
        t.append({"n": 0}, key="k")
        records = t.read_from(0, from_offset=1)
        assert records == []

    def test_end_offset_equals_record_count(self):
        t = Topic("t", num_partitions=1)
        assert t.end_offset(0) == 0
        t.append({}, key="k")
        assert t.end_offset(0) == 1
        t.append({}, key="k")
        assert t.end_offset(0) == 2

    def test_total_records(self):
        t = Topic("t", num_partitions=4)
        for i in range(12):
            t.append({}, key=f"k{i}")
        assert t.total_records() == 12

    def test_invalid_partition_raises(self):
        t = Topic("t", num_partitions=2)
        with pytest.raises(IndexError):
            t.read_from(99, 0)

    def test_invalid_num_partitions_raises(self):
        with pytest.raises(ValueError):
            Topic("t", num_partitions=0)

    def test_record_fields(self):
        t = Topic("t", num_partitions=1)
        t.append({"payload": "hello"}, key="mykey")
        rec = t.read_from(0, 0)[0]
        assert isinstance(rec, Record)
        assert rec.key == "mykey"
        assert rec.value == {"payload": "hello"}
        assert rec.partition == 0
        assert rec.offset == 0


# ---------------------------------------------------------------------------
# Producer tests
# ---------------------------------------------------------------------------

class TestProducer:
    def test_produce_returns_partition_offset(self):
        t = Topic("t", num_partitions=4)
        p = Producer(t)
        part, offset = p.produce({"v": 1}, key="k")
        assert 0 <= part < 4
        assert offset == 0

    def test_produce_record_readable(self):
        t = Topic("t", num_partitions=1)
        p = Producer(t)
        p.produce({"msg": "hi"}, key="k1")
        records = t.read_from(0, 0)
        assert len(records) == 1
        assert records[0].value == {"msg": "hi"}

    def test_multiple_produces_increment_offset(self):
        t = Topic("t", num_partitions=1)
        p = Producer(t)
        offsets = [p.produce({}, key="k")[1] for _ in range(5)]
        assert offsets == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# ConsumerGroup tests
# ---------------------------------------------------------------------------

class TestConsumerGroup:
    def test_all_partitions_covered(self):
        t = Topic("t", num_partitions=6)
        g = ConsumerGroup(t, num_consumers=3)
        assert g.all_partitions_covered()

    def test_no_partition_overlap(self):
        t = Topic("t", num_partitions=6)
        g = ConsumerGroup(t, num_consumers=3)
        all_assigned = []
        for cid in range(3):
            all_assigned.extend(g.assignment(cid))
        assert len(all_assigned) == len(set(all_assigned))

    def test_assignment_covers_all_partitions(self):
        t = Topic("t", num_partitions=8)
        g = ConsumerGroup(t, num_consumers=4)
        all_parts = set()
        for cid in range(4):
            all_parts.update(g.assignment(cid))
        assert all_parts == set(range(8))

    def test_single_consumer_gets_all_partitions(self):
        t = Topic("t", num_partitions=4)
        g = ConsumerGroup(t, num_consumers=1)
        assert set(g.assignment(0)) == {0, 1, 2, 3}

    def test_more_consumers_than_partitions(self):
        # Extra consumers get empty assignments — still covers all partitions
        t = Topic("t", num_partitions=2)
        g = ConsumerGroup(t, num_consumers=4)
        assert g.all_partitions_covered()
        # Consumers 2 and 3 have no partitions
        assert g.assignment(2) == []
        assert g.assignment(3) == []

    def test_poll_returns_produced_records(self):
        t = Topic("t", num_partitions=2)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        p.produce({"n": 1}, key="k1")
        p.produce({"n": 2}, key="k2")
        records = g.poll(0)
        assert len(records) == 2

    def test_commit_advances_offset(self):
        t = Topic("t", num_partitions=1)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        p.produce({"n": 1}, key="k")
        g.poll(0)
        g.commit(0)
        # After commit, poll returns nothing
        records = g.poll(0)
        assert records == []

    def test_uncommitted_records_redelivered(self):
        t = Topic("t", num_partitions=1)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        p.produce({"n": 1}, key="k")
        # Poll but do NOT commit -> same record redelivered
        r1 = g.poll(0)
        r2 = g.poll(0)
        assert len(r1) == 1
        assert len(r2) == 1
        assert r1[0].value == r2[0].value

    def test_seek_replays_from_earlier_offset(self):
        t = Topic("t", num_partitions=1)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        for i in range(5):
            p.produce({"n": i}, key="k")
        g.poll(0)
        g.commit(0)
        # Seek back to offset 3 -> get last 2 records
        g.seek(0, 3)
        replayed = g.poll(0)
        assert len(replayed) == 2
        assert replayed[0].value["n"] == 3

    def test_lag_zero_when_fully_committed(self):
        t = Topic("t", num_partitions=2)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        p.produce({}, key="k1")
        p.produce({}, key="k2")
        g.poll(0)
        g.commit(0)
        lags = g.lag()
        assert all(v == 0 for v in lags.values())

    def test_lag_nonzero_when_uncommitted(self):
        t = Topic("t", num_partitions=1)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        p.produce({}, key="k")
        # No commit -> lag == 1
        lags = g.lag()
        assert lags[0] == 1

    def test_committed_offset_reported(self):
        t = Topic("t", num_partitions=1)
        g = ConsumerGroup(t, num_consumers=1)
        p = Producer(t)
        p.produce({}, key="k")
        p.produce({}, key="k")
        g.poll(0)
        g.commit(0)
        assert g.committed_offset(0) == 2

    def test_invalid_num_consumers_raises(self):
        t = Topic("t", num_partitions=2)
        with pytest.raises(ValueError):
            ConsumerGroup(t, num_consumers=0)
