# CTEs and the Diagnostic Chain

The freshness alert fires at 2 a.m. You know the breach happened; you need to know when the last
successful corpus load ran and how wide the gap is. That question has three steps: find the last good
load per source, compute the current age, compare it to the SLO, and return only the breached sources.
You can write those steps as a pyramid of nested subqueries, or you can name each step and read them
top to bottom. The second form is the one you can actually debug at 2 a.m.

A common table expression (CTE) names an intermediate result at the top of a query so you can
reference it below like a table. You build the diagnostic chain once, and the shape is obvious to
anyone who reads it six months later, including you.

## Two New Tables

This lesson extends `module1-sql/` with two tables your ingestion pipeline owns.

```sql
CREATE TABLE corpus_loads (
    id        INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL,
    status    TEXT NOT NULL,   -- 'success' | 'failure'
    loaded_at TIMESTAMP NOT NULL
);
CREATE TABLE freshness_slos (
    source_id     TEXT PRIMARY KEY,
    max_age_hours INTEGER NOT NULL
);
```

`corpus_loads` records every load attempt: one row per run, with the source, the outcome, and the
timestamp. `freshness_slos` records your team's tolerance per source: how many hours old is too old.
These two tables are the inputs to the freshness breach diagnosis.

## The CTE Syntax

Before looking at the full query, see the skeleton.

```sql
WITH cte_name AS (
    SELECT ...
),
second_cte AS (
    SELECT ... FROM cte_name ...
)
SELECT ... FROM second_cte ...;
```

Each CTE is a named block inside the `WITH` clause, separated by commas. A CTE can reference any CTE
defined above it in the same `WITH` block. The final `SELECT` sees all of them as if they were tables.
[Common table expressions in T-SQL: https://learn.microsoft.com/sql/t-sql/queries/with-common-table-expression-transact-sql]

One thing CTEs do not do: change how the query runs. The planner decides whether to materialize a CTE
or inline it. What CTEs guarantee is that the human reading the query can understand it. Clarity is
the feature.

## The Freshness Breach Diagnosis

Q7 is the query you run after the alert fires.

```sql
WITH last_successful_load AS (
    SELECT source_id, MAX(loaded_at) AS last_load_ts
    FROM corpus_loads
    WHERE status = 'success'
    GROUP BY source_id
),
freshness_status AS (
    SELECT
        s.source_id, s.last_load_ts,
        NOW() - s.last_load_ts AS index_age,
        f.max_age_hours,
        (NOW() - s.last_load_ts) > (f.max_age_hours * INTERVAL '1 hour') AS is_stale
    FROM last_successful_load s
    JOIN freshness_slos f ON s.source_id = f.source_id
)
SELECT source_id, last_load_ts, index_age, max_age_hours, is_stale
FROM freshness_status
WHERE is_stale
ORDER BY index_age DESC;
```

Read the chain step by step. `last_successful_load` filters to successful rows only and takes the most
recent one per source. `freshness_status` joins that result against `freshness_slos` to compute the
current age and evaluate the boolean breach flag. The final `SELECT` filters to the breached sources
and sorts by age, putting the most overdue source first.

If you wrote this as nested subqueries, the breach comparison would be buried three levels deep. Named
as CTEs, each step is legible on its own. That is the diagnostic chain: a series of named steps that
build on each other, reading top to bottom.

Note that only successful loads count. A source whose most recent load failed is still judged by its
last *successful* load, not by the failure timestamp. That is the semantically correct behavior: a
failed reload did not refresh the index.

## The Deploy-Delta Pattern

Q6 uses the same two-CTE structure, this time to isolate before and after windows around a deploy
timestamp.

```sql
WITH before_deploy AS (
    SELECT route, QUANTILE_CONT(latency_ms, 0.95) AS p95_ms
    FROM spans
    WHERE ts BETWEEN $deploy_ts::TIMESTAMP - INTERVAL '2 hours' AND $deploy_ts::TIMESTAMP
    GROUP BY route
),
after_deploy AS (
    SELECT route, QUANTILE_CONT(latency_ms, 0.95) AS p95_ms
    FROM spans
    WHERE ts BETWEEN $deploy_ts::TIMESTAMP AND $deploy_ts::TIMESTAMP + INTERVAL '2 hours'
    GROUP BY route
)
SELECT
    b.route, b.p95_ms AS p95_before, a.p95_ms AS p95_after,
    a.p95_ms - b.p95_ms AS delta_ms,
    ROUND(100.0 * (a.p95_ms - b.p95_ms) / b.p95_ms, 1) AS delta_pct
FROM before_deploy b
JOIN after_deploy a ON b.route = a.route
ORDER BY delta_ms DESC;
```

`before_deploy` computes the p95 for each route in the two hours leading up to the deploy.
`after_deploy` computes the same for the two hours following it. The final `SELECT` joins on route and
computes the delta in absolute milliseconds and percentage. The route at the top of the result is the
one that regressed the most.

The `$deploy_ts` is a bound parameter you supply at runtime with the exact deploy timestamp. The
syntax is DuckDB's form; a warehouse using T-SQL uses `@deploy_ts`, and Python's standard library
`sqlite3` module uses `?`. The pattern is the same across dialects.

The `QUANTILE_CONT` call is the same function the prior lesson taught for p95 latency. You are not
learning a new function here; you are seeing how CTEs let you compose a function you already know into
a before/after comparison without repeating the window logic or nesting it inside itself.

## Core Concepts

- A CTE names an intermediate result at the top of a query; later CTEs and the final `SELECT` see it
  as a table. A chain of named CTEs makes a multi-step diagnosis readable top to bottom rather than
  inside out.
- CTEs are a clarity feature, not a performance feature. The query planner decides whether to
  materialize them; what they guarantee is that the query is legible.
- The freshness breach chain (`last_successful_load` then `freshness_status`) isolates only successful
  loads before computing the age, so a source with a recent failure is still judged by its last good
  load.
- The deploy-delta pattern (`before_deploy` / `after_deploy`) uses two CTEs to isolate two time
  windows and join them on route; `delta_ms` and `delta_pct` show exactly which routes regressed and
  by how much.

The breach fires, you run the chain, you see the gap. Every minute you spend on nested subquery
archaeology is a minute the index is serving stale results to your retrieval system.

<div class="claude-handoff" data-exercise="exercises/module1/ctes-and-the-diagnostic-chain/">

**Build It in Claude Code**: Add `corpus_loads` and `freshness_slos` to `db/schema.sql`; extend
`db/seed.py` to insert one source whose last successful load exceeds its SLO (stale) and one whose
last successful load is recent (fresh); write `queries/07_freshness_breach.sql` and
`queries/06_latency_delta_around_deploy.sql` using the verbatim CTE forms from the lesson; and extend
`smoke.py` to assert that the freshness breach query returns exactly the stale source and that the
deploy-delta query returns rows for every route present on both sides of the seeded deploy timestamp.

</div>
