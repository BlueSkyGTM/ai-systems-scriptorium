# Exercise: The Medallion Pattern

## Goal

Extend `module2-ingestion/` with three medallion layers: a bronze model holding raw documents
as-ingested, a silver model applying the cleaning recipe and computing a `content_hash`, and gold
serving models (`source_documents`, `chunks`) the lineage walk queries.

## Why

The retrieval layer queries gold tables, not bronze. Without the medallion structure, every consumer
defends itself against the same raw defects. Once the layers are in place, cleaning is a single
versioned recipe and the blast radius of any recipe change is bounded.

## Steps

1. Inside `module2-ingestion/models/`, create three subdirectories:
   `bronze/`, `silver/`, and `gold/`.

2. Write `models/bronze/bronze_corpus_raw.sql`. It selects from `{{ ref('corpus_raw') }}` and adds
   an `ingested_at` column (`CURRENT_TIMESTAMP`). Cast `created_on` to `DATE`. Apply no cleaning:
   title and body arrive exactly as ingested.

3. Write `models/silver/silver_corpus_clean.sql`. It reads from `{{ ref('bronze_corpus_raw') }}`
   and applies the full cleaning recipe in order:
   - Lowercase and trim `title` and `body`.
   - Strip URLs with `regexp_replace(col, 'https?://\S+', '', 'g')`.
   - Collapse runs of whitespace with `regexp_replace(col, '\s+', ' ', 'g')` and trim again.
   - Concatenate cleaned title and body into a single `text` column.
   - Compute `content_hash` as `md5(text)`.
   - Add `cleaned_at` as `CURRENT_TIMESTAMP`.

4. Write `models/gold/gold_source_documents.sql`. It reads from `{{ ref('silver_corpus_clean') }}`
   and produces one row per `(doc_id, content_hash)` pair. Columns: `doc_id`, `version_id`
   (hardcode `'v1'`), `MAX(cleaned_at) AS last_modified_at`, `content_hash`, and
   `created_on AS source_created_on`.

5. Write `models/gold/gold_chunks.sql`. It reads from `{{ ref('silver_corpus_clean') }}` and
   exposes `doc_id`, `content_hash`, and `text` for the chunking step downstream. For now the model
   is one row per document (chunking is a later lesson); the column shape is what matters.

6. Run `dbt run --select bronze+ silver+ gold+` and confirm the three layers materialize in order
   with no errors.

## Done When

- `dbt run` materializes `bronze_corpus_raw`, `silver_corpus_clean`, `gold_source_documents`, and
  `gold_chunks` in dependency order (bronze before silver, silver before gold) with exit code 0.
- Silver rows are lowercased, URL-free, and whitespace-collapsed: query a silver row and confirm no
  uppercase letters, no `http` strings, and no double spaces in `text`.
- `gold_source_documents` has exactly one row per `(doc_id, content_hash)` combination: run
  `SELECT doc_id, content_hash, COUNT(*) FROM gold_source_documents GROUP BY doc_id, content_hash
  HAVING COUNT(*) > 1` and confirm zero rows returned.

## Stretch

Add a row count check: silver must have no more rows than bronze (deduplication held at or before
this layer). Write a dbt test or a standalone SQL assertion that reads `COUNT(*)` from both tables
and fails if `COUNT(silver) > COUNT(bronze)`. This is the simplest guard against a silver model
that fans out instead of deduplicating.
