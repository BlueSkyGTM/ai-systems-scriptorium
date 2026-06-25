"""
ingest.py
Nightly corpus reload: bronze -> silver -> gold via an idempotent MERGE.

Reads seeds/corpus_raw.csv (or an injected override) and writes into
corpus.db (SQLite) — the persistent store queried by DuckDB analytic queries.

The MERGE is keyed on (doc_id, content_hash):
  - Unchanged document: content_hash already in source_documents -> no new version.
  - Changed body: new content_hash -> new version_id, old version retained.

Usage:
  python ingest.py                      # standard run, reads seeds/corpus_raw.csv
  python ingest.py --corpus path/to.csv # inject alternate source (for test mutations)
  python ingest.py --db path/to.db      # alternate DB path (for isolated test runs)

Exits 0 on success.
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
CHUNK_TARGET_WORDS = 80     # target words per chunk
MAX_CHUNKS = 3              # hard cap: 1-3 chunks per document


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

-- answers table mirrors M1's lineage schema (written by smoke.py for lineage test)
CREATE TABLE IF NOT EXISTS answers (
    answer_id           TEXT PRIMARY KEY,
    trace_id            TEXT NOT NULL,
    retrieved_chunk_ids TEXT NOT NULL
);
"""

SEED_SLOS = [
    ("corpus_raw",          25),   # nightly: fresh within 25 hours
    ("corpus_raw_realtime",  2),   # near-RT: fresh within 2 hours
]


def bootstrap_db(db_path: str) -> sqlite3.Connection:
    """Create/open SQLite corpus store, apply schema."""
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    # Seed SLOs (INSERT OR IGNORE so re-runs are idempotent)
    conn.executemany(
        "INSERT OR IGNORE INTO freshness_slos VALUES (?, ?)",
        SEED_SLOS,
    )
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Text cleaning — made-with-ml recipe
# ---------------------------------------------------------------------------

def clean_text(title: str, body: str) -> str:
    """Apply the made-with-ml text recipe; return cleaned concatenated text."""
    # 1. Lowercase
    t = title.lower()
    b = body.lower()
    # 2. Strip
    t = t.strip()
    b = b.strip()
    # 3+4. Remove URLs then collapse whitespace
    t = re.sub(r"https?://\S+", "", t)
    b = re.sub(r"https?://\S+", "", b)
    t = re.sub(r"\s+", " ", t).strip()
    b = re.sub(r"\s+", " ", b).strip()
    # 5. Concat
    return t + " " + b


def content_hash(text: str) -> str:
    """md5 hex digest of UTF-8 encoded text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Bronze: read CSV as-is
# ---------------------------------------------------------------------------

def read_bronze(csv_path: str) -> list[dict]:
    """Read raw CSV; return list of dicts with ingested_at stamped."""
    ingested_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["ingested_at"] = ingested_at
            rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Silver: clean + hash
# ---------------------------------------------------------------------------

def to_silver(bronze_rows: list[dict]) -> list[dict]:
    """Apply text recipe + hash; deduplicate on doc_id (last wins = last in file)."""
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
# Chunking — deterministic split
# ---------------------------------------------------------------------------

def chunk_text(doc_id: str, text: str, target_words: int = CHUNK_TARGET_WORDS,
               max_chunks: int = MAX_CHUNKS) -> list[tuple[str, str]]:
    """
    Split text into 1-max_chunks slices of ~target_words each.
    Returns list of (chunk_id, chunk_text).
    chunk_id format: doc_id + '_c' + zero-padded index (e.g. doc_0001_c00).
    """
    words = text.split()
    if not words:
        return [(f"{doc_id}_c00", "")]
    chunks = []
    for idx in range(max_chunks):
        start = idx * target_words
        if start >= len(words):
            break
        end = min(start + target_words, len(words))
        chunk_words = words[start:end]
        chunk_id = f"{doc_id}_c{idx:02d}"
        chunks.append((chunk_id, " ".join(chunk_words)))
    return chunks


# ---------------------------------------------------------------------------
# Gold MERGE: idempotent UPSERT into SQLite
# ---------------------------------------------------------------------------

def next_version_id(conn: sqlite3.Connection, doc_id: str) -> str:
    """Compute the next version_id for a document (v1, v2, v3, ...)."""
    row = conn.execute(
        "SELECT COUNT(*) FROM source_documents WHERE doc_id = ?", (doc_id,)
    ).fetchone()
    n = row[0] if row else 0
    return f"v{n + 1}"


def merge_gold(conn: sqlite3.Connection, silver_rows: list[dict],
               corpus_version: str) -> int:
    """
    Idempotent MERGE into source_documents + chunks.

    Keyed on (doc_id, content_hash):
      - If (doc_id, content_hash) already exists -> skip (idempotent).
      - If doc_id exists with DIFFERENT content_hash -> insert new version.
      - If doc_id is new -> insert v1.

    Returns: number of NEW source_document versions inserted.
    """
    now_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_versions = 0

    for row in silver_rows:
        doc_id = row["doc_id"]
        c_hash = row["content_hash"]
        text = row["text"]

        # Check: does (doc_id, content_hash) already exist?
        existing = conn.execute(
            "SELECT version_id FROM source_documents "
            "WHERE doc_id = ? AND content_hash = ?",
            (doc_id, c_hash),
        ).fetchone()

        if existing:
            # Idempotent: same content already recorded — do nothing.
            version_id = existing[0]
        else:
            # New content version for this doc_id.
            version_id = next_version_id(conn, doc_id)
            conn.execute(
                "INSERT INTO source_documents (doc_id, version_id, last_modified_at, content_hash) "
                "VALUES (?, ?, ?, ?)",
                (doc_id, version_id, now_ts, c_hash),
            )
            new_versions += 1

        # Chunks: UPSERT — deterministic chunk_ids are idempotent.
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
# Audit: write corpus_loads row
# ---------------------------------------------------------------------------

def write_load_row(conn: sqlite3.Connection, source_id: str, status: str,
                   rows_ingested: int) -> str:
    """Append one corpus_loads row; return the load_id."""
    load_id = str(uuid.uuid4())
    loaded_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO corpus_loads (load_id, source_id, status, loaded_at, rows_ingested) "
        "VALUES (?, ?, ?, ?, ?)",
        (load_id, source_id, status, loaded_at, rows_ingested),
    )
    conn.commit()
    return load_id


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_ingest(csv_path: str = DEFAULT_CSV, db_path: str = DEFAULT_DB) -> dict:
    """
    Full pipeline: bronze -> silver -> gold MERGE -> audit row.
    Returns a summary dict with load metadata.
    """
    conn = bootstrap_db(db_path)

    # Bronze
    bronze = read_bronze(csv_path)

    # Silver
    silver = to_silver(bronze)

    # Corpus version tag: UTC date
    corpus_version = CORPUS_VERSION_PREFIX + datetime.utcnow().strftime("%Y%m%d")

    try:
        # Gold MERGE
        new_versions = merge_gold(conn, silver, corpus_version)

        # Audit
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
