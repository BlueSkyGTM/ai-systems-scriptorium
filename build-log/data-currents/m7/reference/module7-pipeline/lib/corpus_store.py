"""
corpus_store.py
Reused M2 schema bootstrap + document merge/upsert for M4 streaming.

Lifted verbatim from module2-ingestion/ingest.py with two changes:
  1. merge_one_event() exposes a per-event (not per-batch) merge surface.
  2. delete semantics added: soft-delete marks is_deleted=1 on the row.

Schema note: source_documents gains an `is_deleted` column (0/1).  The
primary key (doc_id, content_hash) is unchanged; idempotency contract
is unchanged.
"""

import hashlib
import re
import sqlite3
import uuid
from datetime import datetime


# ---------------------------------------------------------------------------
# Schema (extends M2 with is_deleted flag and event_log table)
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    last_modified_at TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    is_deleted       INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (doc_id, version_id)
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id           TEXT PRIMARY KEY,
    source_doc_id      TEXT NOT NULL,
    source_doc_version TEXT NOT NULL,
    corpus_version     TEXT NOT NULL,
    text               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS corpus_loads (
    load_id       TEXT PRIMARY KEY,
    source_id     TEXT NOT NULL,
    status        TEXT NOT NULL,
    loaded_at     TEXT NOT NULL,
    rows_ingested INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS freshness_slos (
    source_id     TEXT PRIMARY KEY,
    max_age_hours INTEGER NOT NULL
);

-- CDC event log: every applied event is recorded for audit + replay
CREATE TABLE IF NOT EXISTS cdc_event_log (
    event_id      TEXT PRIMARY KEY,
    doc_id        TEXT NOT NULL,
    op            TEXT NOT NULL,
    content_hash  TEXT,
    applied_at    TEXT NOT NULL
);
"""

SEED_SLOS = [
    ("corpus_cdc",  2),   # streaming: fresh within 2 hours
]

CORPUS_VERSION_PREFIX = "corpus_v"


def bootstrap_db(db_path: str) -> sqlite3.Connection:
    """Create/open SQLite corpus store, apply schema (idempotent)."""
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.executemany(
        "INSERT OR IGNORE INTO freshness_slos VALUES (?, ?)",
        SEED_SLOS,
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Text helpers (identical to M2 — shared contract)
# ---------------------------------------------------------------------------

def clean_text(title: str, body: str) -> str:
    """Apply the made-with-ml text recipe; return cleaned concatenated text."""
    t = re.sub(r"\s+", " ", re.sub(r"https?://\S+", "", title.lower())).strip()
    b = re.sub(r"\s+", " ", re.sub(r"https?://\S+", "", body.lower())).strip()
    return t + " " + b


def content_hash(text: str) -> str:
    """md5 hex digest of UTF-8 encoded text (same as M2)."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Chunking (deterministic, identical to M2)
# ---------------------------------------------------------------------------

CHUNK_TARGET_WORDS = 80
MAX_CHUNKS = 3


def chunk_text(doc_id: str, text: str,
               target_words: int = CHUNK_TARGET_WORDS,
               max_chunks: int = MAX_CHUNKS) -> list[tuple[str, str]]:
    """Split text into 1–max_chunks slices of ~target_words each."""
    words = text.split()
    if not words:
        return [(f"{doc_id}_c00", "")]
    chunks = []
    for idx in range(max_chunks):
        start = idx * target_words
        if start >= len(words):
            break
        end = min(start + target_words, len(words))
        chunks.append((f"{doc_id}_c{idx:02d}", " ".join(words[start:end])))
    return chunks


# ---------------------------------------------------------------------------
# Gold MERGE — per-event surface (key reuse from M2 merge_gold)
# ---------------------------------------------------------------------------

def _next_version_id(conn: sqlite3.Connection, doc_id: str) -> str:
    """Compute the next version_id for a document (v1, v2, ...)."""
    row = conn.execute(
        "SELECT COUNT(*) FROM source_documents WHERE doc_id = ?", (doc_id,)
    ).fetchone()
    return f"v{(row[0] if row else 0) + 1}"


def merge_one_document(conn: sqlite3.Connection, doc_id: str, text: str,
                        corpus_version: str, now_ts: str) -> tuple[str, bool]:
    """
    Idempotent MERGE of one document (insert/update op).

    Keyed on (doc_id, content_hash):
      - Same hash already exists -> skip, return (version_id, False).
      - New hash -> insert new version, return (version_id, True).

    Also clears is_deleted flag on any existing row for this doc_id
    (an 'update' after a prior 'delete' resurrects the document).

    Returns: (version_id, is_new_version).
    """
    c_hash = content_hash(text)

    existing = conn.execute(
        "SELECT version_id FROM source_documents "
        "WHERE doc_id = ? AND content_hash = ?",
        (doc_id, c_hash),
    ).fetchone()

    if existing:
        version_id = existing[0]
        # Clear deleted flag if it was previously soft-deleted
        conn.execute(
            "UPDATE source_documents SET is_deleted = 0 "
            "WHERE doc_id = ? AND content_hash = ?",
            (doc_id, c_hash),
        )
        is_new = False
    else:
        version_id = _next_version_id(conn, doc_id)
        conn.execute(
            "INSERT INTO source_documents "
            "(doc_id, version_id, last_modified_at, content_hash, is_deleted) "
            "VALUES (?, ?, ?, ?, 0)",
            (doc_id, version_id, now_ts, c_hash),
        )
        is_new = True

    # Chunks: deterministic chunk_ids make this idempotent (INSERT OR REPLACE)
    for chunk_id, chunk_text_val in chunk_text(doc_id, text):
        conn.execute(
            "INSERT OR REPLACE INTO chunks "
            "(chunk_id, source_doc_id, source_doc_version, corpus_version, text) "
            "VALUES (?, ?, ?, ?, ?)",
            (chunk_id, doc_id, version_id, corpus_version, chunk_text_val),
        )

    return version_id, is_new


def soft_delete_document(conn: sqlite3.Connection, doc_id: str, now_ts: str) -> bool:
    """
    Soft-delete: mark all versions of doc_id as is_deleted=1.
    Returns True if any rows were updated; False if doc_id unknown.
    Idempotent: re-deleting an already-deleted doc is a no-op (returns False
    to signal 'no change', not an error).
    """
    rows = conn.execute(
        "UPDATE source_documents SET is_deleted = 1 WHERE doc_id = ? AND is_deleted = 0",
        (doc_id,),
    ).rowcount
    return rows > 0
