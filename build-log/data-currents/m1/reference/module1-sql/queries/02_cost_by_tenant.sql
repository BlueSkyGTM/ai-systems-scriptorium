-- Query 2: Cost by Tenant (current week)
-- Answers: which tenant is driving this week's cost spike.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   DATE_TRUNC('week', NOW())
--   -> DATE_TRUNC('week', NOW())   [identical in DuckDB]
--   DuckDB supports DATE_TRUNC with the same string granularity labels as Postgres.
--
--   WHERE billed_at >= DATE_TRUNC('week', NOW())
--   uses ISO week start (Monday). DuckDB week truncation follows ISO 8601.

SELECT
    tenant_id,
    ROUND(SUM(total_cost_usd), 6)   AS total_cost_usd,
    SUM(input_tokens)               AS total_input_tokens,
    SUM(output_tokens)              AS total_output_tokens,
    COUNT(*)                        AS request_count,
    ROUND(AVG(total_cost_usd), 6)   AS avg_cost_per_request
FROM cost_stamps
WHERE billed_at >= DATE_TRUNC('week', NOW())
GROUP BY tenant_id
ORDER BY total_cost_usd DESC;
