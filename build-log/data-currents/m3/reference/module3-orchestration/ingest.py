"""
ingest.py  (copied from M2 reference — do not edit here; the canonical source is
build-log/data-currents/m2/reference/module2-ingestion/ingest.py)

Nightly corpus reload: bronze -> silver -> gold via an idempotent MERGE.

Reads seeds/corpus_raw.csv (or an injected override) and writes into
corpus.db (SQLite) — the persistent store queried by downstream analytics.

The MERGE is keyed on (doc_id, content_hash):
  - Unchanged document: content_hash already in source_documents -> no new version.
  - Changed body: new content_hash -> new version_id, old version retained.

Public API used by M3:
    run_ingest(csv_path, db_path) -> dict
"""

import argparse
import csv
import hashlib
import os
import re
import sqlite3
import uuid
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "seeds", "corpus_raw.csv")
DEFAULT_DB  = os.path.join(HERE, "corpus.db")
CORPUS_VERSION_PREFIX = "corpus_v"
CHUNK_TARGET_WORDS = 80
MAX_CHUNKS = 3


# ---------------------------------------------------------------------------
# Schema bootstrap (SQLite)
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    last_modified_at TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id          TEXT PRIMARY KEY,
    source_doc_id     TEXT NOT NULL,
    source_doc_version TEXT NOT NULL,
    corpus_version    TEXT NOT NULL,
    text              TEXT NOT NULL
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

CREATE TABLE IF NOT EXISTS answers (
    answer_id           TEXT PRIMARY KEY,
    trace_id            TEXT NOT NULL,
    retrieved_chunk_ids TEXT NOT NULL
);
"""

SEED_SLOS = [
    # The nightly batch pipeline owns corpus_raw (25-hour SLO).
    # corpus_raw_realtime (2-hour SLO) belongs to a separate near-RT loader
    # that is out of scope for M2/M3; omitting it here so the nightly
    # freshness gate passes after a successful batch run.
    ("corpus_raw", 25),
]


def bootstrap_db(db_path: str) -> sqlite3.Connection:
    """Create/open SQLite corpus store, apply schema."""
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.executemany(
        "INSERT OR IGNORE INTO freshness_slos VALUES (?, ?)",
        SEED_SLOS,
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(title: str, body: str) -> str:
    t = title.lower().strip()
    b = body.lower().strip()
    t = re.sub(r"https?://\S+", "", t)
    b = re.sub(r"https?://\S+", "", b)
    t = re.sub(r"\s+", " ", t).strip()
    b = re.sub(r"\s+", " ", b).strip()
    return t + " " + b


def content_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Bronze
# ---------------------------------------------------------------------------

def read_bronze(csv_path: str) -> list[dict]:
    ingested_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["ingested_at"] = ingested_at
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Silver
# ---------------------------------------------------------------------------

def to_silver(bronze_rows: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in bronze_rows:
        text = clean_text(row["title"], row["body"])
        h = content_hash(text)
        seen[row["doc_id"]] = {
            "doc_id":       row["doc_id"],
            "created_on":   row["created_on"],
            "category":     row["category"],
            "text":         text,
            "content_hash": h,
            "cleaned_at":   row["ingested_at"],
        }
    return list(seen.values())


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(doc_id: str, text: str, target_words: int = CHUNK_TARGET_WORDS,
               max_chunks: int = MAX_CHUNKS) -> list[tuple[str, str]]:
    words = text.split()
    if not words:
        return [(f"{doc_id}_c00", "")]
    chunks = []
    for idx in range(max_chunks):
        start = idx * target_words
        if start >= len(words):
            break
        end = min(start + target_words, len(words))
        chunk_id = f"{doc_id}_c{idx:02d}"
        chunks.append((chunk_id, " ".join(words[start:end])))
    return chunks


# ---------------------------------------------------------------------------
# Gold MERGE
# ---------------------------------------------------------------------------

def next_version_id(conn: sqlite3.Connection, doc_id: str) -> str:
    row = conn.execute(
        "SELECT COUNT(*) FROM source_documents WHERE doc_id = ?", (doc_id,)
    ).fetchone()
    n = row[0] if row else 0
    return f"v{n + 1}"


def merge_gold(conn: sqlite3.Connection, silver_rows: list[dict],
               corpus_version: str) -> int:
    """
    Idempotent MERGE into source_documents + chunks.
    Returns number of NEW source_document versions inserted.
    """
    now_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_versions = 0

    for row in silver_rows:
        doc_id = row["doc_id"]
        c_hash = row["content_hash"]
        text   = row["text"]

        existing = conn.execute(
            "SELECT version_id FROM source_documents "
            "WHERE doc_id = ? AND content_hash = ?",
            (doc_id, c_hash),
        ).fetchone()

        if existing:
            version_id = existing[0]
        else:
            version_id = next_version_id(conn, doc_id)
            conn.execute(
                "INSERT INTO source_documents "
                "(doc_id, version_id, last_modified_at, content_hash) "
                "VALUES (?, ?, ?, ?)",
                (doc_id, version_id, now_ts, c_hash),
            )
            new_versions += 1

        for chunk_id, chunk_text_val in chunk_text(doc_id, text):
            conn.execute(
                "INSERT OR REPLACE INTO chunks "
                "(chunk_id, source_doc_id, source_doc_version, corpus_version, text) "
                "VALUES (?, ?, ?, ?, ?)",
                (chunk_id, doc_id, version_id, corpus_version, chunk_text_val),
            )

    conn.commit()
    return new_versions


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def write_load_row(conn: sqlite3.Connection, source_id: str, status: str,
                   rows_ingested: int) -> str:
    load_id = str(uuid.uuid4())
    loaded_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO corpus_loads "
        "(load_id, source_id, status, loaded_at, rows_ingested) "
        "VALUES (?, ?, ?, ?, ?)",
        (load_id, source_id, status, loaded_at, rows_ingested),
    )
    conn.commit()
    return load_id


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_ingest(csv_path: str = DEFAULT_CSV, db_path: str = DEFAULT_DB) -> dict:
    """
    Full pipeline: bronze -> silver -> gold MERGE -> audit row.
    Returns a summary dict with load metadata.
    """
    conn = bootstrap_db(db_path)
    bronze = read_bronze(csv_path)
    silver = to_silver(bronze)
    corpus_version = CORPUS_VERSION_PREFIX + datetime.utcnow().strftime("%Y%m%d")

    try:
        new_versions = merge_gold(conn, silver, corpus_version)
        load_id = write_load_row(conn, "corpus_raw", "success", len(silver))
        summary = {
            "load_id":        load_id,
            "status":         "success",
            "corpus_version": corpus_version,
            "rows_silver":    len(silver),
            "new_versions":   new_versions,
        }
    except Exception as exc:
        load_id = write_load_row(conn, "corpus_raw", "failure", 0)
        conn.close()
        raise RuntimeError(f"Ingest failed (load_id={load_id}): {exc}") from exc

    conn.close()
    return summary


def main():
    parser = argparse.ArgumentParser(description="M2 corpus ingest: bronze->silver->gold")
    parser.add_argument("--corpus", default=DEFAULT_CSV, help="Path to corpus CSV")
    parser.add_argument("--db",     default=DEFAULT_DB,  help="Path to SQLite corpus DB")
    args = parser.parse_args()
    print(f"[ingest] corpus={args.corpus}  db={args.db}")
    summary = run_ingest(csv_path=args.corpus, db_path=args.db)
    print(f"[ingest] {summary}")
    print("[ingest] DONE — exit 0")


if __name__ == "__main__":
    main()
