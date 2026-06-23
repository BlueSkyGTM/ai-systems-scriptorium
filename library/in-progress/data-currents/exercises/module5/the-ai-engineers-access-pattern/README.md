# Exercise: The AI Engineer's Access Pattern

## Goal

Confirm the warehouse query functions are read-only, use `choose_tier` as the tier router across several real workloads, and finalize `smoke.py` to assert the read does not change the Delta version and the router classifications are correct.

## Why

The AI engineer's contract with the data team is narrow: read the surface they expose, do not mutate it, and pick the tier before the query runs. This exercise makes that contract verifiable in code.

## Steps

This exercise extends `module5-warehouse/` from prior lessons. Find it, read its current state, and continue the build.

**1. Confirm the warehouse query is read-only.**

In `warehouse.py`, verify that `doc_count_by_category(df)` only runs a `SELECT` query. No `INSERT`, no `UPDATE`, no `DELETE` may appear in that function. The DuckDB query must be read-only; the function returns a DataFrame and mutates nothing.

**2. Use `choose_tier` as the tier router.**

In `tier.py` (already present from `warehouse-vs-lakehouse`), confirm `choose_tier` handles all of these workloads correctly:

- `"bi dashboard for compliance reporting"` returns `"warehouse"`
- `"rag corpus embeddings for retrieval"` returns `"lakehouse"`
- `"feature-store extraction for model training"` returns `"lakehouse"`
- `"exploratory analysis of open corpus"` returns `"lakehouse"`

**3. Finalize `smoke.py`.**

Add two assertions to `smoke.py`:

First, record the Delta table version before calling `doc_count_by_category`, call the function, then record the version after. Assert they are equal: the read must not change the version.

Second, call `choose_tier` on at least three workloads and assert the return values. Call `choose_tier("nonsense")` and assert it raises `ValueError`.

`smoke.py` must exit 0 on success with no cloud calls.

**4. Finalize `tests/`.**

Add or extend `tests/test_access_pattern.py` to cover:

- `doc_count_by_category` returns a DataFrame with `category` and `doc_count` columns, ordered descending.
- The Delta version before and after the query call is the same integer.
- `choose_tier` returns `"warehouse"` for compliance BI, `"lakehouse"` for RAG corpus and feature extraction.
- `choose_tier("nonsense")` raises `ValueError`.

## Done When

- `python smoke.py` exits 0 with no cloud calls: the Delta version is unchanged before and after the read, and `choose_tier` routes the workloads correctly.
- `python -m pytest` passes: the read leaves the Delta version unchanged, `choose_tier` routes all four workloads correctly, and `choose_tier("nonsense")` raises.

## Stretch

Assert that attempting a write through the read-only warehouse path is rejected or simply not provided. Specifically, confirm that `warehouse.py` exposes no function that calls `write_deltalake` or any DML statement. Writes go through the Delta table only; the warehouse module must be free of write paths.
