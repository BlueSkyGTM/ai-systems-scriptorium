# Exercise: Window Functions and CTE Diagnostic Chains

## Goal

Extend the `module1-sql/` telemetry store from Exercise 01 with two new tables (`corpus_loads`,
`freshness_slos`) and implement four advanced queries: a rolling 7-day eval pass-rate, a
per-tenant cost rank comparison across two weeks, a p95 latency delta around a deployment
timestamp, and a freshness breach CTE chain.

## Why

The three foundational queries from Exercise 01 answer "what is the current state?" Window
functions and CTEs answer "how did we get here?" and "what changed?" The rolling pass-rate query
is how you distinguish a genuine quality regression from daily noise. The rank comparison is how
you identify tenant-level behavior changes week over week. The deployment delta is how you
attribute a latency shift to a specific deploy. The freshness breach chain is how you triage a
stale index alert. These four patterns cover the investigative half of the operator playbook.

## Steps

1. Add two tables to `db/schema.sql`:
   - `corpus_loads`: `id INTEGER PRIMARY KEY, source_id TEXT, status TEXT, loaded_at TIMESTAMP`
     Status values: `'success'` or `'failed'`.
   - `freshness_slos`: `source_id TEXT PRIMARY KEY, max_age_hours INTEGER`

2. Extend `db/seed.py` with data for both new tables:
   - Two sources: `corpus_docs` (max age 8 hours) and `corpus_tickets` (max age 2 hours).
   - Seed `corpus_docs` with 14 days of successful loads at 2 a.m. daily, plus a gap: no
     successful load in the last 10 hours (so it is 2 hours stale against its 8-hour SLO).
   - Seed `corpus_tickets` with a last successful load 4 hours ago (within its 2-hour SLO, so
     it should NOT appear as stale). Seed one recent failed load for `corpus_tickets` at 1 hour
     ago to confirm that failed loads do not reset the freshness clock.

3. Create `queries/04_rolling_7d_passrate.sql` with the rolling 7-day eval pass-rate window query
   from Lesson 02. It should return one row per (day, criterion) pair for the last 14 days.

4. Create `queries/05_tenant_cost_rank.sql` with the two-week cost rank comparison CTE from Lesson
   02. It should return one row per tenant showing rank this week, rank last week, cost this week,
   and cost last week.

5. Create `queries/06_latency_delta.sql` with the deployment delta CTE from Lesson 02. Parameterize
   the deploy timestamp as a Python string substitution in `runner.py` (pass it as a variable;
   do not hardcode it in the SQL file).

6. Create `queries/07_freshness_breach.sql` with the freshness breach CTE chain from Lesson 02.
   It should return only sources where `is_stale = TRUE`.

7. Update `runner.py` to accept an optional `--query N` flag that runs only query N (1-7) by
   number. Without the flag, it runs all queries in order. For query 06, inject a hardcoded
   deploy timestamp from 6 days ago (midpoint of the seeded data range) so the smoke test can
   assert against it.

8. Extend `smoke.py` with four new assertions:
   - The rolling pass-rate result contains 28 rows (14 days x 2 criteria); the last day's
     rolling average for `groundedness` is numerically within 5 percentage points of the raw
     daily value for that day (confirming the window is computing correctly).
   - `tenant_a` ranks 1 this week and last week (confirming the seed data is stable across both
     weeks and the rank query is correct).
   - The latency delta query returns `/summarize` with a non-zero delta (confirming the route
     appears in both pre- and post-deploy windows in the seeded data).
   - Only `corpus_docs` appears in the freshness breach result (`corpus_tickets` is within SLO).

9. Extend `tests/test_queries.py` with four new test functions, one per new query, asserting the
   same conditions as the new `smoke.py` assertions.

## Done When

- `python db/seed.py` seeds all five tables and prints a summary row count for each.
- `python runner.py` runs all seven queries in order with formatted output.
- `python runner.py --query 7` runs only the freshness breach query and returns one row:
  `corpus_docs`.
- `python smoke.py` prints `PASS` for all seven assertions (three from Exercise 01, four new).
- `python -m pytest tests/` passes all seven tests.

## Stretch

Add a lineage skeleton: create a `answers` table (`answer_id TEXT PRIMARY KEY, trace_id TEXT,
retrieved_chunk_ids TEXT`) and a `chunks` table (`chunk_id TEXT PRIMARY KEY, corpus_version TEXT,
source_doc_id TEXT, source_doc_version TEXT`). Seed one answer with three chunk ids. Write a CTE
query that walks from the answer id back to the three source document versions. This is the shape
of the full lineage walk that Module 6 will build into a production lineage store; doing it here
in SQL-only form (no pipeline, no automation) locks in the schema contract before the pipeline
code is written.
