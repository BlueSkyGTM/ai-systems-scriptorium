-- Query 3b: Three-Table Join (spans + cost_stamps + eval_verdicts)
-- Answers: when quality fails, does it correlate with high cost or high latency?
-- Returns the full picture per failed eval in the last hour.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   NOW() - INTERVAL '1 hour'
--   -> NOW() - INTERVAL '1 hour'   [identical in DuckDB]

SELECT
    s.route,
    s.tenant_id,
    s.latency_ms,
    c.total_cost_usd,
    ev.criterion,
    ev.verdict
FROM spans s
JOIN cost_stamps c    ON s.trace_id = c.trace_id
JOIN eval_verdicts ev ON s.trace_id = ev.trace_id
WHERE s.ts >= NOW() - INTERVAL '1 hour'
  AND ev.verdict = 'fail'
ORDER BY s.latency_ms DESC;
