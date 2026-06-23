# Exercise: The Medallion in OneLake

**Goal**: Organize the corpus store as a single lake root with bronze, silver, and gold Delta
layers; confirm the gold Delta table reads back; write a note identifying where a shortcut removes
a copy.

**Why**: A data platform that duplicates corpora across teams accumulates stale data faster than
it can catch the drift. The single-lake + shortcut model is the production answer; proving the
gold layer is an open Delta table is the first step to making that answer real.

## Steps

Extend `module5-warehouse/` with the following:

1. Create a single lake root directory (call it `lake/`) with three subpaths:
   `lake/bronze/`, `lake/silver/`, `lake/gold/`.

2. Write the raw corpus to `lake/bronze/` as a Delta table (use `write_deltalake` with the raw
   `corpus_raw` data from the lesson-2 seed; schema: `doc_id`, `title`, `body`, `category`,
   `ingested_at`).

3. Write the cleaned corpus to `lake/silver/` as a Delta table (apply the cleaning recipe from
   lesson 2: lowercase, strip URLs, collapse whitespace, concat title + body, add `content_hash`).

4. Write the gold corpus to `lake/gold/` as a Delta table (one row per `doc_id`, curated for
   consumer reads; reuse the `write_deltalake` call from lesson 2, targeting `lake/gold/`).

5. Read back the gold Delta table with DuckDB and confirm the row count matches what you wrote.

6. Write `LAKE_LAYOUT.md` (or a module-level docstring in a `layout.py`) that:
   - names each layer's role in one sentence each,
   - identifies one concrete location where a OneLake shortcut would replace a copy (for
     example: "the ML workspace would shortcut to `lake/gold/` instead of running its own
     ingest pipeline").

## Done When

- Three layer paths exist under `lake/`: `bronze/`, `silver/`, `gold/`.
- The gold Delta table reads back via DuckDB and the row count is non-zero.
- `LAKE_LAYOUT.md` (or equivalent docstring) names each layer and calls out one concrete
  zero-copy shortcut opportunity by name.
- Everything runs offline (no cloud calls, no Fabric tenant required).

## Stretch

Add a `shortcut_target(layer: str) -> str` helper in a `layout.py` that, given `"bronze"`,
`"silver"`, or `"gold"`, returns the path another workspace would reference to read that layer
without copying it. Write a short test that calls it for each layer and asserts the returned
path is under `lake/`.
