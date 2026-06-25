# The Lineage Walk

Eval pass-rate dropped for the `/compliance` route Tuesday. You suspect a corpus reload swapped the paragraph the model cited. The only way to prove it is to walk backward: from the answer, through the chunks it retrieved, to the exact document version and content hash that produced them.

That walk is a query. You build it here.

## Three Tables, One Chain

The telemetry store already tracks what your system did. Lineage tracks what it read. Three tables extend the schema.

```sql
-- retrieved_chunk_ids stored as a comma-separated list (SQLite has no array type)
CREATE TABLE answers (
    answer_id           TEXT PRIMARY KEY,
    trace_id            TEXT NOT NULL REFERENCES spans(trace_id),
    retrieved_chunk_ids TEXT NOT NULL   -- e.g. 'chunk_001,chunk_002'
);
CREATE TABLE chunks (
    chunk_id           TEXT PRIMARY KEY,
    corpus_version     TEXT NOT NULL,
    source_doc_id      TEXT NOT NULL,
    source_doc_version TEXT NOT NULL
);
CREATE TABLE source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    last_modified_at TIMESTAMP NOT NULL,
    content_hash     TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);
```

`answers` links a trace to the chunks the retriever pulled. `chunks` links each chunk to the corpus version and source document version it came from. `source_documents` is the version ledger: every document reload writes a new row with a new `content_hash`, and old rows stay. The `PRIMARY KEY (doc_id, version_id)` enforces that.

This is a minimal lineage schema. It records enough to answer the question: did the document change between the load that produced this answer and the one before it?

## The Storage Seam: Comma Lists vs. Arrays

The artifact stores `retrieved_chunk_ids` as a comma-separated TEXT column because SQLite has no array type. DuckDB reads it with `string_split(..., ',')` and `list_contains(...)`. A Postgres column would use `= ANY(array_column)`; a warehouse without arrays uses a bridge table, one row per answer-chunk pair.

## Query 8: Walk an Answer Back to Its Source Version

```sql
WITH answer_context AS (
    SELECT a.answer_id, a.trace_id, a.retrieved_chunk_ids
    FROM answers a
    WHERE a.answer_id = $target_answer_id
),
chunk_sources AS (
    SELECT ac.answer_id, c.chunk_id, c.corpus_version, c.source_doc_id, c.source_doc_version
    FROM answer_context ac
    JOIN chunks c ON list_contains(string_split(ac.retrieved_chunk_ids, ','), c.chunk_id)
),
doc_versions AS (
    SELECT cs.answer_id, cs.chunk_id, cs.source_doc_id, cs.source_doc_version,
        d.last_modified_at, d.content_hash
    FROM chunk_sources cs
    JOIN source_documents d ON d.doc_id = cs.source_doc_id AND d.version_id = cs.source_doc_version
)
SELECT * FROM doc_versions ORDER BY chunk_id;
```

Read it as three steps named in order. `answer_context` pins the target answer and pulls its chunk list. `chunk_sources` joins that list to the `chunks` table, resolving each chunk ID to the corpus version and document version it belongs to. `doc_versions` joins to `source_documents` to retrieve the content hash for that exact version.

Each row in the result is one chunk the answer drew on, with the document version and content hash that produced it. Compare Tuesday's hash to Monday's: if they differ, the corpus reload swapped the paragraph. That is the answer.

This is the lineage lookup Module 6 will automate into a full lineage store. Here you write it by hand, so you understand the data shape before the automation hides it.

## The Module 1 Diagnostic Playbook

These eight queries are the ones you run in order during a production incident. Lessons 1 and 2 built them; this lesson closes the set.

1. P95 latency by route (current window)
2. Cost by tenant (current week)
3. Eval pass-rate by day and criterion (rolling 14 days)
4. Rolling seven-day pass-rate to smooth noise
5. Per-tenant cost rank, this week versus last week
6. Latency delta around a deployment timestamp
7. Freshness breach: which sources are stale and by how much
8. Lineage walk: answer back to source document version and content hash

Run them in this order and you cover the full surface of what can go wrong: latency, cost, quality trend, quality smoothed, cost attribution shift, deploy regression, corpus staleness, and corpus content change. The eight queries together are the operator's toolkit for a production AI system.

Module 2 extends this same `module1-sql/` store: you land its tables as warehouse targets and write dbt models that transform the raw telemetry into the query layer a data team can build dashboards on.

## Core Concepts

- Lineage resolves an answer to the exact source-document version and content hash that produced it; a changed content hash between two loads is the evidence that a corpus reload altered what the model cited.
- The lineage CTE chain runs in three named steps: isolate the target answer, join its chunk IDs to the `chunks` table, then join to `source_documents` for the version record and content hash.
- `retrieved_chunk_ids` is stored as comma-separated TEXT in SQLite (no array type); DuckDB reads it with `string_split(..., ',')` and `list_contains(...)`; Postgres uses `= ANY(array_column)`.
- The eight-query diagnostic playbook (latency, cost, pass-rate, rolling pass-rate, cost rank delta, deploy delta, freshness breach, lineage walk) covers the full incident surface for a production AI system.

<div class="claude-handoff" data-exercise="exercises/module1/the-lineage-walk/">

**Build It in Claude Code**: Add the three lineage tables (`answers`, `chunks`, `source_documents`) to `db/schema.sql`; extend `db/seed.py` to seed one target answer whose retrieved chunk resolves to a document with a changed `content_hash` (seed two versions of the same `source_doc_id` so the walk lands on the newer, changed hash); add `queries/08_lineage_walk.sql` using the locked CTE chain from this lesson; then finalize `smoke.py` to run and assert all eight queries (exit non-zero on any failure) and write a `tests/test_queries.py` pytest suite that mirrors every smoke assertion as a named test.

</div>
