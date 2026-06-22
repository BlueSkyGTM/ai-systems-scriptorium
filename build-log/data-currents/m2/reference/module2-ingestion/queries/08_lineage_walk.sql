-- queries/08_lineage_walk.sql
-- Reused from M1: Query 8 "Lineage Walk — Answer -> Chunks -> Source Document Versions"
-- Answers: for a specific answer, what corpus versions and document hashes backed it?
-- If a content_hash changed between reloads, that is the source of the eval regression.
--
-- M2 adaptation note:
--   This query is byte-for-byte the M1 reference query. It runs against M2's gold
--   tables (source_documents, chunks) plus the answers table written by ingest.py.
--   The corpus ATTACH + USE pattern is the same DuckDB attachment used in M1.
--
-- DuckDB: string_split() + list_contains() replaces Postgres ANY(array_col).

WITH answer_context AS (
    SELECT
        a.answer_id,
        a.trace_id,
        a.retrieved_chunk_ids
    FROM answers a
    WHERE a.answer_id = $target_answer_id
),
chunk_sources AS (
    SELECT
        ac.answer_id,
        c.chunk_id,
        c.corpus_version,
        c.source_doc_id,
        c.source_doc_version
    FROM answer_context ac
    JOIN chunks c
        ON list_contains(string_split(ac.retrieved_chunk_ids, ','), c.chunk_id)
),
doc_versions AS (
    SELECT
        cs.answer_id,
        cs.chunk_id,
        cs.source_doc_id,
        cs.source_doc_version,
        d.last_modified_at,
        d.content_hash
    FROM chunk_sources cs
    JOIN source_documents d
        ON  d.doc_id     = cs.source_doc_id
        AND d.version_id = cs.source_doc_version
)
SELECT * FROM doc_versions ORDER BY chunk_id;
