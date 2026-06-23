# The Lineage Graph

When an eval verdict comes back "fail," the first question is: what did the model actually read? "The corpus" is not an answer. You need the exact document version, the exact chunk, the rank it held in the retrieval list, and the verdict that closed the chain. Lineage is the graph that gives you all of that, row by row.

Module 1 reconstructed this graph by hand with a CTE query, walking backward from an answer through comma-separated chunk IDs to a source document version. M6 records it as a first-class store as the pipeline runs, so the walk is a join, not a reconstruction.

## The Graph, Table by Table

Six tables, six node types. Every foreign key is an edge. Read the chain left to right.

```sql
-- Versioned source documents (the M1/M5 shape).
CREATE TABLE source_documents (
    doc_id TEXT NOT NULL, version_id TEXT NOT NULL, content_hash TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);
-- Chunks anchored to a specific source-doc VERSION.
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY, source_doc_id TEXT NOT NULL, source_doc_version TEXT NOT NULL, text TEXT NOT NULL,
    FOREIGN KEY (source_doc_id, source_doc_version) REFERENCES source_documents(doc_id, version_id)
);
-- Embeddings pin the model AND the content_hash of the chunk text at encode time.
CREATE TABLE embeddings (
    embedding_id TEXT PRIMARY KEY, chunk_id TEXT NOT NULL REFERENCES chunks(chunk_id),
    model_pin TEXT NOT NULL, content_hash TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE answers (
    answer_id TEXT PRIMARY KEY, query TEXT NOT NULL, answer_text TEXT NOT NULL, created_at TEXT NOT NULL
);
-- Which chunks were retrieved for each answer (the join table).
CREATE TABLE retrievals (
    retrieval_id INTEGER PRIMARY KEY AUTOINCREMENT, answer_id TEXT NOT NULL REFERENCES answers(answer_id),
    chunk_id TEXT NOT NULL REFERENCES chunks(chunk_id), rank INTEGER NOT NULL, score REAL NOT NULL
);
-- Eval verdicts: the terminal node of the chain.
CREATE TABLE eval_verdicts (
    verdict_id INTEGER PRIMARY KEY AUTOINCREMENT, answer_id TEXT NOT NULL REFERENCES answers(answer_id),
    criterion TEXT NOT NULL, verdict TEXT NOT NULL, score REAL NOT NULL, created_at TEXT NOT NULL
);
```

`source_documents` is the origin: a document at a version, identified by its `content_hash`. `chunks` are the fragments of that document, and they carry `source_doc_version` in their own row. `embeddings` pin the encoding model and hash the chunk text at encode time. `answers` are the RAG responses. `retrievals` is the join table that records which chunks an answer drew on, their rank, and their score. `eval_verdicts` is the terminal node: a criterion, a verdict, a score.

That is the whole chain. Source doc at a version produces chunks; a chunk is embedded; an answer retrieves chunks via the `retrievals` edge; the answer receives a verdict.

## The Load-Bearing Detail: Chunk Anchoring

The reason lineage stays honest across corpus reloads is a single column: `source_doc_version` in `chunks`.

When a document is re-ingested at a new version, the pipeline writes a new row in `source_documents` with a new `content_hash` and a new `version_id`. It also writes new chunk rows, carrying that new `version_id`. The old chunk rows are untouched; their `source_doc_version` still points at the old version.

An answer produced before the reload retrieved old chunks. Those chunks still foreign-key to the old document version. The lineage graph for that answer resolves cleanly to the corpus state that produced it, not the current state. Without version anchoring on the chunk, any reload would silently sever that connection: the chunk would re-point at the new version, and the walk would lie.

M5's Delta time-travel gives you this same guarantee at the warehouse layer. Here it lives in the SQLite foreign key. The mechanism differs; the commitment is identical.

## What M1 Did, and What M6 Does

M1's CTE query reconstructed the source-to-answer chain from tables that weren't designed to record it. It worked because the schema had the right keys, but the lineage was a query against an existing store, not a property the pipeline wrote down as it ran.

M6 inverts that. The pipeline captures each link as it creates it: a chunk capture writes to `chunks`, a retrieval capture writes to `retrievals`, a verdict capture writes to `eval_verdicts`. The graph accumulates in real time. Lessons 2 and 3 build the capture wrapper and the queries; this lesson defines the schema those lessons depend on.

## Core Concepts

- Lineage is a graph: each table is a node type (`source_documents`, `chunks`, `embeddings`, `answers`, `retrievals`, `eval_verdicts`), and each foreign key is a directed edge from origin to terminal.
- Chunks carry `source_doc_version`, not just `source_doc_id`; when a document reloads at a new version, old chunks still foreign-key to the old version, so every answer traces to the corpus state that produced it.
- `eval_verdicts` is the terminal node: it closes the chain at the judgment the pipeline made about the answer's quality.
- M1 reconstructed this chain from existing tables by query; M6 records it row by row as the pipeline runs, making the walk a join rather than a reconstruction.

<div class="claude-handoff" data-exercise="exercises/module6/the-lineage-graph/">

**Build It in Claude Code**: Seed `module6-lineage/` with `schema.py` containing the six-table DDL above and an `init_schema(conn)` function; then insert a complete chain by hand (one source document at one version, one chunk anchored to that version, one embedding, one answer, one retrieval, one eval verdict) and assert each table holds its row and every foreign key resolves via join, from source document through to verdict.

</div>
