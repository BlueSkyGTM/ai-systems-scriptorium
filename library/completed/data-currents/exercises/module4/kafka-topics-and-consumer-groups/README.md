# Exercise: Kafka Topics and Consumer Groups

## Goal

Build `kafka_sim.py` inside `module4-streaming/` with a `Topic`, a `Producer`, and a
`ConsumerGroup` that together simulate Kafka's partitioning, offset, and at-least-once delivery
contracts in-process.

## Why

The streaming pipeline needs a durable, ordered substrate between the CDC source and the consumer.
Understanding how topics partition by key and how consumer groups divide that work is the prerequisite
for everything downstream in this module.

## Steps

1. Create `module4-streaming/kafka_sim.py`. Define `Record` as a dataclass holding `key`, `value`,
   `partition`, and `offset`.

2. Implement `Topic(name, num_partitions=4)`:
   - `_partition_for_key(key)` routes by MD5 hash mod partition count.
   - `append(value, key)` writes to the correct partition, assigns the next monotonic offset, and
     returns `(partition, offset)`.
   - `read_from(partition, from_offset)` returns all records at or after `from_offset`.
   - `end_offset(partition)` returns the length of that partition's list.

3. Implement `Producer(topic)` with a `send(value, key)` method that calls `topic.append`.

4. Implement `ConsumerGroup(topic, num_consumers)`:
   - `assignment(consumer_id)` returns the list of partitions assigned to that consumer (round-robin:
     partition `p` belongs to consumer `p % num_consumers`).
   - `poll(consumer_id)` reads from the committed offset on each assigned partition without advancing
     it; returns all unread records.
   - `commit(consumer_id)` advances the committed offset on each assigned partition to
     `topic.end_offset(partition)`.
   - `seek(partition, offset)` sets the committed offset for one partition to `offset`.

5. Write `tests/test_kafka_sim.py` with four assertions (each a separate test):
   - Every event for the same `doc_id` lands on the same partition.
   - Every partition is assigned to exactly one consumer in the group (no gaps, no overlaps).
   - A normal poll-then-commit cycle delivers all produced events; a second poll returns nothing.
   - A `seek` to an earlier offset causes the next poll to replay those records.

6. Run `pytest module4-streaming/tests/test_kafka_sim.py` offline.

## Done When

- `pytest` exits 0 with all four tests passing.
- The same `doc_id` always maps to the same partition across multiple `append` calls.
- The union of all consumer assignments equals the full partition set with no duplicates.
- A second `poll` after `commit` returns an empty list.
- After `seek(partition, earlier_offset)`, `poll` returns the records from that offset onward.

## Stretch

Add a second consumer (raise `num_consumers` to 2) and assert that the partition assignment splits
cleanly: consumer 0 holds partitions 0 and 2, consumer 1 holds 1 and 3, and the union still covers
all four partitions with no overlap.
