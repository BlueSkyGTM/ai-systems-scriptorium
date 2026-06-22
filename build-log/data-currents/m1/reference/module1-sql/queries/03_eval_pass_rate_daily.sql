-- Query 3: Eval Pass-Rate over a Rolling 14-Day Window (daily by criterion)
-- Answers: is quality trending up or down, and on which criterion?
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   DATE_TRUNC('day', ev.created_at)
--   -> DATE_TRUNC('day', ev.created_at)   [identical in DuckDB]
--
--   NOW() - INTERVAL '14 days'
--   -> NOW() - INTERVAL '14 days'          [identical in DuckDB]

SELECT
    DATE_TRUNC('day', ev.created_at)  AS eval_day,
    ev.criterion,
    COUNT(*)                           AS total_evals,
    SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END)  AS passes,
    ROUND(
        100.0 * SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                  AS pass_rate_pct
FROM eval_verdicts ev
WHERE ev.created_at >= NOW() - INTERVAL '14 days'
GROUP BY eval_day, ev.criterion
ORDER BY eval_day, ev.criterion;
