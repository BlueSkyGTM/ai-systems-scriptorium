# Window Functions

The daily pass-rate query from the last lesson tells you the number for today. What it cannot tell you is whether the trend is improving or collapsing: "is it getting worse or better?" needs a rolling average, not a point. "Did this tenant rank high last week too?" needs a rank comparison across two time windows, not a single aggregate. These are the questions `GROUP BY` cannot answer, and they are the ones that drive the real follow-up work.

## What a Window Function Is

A `GROUP BY` collapses rows: one group becomes one output row. A window function computes over a partition of rows and keeps every input row in the result. The source data is preserved; the computed column rides alongside it.

The generic form:

```sql
<function>(<column>)
OVER (
    PARTITION BY <group_column>
    ORDER BY <sort_column>
    ROWS BETWEEN <n> PRECEDING AND CURRENT ROW
)
```

`PARTITION BY` defines the group, the way `GROUP BY` does. `ORDER BY` sorts rows within the partition before the computation runs. `ROWS BETWEEN` sets the frame: which preceding and following rows to include in each computation. Leave the frame out and the engine uses a default that depends on whether you specified `ORDER BY`; always state it explicitly for rolling aggregates so the behavior is unambiguous.
[MS-Learn OVER clause: https://learn.microsoft.com/sql/t-sql/queries/select-over-clause-transact-sql]

## Query 4: Rolling 7-Day Eval Pass-Rate

The daily pass-rate chart is noisy. One low-traffic day with two failures swings the number; one high-traffic day with perfect results pulls it back. The rolling seven-day average removes that noise: it always covers a full week's traffic pattern, so a genuine regression shows up as a sustained drop rather than a spike.

```sql
SELECT
    eval_day, criterion, pass_rate_pct,
    AVG(pass_rate_pct) OVER (
        PARTITION BY criterion
        ORDER BY eval_day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_pass_rate
FROM (
    SELECT
        DATE_TRUNC('day', created_at)  AS eval_day,
        criterion,
        ROUND(100.0 * SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate_pct
    FROM eval_verdicts
    GROUP BY eval_day, criterion
) daily
ORDER BY eval_day, criterion;
```

The inner subquery is the daily aggregate from the last lesson: one row per `(eval_day, criterion)` with a `pass_rate_pct`. The outer query adds `rolling_7d_pass_rate` via a window function. `PARTITION BY criterion` keeps `groundedness` and `relevance` in separate windows so their averages never mix. `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` is seven rows total: the six days before today, plus today.

The result set has the same number of rows as the inner subquery. Both the raw daily rate and the smoothed rate sit on every row, so you can compare them directly.

**Dialect note.** This query runs identically in DuckDB and standard warehouse SQL. The only dialect differences in this module are the percentile and date helpers from lesson 1; window function syntax is standard.

## Query 5: Per-Tenant Cost Rank, This Week vs. Last Week

When a tenant's bill is flagged, the first question is simple: how does their rank now compare to last week? A tenant that ranked first last week and first again this week has not changed; something that changed around them may explain the absolute cost movement. A tenant that jumped from eighth to first in a single week is the investigation.

```sql
WITH weekly_cost AS (
    SELECT tenant_id, DATE_TRUNC('week', billed_at) AS cost_week, SUM(total_cost_usd) AS weekly_cost_usd
    FROM cost_stamps
    WHERE billed_at >= NOW() - INTERVAL '14 days'
    GROUP BY tenant_id, cost_week
),
ranked AS (
    SELECT tenant_id, cost_week, weekly_cost_usd,
        RANK() OVER (PARTITION BY cost_week ORDER BY weekly_cost_usd DESC) AS cost_rank
    FROM weekly_cost
)
SELECT
    this_week.tenant_id,
    this_week.cost_rank        AS rank_this_week,
    last_week.cost_rank        AS rank_last_week,
    this_week.weekly_cost_usd  AS cost_this_week,
    last_week.weekly_cost_usd  AS cost_last_week
FROM ranked this_week
LEFT JOIN ranked last_week
    ON this_week.tenant_id = last_week.tenant_id
   AND last_week.cost_week = this_week.cost_week - INTERVAL '1 week'
WHERE this_week.cost_week = DATE_TRUNC('week', NOW())
ORDER BY this_week.cost_rank;
```

This query uses a CTE to stage the work: `weekly_cost` builds the per-tenant, per-week aggregate; `ranked` applies `RANK()` within each week's partition; the final `SELECT` self-joins on tenant and a one-week offset to get both weeks in one row. CTEs are the subject of the next lesson; for now, read them as named subqueries that let you break a multi-step computation into legible parts.

`RANK()` assigns the same rank to ties and leaves a gap after them: two tenants tied for first both get rank 1, and the next tenant gets rank 3. `DENSE_RANK()` fills that gap, assigning rank 2 instead. Know which you want before you write the query: cost reporting usually wants `RANK()` so the gap signals the tie; leaderboards often want `DENSE_RANK()` so no rank is skipped.
[MS-Learn DENSE_RANK: https://learn.microsoft.com/sql/t-sql/functions/dense-rank-transact-sql]

The `LEFT JOIN` on the `ranked` CTE is what pulls both weeks onto one row. The `WHERE` clause filters to the current week on the left side; the join condition shifts the right side back one week. A tenant with `rank_last_week IS NULL` was not in the top cost drivers two weeks ago; the `LEFT JOIN` preserves them anyway so they appear in the current-week result.

## Core Concepts

- A window function computes over a partition of rows and keeps every input row in the result; `GROUP BY` collapses them. `PARTITION BY` sets the group, `ORDER BY` sorts within it, and `ROWS BETWEEN` defines the sliding frame.
- `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` is the standard frame for a seven-day rolling average; always state the frame explicitly for rolling aggregates.
- `RANK()` assigns the same rank to ties and leaves gaps; `DENSE_RANK()` fills those gaps. For cost or quality leaderboards, choose before you write the query.
- The rank-comparison pattern self-joins a ranked CTE on tenant and a one-week offset, so both weeks appear on one row; a `LEFT JOIN` preserves tenants present only in the current week.

Knowing a tenant's rank today is a fact. Knowing whether that rank moved is the signal that drives action: the rolling average and the rank delta are what separate reactive incident response from the early pattern recognition that stops incidents before they reach the pager.

<div class="claude-handoff" data-exercise="exercises/module1/window-functions/">

**Build It in Claude Code**: Extend `module1-sql/` with two new query files and two new smoke assertions: add `queries/04_rolling_7d_pass_rate.sql` (the `AVG ... OVER ... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` query partitioned by criterion) and `queries/05_cost_rank_week_over_week.sql` (the `RANK() OVER (PARTITION BY cost_week ...)` self-join query), then extend `smoke.py` to assert that the rolling 7-day average matches a known sequence for one criterion and that `tenant_a` ranks first in the current week.

</div>
