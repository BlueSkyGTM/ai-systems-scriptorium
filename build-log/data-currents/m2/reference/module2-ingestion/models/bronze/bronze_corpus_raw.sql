-- models/bronze/bronze_corpus_raw.sql
-- Bronze layer: raw documents as-ingested, typed + ingestion timestamp.
-- Source: seeds/corpus_raw.csv loaded as a dbt seed (or read directly).
-- No cleaning, no dedup. Append semantics — every run stamps ingested_at.
--
-- Columns:
--   doc_id          TEXT     -- source document identifier
--   created_on      DATE     -- document creation date from source
--   title           TEXT     -- raw title
--   body            TEXT     -- raw body text
--   category        TEXT     -- source category label
--   ingested_at     TIMESTAMP -- wall-clock time this row entered bronze

{{ config(materialized='table') }}

SELECT
    doc_id                                  AS doc_id,
    CAST(created_on AS DATE)                AS created_on,
    title                                   AS title,
    body                                    AS body,
    category                                AS category,
    CURRENT_TIMESTAMP                       AS ingested_at
FROM {{ ref('corpus_raw') }}
