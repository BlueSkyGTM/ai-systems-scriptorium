-- Query 1: P95 Latency by Route
-- Answers: which route is blowing the SLO, ordered worst-first.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)
--   -> QUANTILE_CONT(latency_ms, 0.95)
--   DuckDB's QUANTILE_CONT takes the column and quantile as positional args;
--   no WITHIN GROUP clause needed.
--
--   NOW() - INTERVAL '24 hours'
--   -> NOW() - INTERVAL '24 hours'   [identical in DuckDB]
--   (DuckDB accepts standard INTERVAL literal syntax.)

SELECT
    route,
    COUNT(*)                          AS request_count,
    ROUND(AVG(latency_ms), 1)         AS avg_latency_ms,
    ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_latency_ms
FROM spans
WHERE ts >= NOW() - INTERVAL '24 hours'
GROUP BY route
ORDER BY p95_latency_ms DESC;
