# Capturing Lineage Automatically

Lineage you reconstruct after an incident is lineage you might not have. The tables you need may have been overwritten, the version ids may not match, and the join you were counting on resolves to nothing. Capture it as the pipeline runs and the chain is always there, complete, by the time you need it.

The lesson 1 schema gave you the graph. This lesson puts a wrapper around the pipeline so every step writes its own node as it executes. By the time an answer reaches the user, `source_documents`, `chunks`, `embeddings`, `answers`, `retrievals`, and `eval_verdicts` all hold matching rows. Nothing needs to be reconstructed; the lineage simply is.

## The Wrapper's Job

`LineageCapture` holds one connection and exposes one method per pipeline step. Each method writes exactly one row and commits before returning. The step that called it does not need to know the schema; it just calls the method.

```python
class LineageCapture:
    def __init__(self, conn): self._conn = conn

    def record_source(self, doc_id, version_id, content_hash):
        self._conn.execute("INSERT OR IGNORE INTO source_documents (doc_id, version_id, content_hash) VALUES (?, ?, ?)",
                           (doc_id, version_id, content_hash)); self._conn.commit()

    def record_chunk(self, chunk_id, doc_id, version_id, text):
        self._conn.execute("INSERT OR IGNORE INTO chunks (chunk_id, source_doc_id, source_doc_version, text) VALUES (?, ?, ?, ?)",
                           (chunk_id, doc_id, version_id, text)); self._conn.commit()

    def record_embedding(self, embedding_id, chunk_id, model_pin):
        """Computes content_hash from the chunk text so the hash is verifiable without storing the vector."""
        row = self._conn.execute("SELECT text FROM chunks WHERE chunk_id = ?", (chunk_id,)).fetchone()
        if row is None:
            raise ValueError(f"record_embedding: chunk_id '{chunk_id}' not found. Call record_chunk first.")
        content_hash = _sha256(row[0])
        self._conn.execute("INSERT OR IGNORE INTO embeddings (embedding_id, chunk_id, model_pin, content_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                           (embedding_id, chunk_id, model_pin, content_hash, _now())); self._conn.commit()
        return content_hash

    def record_answer(self, query, answer_text, answer_id=None):
        aid = answer_id or _uid()
        self._conn.execute("INSERT OR IGNORE INTO answers (answer_id, query, answer_text, created_at) VALUES (?, ?, ?, ?)",
                           (aid, query, answer_text, _now())); self._conn.commit()
        return aid

    def record_retrieval(self, answer_id, chunk_id, rank, score):
        self._conn.execute("INSERT INTO retrievals (answer_id, chunk_id, rank, score) VALUES (?, ?, ?, ?)",
                           (answer_id, chunk_id, rank, score)); self._conn.commit()

    def record_verdict(self, answer_id, criterion, verdict, score):
        if verdict not in ("pass", "fail"):
            raise ValueError(f"record_verdict: verdict must be 'pass' or 'fail', got '{verdict}'")
        self._conn.execute("INSERT INTO eval_verdicts (answer_id, criterion, verdict, score, created_at) VALUES (?, ?, ?, ?, ?)",
                           (answer_id, criterion, verdict, score, _now())); self._conn.commit()
```

Six methods, six tables. The order is not arbitrary: `record_embedding` reads from `chunks` to derive the content hash, so it raises `ValueError` if you call it before `record_chunk`. The wrapper enforces the chain order at runtime rather than relying on you to remember it.

## Why `INSERT OR IGNORE`

Four of the six methods use `INSERT OR IGNORE`. If the same source document at the same version is ingested twice, the second call finds the primary key already present and does nothing. The run is idempotent on the rows that represent stable facts: a source document either exists at a given version or it does not.

`retrievals` does not use `INSERT OR IGNORE` because the same chunk can legitimately be retrieved at different ranks across different answers. `eval_verdicts` likewise accepts one row per criterion per answer, not one row total. The distinction matters: idempotency applies to the stable nodes in the graph, not the edges that connect them.

## The End-to-End Driver

`simulate_rag_run` drives the full sequence through the wrapper. It is a minimal but complete RAG run: one source document, one chunk, one embedding, one answer, one retrieval, one eval verdict.

```python
def simulate_rag_run(conn, *, doc_id="doc-1", version_id="v1", content_hash=None, chunk_id="chunk-1",
                     chunk_text="Paris is the capital of France.", embedding_id="emb-1",
                     model_pin="text-embedding-3-small@2024-03", query="What is the capital of France?",
                     answer_text="The capital of France is Paris.", answer_id=None,
                     retrieval_rank=1, retrieval_score=0.92, criterion="groundedness", verdict="pass", verdict_score=0.95):
    if content_hash is None: content_hash = _sha256(chunk_text)
    cap = LineageCapture(conn)
    cap.record_source(doc_id, version_id, content_hash)
    cap.record_chunk(chunk_id, doc_id, version_id, chunk_text)
    cap.record_embedding(embedding_id, chunk_id, model_pin)
    aid = cap.record_answer(query, answer_text, answer_id=answer_id)
    cap.record_retrieval(aid, chunk_id, rank=retrieval_rank, score=retrieval_score)
    cap.record_verdict(aid, criterion, verdict, verdict_score)
    return aid
```

Every parameter is keyword-only so tests can override a single field without touching the rest. The function returns the `answer_id` so the caller can use it immediately as a query key for the backward walk you will build in lesson 3.

## What This Buys

In lesson 1 you built the schema from existing tables, reconstructing a lineage chain that was already complete. Here the chain is complete by construction: every step writes before returning. The difference is not academic. When you need to audit an answer at 2 a.m., capture-by-construction means the lineage is already there and `trace_answer_to_sources` will resolve every join. Reconstructed lineage means you are relying on a pipeline that did not know lineage mattered at the time it ran.

A system that captures as it goes treats lineage as a first-class output of every step, not an afterthought. That is the production standard.

## Core Concepts

- `LineageCapture` writes one row per pipeline step; the chain is complete the moment the step returns, not after a reconstruction pass.
- `record_embedding` reads the chunk text from the store to compute `content_hash`, so calling it before `record_chunk` raises `ValueError`; the wrapper enforces order at runtime.
- `INSERT OR IGNORE` on the stable nodes (source documents, chunks, embeddings, answers) makes each method idempotent; re-running the same pipeline step is a silent no-op on rows that already exist.
- `simulate_rag_run` is a keyword-only driver that exercises the full six-step sequence and returns the `answer_id` so callers can query or assert against the populated store immediately.

<div class="claude-handoff" data-exercise="exercises/module6/capturing-lineage-automatically/">

**Build It in Claude Code**: Extend `module6-lineage/` with a `LineageCapture` class whose six `record_*` methods each write one row to the lineage store as the pipeline step executes, plus a `simulate_rag_run` driver that calls all six in order and returns the `answer_id`; prove that a single `simulate_rag_run(conn)` call leaves a matching row in every table (`source_documents`, `chunks`, `embeddings`, `answers`, `retrievals`, `eval_verdicts`), that `record_embedding` for an unknown `chunk_id` raises `ValueError`, and that `record_verdict` with a verdict other than `"pass"` or `"fail"` raises `ValueError`.

</div>
