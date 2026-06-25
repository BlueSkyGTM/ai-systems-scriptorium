# The Incremental Merge

Truncating and reloading your corpus every night is quiet until it isn't: the moment a document
changes, you lose the old version, every chunk re-indexes from scratch, and the lineage walk M1
built has nothing to compare against. You traded version history for simplicity, and you will
not know the cost until the day someone asks "what did this doc say last week?"

The fix is a MERGE keyed on a content hash. You insert only what changed, keep what didn't,
and retain every old version without touching it.

## How the MERGE Works

Every document enters the pipeline as a hash and a row in `source_documents`. The schema is:

```sql
CREATE TABLE source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    last_modified_at TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);
```

The primary key is `(doc_id, version_id)`, not `doc_id` alone. That is what allows a document
to accumulate versions: `v1`, `v2`, `v3`, each with its own hash and timestamp. A truncate-and-reload
schema uses `doc_id` as the sole key and overwrites the row; this one extends it.

The hash is an MD5 of the document's UTF-8 body:

```python
def content_hash(text: str) -> str:
    """md5 hex digest of UTF-8 encoded text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()
```

Before inserting anything, you check whether the `(doc_id, content_hash)` pair already exists.
If it does, the content is identical to a previously ingested version; skip it. If the `doc_id`
exists with a different hash, the document changed; assign the next version_id and insert. If
the `doc_id` is new, insert v1.

```python
def merge_gold(conn, silver_rows, corpus_version) -> int:
    """
    Idempotent MERGE into source_documents + chunks, keyed on (doc_id, content_hash):
      - (doc_id, content_hash) already exists -> skip (idempotent).
      - doc_id exists with a DIFFERENT content_hash -> insert a new version.
      - doc_id is new -> insert v1.
    Returns the number of NEW source_document versions inserted.
    """
    now_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_versions = 0
    for row in silver_rows:
        doc_id, c_hash, text = row["doc_id"], row["content_hash"], row["text"]
        existing = conn.execute(
            "SELECT version_id FROM source_documents WHERE doc_id = ? AND content_hash = ?",
            (doc_id, c_hash),
        ).fetchone()
        if existing:
            version_id = existing[0]                    # same content -> do nothing
        else:
            version_id = next_version_id(conn, doc_id)  # v1, v2, v3 ...
            conn.execute(
                "INSERT INTO source_documents (doc_id, version_id, last_modified_at, content_hash) "
                "VALUES (?, ?, ?, ?)",
                (doc_id, version_id, now_ts, c_hash),
            )
            new_versions += 1
        # chunks: deterministic chunk_ids make this UPSERT idempotent too
        for chunk_id, chunk_text_val in chunk_text(doc_id, text):
            conn.execute(
                "INSERT OR REPLACE INTO chunks "
                "(chunk_id, source_doc_id, source_doc_version, corpus_version, text) "
                "VALUES (?, ?, ?, ?, ?)",
                (chunk_id, doc_id, version_id, corpus_version, chunk_text_val),
            )
    conn.commit()
    return new_versions
```

The return value is the proof: run the same corpus twice and `merge_gold` returns `0` the second
time. That is the idempotency contract. Change one document's body and it returns `1`: one new
version, old version retained.

## The Warehouse Equivalent

A warehouse runs this as a single statement against a Delta or Lakehouse table:

```sql
MERGE INTO source_documents AS target
USING new_batch AS source
ON target.doc_id = source.doc_id AND target.content_hash = source.content_hash
WHEN NOT MATCHED THEN INSERT (doc_id, version_id, last_modified_at, content_hash)
  VALUES (source.doc_id, source.version_id, source.last_modified_at, source.content_hash);
```

The semantics are identical: match on `(doc_id, content_hash)`, insert only the rows that don't
already exist, leave the rest untouched.
[MS-Learn MERGE INTO (Delta): https://learn.microsoft.com/azure/databricks/delta/merge]

The artifact runs the same logic in Python over SQLite so it stays offline. The production path
swaps the `conn.execute` calls for a single `MERGE INTO`; the key and the contract stay the same.

## Why Not Truncate and Reload

A nightly truncate-and-reload feels cheaper: one `DELETE`, one bulk insert, done. But it has three
costs that compound. First, every chunk re-indexes from zero, even for documents that did not change.
Second, old versions are gone; the lineage walk cannot answer "what changed and when." Third, the
operation is not idempotent: run it twice on the same corpus and you get two full reloads, not one
quiet no-op.

A content-hash MERGE absorbs all three at the cost of one `SELECT` per document before each insert.
At nightly batch scale, that is an acceptable trade.

The hash is the key. Know what it commits you to: identical content always produces the same hash,
so the idempotency check is exact; any byte-level change produces a new hash and a new version, so
no mutation slips through silently.

## Core Concepts

- A batch corpus reload is idempotent when it is keyed on `(doc_id, content_hash)`: re-running an
  unchanged source inserts zero new rows.
- When a document's body changes, the MERGE inserts a new version_id and retains the old row; the
  version history is append-only, never overwritten.
- The content hash is an MD5 of the UTF-8 body: identical content always produces the same hash,
  any byte change produces a different one.
- A warehouse `MERGE INTO ... WHEN NOT MATCHED THEN INSERT` is the single-statement equivalent;
  the Python loop over SQLite runs the same semantics offline.

<div class="claude-handoff" data-exercise="exercises/module2/the-incremental-merge/">

**Build It in Claude Code**: Build the `ingest.py` loader that reads a synthetic raw corpus, computes a `content_hash` per document using the MD5 helper, and MERGEs into a versioned `source_documents` store keyed on `(doc_id, content_hash)`; prove it is idempotent by running it twice and asserting zero new versions on the second run, then mutate one document's body, re-run, and assert exactly one new version inserted with the old version retained.

</div>
