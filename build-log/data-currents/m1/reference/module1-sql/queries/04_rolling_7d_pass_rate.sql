-- Query 4: Rolling Seven-Day Eval Pass-Rate
-- Answers: is quality getting better or worse after smoothing daily noise?
-- The window function keeps every daily row and adds a 7-day rolling average.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   DATE_TRUNC('day', created_at)
--   -> DATE_TRUNC('day', created_at)   [identical in DuckDB]
--
--   Window function syntax (AVG ... OVER ... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
--   is standard SQL:2003 and identical in T-SQL, Postgres, and DuckDB.

SELECT
    eval_day,
    criterion,
    pass_rate_pct,
    ROUND(
        AVG(pass_rate_pct) OVER (
            PARTITION BY criterion
            ORDER BY eval_day
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        1
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
