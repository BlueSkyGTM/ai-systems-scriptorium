# Querying the Lineage Store

**Goal**: Implement `trace_answer_to_sources`, `impact_of_version`, and `find_lineage_gaps` in
`module6-lineage/lineage.py`, then prove that a regression traces back to a changed source version
and that an incomplete chain is flagged.

**Why**: Backward and forward lineage queries are what turn a corpus incident from a guessing game into
a root-cause read; gap detection ensures an incomplete chain never returns as a valid trace.

## Steps

1. Open `module6-lineage/` and run the existing smoke gate (`python smoke.py`) to confirm the schema
   and capture wrapper are green before you add anything.

2. Implement `trace_answer_to_sources(conn, answer_id)` in `lineage.py`. The function walks backward
   from an answer through `retrievals`, `chunks`, and `source_documents` to the `content_hash`, and
   left-joins `eval_verdicts` so each row carries the verdict alongside the provenance. Order results
   by `rank` then `criterion`. Return `[]` for an unknown `answer_id`.

3. Implement `impact_of_version(conn, doc_id, version_id)` in `lineage.py`. The function walks forward
   from a `source_documents` row through `chunks` and `retrievals` to `answers`. Use `DISTINCT` so an
   answer that cited multiple chunks from the same version appears once. Order by `answer_id`. Return
   `[]` when no answer cited any chunk from that version.

4. Implement `find_lineage_gaps(conn)` in `lineage.py`. For every row in `answers`, check three
   conditions: at least one row in `retrievals`, at least one row in `eval_verdicts`, and every
   retrieved chunk resolves to a `source_documents` row. Return a list of `LineageGap` objects; each
   `LineageGap` carries the `answer_id` and a `missing_links` list containing any of `"no_retrieval"`,
   `"no_verdict"`, or `"unresolved_chunks:<ids>"`. Return `[]` when all chains are complete.

5. Write `tests/test_queries.py` (or extend the existing test file). Seed the store using
   `simulate_rag_run` for the happy path, then write the following assertions:

   - Backward: `trace_answer_to_sources(conn, answer_id)` returns at least one row; the row contains
     `source_doc_id`, `source_doc_version`, `content_hash`, and `verdict`.
   - Backward nonexistent: `trace_answer_to_sources(conn, "nonexistent")` returns `[]`.
   - Forward: `impact_of_version(conn, "doc-1", "v1")` returns the `answer_id` of the seeded answer.
   - Gap detection: insert an answer row with no retrieval and no verdict, then assert
     `find_lineage_gaps` returns a `LineageGap` for that answer with `"no_retrieval"` and
     `"no_verdict"` in `missing_links`.

6. Seed a regression scenario in a test or in an extended `smoke.py` block:

   - Run `simulate_rag_run` for `doc-1 / v1` with verdict `"fail"`.
   - Call `trace_answer_to_sources` and read the `content_hash` from the result.
   - Compute the hash of the chunk text as it originally was; assert the stored hash matches.
   - Now call `impact_of_version(conn, "doc-1", "v1")` and assert the failed answer appears in the
     result, confirming the regression traces back to the version that would need to change.

## Done When

- `trace_answer_to_sources(conn, answer_id)` returns rows containing `source_doc_id`,
  `source_doc_version`, `content_hash`, and `verdict` for a seeded answer.
- `trace_answer_to_sources(conn, "nonexistent")` returns `[]`.
- `impact_of_version(conn, "doc-1", "v1")` returns the answer ID of every answer that cited a chunk
  from that version.
- An answer seeded with a `"fail"` verdict traces back to its source version and content hash via the
  backward query; `impact_of_version` for that same version returns that answer ID.
- An answer row with no retrieval and no verdict is flagged by `find_lineage_gaps` with
  `"no_retrieval"` and `"no_verdict"` in `missing_links`.
- `python smoke.py` exits 0. `pytest` is green, offline, no cloud calls.

## Stretch

Assert that `impact_of_version(conn, "doc-1", "v99")` returns `[]`: a version no answer ever cited
produces an empty impact list, not an error.
