# Exercise: Warehouse vs Lakehouse

## Goal

Seed `module5-warehouse/` with a small gold corpus, write it as a Delta table (lakehouse), query it with DuckDB (warehouse stand-in), and implement `choose_tier` with keyword routing.

## Why

The same corpus surfaces two ways depending on the workload: open Delta for ML pipelines that need any-engine access, structured SQL for BI that needs governed aggregates. `choose_tier` makes the routing explicit and testable.

## Steps

Install the deps first:

```
pip install deltalake pandas pyarrow duckdb pytest
```

**1. Create `module5-warehouse/` and seed the gold corpus.**

In `seed.py`, define a small DataFrame with columns `doc_id` (int), `title` (str), `text` (str), `content_hash` (str), and `category` (str). Include at least three categories with multiple documents each so the aggregate query has something to rank.

**2. Write the corpus as a Delta table.**

Use `write_deltalake` with `mode="overwrite"`. Store it at `module5-warehouse/delta/gold_corpus/`.

**3. Query it with DuckDB.**

Implement `doc_count_by_category(df)` exactly as shown in the lesson: a DuckDB SQL query over the DataFrame that returns category and doc_count, ordered by doc_count descending. Call it after reading the Delta table back into a DataFrame.

**4. Implement `choose_tier`.**

In `tier.py`, define `_WAREHOUSE_KEYWORDS` and `_LAKEHOUSE_KEYWORDS` as tuples of lowercase strings, then implement `choose_tier(access_pattern: str) -> str` exactly as shown in the lesson. Warehouse keywords include: `bi`, `dashboard`, `t-sql`, `reporting`, `dml`, `power-bi`. Lakehouse keywords include: `ml`, `rag`, `embedding`, `open-format`, `delta`, `spark`, `corpus`.

**5. Wire a `smoke.py` entry point.**

`smoke.py` should: write the corpus, read it back, run `doc_count_by_category`, print the result, call `choose_tier` on two example access patterns, and print the results. It must exit 0 on success.

**6. Write `tests/test_tier.py`.**

Cover: `choose_tier("bi dashboard for sales") == "warehouse"`, `choose_tier("rag corpus embeddings") == "lakehouse"`, and `choose_tier("nonsense")` raises `ValueError`.

## Done When

- `python smoke.py` exits 0 and prints per-category counts plus two tier decisions.
- `write_deltalake` writes to `module5-warehouse/delta/gold_corpus/` without error.
- `doc_count_by_category` returns a DataFrame with a `category` column and a `doc_count` column, ordered descending.
- `choose_tier("bi dashboard for sales") == "warehouse"` passes.
- `choose_tier("rag corpus embeddings") == "lakehouse"` passes.
- `choose_tier("nonsense")` raises `ValueError`.
- `pytest tests/` passes offline with no cloud calls.

## Stretch

Add a third access pattern (your choice of workload description) to `tests/test_tier.py`, assert the tier it should return, and add a one-sentence comment explaining why that workload belongs on that surface.
