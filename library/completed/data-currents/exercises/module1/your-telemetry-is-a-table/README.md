# Exercise: The Telemetry Store and the Foundational Operator Queries

## Goal

Build `module1-sql/`, a self-contained local telemetry store with the three foundational operator
queries a Production AI Engineer runs in any incident: p95 latency by route, cost by tenant, and eval
pass-rate over a window.

## Why

Your AI system already emits telemetry; the seam is the step that makes it queryable. The engineer who
can reach into the store and answer "where did the latency, the cost, or the quality go" in ten
minutes is worth more than the one who waits for the dashboard to refresh. This exercise builds that
muscle and seeds the artifact every later lesson in the module extends.

## Steps

1. Create `module1-sql/` at the project root. This is the shared artifact for the whole module. Inside
   it, write `db/schema.sql` with three `CREATE TABLE` statements:
   - `spans`: `trace_id TEXT PRIMARY KEY, route TEXT, tenant_id TEXT, latency_ms INTEGER, input_tokens INTEGER, output_tokens INTEGER, ts TIMESTAMP`
   - `eval_verdicts`: `id INTEGER PRIMARY KEY, trace_id TEXT REFERENCES spans, criterion TEXT, verdict TEXT, score REAL, created_at TIMESTAMP`
   - `cost_stamps`: `id INTEGER PRIMARY KEY, trace_id TEXT REFERENCES spans, tenant_id TEXT, total_cost_usd REAL, input_tokens INTEGER, output_tokens INTEGER, billed_at TIMESTAMP`

2. Write `db/seed.py`. Seed the store deterministically (fix the random seed so the answers are
   stable) with realistic synthetic telemetry:
   - 4 routes: `/summarize`, `/classify`, `/retrieve`, `/generate`; give `/summarize` a visibly higher
     p95 than the others (a different latency mean per route).
   - 3 tenants: `tenant_a`, `tenant_b`, `tenant_c`; make `tenant_a` the clear top weekly cost driver.
   - About 140 spans over a 14-day window; one eval verdict per span for each of two criteria
     (`groundedness`, `relevance`); set `tenant_b`'s groundedness pass-rate near 60% so it is the
     outlier; one cost stamp per span.
   - Print a per-table row count after seeding.

3. Write the three queries, one file each, in `queries/`: `01_p95_latency_by_route.sql`,
   `02_cost_by_tenant.sql`, `03_eval_pass_rate_daily.sql`. Use the DuckDB forms from the lesson
   (`QUANTILE_CONT(latency_ms, 0.95)` for p95).

4. Write `runner.py`. It opens a DuckDB connection, attaches the SQLite file
   (`db/telemetry.db`), reads a named query file, runs it, and prints the result as a formatted table.
   This is the tool you reuse for every query in the module.

5. Write `smoke.py`. It resets and reseeds the database, runs all three queries, and asserts:
   - `/summarize` is the top row of the p95 result (highest p95).
   - `tenant_a` is the top row of the cost result (highest weekly cost).
   - `tenant_b`'s `groundedness` pass-rate is between 55% and 65% (the seeded outlier).
   Print `PASS` or `FAIL` next to each assertion and exit non-zero on any failure.

## Done When

- `python db/seed.py` creates `db/telemetry.db` with three populated tables and prints the row counts.
- `python runner.py` prints any query's result; `/summarize` is visibly the slowest at p95, `tenant_a`
  is the top cost driver, and `tenant_b` is the groundedness outlier.
- `python smoke.py` prints `PASS` for all three assertions and exits 0.
- The whole flow runs offline: `sqlite3` (standard library) plus `duckdb` (one pip install), no cloud.

## Stretch

Add a fourth assertion: join `spans`, `eval_verdicts`, and `cost_stamps` on `trace_id` over the last
hour and confirm the result has exactly one row per span (no fan-out from the join). This is the
join-correctness check every multi-table telemetry seam needs before you trust an aggregate over it.
