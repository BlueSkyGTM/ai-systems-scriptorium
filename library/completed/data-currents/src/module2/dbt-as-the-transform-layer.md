# dbt as the Transform Layer

A hand-written SQL transform with no tests is a silent-regression machine: it runs, produces rows,
and tells you nothing about whether those rows are correct. The day a null slips into `content_hash`
or a chunk loses its parent document, your retrieval system gets garbage and the pipeline logs
"success." dbt breaks that silence by making the transform reviewable code and running tests that
block promotion when the data fails.

You build a dbt project that wraps `module2-ingestion/` in versioned models with schema tests. A
`SELECT` becomes a model. A model materializes as a table. A test asserts a property of that table.
When a test fails, `dbt build` exits non-zero and the load does not advance.

## dbt Models Are SELECT Statements

In dbt, a model is a `.sql` file that contains one `SELECT`. dbt runs that `SELECT` and materializes
the result as a table or view in your target database. The materialization strategy lives in
`dbt_project.yml`, not in the SQL file:

```yaml
# dbt_project.yml
name: module2_ingestion
version: "1.0.0"
config-version: 2
profile: module2_ingestion
model-paths: ["models"]
seed-paths: ["seeds"]
models:
  module2_ingestion:
    bronze: { +materialized: table, +schema: bronze }
    silver: { +materialized: table, +schema: silver }
    gold:   { +materialized: table, +schema: gold }
```

Each directory under `models/` maps to a medallion layer. Every model in `models/bronze/` lands in
the `bronze` schema as a table. Every model in `models/gold/` lands in `gold`. The SQL stays
portable; the destination is configuration.

The database adapter is declared in `profiles.yml`. For this module, dbt targets DuckDB, which is
offline and file-based:

```yaml
# profiles.yml
module2_ingestion:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "corpus.duckdb"
      threads: 1
```

No server to spin up. No credentials to manage. The same project structure and the same
`dbt_project.yml` run against a Fabric Warehouse in production, swapping only the adapter in
`profiles.yml`. Microsoft Fabric supports dbt Core 1.9 natively as a Data Factory job type
(preview as of mid-2026), targeting a Fabric Warehouse with the same model-and-test contract.
[MS-Learn dbt jobs in Fabric: https://learn.microsoft.com/fabric/data-factory/dbt-job-overview]
The offline artifact you build here transfers directly: models are SELECT statements; the adapter
is the only seam.

## Schema Tests Gate Promotion

The medallion pattern establishes bronze, silver, and gold as quality tiers. dbt's schema tests are
what enforces those tiers: they run after models build, and a failure exits non-zero before any
downstream model can consume bad data.

Tests live in `models/schema.yml`. They declare properties of columns that must hold true in the
materialized table:

```yaml
# models/schema.yml  (excerpt)
version: 2
models:
  - name: silver_corpus_clean
    columns:
      - name: doc_id
        data_tests: [not_null, unique]
      - name: content_hash
        data_tests: [not_null]
  - name: gold_chunks
    columns:
      - name: chunk_id
        data_tests: [not_null, unique]
      - name: source_doc_id
        data_tests:
          - not_null
          - relationships:
              arguments: { to: ref('gold_source_documents'), field: doc_id }
  - name: gold_corpus_loads
    columns:
      - name: status
        data_tests:
          - not_null
          - accepted_values: { values: ['success', 'failure'] }
```

Read each block as a contract. `silver_corpus_clean.doc_id` must be present and unique; a duplicate
or a null fails the gate. `gold_chunks.source_doc_id` must refer to an actual `doc_id` in
`gold_source_documents`; an orphaned chunk fails the referential integrity test. `gold_corpus_loads.status`
must be either `'success'` or `'failure'`; any other value fails `accepted_values`.

These are not documentation. dbt executes each one as a query against the materialized table and
counts the failures. A non-zero failure count fails the test; a failed test exits `dbt build`
non-zero.

## The Build Command Is the Gate

Three commands cover the full workflow:

```text
dbt seed     # load seeds/corpus_raw.csv
dbt build    # run models in dependency order, then run every test; non-zero exit on any test failure
dbt test     # run only the tests
```

`dbt build` is the one that matters for a pipeline. It resolves the model dependency graph, builds
each model in order, and then runs every test. If any test fails, the exit code is non-zero and the
build stops. A nightly orchestrator running `dbt build` gets a clean boolean: 0 means all models
built and all tests passed; anything else means the corpus did not promote.

That is the gate. The SQL transform is no longer silent because dbt makes it runnable, testable,
and blockable.

## Core Concepts

- A dbt model is a single `SELECT` that dbt materializes as a table or view; the materialization
  strategy and target schema are configuration in `dbt_project.yml`, not in the SQL.
- Schema tests in `models/schema.yml` assert properties of materialized columns: `not_null`,
  `unique`, `relationships`, and `accepted_values` each compile to a query dbt runs against the
  table.
- `dbt build` runs models in dependency order then runs every test; a failing test exits non-zero,
  blocking promotion of downstream layers.
- The DuckDB adapter makes the full dbt project run offline, file-based; swapping the adapter in
  `profiles.yml` targets a Fabric Warehouse with the same models and tests unchanged.

The transform is now a commit, not a script someone ran once and forgot. A reviewer can read it,
a test can break it, and a broken test means the pipeline never claims the load succeeded.

<div class="claude-handoff" data-exercise="exercises/module2/dbt-as-the-transform-layer/">

**Build It in Claude Code**: Wrap the `module2-ingestion/` medallion models in a dbt project by adding `dbt_project.yml` (with bronze/silver/gold materialization config) and `profiles.yml` (DuckDB adapter, offline); add `models/schema.yml` with `not_null`, `unique`, `relationships`, and `accepted_values` tests that gate promotion between layers; run `dbt build` to confirm all models build and all tests pass; then introduce a null `content_hash` in the silver model and prove `dbt test` exits non-zero, confirming the gate blocks the bad data.

</div>
