# Window Functions and CTEs for AI Telemetry

The three queries in Lesson 01 answer the first round of questions in any incident. Then the
follow-up questions arrive: "Yes, p95 latency is up, but is it getting worse or better over the
last six hours?" "Which tenants ranked highest for cost this week, and how does that compare to
last week?" "The freshness breach fired at 2 a.m.; what was the last successful corpus reload
before it, and how long was the gap?" These questions cannot be answered with a `GROUP BY`. They
require two more tools: window functions and common table expressions.

Neither is exotic. Window functions have been standard SQL since SQL:2003. CTEs have been in
Azure SQL Database, Microsoft Fabric Warehouse, and DuckDB for years. What makes them feel hard
is that most tutorials introduce them abstractly; this lesson introduces them through the six
production questions an AI engineer actually asks, so you learn the pattern and the context at the
same time.

## Window Functions: Compute within a Partition, Keep Every Row

A `GROUP BY` collapses rows: one group becomes one output row. A window function computes over a
group but keeps every input row in the result. That distinction is what makes them useful for
AI telemetry.

The basic syntax:

```sql
<aggregate_or_ranking_function>(<column>)
OVER (
    PARTITION BY <group_column>
    ORDER BY <sort_column>
    ROWS BETWEEN <frame_start> AND <frame_end>
)
```

The `PARTITION BY` defines the group (like `GROUP BY`). The `ORDER BY` sorts rows within the
group. The `ROWS BETWEEN` defines the window frame: how many rows before and after the current
row to include in the computation. [MS-Learn: Azure Databricks SQL window functions support
`PARTITION BY`, `ORDER BY`, and `ROWS BETWEEN` frame specifications for aggregate and analytic
functions over partitioned data.]

### Query 4: Rolling Seven-Day Eval Pass-Rate

A rolling average smooths the noise out of daily pass-rate scores. Seven days is the standard
smoothing window for AI system quality metrics; it captures a full week's traffic pattern without
obscuring a genuine regression.

```sql
SELECT
    eval_day,
    criterion,
    pass_rate_pct,
    AVG(pass_rate_pct) OVER (
        PARTITION BY criterion
        ORDER BY eval_day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_pass_rate
FROM (
    SELECT
        DATE_TRUNC('day', created_at)  AS eval_day,
        criterion,
        ROUND(
            100.0 * SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*),
            1
        )                              AS pass_rate_pct
    FROM eval_verdicts
    GROUP BY eval_day, criterion
) daily
ORDER BY eval_day, criterion;
```

The inner subquery computes the daily pass-rate. The outer query applies a rolling average over
the preceding six rows (plus the current row: seven days total), partitioned by criterion so the
`groundedness` and `relevance` windows do not mix. The result is a smoothed quality trend line
per criterion that you can read or plot.

### Query 5: Per-Tenant Cost Rank, This Week vs. Last Week

When the monthly bill comes in and one tenant is flagged, the follow-up question is always "was
this tenant the top driver last week too, or did something change?"

```sql
WITH weekly_cost AS (
    SELECT
        tenant_id,
        DATE_TRUNC('week', billed_at)  AS cost_week,
        SUM(total_cost_usd)            AS weekly_cost_usd
    FROM cost_stamps
    WHERE billed_at >= NOW() - INTERVAL '14 days'
    GROUP BY tenant_id, cost_week
),
ranked AS (
    SELECT
        tenant_id,
        cost_week,
        weekly_cost_usd,
        RANK() OVER (
            PARTITION BY cost_week
            ORDER BY weekly_cost_usd DESC
        ) AS cost_rank
    FROM weekly_cost
)
SELECT
    this_week.tenant_id,
    this_week.cost_rank           AS rank_this_week,
    last_week.cost_rank           AS rank_last_week,
    this_week.weekly_cost_usd     AS cost_this_week,
    last_week.weekly_cost_usd     AS cost_last_week
FROM ranked this_week
LEFT JOIN ranked last_week
    ON this_week.tenant_id = last_week.tenant_id
   AND last_week.cost_week = this_week.cost_week - INTERVAL '1 week'
WHERE this_week.cost_week = DATE_TRUNC('week', NOW())
ORDER BY this_week.cost_rank;
```

