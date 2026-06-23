# Exercise: Lineage as a Governance Surface

**Goal**: Write a `governance_report` function over the lineage store, assert it returns the impact set and any lineage gaps, and document the mapping to Microsoft Purview Unified Catalog.

**Why**: Governance is not a dashboard someone builds later; it is a query you can answer now. The same store that powers backward and forward lineage queries is the one a governance reviewer reads. Knowing where enterprise tooling (Purview) ends and custom capture begins is the production decision.

## Steps

Extend `module6-lineage/` (the throughline artifact from earlier M6 exercises) with the following.

1. Read the current state of `module6-lineage/` before touching it. Run the existing `smoke.py` and confirm the tests that already pass are still passing.

2. In `lineage.py` (or a new `governance.py` if the file is large), write this function:

   ```python
   def governance_report(conn, doc_id, version_id):
       ...
   ```

   It must return a dict with two keys:

   - `"impact"`: the list returned by `impact_of_version(conn, doc_id, version_id)`
   - `"gaps"`: the list returned by `find_lineage_gaps(conn)`

   No new queries. No new schema. Call the functions already in the store.

3. In `smoke.py`, add assertions that:

   - call `governance_report` with a `doc_id` and `version_id` that exist in the seeded store
   - assert `report["impact"]` contains at least one entry and that the `answer_id` in the first entry matches a known seeded answer
   - assert `report["gaps"]` is empty when the store is complete

4. In `tests/`, add (or extend) a test that seeds an intentionally incomplete chain: an answer with a retrieval but no eval verdict. Assert that `governance_report` returns a gap with `"no_verdict"` in its `missing_links` for that answer.

5. Write `PURVIEW.md` in `module6-lineage/`. It must be grounded only in the MS-Learn URLs from the lesson:

   - Map `impact_of_version` to Purview impact analysis (cross-system downstream impact). [https://learn.microsoft.com/purview/data-gov-classic-lineage]
   - Map `content_hash` column tracking in `embeddings` to Purview column-level lineage (which source field changed, at what granularity). [https://learn.microsoft.com/purview/data-gov-classic-lineage-user-guide]
   - Map the local lineage store as a whole to what an enterprise would surface in Microsoft Purview Unified Catalog as a custom lineage source. [https://learn.microsoft.com/purview/unified-catalog]
   - State plainly: Purview does not yet provide lineage for AI inference or RAG pipeline steps (query through retrieval through generation through eval verdict). RAG-step lineage is not a built-in Purview feature; the local store fills that gap.

## Done When

- `governance_report(conn, doc_id, version_id)` returns `{"impact": [...], "gaps": [...]}` and calls only the existing `impact_of_version` and `find_lineage_gaps` functions.
- `smoke.py` asserts the impact set names at least one affected answer for a known seeded version, and that no gaps appear when the chain is complete.
- The incomplete-chain test in `tests/` passes: a verdict-less answer produces a gap with `"no_verdict"` in `missing_links`.
- `PURVIEW.md` maps each local function to its Purview equivalent using only the MS-Learn URLs listed above, and states the RAG-step limitation directly.
- `pytest` exits 0. All assertions are offline; no cloud calls, no network required.

## Stretch

Add a column-level analogue to `governance_report`: for the returned impact set, look up the `content_hash` and `model_pin` from `embeddings` for each cited chunk and include them in the report under a `"column_level"` key. A reviewer can then see not just which answers are affected but which encoded field (identified by `content_hash`) would change if the source version updates. Assert in `smoke.py` that the `"column_level"` key is present and contains a non-empty list.
