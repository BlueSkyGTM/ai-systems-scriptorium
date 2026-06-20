# Exercise: The Data Seam (SQL, Streams, and Lineage)

## Goal

Add a data seam to `module5-serving/`: persist the telemetry the stack already emits into a local SQLite store, query it the way an operator does, put a freshness SLO on the Docling index, and record end-to-end lineage for every answer; all offline, standard-library SQL, no warehouse and no cloud.

## Why

Your traces, eval verdicts, and cost stamps are not dashboards; they are rows. A Production AI Engineer answers "where did the latency, cost, or quality go" with a query, owns a freshness SLO on the index, and can walk any answer back to the data that produced it. This exercise builds that seam on top of the serving stack you already have.

## Steps

1. In `module5-serving/`, create a `seam/` package with a SQLite store (`seam/store.py`). Use the stdlib `sqlite3`; no ORM, no service. Create three tables: `spans` (request_id, route, tenant, latency_ms, ts), `costs` (request_id, tenant, tokens_in, tokens_out, usd, ts), and `evals` (request_id, criterion, passed, ts).
2. Wire capture in. Have the app's request path append a `span` and a `cost` row per call (reuse the latency and cost numbers the Lesson 04 and Lesson 08 layers already compute), and the eval path append `eval` rows. Keep every table append-only.
3. Implement `seam/queries.py` with three operator queries as functions that return rows:
   - `p95_latency_by_route()`: p95 latency per route (compute the percentile in SQL, or in Python over the ordered rows).
   - `cost_by_tenant(since)`: total USD per tenant over a window.
   - `eval_pass_rate(window_days)`: pass-rate per criterion over a rolling window.
4. Put a freshness SLO on the Docling index from Lesson 11. When you build the index, write `seam/index_meta.json` with `built_at` and a `max_age_seconds`. Add `freshness_breach(now) -> bool` that returns True when the index is older than its SLO, and expose it on a `GET /health/freshness` route.
5. Record lineage. Add a `lineage` table (answer_id, request_id, corpus_version, chunk_id, eval_request_id) and stamp one row per answered query, pulling `corpus_version` from the Lesson 11 manifest. Implement `trace_answer(answer_id)` that walks an answer back to the corpus version and chunk that produced it and the eval verdict that graded it.
6. Write `smoke.py`: load a small fixture of telemetry, run the three queries and print them, flag a deliberately stale index, and resolve one lineage chain end to end. Exit zero only if all four behave.
7. Write `tests/test_seam.py`: assert `p95_latency_by_route` returns the known p95 for a fixed fixture, `freshness_breach` fires for an index past its max age and not before, and `trace_answer` returns the correct corpus version and chunk id for a seeded answer.

## Done when

- `python smoke.py` prints the three operator queries against the fixture, reports a freshness breach for the stale index, and walks one answer back to its corpus version; exits zero.
- `python -m pytest tests/` passes: the p95 query is correct, the freshness breach fires only when stale, and the lineage walk resolves to the right source version.
- The whole flow runs offline with the standard library alone; no warehouse, no Kafka, no cloud.
- `GET /health/freshness` returns the index's age against its SLO.

## Stretch

Simulate the streaming shape: add a tiny `seam/stream.py` that accepts "document-changed" events, marks the affected corpus version stale, and resets the freshness clock, so a stream of events drives re-index timing instead of a fixed schedule. Then write the one question a data engineer would actually ask of your telemetry that you could not answer before, and notice it is a `JOIN` across two of your tables. That join is the moment your telemetry became a dataset.
