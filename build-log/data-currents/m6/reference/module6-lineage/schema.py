"""
schema.py
DDL for the M6 lineage store (SQLite).

Shape mirrors M1's lineage walk (08_lineage_walk.sql) and the versioned
source_documents pattern established there and in M5's Delta-table
content_hash lookup (lakehouse.py::get_content_hash_at_version).

In production the versioned content_hash would come from M5's Delta table;
here we store it directly in SQLite so the whole module is offline + self-contained.
"""

CREATE_SQL = """
-- Versioned source documents.
-- In production: content_hash is the anchor written by M5's Delta table
-- write (lakehouse.get_content_hash_at_version tracks it across versions).
CREATE TABLE IF NOT EXISTS source_documents (
    doc_id          TEXT    NOT NULL,
    version_id      TEXT    NOT NULL,
    content_hash    TEXT    NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);

-- Chunks anchored to a specific source-doc VERSION.
-- If the doc is re-ingested at a new version, new chunk_ids are created
-- so old answers remain traceable to the old version.
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id            TEXT    PRIMARY KEY,
    source_doc_id       TEXT    NOT NULL,
    source_doc_version  TEXT    NOT NULL,
    text                TEXT    NOT NULL,
    FOREIGN KEY (source_doc_id, source_doc_version)
        REFERENCES source_documents(doc_id, version_id)
);

-- Embeddings pin the model AND the content_hash of the chunk text at encode time.
-- If the chunk text changes, a new embedding_id is created (new content_hash).
CREATE TABLE IF NOT EXISTS embeddings (
    embedding_id    TEXT    PRIMARY KEY,
    chunk_id        TEXT    NOT NULL REFERENCES chunks(chunk_id),
    model_pin       TEXT    NOT NULL,   -- e.g. "text-embedding-3-small@2024-03"
    content_hash    TEXT    NOT NULL,   -- SHA-256 of chunk.text at encode time
    created_at      TEXT    NOT NULL    -- ISO-8601
);

-- Answers produced by the RAG pipeline.
CREATE TABLE IF NOT EXISTS answers (
    answer_id       TEXT    PRIMARY KEY,
    query           TEXT    NOT NULL,
    answer_text     TEXT    NOT NULL,
    created_at      TEXT    NOT NULL
);

-- Which chunks were retrieved for each answer, and at what rank/score.
CREATE TABLE IF NOT EXISTS retrievals (
    retrieval_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    answer_id       TEXT    NOT NULL REFERENCES answers(answer_id),
    chunk_id        TEXT    NOT NULL REFERENCES chunks(chunk_id),
    rank            INTEGER NOT NULL,
    score           REAL    NOT NULL
);

-- Eval verdicts: the terminal node of the lineage chain.
-- criterion examples: "groundedness", "faithfulness", "relevance"
CREATE TABLE IF NOT EXISTS eval_verdicts (
    verdict_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    answer_id       TEXT    NOT NULL REFERENCES answers(answer_id),
    criterion       TEXT    NOT NULL,
    verdict         TEXT    NOT NULL,   -- "pass" | "fail"
    score           REAL    NOT NULL,
    created_at      TEXT    NOT NULL
);
"""


def init_schema(conn) -> None:
    """Apply the lineage schema to an open SQLite connection."""
    conn.executescript(CREATE_SQL)
    conn.commit()
