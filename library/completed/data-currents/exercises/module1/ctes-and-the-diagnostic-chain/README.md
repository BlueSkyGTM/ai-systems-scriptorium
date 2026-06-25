# Exercise: CTEs and the Diagnostic Chain

## Goal

Extend `module1-sql/` with the freshness-breach CTE chain and the deploy-delta query, gated by
`smoke.py` assertions that prove each query fires on the right data and ignores the rest.

## Why

The freshness breach and the deploy regression are the two most common operational questions in a
production AI system. Writing them as named CTE chains is what makes them debuggable at 2 a.m.
This exercise cements the pattern by building it against data you seeded yourself.

## Steps

1. Open `module1-sql/db/schema.sql` and add the two new tables at the end:

   ```sql
   CREATE TABLE corpus_loads (
       id        INTEGER PRIMARY KEY,
       source_id TEXT NOT NULL,
       status    TEXT NOT NULL,
       loaded_at TIMESTAMP NOT NULL
   );
   CREATE TABLE freshness_slos (
       source_id     TEXT PRIMARY KEY,
       max_age_hours INTEGER NOT NULL
   );
   ```

2. Extend `db/seed.py` to populate the new tables with two sources:
   - `source_a`: SLO of 24 hours; most recent successful load is 30 hours ago (breaches the SLO).
     Add at least one `failure` row more recent than the last success, so the query must look past it.
   - `source_b`: SLO of 48 hours; most recent successful load is 2 hours ago (within SLO, fresh).
   Seed enough spans across two time windows around a fixed deploy timestamp (e.g. `2024-01-15
   12:00:00`) so the deploy-delta query has data on both sides. At least two routes must appear in
   both windows; one route may appear only in the after window (to confirm it is excluded from the
   join result).

3. Write `queries/07_freshness_breach.sql` with the exact CTE chain from the lesson:
   `last_successful_load` then `freshness_status`, filtering to `WHERE is_stale` and ordering by
   `index_age DESC`.

4. Write `queries/06_latency_delta_around_deploy.sql` with the `before_deploy` / `after_deploy`
   pattern from the lesson. Use `$deploy_ts` as the bound parameter name (DuckDB form).

5. Extend `smoke.py` with two new assertion blocks that run after the existing three pass:
   - Run Q7. Assert the result contains exactly one row and that its `source_id` is `source_a`.
     Print `PASS: freshness breach fires for stale source only` or `FAIL` with detail.
   - Run Q6 with `deploy_ts` bound to the seeded timestamp. Assert every row in the result
     corresponds to a route present on both sides of the window (no route appears with a null
     `p95_before` or `p95_after`). Print `PASS: deploy-delta covers bilateral routes only` or `FAIL`.
   Exit non-zero on any failure.

## Done When

- `python db/seed.py` seeds all five tables and prints row counts for each.
- `python smoke.py` prints `PASS` for all five assertions (three from the prior exercise plus the
  two new ones) and exits 0.
- The whole flow runs offline: `sqlite3` (standard library) plus `duckdb` (one pip install).

## Stretch

Add a third corpus source, `source_c`, whose most recent row in `corpus_loads` has `status =
'failure'` and no prior success rows at all. Run Q7 and confirm `source_c` does not appear in the
breach results (a source with no successful load history is not surfaced by this query; it would
require a separate "never loaded" check). Add a `smoke.py` assertion that the breach result still
contains exactly one row after you add `source_c`.
