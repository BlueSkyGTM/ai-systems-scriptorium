-- models/gold/gold_chunks.sql
-- Gold layer: chunks serving table.
--
-- Each silver document is split into 1-3 chunks by a deterministic word-count
-- split (target ~80 words per chunk). Chunk IDs are deterministic:
--   chunk_id = doc_id || '_c' || chunk_index (zero-padded)
--
-- Schema (matches M1 lineage schema):
--   chunk_id          TEXT PRIMARY KEY
--   source_doc_id     TEXT     -- FK -> source_documents.doc_id
--   source_doc_version TEXT    -- FK -> source_documents.version_id
--   corpus_version    TEXT     -- load batch identifier
--   text              TEXT     -- the chunk text slice
--
-- Note: corpus_version is set by ingest.py at runtime; the dbt model uses
-- 'corpus_v_dbt_build' as a placeholder for the initial medallion build.

{{ config(materialized='table') }}

WITH silver AS (
    SELECT
        doc_id,
        text,
        content_hash
    FROM {{ ref('silver_corpus_clean') }}
),
-- DuckDB: split text into words, assign chunk index based on word position
-- Each chunk targets ~80 words. We use integer division on word array index.
word_arrays AS (
    SELECT
        doc_id,
        content_hash,
        string_split(text, ' ') AS words
    FROM silver
),
chunked AS (
    SELECT
        doc_id,
        content_hash,
        -- chunk index: floor(word_position / 80), capped at 2 (max 3 chunks = 0,1,2)
        LEAST(FLOOR(word_pos / 80), 2)::INTEGER AS chunk_idx,
        word
    FROM word_arrays,
    UNNEST(words) WITH ORDINALITY AS t(word, word_pos)
),
chunk_text AS (
    SELECT
        doc_id,
        content_hash,
        chunk_idx,
        -- Deterministic chunk_id: doc_id + '_c' + zero-padded chunk index
        doc_id || '_c' || LPAD(chunk_idx::TEXT, 2, '0') AS chunk_id,
        -- Re-join words back into text
        string_agg(word, ' ' ORDER BY rowid) AS text
    FROM (
        SELECT
            doc_id,
            content_hash,
            chunk_idx,
            word,
            ROW_NUMBER() OVER (PARTITION BY doc_id, chunk_idx ORDER BY (SELECT NULL)) AS rowid
        FROM chunked
    ) ordered
    GROUP BY doc_id, content_hash, chunk_idx
)
SELECT
    chunk_id,
    doc_id                       AS source_doc_id,
    'v1'                         AS source_doc_version,
    'corpus_v_dbt_build'         AS corpus_version,
    text
FROM chunk_text
