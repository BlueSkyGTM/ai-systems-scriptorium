# Wiring the Legs

Composition fails if each module dictates its own write path. It works here because batch and stream share one contract.

## One MERGE, Two Legs

The batch ingestion and the streaming pipeline both rely on the same upsert logic. This logic lives inside `merge_one_document`. The function computes the text hash, checks for an existing row, and decides whether to skip or insert a new version.

```python
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
```

Batch ingestion uses this function during the [incremental merge](../module2/the-incremental-merge.md). The streaming pipeline routes [change data capture](../module4/change-data-capture.md) events through the exact same code.

## The Idempotency Contract

The stream must handle retries without corrupting the corpus. The idempotency contract guarantees that replaying an event produces no duplicates.

```python
"""
Idempotency contract (inherited from M2 merge_gold):
  - insert/update: keyed on (doc_id, content_hash); replaying the same
    event cannot create a duplicate source_documents version.
  - delete: soft-delete is idempotent; re-applying to an already-deleted
    doc is a no-op.
"""
```

This resilience is essential for handling [retries and idempotency](../module3/retries-and-idempotency.md) safely across distributed systems.

## Thin Adapters Bridge Schemas

Vendored modules have different expectations. The pipeline uses adapter functions to translate data structures without modifying the original modules.

The corpus store collapses the document title and body into a single text field at the silver stage. The Delta writer expects a title column. The `_corpus_to_dataframe` adapter handles this mismatch by injecting an empty string.

```python
def _corpus_to_dataframe(db_path: str) -> pd.DataFrame:
    """
    Adapter: read the gold source_documents table from SQLite (M2/M4 output)
    and return a DataFrame shaped for M5's Delta write.

    Adds a synthetic 'title' column (derived from doc_id) since the M2
    corpus store collapses title+body into 'text' at the silver stage.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT doc_id, version_id, content_hash, last_modified_at,
               '' AS title
        FROM source_documents
        WHERE is_deleted = 0
        ORDER BY doc_id, version_id
        """
    ).fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=["doc_id", "version_id", "content_hash",
                                     "last_modified_at", "title"])
    return pd.DataFrame([dict(r) for r in rows])
```

## Delta as the Shared Output

The `land_lakehouse` task writes v0 as the batch baseline by filtering for `version_id == 'v1'`. It then writes v1 to capture the post-stream state. This output format relies on [open table formats Delta and Iceberg](../module5/open-table-formats-delta-and-iceberg.md) to expose versioned data.

## Why No Edits Were Needed

The shared hash contract and the thin adapters make composition painless. Vendored modules import clean because you route their outputs through unified interfaces rather than hacking their internals.

## Core Concepts

1. The pipeline prevents duplicate documents by keying merges on a tuple of doc_id and content_hash.
2. Thin adapter functions resolve schema mismatches between vendored modules without altering source code.
3. A shared idempotency contract allows the system to safely replay events without duplicating state.

The edits you didn't make are the proof the contract held.

<div class="claude-handoff" data-exercise="exercises/module7/wiring-the-legs/">
**Inspect It in Claude Code** · Exercise · exercises/module7/wiring-the-legs/
</div>