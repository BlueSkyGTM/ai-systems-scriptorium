# Exercise: Capturing Lineage Automatically

## Goal

Build `LineageCapture` with six `record_*` methods that each write one lineage link as the pipeline step executes, and a `simulate_rag_run` driver that runs the full sequence end to end.

## Why

Lineage reconstructed after the fact relies on tables that may not have been written with lineage in mind. Capture-by-construction means the chain is complete the moment a pipeline run finishes, and every audit query resolves without guesswork.

## Steps

1. Open `module6-lineage/` and read `schema.py` to understand the six tables: `source_documents`, `chunks`, `embeddings`, `answers`, `retrievals`, `eval_verdicts`.

2. In `lineage.py`, implement `LineageCapture.__init__(self, conn)` that stores the connection.

3. Implement `record_source(self, doc_id, version_id, content_hash)`. Use `INSERT OR IGNORE` so repeated calls for the same `(doc_id, version_id)` are silent no-ops.

4. Implement `record_chunk(self, chunk_id, doc_id, version_id, text)`. Use `INSERT OR IGNORE` keyed on `chunk_id`.

5. Implement `record_embedding(self, embedding_id, chunk_id, model_pin)`. Read the chunk text from the `chunks` table to compute `content_hash = _sha256(row[0])`; raise `ValueError` if `chunk_id` is not found. Use `INSERT OR IGNORE` keyed on `embedding_id`.

6. Implement `record_answer(self, query, answer_text, answer_id=None)`. Generate an `answer_id` via `_uid()` if none is supplied; return the `answer_id`. Use `INSERT OR IGNORE`.

7. Implement `record_retrieval(self, answer_id, chunk_id, rank, score)`. Use a plain `INSERT` (the same chunk can appear at different ranks for different answers).

8. Implement `record_verdict(self, answer_id, criterion, verdict, score)`. Raise `ValueError` if `verdict` is not `"pass"` or `"fail"`. Use a plain `INSERT`.

9. Implement `simulate_rag_run(conn, *, ...)` with keyword-only parameters matching the locked signature. Call all six `record_*` methods in order and return the `answer_id`.

10. Run `pytest tests/` and confirm all tests pass. If a smoke gate exists, run it first.

## Done When

- `simulate_rag_run(conn)` returns an `answer_id` string.
- Each of the six tables holds exactly one matching row for that `answer_id` (query by `answer_id` in `answers`, `retrievals`, and `eval_verdicts`; by `doc_id`/`chunk_id`/`embedding_id` in the others).
- Calling `record_embedding` with an unknown `chunk_id` raises `ValueError`.
- Calling `record_verdict` with `verdict="maybe"` raises `ValueError`.
- `pytest tests/` exits 0 (offline, no model calls required).

## Stretch

Call `simulate_rag_run(conn)` twice with the same keyword arguments. Confirm that `source_documents`, `chunks`, `embeddings`, and `answers` each still hold one row (the `INSERT OR IGNORE` absorbed the second call), while `retrievals` and `eval_verdicts` each hold two rows (plain `INSERT` fires both times). Assert these counts in a short test or at the Python REPL.
