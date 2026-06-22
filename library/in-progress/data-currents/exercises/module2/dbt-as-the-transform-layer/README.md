# Exercise: dbt as the Transform Layer

## Goal

Wrap `module2-ingestion/` in a dbt project, add schema tests that gate each medallion layer, and
confirm that a deliberately broken transform causes `dbt test` to exit non-zero.

## Why

A transform with no tests is silent on failure. dbt makes the transform runnable, reviewable, and
blockable: a failing test stops the build before bad data reaches the gold layer.

## Steps

Before writing anything, find `module2-ingestion/` and read its current state. You are extending an
existing build, not starting one.

1. Add `dbt_project.yml` at the root of `module2-ingestion/`. Use the verbatim config from the
   lesson: `name: module2_ingestion`, model paths `["models"]` and `["seeds"]`, and materialization
   blocks that assign bronze/silver/gold each to their own schema as tables.

2. Add `profiles.yml` beside it with the DuckDB adapter pointing at `corpus.duckdb` on one thread.
   No server, no credentials; the project must run offline.

3. Add `models/schema.yml` with the three model blocks from the lesson verbatim:
   `silver_corpus_clean` (doc_id: not_null + unique; content_hash: not_null), `gold_chunks`
   (chunk_id: not_null + unique; source_doc_id: not_null + relationships to
   `gold_source_documents.doc_id`), and `gold_corpus_loads` (status: not_null + accepted_values
   `['success', 'failure']`).

4. Run the seed, then run the full build:

   ```text
   dbt seed
   dbt build
   ```

   Confirm the build exits 0 and every test passes.

5. Introduce a failure: edit the silver model or a seed row so that at least one `content_hash` is
   null. Run `dbt test` and confirm it exits non-zero. Revert the change.

## Done When

- `dbt build` runs all models in dependency order, then runs every test, and exits 0 on the clean
  corpus.
- Introducing a null `content_hash` in `silver_corpus_clean` causes `dbt test` to exit non-zero;
  the not_null test on that column is the gate that fires.

Note: install `dbt-duckdb` before running (`pip install dbt-duckdb`). Everything else runs offline.

## Stretch

Add an `accepted_values` test on a category column in one of your models. Seed a row with a value
outside the accepted set and confirm `dbt test` exits non-zero. Revert and confirm the build is
green again.
