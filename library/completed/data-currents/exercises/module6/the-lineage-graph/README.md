# Exercise: The Lineage Graph

**Goal**: Build the `module6-lineage/` SQLite store: write `schema.py` with the six-table DDL and `init_schema(conn)`, insert a complete lineage chain by hand, and assert every link in the chain resolves.

**Why**: The graph schema is the foundation every later M6 lesson builds on; getting the foreign keys and the version anchoring right here means Lessons 2 and 3 never have a silent mismatch between old answers and reloaded documents.

## Steps

1. Create `module6-lineage/schema.py`. Define `CREATE_SQL` as the DDL string containing all six tables in order: `source_documents`, `chunks`, `embeddings`, `answers`, `retrievals`, `eval_verdicts`. Write `init_schema(conn)` that calls `conn.executescript(CREATE_SQL)` and commits.

2. Create `module6-lineage/smoke.py`. Open an in-memory SQLite connection, call `init_schema`, then insert one complete chain by hand:

   - One row in `source_documents`: pick `doc_id="doc-a"`, `version_id="v1"`, `content_hash="abc123"`.
   - One row in `chunks`: `chunk_id="chunk-1"`, `source_doc_id="doc-a"`, `source_doc_version="v1"`, `text="Retention is 90 days."`.
   - One row in `embeddings`: `embedding_id="emb-1"`, `chunk_id="chunk-1"`, `model_pin="text-embedding-3-small@2024-03"`, `content_hash="def456"`, `created_at="2026-06-22T00:00:00"`.
   - One row in `answers`: `answer_id="ans-1"`, `query="What is the retention period?"`, `answer_text="90 days."`, `created_at="2026-06-22T00:00:00"`.
   - One row in `retrievals`: `answer_id="ans-1"`, `chunk_id="chunk-1"`, `rank=1`, `score=0.92`.
   - One row in `eval_verdicts`: `answer_id="ans-1"`, `criterion="groundedness"`, `verdict="pass"`, `score=1.0`, `created_at="2026-06-22T00:00:00"`.

3. Assert each table holds exactly one row. Then run the full-chain join:

   ```sql
   SELECT sd.doc_id, sd.version_id, sd.content_hash,
          c.chunk_id, c.text,
          a.answer_id, a.answer_text,
          ev.criterion, ev.verdict, ev.score
   FROM eval_verdicts ev
   JOIN answers a ON a.answer_id = ev.answer_id
   JOIN retrievals r ON r.answer_id = a.answer_id
   JOIN chunks c ON c.chunk_id = r.chunk_id
   JOIN source_documents sd ON sd.doc_id = c.source_doc_id AND sd.version_id = c.source_doc_version
   WHERE ev.answer_id = 'ans-1';
   ```

   Assert the result has exactly one row and that `sd.doc_id == "doc-a"` and `ev.verdict == "pass"`. Exit non-zero on any failure.

4. Create `module6-lineage/tests/test_schema.py`. Mirror every `smoke.py` assertion as a named pytest test using the same in-memory setup.

## Done When

- `init_schema` creates all six tables (verify with `sqlite_master` or `PRAGMA table_list`).
- A hand-inserted chain resolves from `source_documents` through `chunks`, `answers`, and `retrievals` to `eval_verdicts` in a single join query returning one row.
- `python module6-lineage/smoke.py` exits 0.
- `pytest module6-lineage/tests/` passes (stdlib `sqlite3` only, fully offline).

## Stretch

Insert the same `doc_id="doc-a"` at a second version: `version_id="v2"`, `content_hash="xyz999"`. Create a new chunk `chunk-2` anchored to `v2`. Confirm that `chunk-1` still carries `source_doc_version="v1"` and that a lineage walk for `ans-1` (which retrieved `chunk-1`) still resolves to `v1`, not `v2`. Assert both chunks exist and point at different versions in the same query.
