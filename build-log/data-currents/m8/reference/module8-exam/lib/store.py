"""store.py — schema + helpers shared by the broken and fixed exam pipelines.

A distilled corpus store: source documents and chunks, a corpus_loads audit table, a
freshness SLO table, and a lineage chain (answer -> retrieval -> chunk -> source, plus an
eval verdict). The broken and fixed pipelines differ only in the three defects, never in
this shared plumbing.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

SCHEMA = """
CREATE TABLE IF NOT EXISTS source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    last_modified_at TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id   TEXT PRIMARY KEY,
    doc_id     TEXT NOT NULL,
    version_id TEXT NOT NULL,
    text       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS corpus_loads (
    load_id   TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    status    TEXT NOT NULL,
    loaded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS freshness_slos (
    source_id     TEXT PRIMARY KEY,
    max_age_hours INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS answers (
    answer_id   TEXT PRIMARY KEY,
    query       TEXT NOT NULL,
    answer_text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS retrievals (
    answer_id TEXT NOT NULL,
    chunk_id  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS eval_verdicts (
    answer_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    result    TEXT NOT NULL
);
"""

SOURCE_ID = "corpus_raw"
MAX_AGE_HOURS = 25

# A tiny deterministic corpus.
DOCS: List[Tuple[str, str]] = [
    ("doc_alpha", "a vector database stores embeddings for semantic retrieval"),
    ("doc_beta", "retrieval augmented generation grounds answers in sources"),
    ("doc_gamma", "an eval verdict grades whether an answer is supported"),
]


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    p = Path(db_path)
    if p.exists():
        p.unlink()
    conn = connect(db_path)
    conn.executescript(SCHEMA)
    conn.execute(
        "INSERT OR IGNORE INTO freshness_slos VALUES (?, ?)", (SOURCE_ID, MAX_AGE_HOURS)
    )
    conn.commit()
    conn.close()


def ingest(db_path: str, loaded_at: str) -> dict:
    """Ingest the corpus: source rows, chunks, and a corpus_loads audit row."""
    conn = connect(db_path)
    for doc_id, text in DOCS:
        content_hash = str(abs(hash(text)) % (10 ** 12))
        conn.execute(
            "INSERT OR REPLACE INTO source_documents VALUES (?, 'v1', ?, ?)",
            (doc_id, content_hash, loaded_at),
        )
        conn.execute(
            "INSERT OR REPLACE INTO chunks VALUES (?, ?, 'v1', ?)",
            (f"{doc_id}_c0", doc_id, text),
        )
    conn.execute(
        "INSERT INTO corpus_loads VALUES (?, ?, 'success', ?)",
        (str(uuid.uuid4()), SOURCE_ID, loaded_at),
    )
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    conn.close()
    return {"docs_ingested": n, "loaded_at": loaded_at}


def hours_between(earlier: str, later: str) -> float:
    fmt = "%Y-%m-%d %H:%M:%S"
    return (datetime.strptime(later, fmt) - datetime.strptime(earlier, fmt)).total_seconds() / 3600.0


def last_load(db_path: str, source_id: str = SOURCE_ID) -> str | None:
    conn = connect(db_path)
    row = conn.execute(
        "SELECT MAX(loaded_at) AS t FROM corpus_loads WHERE source_id = ? AND status = 'success'",
        (source_id,),
    ).fetchone()
    conn.close()
    return row["t"] if row else None
