# Module 4 — Streaming and Change-Data-Capture — Build Plan (self-locked)

Status: **PLAN SELF-LOCKED 2026-06-21** (straight-through mandate; gates self-cleared). M4 adds the
sources that cannot wait for the nightly run: a change-data-capture feed, the Kafka substrate that
carries it, and the continuous freshness monitor that replaces the batch check for streaming legs.

## The stage in one line

M3 scheduled the nightly batch; M4 handles what needs to be in the index in seconds, not hours. Seam:
the freshness SLO is the decision variable; it tells you which sources stream and which batch, and the
streaming leg needs a continuous lag monitor, not a once-a-night gate.

## Settled decisions

1. **Throughline extends M2 + M3.** `module4-streaming/` consumes a CDC event feed and applies each
   change to the corpus via M2's idempotent MERGE (per-event upsert), so a changed document lands in
   seconds. The streaming freshness monitor extends M3's freshness gate to a continuous lag measure.
2. **Teach Kafka/Eventstream; run an offline simulation.** No broker runs offline, so the artifact
   simulates the streaming substrate in-process: a `Topic` (an append log with offsets), a
   `ConsumerGroup` (partition assignment + at-least-once delivery), and a CDC source that emits
   insert/update/delete events. The lessons teach real Kafka (topics, partitions, consumer groups,
   offsets) and Microsoft Fabric Eventstream / Real-Time Intelligence as the production substrate,
   grounded in MS-Learn. The artifact-engineer confirms the simulation is deterministic + pytest-green.
3. **CDC is the bridge from batch to stream.** A change-data-capture feed turns a table's mutations
   into an event stream; the consumer applies them with the same MERGE semantics as the batch load, so
   correctness is identical and only the latency differs.
4. **Streaming freshness is a continuous lag, not a nightly check.** The monitor measures
   event-time-to-applied lag per source and breaches when lag exceeds a seconds-scale SLO, connecting
   to M3's alerting.

## Proposed M4 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | Some sources cannot wait for the nightly run; here is CDC, the Kafka substrate, and the streaming freshness monitor. | concept |
| 1 | `streaming-vs-batch` | The freshness SLO is the decision: seconds-to-index means streaming, hours-to-index means batch; you choose per source, not per system. | concept/build |
| 2 | `change-data-capture` | CDC turns a table's inserts, updates, and deletes into an event stream the pipeline consumes and applies with the same MERGE. | build |
| 3 | `kafka-topics-and-consumer-groups` | A topic is a durable, partitioned append log; a consumer group divides its partitions for scale and tracks offsets for at-least-once delivery. | build |
| 4 | `the-streaming-freshness-monitor` | Streaming freshness is a continuous event-to-applied lag measure that breaches at seconds scale; closes the module by extending M3's gate to the streaming leg. | build |

## The artifact + oracle (locked first)

`module4-streaming/`: an in-process `Topic`/`ConsumerGroup` (offsets, partitions, at-least-once), a CDC
source emitting change events, a streaming consumer that applies each event via M2's MERGE, and a
`lag_monitor` measuring per-source event-to-applied lag. Oracle (`smoke.py` + `pytest`, offline,
deterministic): a produced event is consumed and applied (the corpus reflects the change); at-least-once
redelivery is idempotent (a redelivered event applies the MERGE without creating a duplicate version);
consumer-group partition assignment covers all partitions; the lag monitor reports low lag for a kept-up
consumer and breaches when the consumer falls behind a seconds-scale SLO. Negative: a stalled consumer
trips the lag breach; a malformed event is rejected without corrupting the corpus.

## Fleet plan

- **Haiku fetch (2):** (a) MS-Learn Fabric Eventstream + Real-Time Intelligence + Eventhouse/KQL + CDC
  patterns, verified URL pack; (b) Kafka fundamentals (topics, partitions, consumer groups, offsets,
  at-least-once vs exactly-once) from authoritative docs + the made-with-ml serving seam if relevant.
- **Sonnet artifact-engineer (1):** builds + tests `module4-streaming/`; returns byte-identical code +
  a green run; confirms the simulation is deterministic.
- **Sonnet authors (4):** L1–L4 around the locked code + grounding.
- **Opus conductor:** overview, schema/oracle lock, review, em-dash sweep + `mdbook build`, ship + push.
