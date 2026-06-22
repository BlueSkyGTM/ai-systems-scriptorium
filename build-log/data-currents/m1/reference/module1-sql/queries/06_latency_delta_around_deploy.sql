-- Query 6: Latency Delta between Deployment Windows
-- Answers: which routes got faster/slower after the deploy, and by how much?
-- Parameterized: pass deploy_ts as a Python string '2026-06-20 10:00:00'.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)
--   -> QUANTILE_CONT(latency_ms, 0.95)
--   (same change as Query 1)
--
--   :deploy_ts placeholder (SQLAlchemy/psycopg2 named style)
--   -> ? placeholder (Python DB-API positional style used by duckdb.execute())
--   In runner.py and smoke.py we pass the value as a positional parameter.
--   The query uses $deploy_ts DuckDB macro substitution; caller passes via params list.
--
--   ts BETWEEN :deploy_ts - INTERVAL '2 hours' AND :deploy_ts
--   -> ts BETWEEN $deploy_ts::TIMESTAMP - INTERVAL '2 hours' AND $deploy_ts::TIMESTAMP
--   DuckDB uses $name for named parameters with duckdb.execute(sql, {"name": val}).

WITH before_deploy AS (
    SELECT
        route,
        ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
    FROM spans
    WHERE ts BETWEEN $deploy_ts::TIMESTAMP - INTERVAL '2 hours'
                 AND $deploy_ts::TIMESTAMP
    GROUP BY route
),
after_deploy AS (
    SELECT
        route,
        ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_ms
    FROM spans
    WHERE ts BETWEEN $deploy_ts::TIMESTAMP
                 AND $deploy_ts::TIMESTAMP + INTERVAL '2 hours'
    GROUP BY route
)
SELECT
    b.route,
    b.p95_ms                                          AS p95_before,
    a.p95_ms                                          AS p95_after,
    ROUND(a.p95_ms - b.p95_ms, 1)                    AS delta_ms,
    ROUND(100.0 * (a.p95_ms - b.p95_ms) / b.p95_ms, 1) AS delta_pct
FROM before_deploy b
JOIN after_deploy a ON b.route = a.route
ORDER BY delta_ms DESC;
