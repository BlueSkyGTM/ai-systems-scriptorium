-- Query 8: Lineage Walk (Answer -> Chunks -> Source Document Versions)
-- Answers: for a specific answer, what corpus versions and document hashes backed it?
-- If a content_hash changed between reloads, that is the source of the eval regression.
--
-- DIALECT NOTE (Postgres/T-SQL -> DuckDB):
--   JOIN chunks c ON c.chunk_id = ANY(ac.retrieved_chunk_ids)
--   The draft uses ANY() over an array column. Our schema stores retrieved_chunk_ids
--   as a comma-separated TEXT string (see schema.sql comments).
--   DuckDB: use string_split() to produce an array, then unnest() + filter:
--
--     JOIN chunks c
--       ON list_contains(string_split(ac.retrieved_chunk_ids, ','), c.chunk_id)
--
--   string_split(str, ',') returns a LIST; list_contains() checks membership.
--   This replaces Postgres' ANY(array_column) without changing the query semantics.
--
--   :target_answer_id (named bind param) -> $target_answer_id (DuckDB named param)

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
    -- Expand comma list into membership check; replaces ANY(array_col)
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
