# Exercise: The Incremental Merge

**Goal**: Build `ingest.py`, a batch loader that reads a synthetic raw corpus and MERGEs each document
into a versioned `source_documents` store keyed on `(doc_id, content_hash)`.

**Why**: A truncate-and-reload discards version history and forces a full re-index on every run; an
idempotent MERGE keyed on a content hash inserts only what changed and retains every prior version.

---

## Steps

This exercise seeds `module2-ingestion/`. Start there.

**1. Create the project layout.**

```
module2-ingestion/
├── corpus/
│   └── raw/          # synthetic raw documents land here
├── db/
│   └── schema.sql    # source_documents + chunks tables
├── ingest.py         # the loader
└── smoke.py          # the acceptance gate
```

**2. Generate a synthetic raw corpus.**

Write `corpus/generate.py` (run once; commit the output). Produce ~120 documents with these fields:
`doc_id` (e.g. `doc_001`), `created_on` (ISO date string), `title`, `body` (2-4 sentences), and
`category` (one of: `api-reference`, `tutorial`, `troubleshooting`, `release-notes`). Write them
as JSON Lines to `corpus/raw/corpus.jsonl`.

**3. Create the schema.**

Write `db/schema.sql`:

```sql
CREATE TABLE source_documents (
    doc_id           TEXT NOT NULL,
    version_id       TEXT NOT NULL,
    last_modified_at TEXT NOT NULL,
    content_hash     TEXT NOT NULL,
    PRIMARY KEY (doc_id, version_id)
);

CREATE TABLE chunks (
    chunk_id           TEXT PRIMARY KEY,
    source_doc_id      TEXT NOT NULL,
    source_doc_version TEXT NOT NULL,
    corpus_version     TEXT NOT NULL,
    text               TEXT NOT NULL
);
```

**4. Implement the `content_hash` helper in `ingest.py`.**

Use exactly this function (locked; do not alter):

```python
def content_hash(text: str) -> str:
    """md5 hex digest of UTF-8 encoded text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()
```

**5. Implement `merge_gold` in `ingest.py`.**

Use exactly this function (locked; do not alter):

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

You need to implement two helpers `merge_gold` calls: `next_version_id(conn, doc_id)` (returns the
next version string, e.g. `v1`, `v2`) and `chunk_text(doc_id, text)` (yields `(chunk_id, chunk_text)`
pairs; a simple fixed-size split of `text` is enough for now, with deterministic `chunk_id`s of the
form `<doc_id>_c00`, `<doc_id>_c01`, etc.).

**6. Wire the entry point.**

`ingest.py` run directly (`python ingest.py`) should: open (or create) `module2-ingestion/ingest.db`,
apply `db/schema.sql` if the tables don't exist, read `corpus/raw/corpus.jsonl`, compute the content
hash for each document's `body`, build the `silver_rows` list, call `merge_gold`, and print the count
of new versions inserted.

**7. Write `smoke.py`.**

The smoke gate runs three checks in sequence and exits non-zero if any fail:

- **First run**: call `ingest.py` (or import and call `merge_gold` directly); assert `new_versions == 120`.
- **Second run (idempotency)**: run the same corpus again; assert `new_versions == 0`.
- **Mutation run**: mutate `doc_001`'s body in memory (do not overwrite the file), re-run the merge
  with the modified corpus; assert `new_versions == 1`, then query `source_documents` and assert two
  rows for `doc_001` (both `v1` and `v2` present).

Run it:

```
python smoke.py
```

It should exit 0 and print a short pass summary.

---

## Done When

- `python ingest.py` runs without error and prints the count of new versions.
- Running it a second time prints `0 new versions`.
- `python smoke.py` exits 0: first run inserts 120 versions, second run inserts 0, mutation run
  inserts 1 new version with the old version retained.
- No external dependencies: stdlib `sqlite3`, `hashlib`, `json` only.

---

## Stretch

After `smoke.py` passes, add a fourth assertion: query `chunks` and confirm that for `doc_001`,
after the mutation run, the chunk rows for `v2` use the new `source_doc_version` (`v2`) while the
`v1` chunk rows still exist with `source_doc_version = v1`. This proves the chunk lineage is
version-aware, not just the document row.