The CTE `weekly_cost` builds the per-tenant, per-week aggregate. The CTE `ranked` applies
`RANK()` within each week's partition. The final `SELECT` self-joins on tenant and one-week
offset to get both weeks in one row. A tenant that ranked 1 last week and 8 this week has not
changed behavior; something else changed around them. A tenant that jumped from 8 to 1 in a week
is the investigation.

### Query 6: Latency Delta between Deployment Windows

When you deploy a new model or prompt and latency moves, you want to see it in numbers, not feel
it in a graph. This query computes the p95 latency for each route before and after a deployment
timestamp and returns the delta.

```sql
WITH before_deploy AS (
    SELECT
        route,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_ms
    FROM spans
    WHERE ts BETWEEN :deploy_ts - INTERVAL '2 hours' AND :deploy_ts
    GROUP BY route
),
after_deploy AS (
    SELECT
        route,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_ms
    FROM spans
    WHERE ts BETWEEN :deploy_ts AND :deploy_ts + INTERVAL '2 hours'
    GROUP BY route
)
SELECT
    b.route,
    b.p95_ms                              AS p95_before,
    a.p95_ms                              AS p95_after,
    a.p95_ms - b.p95_ms                   AS delta_ms,
    ROUND(100.0 * (a.p95_ms - b.p95_ms) / b.p95_ms, 1) AS delta_pct
FROM before_deploy b
JOIN after_deploy a ON b.route = a.route
ORDER BY delta_ms DESC;
```

