-- models/gold/gold_source_documents.sql
-- Gold layer: source_documents serving table.
--
-- Schema (matches M1 lineage schema):
--   doc_id           TEXT
--   version_id       TEXT       -- 'v' || ROW_NUMBER within doc's content history
--   last_modified_at TIMESTAMP  -- when this content version was first seen
--   content_hash     TEXT       -- md5 of cleaned text
--   PRIMARY KEY (doc_id, version_id)
--
-- Idempotent MERGE semantics (enforced in ingest.py):
--   - Re-running on unchanged source inserts ZERO new versions.
--   - A changed body yields ONE new version (new content_hash), old rows retained.
--
-- This dbt model materializes the CURRENT silver snapshot as version-1 rows
-- for a clean initial build. ingest.py handles the incremental MERGE into
-- the persistent SQLite corpus store.
--
-- For the dbt build pass (smoke test), we produce a canonical v1 view of all docs.

{{ config(materialized='table') }}

SELECT
    doc_id,
    'v1'                   AS version_id,
    MAX(cleaned_at)        AS last_modified_at,
    content_hash,
    created_on             AS source_created_on
FROM {{ ref('silver_corpus_clean') }}
GROUP BY doc_id, content_hash, created_on
