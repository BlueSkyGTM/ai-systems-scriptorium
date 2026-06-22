-- models/gold/gold_freshness_slos.sql
-- Gold layer: per-source freshness SLO targets.
--
-- Schema:
--   source_id      TEXT PRIMARY KEY
--   max_age_hours  INTEGER
--
-- Seeds two sources: corpus_raw (nightly, 25h SLO) and corpus_raw_realtime
-- (near-real-time, 2h SLO — demonstrates a source that can go stale quickly).

{{ config(materialized='table') }}

SELECT source_id, max_age_hours
FROM (
    VALUES
        ('corpus_raw',          25),   -- nightly batch: fresh if loaded within 25h
        ('corpus_raw_realtime',  2)    -- near-RT feed: fresh if loaded within 2h
) AS t(source_id, max_age_hours)
