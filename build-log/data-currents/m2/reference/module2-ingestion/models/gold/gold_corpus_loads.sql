-- models/gold/gold_corpus_loads.sql
-- Gold layer: corpus_loads audit table.
--
-- Schema (extends M1's corpus_loads):
--   load_id       TEXT PRIMARY KEY   -- uuid-style identifier
--   source_id     TEXT               -- 'corpus_raw' for this pipeline
--   status        TEXT               -- 'success' | 'failure'
--   loaded_at     TIMESTAMP          -- when the load ran
--   rows_ingested INTEGER            -- documents processed in this run
--
-- This model creates the schema for the dbt build pass.
-- ingest.py appends real rows to the persistent corpus.db on each run.
-- The dbt build seeds one synthetic 'dbt_build' row so schema tests can run.

{{ config(materialized='table') }}

SELECT
    'load_dbt_build_001'    AS load_id,
    'corpus_raw'            AS source_id,
    'success'               AS status,
    CURRENT_TIMESTAMP       AS loaded_at,
    (SELECT COUNT(*) FROM {{ ref('silver_corpus_clean') }}) AS rows_ingested
