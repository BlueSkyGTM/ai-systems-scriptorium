-- Query 5: Per-Tenant Cost Rank, This Week vs. Last Week
-- Answers: which tenant jumped in cost rank? A rank jump from 8->1 in a week is the
-- investigation; a tenant that was rank 1 last week too probably hasn't changed.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   NOW() - INTERVAL '14 days'
--   -> NOW() - INTERVAL '14 days'   [identical in DuckDB]
--
--   this_week.cost_week - INTERVAL '1 week'
--   -> this_week.cost_week - INTERVAL '1 week'   [identical in DuckDB]
--   DuckDB supports arithmetic subtraction of INTERVAL from TIMESTAMP/DATE.
--
--   DATE_TRUNC('week', NOW()) returns the Monday of the current ISO week in DuckDB.
--   In T-SQL you would use DATETRUNC('week', GETDATE()).

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
    this_week.cost_rank            AS rank_this_week,
    last_week.cost_rank            AS rank_last_week,
    ROUND(this_week.weekly_cost_usd, 6) AS cost_this_week,
    ROUND(last_week.weekly_cost_usd, 6) AS cost_last_week
FROM ranked this_week
LEFT JOIN ranked last_week
    ON  this_week.tenant_id = last_week.tenant_id
    AND last_week.cost_week = this_week.cost_week - INTERVAL '1 week'
WHERE this_week.cost_week = DATE_TRUNC('week', NOW())
ORDER BY this_week.cost_rank;
