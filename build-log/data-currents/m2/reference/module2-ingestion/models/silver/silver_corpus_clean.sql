-- models/silver/silver_corpus_clean.sql
-- Silver layer: cleaned + typed documents, one row per doc_id (latest wins).
--
-- made-with-ml text recipe applied:
--   1. Lowercase title and body
--   2. Strip leading/trailing whitespace
--   3. Collapse internal whitespace to single spaces
--   4. Remove URLs (http/https prefixed tokens)
--   5. Concatenate cleaned_title + ' ' + cleaned_body -> text
--
-- content_hash: md5(text) — used as the MERGE key in the gold UPSERT.
-- Deduplication: keeps the single row per doc_id (all source rows are unique
-- by doc_id in this corpus; the QUALIFY guard handles future duplicates).
--
-- Columns:
--   doc_id          TEXT
--   created_on      DATE
--   category        TEXT
--   text            TEXT     -- cleaned, lowercased, whitespace-collapsed
--   content_hash    TEXT     -- md5 of text; never NULL
--   cleaned_at      TIMESTAMP

{{ config(materialized='table') }}

WITH raw AS (
    SELECT
        doc_id,
        created_on,
        category,
        ingested_at,
        -- Step 1+2: lowercase and strip
        TRIM(LOWER(title)) AS title_lc,
        TRIM(LOWER(body))  AS body_lc
    FROM {{ ref('bronze_corpus_raw') }}
),
url_stripped AS (
    -- Step 4: remove URL tokens (words starting with http:// or https://)
    -- DuckDB: regexp_replace with global flag strips all occurrences
    SELECT
        doc_id,
        created_on,
        category,
        ingested_at,
        regexp_replace(title_lc, 'https?://\S+', '', 'g') AS title_no_url,
        regexp_replace(body_lc,  'https?://\S+', '', 'g') AS body_no_url
    FROM raw
),
collapsed AS (
    -- Step 3: collapse internal whitespace
    SELECT
        doc_id,
        created_on,
        category,
        ingested_at,
        TRIM(regexp_replace(title_no_url, '\s+', ' ', 'g')) AS cleaned_title,
        TRIM(regexp_replace(body_no_url,  '\s+', ' ', 'g')) AS cleaned_body
    FROM url_stripped
),
assembled AS (
    -- Step 5: concat
    SELECT
        doc_id,
        created_on,
        category,
        ingested_at,
        cleaned_title || ' ' || cleaned_body AS text
    FROM collapsed
),
hashed AS (
    SELECT
        doc_id,
        created_on,
        category,
        ingested_at,
        text,
        md5(text) AS content_hash
    FROM assembled
),
deduped AS (
    -- Keep latest ingested row per doc_id
    SELECT *
    FROM hashed
    QUALIFY ROW_NUMBER() OVER (PARTITION BY doc_id ORDER BY ingested_at DESC) = 1
)
SELECT
    doc_id,
    created_on,
    category,
    text,
    content_hash,
    CURRENT_TIMESTAMP AS cleaned_at
FROM deduped
