-- Query 7: Freshness Breach Diagnosis Chain
-- Answers: which corpus sources are stale, and by how much?
-- Returns only sources that breach their SLO.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   NOW() - s.last_load_ts  (produces an INTERVAL in Postgres)
--   -> epoch_ms(NOW()) - epoch_ms(s.last_load_ts)  would give milliseconds, but
--      DuckDB supports timestamp subtraction natively returning an INTERVAL:
--      (NOW() - s.last_load_ts) is a valid DuckDB INTERVAL expression.
--
--   (NOW() - s.last_load_ts) > (f.max_age_hours * INTERVAL '1 hour')
--   -> same expression is valid DuckDB; scalar * INTERVAL works natively.
--
--   is_stale = TRUE  (T-SQL uses bit comparison; DuckDB uses boolean natively)
--   -> WHERE is_stale  [DuckDB boolean column; both forms work]

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
        (NOW() - s.last_load_ts)                                     AS index_age,
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
WHERE is_stale
ORDER BY index_age DESC;
