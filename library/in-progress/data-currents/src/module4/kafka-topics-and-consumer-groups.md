# Kafka Topics and Consumer Groups

CDC events don't vanish the moment they leave the source database. They need somewhere durable and
ordered to wait while one or more consumers read them at their own pace. That somewhere is a topic,
and the mechanism that lets you scale reading is a consumer group.

## A Topic Is an Append Log, Not a Queue

A queue delivers each message once and discards it. A topic keeps every record. A producer appends
to the end; a consumer reads from any offset it chooses. Nothing is removed when a consumer reads.

A topic is also partitioned. The producer hashes each record's key to pick a partition:

```python
class Topic:
    def __init__(self, name, num_partitions=4):
        self._partitions = [[] for _ in range(num_partitions)]

    def _partition_for_key(self, key):
        digest = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
        return digest % self.num_partitions          # same key -> same partition -> per-key order

    def append(self, value, key):
        part = self._partition_for_key(key)
        offset = len(self._partitions[part])          # monotonic, per-partition
        self._partitions[part].append(Record(key, value, part, offset))
        return part, offset

    def read_from(self, partition, from_offset):
        return self._partitions[partition][from_offset:]
```

Two things follow from this design. First, the same key always lands on the same partition, so
records for the same key arrive in the order they were written. Second, each record's offset is
monotonic within its partition: it is the position in that partition's list, and it never resets.
Ordering is guaranteed per partition, not across the whole topic.
[Apache Kafka intro: https://kafka.apache.org/intro]

## A Consumer Group Divides the Partitions

One consumer reading all partitions is a ceiling. To scale throughput, you add consumers to a
group. Kafka assigns each partition to exactly one consumer in the group, so no two consumers
race over the same records:

```python
class ConsumerGroup:
    def assignment(self, consumer_id):
        return [p for p in range(self.topic.num_partitions) if p % self.num_consumers == consumer_id]
```

With four partitions and two consumers: consumer 0 gets partitions 0 and 2, consumer 1 gets 1 and 3.
Every partition is covered; no partition is doubled. Adding a fifth consumer beyond the partition
count gains nothing, because there is no unclaimed partition left to assign.
[Kafka primer (topics/partitions/offsets, consumer groups): https://docs.confluent.io/platform/current/ksqldb/concepts/apache-kafka-primer.html]

## Poll and Commit Give You At-Least-Once Delivery

A consumer does not advance its position by reading. It polls from its last committed offset, then
commits explicitly when it is done processing:

```python
    def poll(self, consumer_id):
        # read undelivered records from committed offset onward; does NOT advance the offset
        records = []
        for part in self.assignment(consumer_id):
            records.extend(self.topic.read_from(part, self._committed[part]))
        return records

    def commit(self, consumer_id):
        for part in self.assignment(consumer_id):
            self._committed[part] = self.topic.end_offset(part)   # mark processed

    def seek(self, partition, offset):
        self._committed[partition] = offset                       # roll back -> replay (at-least-once)
```

If the consumer crashes between `poll` and `commit`, the offset stays where it was. The next poll
returns the same records. That is at-least-once delivery: a record is redelivered until the consumer
commits past it. `seek` makes this explicit: roll back to an earlier offset and those records replay.
Your consumer must be idempotent, because it will see them again.
[at-least-once / exactly-once: https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/]

## The Simulation Is Faithful, Not Real

The `Topic` and `ConsumerGroup` classes above run in-process with no broker, no network, and no
serialization. They model the contracts: key-hashed partitioning, monotonic offsets, partition
exclusivity, and uncommitted-offset replay. Microsoft Fabric Eventstream can source from Apache Kafka
(preview) and route to a Lakehouse or Eventhouse, so the vocabulary you build here maps directly to a
production path. The simulation lets you test that vocabulary offline, before any cloud resource exists.

## Core Concepts

- A topic is a partitioned, append-only log: records are never deleted on read, each record has a
  monotonic offset within its partition, and the same key always routes to the same partition.
- A consumer group assigns each partition to exactly one consumer, so adding consumers scales
  throughput up to the partition count, with no duplicate reads.
- Poll does not advance the offset; commit does. A crash between the two replays the records on the
  next poll, giving at-least-once delivery.
- `seek` lets you roll back a committed offset to any earlier position, forcing a replay; this is
  the mechanism at-least-once delivery rests on.

<div class="claude-handoff" data-exercise="exercises/module4/kafka-topics-and-consumer-groups/">

**Build It in Claude Code**: Build `kafka_sim.py` inside `module4-streaming/` with the `Topic` class (key-hashed partition routing, monotonic offsets, `append` and `read_from`), a `Producer`, and a `ConsumerGroup` (round-robin `assignment`, `poll` from the committed offset without advancing it, `commit` to mark processed, `seek` to roll back). Produce CDC events keyed by `doc_id`, then consume them across a two-consumer group; assert that every event for the same `doc_id` lands on the same partition, that every partition is assigned to exactly one consumer, that a normal poll-commit cycle delivers all events exactly once, and that a `seek` to an earlier offset replays those records (proving at-least-once delivery). Run offline pytest to verify all four assertions.

</div>
