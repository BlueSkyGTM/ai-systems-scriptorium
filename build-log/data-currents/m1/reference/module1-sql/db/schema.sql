-- module1-sql/db/schema.sql
-- Three-table AI telemetry core + freshness pair + lineage extension.
-- All tables are created in SQLite (seeded by seed.py);
-- analytic queries run in DuckDB which reads this file via ATTACH.

CREATE TABLE IF NOT EXISTS spans (
    trace_id      TEXT PRIMARY KEY,
    route         TEXT NOT NULL,
    tenant_id     TEXT NOT NULL,
    latency_ms    INTEGER NOT NULL,
    input_tokens  INTEGER,
    output_tokens INTEGER,
    ts            TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_verdicts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id   TEXT NOT NULL REFERENCES spans(trace_id),
    criterion  TEXT NOT NULL,   -- 'groundedness' | 'relevance'
    verdict    TEXT NOT NULL,   -- 'pass' | 'fail'
    score      REAL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS cost_stamps (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id       TEXT NOT NULL REFERENCES spans(trace_id),
    tenant_id      TEXT NOT NULL,
    total_cost_usd REAL NOT NULL,
    input_tokens   INTEGER,
    output_tokens  INTEGER,
    billed_at      TIMESTAMP NOT NULL
);

-- Freshness pair (Query 7)
CREATE TABLE IF NOT EXISTS corpus_loads (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    status    TEXT NOT NULL,   -- 'success' | 'failure'
    loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS freshness_slos (
    source_id    TEXT PRIMARY KEY,
    max_age_hours INTEGER NOT NULL
);

-- Lineage extension (Query 8)
-- retrieved_chunk_ids: stored as a comma-separated list of chunk_id values
-- (e.g. "chunk_001,chunk_002"). DuckDB's string_split() unnests them in the query.
-- Choice rationale: SQLite has no native array type; a comma list is simpler than
-- JSON for a two-column JOIN pattern and avoids a json_each() dependency in SQLite.
CREATE TABLE IF NOT EXISTS answers (
    answer_id          TEXT PRIMARY KEY,
    trace_id           TEXT NOT NULL REFERENCES spans(trace_id),
    retrieved_chunk_ids TEXT NOT NULL   -- comma-separated chunk_id values
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id          TEXT PRIMARY KEY,
    corpus_version    TEXT NOT NULL,
    source_doc_id     TEXT NOT NULL,
    source_doc_version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    last_modified_at TIMESTAMP NOT NULL,
    content_hash     TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);
