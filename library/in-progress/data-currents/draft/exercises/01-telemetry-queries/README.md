# Exercise: Telemetry Seam and Foundational Operator Queries

## Goal

Add a SQLite telemetry seam to `module5-serving/` and implement the three foundational operator
queries a Production AI Engineer runs in any production incident: p95 latency by route, total
cost by tenant, and eval pass-rate over a rolling window.

## Why

Your AI system already emits telemetry; the seam is the step that makes it queryable. A
Production AI Engineer who can reach into the trace store and answer "where did the latency, the
cost, or the quality go" in ten minutes is more valuable than one who waits for the dashboard to
refresh. This exercise builds that muscle: you write the schema, load synthetic but realistic
data, and verify every query against known values.

## Steps

1. Create `module1-sql/` at the project root (sibling to `module5-serving/`). This is the shared
   artifact for the whole module. Inside it, create `db/schema.sql` with three `CREATE TABLE`
   statements:
   - `spans`: `trace_id TEXT PRIMARY KEY, route TEXT, tenant_id TEXT, latency_ms INTEGER,
     input_tokens INTEGER, output_tokens INTEGER, ts TIMESTAMP`
   - `eval_verdicts`: `id INTEGER PRIMARY KEY, trace_id TEXT REFERENCES spans, criterion TEXT,
     verdict TEXT, score REAL, created_at TIMESTAMP`
   - `cost_stamps`: `id INTEGER PRIMARY KEY, trace_id TEXT REFERENCES spans, tenant_id TEXT,
     total_cost_usd REAL, input_tokens INTEGER, output_tokens INTEGER, billed_at TIMESTAMP`

2. Create `db/seed.py`. Seed the store with realistic synthetic data:
   - 4 routes: `/summarize`, `/classify`, `/retrieve`, `/generate`
   - 3 tenants: `tenant_a`, `tenant_b`, `tenant_c`
   - 140 spans over 14 days; distribute latency so `/summarize` has visibly higher p95 than the
     others (use a normal distribution with a different mean per route)
   - One eval verdict per span for each of two criteria (`groundedness`, `relevance`); set
     `tenant_b`'s groundedness pass-rate to 60% so it is the clear outlier
   - One cost stamp per span; `tenant_a` drives the highest weekly total by a clear margin

3. Create `queries/01_p95_latency_by_route.sql` with the p95 latency query from Lesson 01. Use
   DuckDB's `QUANTILE_CONT(latency_ms, 0.95)` syntax (DuckDB reads the SQLite file directly via
   `duckdb.connect('db/telemetry.db')`).

4. Create `queries/02_cost_by_tenant.sql` with the weekly cost query from Lesson 01.

5. Create `queries/03_eval_passrate_by_day_criterion.sql` with the 14-day pass-rate query from
   Lesson 01.

6. Create `runner.py` that: opens the DuckDB connection to `db/telemetry.db`, reads each query
   file, executes it, and prints the result as a formatted table. This is the tool you will use
   throughout the module to run any query against the telemetry store.

7. Create `smoke.py`. It calls `seed.py` to reset the database, runs all three queries via
   `runner.py`, and asserts:
   - `/summarize` appears in row 1 of the p95 latency result (highest p95)
   - `tenant_a` appears in row 1 of the cost result (highest weekly cost)
   - `tenant_b`'s `groundedness` pass-rate is between 55% and 65% (confirming the seeded outlier)
   Print `PASS` or `FAIL` next to each assertion.

8. Create `tests/test_queries.py` with three pytest test functions, one per query, asserting the
   same conditions as `smoke.py` but using pytest `assert` statements for CI compatibility.

## Done When

- `python db/seed.py` creates `db/telemetry.db` with three populated tables and prints a summary:
  rows seeded per table.
- `python runner.py` prints the result of all three queries; the `/summarize` p95 is visibly
  higher than the others, `tenant_a` is the top cost driver, and the `groundedness` pass-rate
  shows `tenant_b` as the outlier.
- `python smoke.py` prints `PASS` for all three assertions.
- `python -m pytest tests/` passes all three tests.
- The whole flow runs with no cloud calls: `sqlite3` (stdlib) + `duckdb` (pip), offline.

## Stretch

Add a fourth assertion to `smoke.py`: join `spans`, `eval_verdicts`, and `cost_stamps` on
`trace_id` for the last 24 hours and confirm that the query returns exactly one row per span (no
fan-out from the join). This is the join-correctness check that every multi-table telemetry seam
needs before you trust aggregate queries over it.
