# Exercise: The Lineage Walk

## Goal

Extend `module1-sql/` with the lineage schema, seed a target answer whose chunk resolves to a changed content hash, add the lineage-walk query, and close the module with a finalized `smoke.py` and a `pytest` suite over all eight queries.

## Why

A corpus reload that swaps a cited paragraph is silent until you walk the lineage. The query you write here is how you prove a content change caused a quality drop; Module 6 automates the same lookup at scale.

## Steps

1. Open `module1-sql/db/schema.sql`. Append three `CREATE TABLE IF NOT EXISTS` statements for the lineage extension:

   - `answers`: `answer_id TEXT PRIMARY KEY`, `trace_id TEXT NOT NULL REFERENCES spans(trace_id)`, `retrieved_chunk_ids TEXT NOT NULL`
   - `chunks`: `chunk_id TEXT PRIMARY KEY`, `corpus_version TEXT NOT NULL`, `source_doc_id TEXT NOT NULL`, `source_doc_version TEXT NOT NULL`
   - `source_documents`: `doc_id TEXT NOT NULL`, `version_id TEXT NOT NULL`, `last_modified_at TIMESTAMP NOT NULL`, `content_hash TEXT NOT NULL`, `PRIMARY KEY (doc_id, version_id)`

2. Extend `db/seed.py` with a lineage seed block that runs after the existing telemetry seed. Seed:

   - One source document (`doc_id = 'doc_compliance_001'`) at two versions: `v1` with `content_hash = 'hash_v1_stable'` and `v2` with `content_hash = 'hash_v2_changed'`.
   - One chunk (`chunk_id = 'chunk_001'`) belonging to the document's `v2` version.
   - One answer (`answer_id = 'ans_target_001'`) tied to an existing `trace_id` in the store, with `retrieved_chunk_ids = 'chunk_001'`.

   The seed must make the lineage walk resolve `ans_target_001` to `content_hash = 'hash_v2_changed'`. That is the content-change signal.

3. Add `queries/08_lineage_walk.sql`. Use the CTE chain verbatim from the lesson:

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

4. Finalize `smoke.py`. It must reset and reseed the full database (all tables, including lineage), then run and assert all eight queries:

   - Q1: `/summarize` is the top row by p95 latency.
   - Q2: `tenant_a` is the top row by weekly cost.
   - Q3: `tenant_b` groundedness pass-rate is between 55% and 65%.
   - Q4: Rolling seven-day pass-rate returns at least one row per criterion.
   - Q5: Cost rank comparison returns at least one tenant row per week.
   - Q6: Latency delta query returns at least one route row.
   - Q7: Freshness breach query returns the seeded stale source.
   - Q8: Lineage walk for `ans_target_001` returns one row with `content_hash = 'hash_v2_changed'`.

   Print `PASS` or `FAIL` next to each assertion. Exit non-zero on any failure.

5. Write `tests/test_queries.py`. Mirror every `smoke.py` assertion as a named pytest test function. Each test reseeds its own fresh database (or reuses a session-scoped fixture) so tests are order-independent. Import the query runner from `runner.py` rather than duplicating the DuckDB connection logic.

## Done When

- `python smoke.py` prints `PASS` for all eight assertions and exits 0.
- `python -m pytest tests/` is green with one test per smoke assertion.
- Running `python smoke.py` then querying the result for `ans_target_001` returns `content_hash = 'hash_v2_changed'`, proving the lineage walk resolved the target answer to the changed document version.
- The full flow runs offline: `sqlite3` (standard library) plus `duckdb` and `pytest` (two pip installs), no cloud.

## Stretch

Add `tests/test_negative.py`. Seed a deficient store: set `tenant_b` groundedness pass-rate to 95% (above the outlier threshold). Assert that the `smoke.py` Q3 assertion would fail against this data. This proves the suite catches bad data, not just good data.
