# Exercise: Open Table Formats, Delta and Iceberg

## Goal

Extend `module5-warehouse/` with a Delta table write-and-time-travel workflow: write a corpus at
version 0, update one document and write version 1, then read each version back and confirm the
snapshots differ for the changed document.

## Why

Time-travel is the capability that makes the M6 lineage store possible. This exercise proves the
Delta log preserves both snapshots and that you can retrieve either one by version number.

## Steps

1. Open `module5-warehouse/`. Read its current layout and run any existing smoke gate before
   touching anything.

2. Call `write_corpus_v0(df, delta_path)` with a synthetic gold corpus DataFrame that has at least
   three rows, each with a `doc_id` and a `content_hash` column. Confirm the return value is `0`.

3. Pick one `doc_id`. Change its `content_hash` value (simulating a document update) and rebuild the
   DataFrame. Call `write_corpus_v1(df_updated, delta_path)`. Confirm the return value is `1`.

4. Call `read_version(0, delta_path)` and `read_version(1, delta_path)`. Assert that the two
   DataFrames differ for the changed document's `content_hash`.

5. Call `get_history(delta_path)` and print the result. Confirm it lists two entries (version 0 and
   version 1).

6. Call `get_content_hash_at_version(doc_id, 0, delta_path)` and
   `get_content_hash_at_version(doc_id, 1, delta_path)`. Assert the two values differ.

7. Wire all assertions into an offline `pytest` test. The test must pass with no network calls.

## Done When

- `write_corpus_v0` returns `0`; `write_corpus_v1` returns `1`.
- `read_version(0, delta_path)` returns the original snapshot; `read_version(1, delta_path)` returns
  the updated one.
- For the document you changed: the `content_hash` value in version 0 differs from the value in
  version 1 (asserted in the test).
- `get_content_hash_at_version(doc_id, 0, delta_path)` and the version-1 equivalent return
  different values.
- `pytest` exits 0 with no live model or network calls.

## Stretch

Assert that `read_version(999, delta_path)` raises an exception (no such version exists) without
corrupting the live table. After the bad read, call `read_version(1, delta_path)` again and confirm
it still returns the expected data.
