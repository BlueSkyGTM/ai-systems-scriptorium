# The Medallion Pattern

Query raw ingested documents directly and you will regret it. Casing is inconsistent, URLs leak into
text, duplicate records pass through, and every consumer downstream has to paper over the same defects
independently. The medallion pattern breaks that cycle: three named layers, one job each, and a clear
rule about what goes where.

## Why Raw Is Dangerous

The document corpus your AI system queries is not clean at the moment it lands. Scrapers vary their
encoding, sources format titles differently, and the same document sometimes arrives more than once
with different timestamps. If your retrieval layer queries that raw table, those defects go straight
into the embedding and into the answer. The bugs are invisible until something retrieves the wrong
chunk and cites a URL in the middle of a sentence.

The real problem is not any one defect. It is the absence of a trust boundary: there is no moment at
which the data has been verified, cleaned, and stamped ready. Without that boundary, every consumer
has to make its own guess about what the data means.

## Three Layers, One Job Each

The medallion architecture defines three layers in a lakehouse. Each raises quality before passing
to the next. [MS-Learn medallion / OneLake: https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture]

**Bronze** holds the data exactly as ingested, with only the minimum casts needed to give it a
schema. Nothing is cleaned. Nothing is deduplicated. The bronze layer is your audit trail: if
something goes wrong downstream, you can always return to what actually arrived. Bronze adds one
column, `ingested_at`, so you can track when each row landed.

```sql
-- models/bronze/bronze_corpus_raw.sql
{{ config(materialized='table') }}
SELECT
    doc_id,
    CAST(created_on AS DATE) AS created_on,
    title, body, category,
    CURRENT_TIMESTAMP AS ingested_at
FROM {{ ref('corpus_raw') }}
```

**Silver** is where the cleaning happens. The raw text passes through a deterministic recipe: titles
and bodies are lowercased and trimmed, URLs are stripped with a regex, whitespace is collapsed, then
the cleaned title and body are concatenated into a single `text` column. A `content_hash` (md5 of
the cleaned text) is computed here. Silver rows are trustworthy. The consumers downstream do not
need to know how dirty the source was.

The cleaning recipe in the silver model below is the same recipe the made-with-ml data pipeline
uses for corpus preprocessing. Landing it here lifts it out of ad hoc preprocessing scripts and
into a versioned, testable dbt model.

```sql
-- models/silver/silver_corpus_clean.sql  (abridged to the transform spine)
{{ config(materialized='table') }}
WITH raw AS (
    SELECT doc_id, created_on, category, ingested_at,
           TRIM(LOWER(title)) AS title_lc, TRIM(LOWER(body)) AS body_lc
    FROM {{ ref('bronze_corpus_raw') }}
),
url_stripped AS (
    SELECT doc_id, created_on, category, ingested_at,
           regexp_replace(title_lc, 'https?://\S+', '', 'g') AS title_no_url,
           regexp_replace(body_lc,  'https?://\S+', '', 'g') AS body_no_url
    FROM raw
),
collapsed AS (
    SELECT doc_id, created_on, category, ingested_at,
           TRIM(regexp_replace(title_no_url, '\s+', ' ', 'g')) AS cleaned_title,
           TRIM(regexp_replace(body_no_url,  '\s+', ' ', 'g')) AS cleaned_body
    FROM url_stripped
)
SELECT doc_id, created_on, category,
       cleaned_title || ' ' || cleaned_body AS text,
       md5(cleaned_title || ' ' || cleaned_body) AS content_hash,
       CURRENT_TIMESTAMP AS cleaned_at
FROM collapsed
```

Notice the CTEs: each CTE does exactly one thing. `raw` lowercases and trims. `url_stripped` removes
URLs. `collapsed` flattens whitespace. The final `SELECT` concatenates and hashes. You can read the
recipe in order without tracing through nested subqueries.

**Gold** is the serving layer. These are the tables your retrieval queries, your freshness SLO
monitor, and the lineage walk in Module 6 all read. Gold does not clean; it shapes. The
`gold_source_documents` table reduces silver to one row per `(doc_id, content_hash)` pair, which is
exactly the grain the lineage store expects: this document, at this content fingerprint, was last
modified at this timestamp.

```sql
-- models/gold/gold_source_documents.sql
{{ config(materialized='table') }}
SELECT doc_id, 'v1' AS version_id, MAX(cleaned_at) AS last_modified_at,
       content_hash, created_on AS source_created_on
FROM {{ ref('silver_corpus_clean') }}
GROUP BY doc_id, content_hash, created_on
```

The `content_hash` is what makes deduplication verifiable. Two runs that produce the same document
text will hash to the same value. Gold keeps only the latest `cleaned_at` for each pair. If the
document is unchanged, no new row lands.

## The Direction Is One-Way

Bronze never reads from silver. Silver reads only from bronze. Gold reads only from silver. The
direction is enforced by `{{ ref() }}` dependencies in dbt: the build order follows the graph, and
the graph only flows down. If you find a query that reads gold to populate silver, something is wrong
with the design.

The reason this matters is blast radius. When you need to rerun the cleaning logic (say, the URL
regex misses a class of malformed links), you drop and rebuild silver from bronze. Gold rebuilds from
silver. The source data in bronze is untouched. The trust boundary held.

## Core Concepts

- Bronze holds the data exactly as ingested; silver cleans and types it; gold shapes it for serving.
  Each layer reads only from the layer above it, never the reverse.
- The cleaning happens in silver: lowercase, strip URLs, collapse whitespace, concatenate title and
  body, hash. Nothing upstream of silver is trusted as clean.
- The `content_hash` in silver is md5 of the cleaned text; gold uses it to reduce to one row per
  `(doc_id, content_hash)`, making deduplication verifiable by query.
- The one-way dependency (bronze to silver to gold) limits blast radius: a recipe change rebuilds
  silver and gold from bronze without touching the source.

<div class="claude-handoff" data-exercise="exercises/module2/the-medallion-pattern/">

**Build It in Claude Code**: Structure `module2-ingestion/` as three medallion layers: add `models/bronze/bronze_corpus_raw.sql` to hold raw documents as-ingested (schema only, no cleaning), add `models/silver/silver_corpus_clean.sql` applying the full cleaning recipe (lowercase, URL-strip, whitespace-collapse, title+body concat, md5 `content_hash`), and add `models/gold/gold_source_documents.sql` plus `models/gold/gold_chunks.sql` as the serving tables the lineage walk queries.

</div>