The `:deploy_ts` is a bound parameter. Run this query with the timestamp of your last deploy and
you immediately see which routes got faster, which got slower, and by how much. [MS-Learn: Azure
SQL Database parameterized queries via T-SQL use `@deploy_ts` syntax rather than `:deploy_ts`;
the pattern translates directly for Python's `sqlite3` module using the `?` placeholder form.]

## Common Table Expressions: Name Your Intermediate Results

A CTE is a named subquery that lives at the top of a statement and can be referenced below it
like a table. Its power is readability: a diagnostic query that requires four steps of data
preparation can be written as four named CTEs followed by a clear final `SELECT`, rather than as
a nested pyramid of subqueries four levels deep.

The syntax:

```sql
WITH cte_name AS (
    SELECT ...
),
second_cte AS (
    SELECT ... FROM cte_name ...
)
SELECT ... FROM second_cte ...;
```

CTEs are not a performance feature; they are a clarity feature. The query planner may or may not
materialize a CTE; that is the engine's decision. What CTEs guarantee is that the human reading
the query in three months (probably you) can understand it. [MS-Learn: Fabric Data Warehouse and
Azure SQL Database both support CTEs in T-SQL using the `WITH` clause; CTEs can reference each
other when defined in order within the same `WITH` block.]

### Query 7: Freshness Breach Diagnosis Chain

The freshness monitor fires: the corpus is stale. You know the breach happened. You want to know
when the last successful reload was, how long the gap is, and what the current index age is.

```sql
WITH last_successful_load AS (
    SELECT
        source_id,
        MAX(loaded_at) AS last_load_ts
    FROM corpus_loads
    WHERE status = 'success'
    GROUP BY source_id
),
freshness_status AS (
    SELECT
        s.source_id,
        s.last_load_ts,
        NOW() - s.last_load_ts                        AS index_age,
        f.max_age_hours,
        (NOW() - s.last_load_ts) > (f.max_age_hours * INTERVAL '1 hour') AS is_stale
    FROM last_successful_load s
    JOIN freshness_slos f ON s.source_id = f.source_id
)
SELECT
    source_id,
    last_load_ts,
    index_age,
    max_age_hours,
    is_stale
FROM freshness_status
WHERE is_stale = TRUE
ORDER BY index_age DESC;
```

`corpus_loads` is the table your ingestion pipeline writes one row to on every load attempt.
`freshness_slos` is the table your team owns that records the maximum tolerated age for each
source. The CTE chain: find the last success for each source, compute the current age, compare
to the SLO, return only the breached sources. This is a query you run after a freshness alert
fires to triage which sources are stale and by how much.

### Query 8: Lineage Walk (Answer to Source Version)

The eval pass-rate dropped for the `/compliance` route on Tuesday. You suspect a corpus reload
changed the retrieved chunks for common queries. This query walks the lineage from a specific
answer back to the corpus version that produced it.

```sql
WITH answer_context AS (
    SELECT
        a.answer_id,
        a.trace_id,
        a.retrieved_chunk_ids
    FROM answers a
    WHERE a.answer_id = :target_answer_id
),
chunk_sources AS (
    SELECT
        ac.answer_id,
        c.chunk_id,
        c.corpus_version,
        c.source_doc_id,
        c.source_doc_version
    FROM answer_context ac
    -- unnest the array of chunk ids into individual rows
    JOIN chunks c ON c.chunk_id = ANY(ac.retrieved_chunk_ids)
),
doc_versions AS (
    SELECT
        cs.answer_id,
        cs.chunk_id,
        cs.source_doc_id,
        cs.source_doc_version,
        d.last_modified_at,
        d.content_hash
    FROM chunk_sources cs
    JOIN source_documents d
        ON d.doc_id     = cs.source_doc_id
       AND d.version_id = cs.source_doc_version
)
SELECT * FROM doc_versions ORDER BY chunk_id;
```

Each row in the result is one chunk the answer drew on, with the exact document version and
content hash that produced it. If the content hash changed between Tuesday's load and Monday's
load, you have your answer: the corpus reload swapped the paragraph the model was citing. This is
the lineage lookup M5 L14 described; Module 6 will build the full lineage store. Here you write
the query manually to understand the shape of the data before you automate it.

## The Full Diagnostic Playbook

These eight queries, run in order, diagnose the most common production incidents:

1. P95 latency by route (current window)
2. Cost by tenant (current week)
3. Eval pass-rate by day and criterion (rolling 14 days)
4. Rolling 7-day pass-rate to smooth noise
5. Cost rank comparison, this week vs. last week
6. Latency delta around a specific deployment
7. Freshness breach diagnosis (which sources are stale, by how much)
8. Lineage walk from answer back to source document version

Queries 1-3 come from Lesson 01. Queries 4-8 come from this lesson. Together they are the twelve
operator queries the blueprint named; the remaining four (corpus freshness trend, eval regression
attribution, token burn rate by model, batch vs. streaming freshness gap) follow the same patterns
and will appear as exercises in later modules.

## Core Concepts

- Window functions compute over a partition of rows and return one result per input row; `PARTITION
  BY` defines the group, `ORDER BY` defines the sort within the group, and `ROWS BETWEEN` defines
  the sliding frame. Unlike `GROUP BY`, the source rows are preserved.
- The rolling 7-day eval pass-rate (`AVG ... OVER ... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW,
  partitioned by criterion`) is the standard pattern for smoothing AI quality metrics; it removes
  day-to-day noise while preserving genuine weekly trends.
- CTEs (`WITH name AS (...)`) name intermediate query steps; they improve readability without
  changing semantics, and the freshness breach and lineage walk queries each require three or four
  named steps to be legible. [MS-Learn: Azure SQL T-SQL CTE syntax with `WITH`.]
- The Production AI Engineer's diagnostic playbook runs eight queries in order: latency, cost,
  eval pass-rate, rolling smoothed pass-rate, rank comparison, deployment delta, freshness breach,
  lineage walk. These cover the full surface of what can go wrong in a production AI system.

<div class="claude-handoff" data-exercise="draft/exercises/02-window-functions-ctes/">

**Build It in Claude Code**: Extend the `module1-sql/` artifact from Lesson 01 with four advanced
queries. Add a `corpus_loads` table and a `freshness_slos` table to the existing SQLite store,
seed them with two sources (one stale, one fresh). Then implement and test: (1) the rolling 7-day
eval pass-rate window query, (2) the per-tenant cost rank comparison (this week vs. last week),
(3) the latency delta query around a synthetic deploy timestamp, and (4) the freshness breach
diagnosis CTE chain. Prove it: `python smoke.py` seeds all tables and runs all four queries,
printing the result set and a pass/fail assertion for each. `python -m pytest tests/` asserts the
rolling average is numerically correct for a known 7-day sequence, the rank comparison correctly
identifies the tenant that jumped in rank, the latency delta fires only for routes that changed,
and the freshness breach fires for the stale source only.

</div>
