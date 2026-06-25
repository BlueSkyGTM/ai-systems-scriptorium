# Exercise: Change Data Capture

**Goal**: Extend `module4-streaming/` with a CDC event schema, a `validate_event` guard, and an `apply_event` function that applies each event using the M2 content-hash MERGE.

**Why**: A streamed change lands in seconds instead of overnight; the same idempotency contract that makes the batch load safe makes stream redelivery a no-op.

---

## Steps

This exercise extends `module4-streaming/`. Find the folder, read its current state, and confirm the existing smoke gate passes before adding anything.

**1. Reuse the M2 helpers.**

`module4-streaming/` already pulls in `content_hash` and `clean_text` from the M2 build. You need two more: `merge_one_document` (the M2 MERGE, applied to a single `doc_id`) and `soft_delete_document`. Add them to `module4-streaming/cdc.py`:

- `merge_one_document(conn, doc_id, text, corpus_version, now_ts) -> tuple[str, bool]`: runs the `(doc_id, content_hash)` check and inserts a new version only if the content changed. Returns `(version_id, is_new)`.
- `soft_delete_document(conn, doc_id, now_ts) -> bool`: marks the document deleted (add a `deleted_at` column to `source_documents` if it does not exist). Returns `True` if the row was found and updated, `False` if the `doc_id` was not in the store.

**2. Define the CDC event schema.**

Document the schema as a module-level comment in `cdc.py`:

```python
# A CDC event represents one row-level change:
# {
#   "op":        "insert" | "update" | "delete",
#   "doc_id":    str,          # required for all ops
#   "title":     str,          # required for insert/update
#   "body":      str,          # required for insert/update
#   "event_time": float,       # Unix timestamp the change occurred
# }
```

**3. Implement `validate_event`.**

Use exactly this function (locked; do not alter):

```python
def validate_event(event: dict) -> None:
    if "doc_id" not in event or not event.get("doc_id"):
        raise ValidationError(f"Event missing required field 'doc_id': {event!r}")
    op = event.get("op")
    if op not in ("insert", "update", "delete"):
        raise ValidationError(f"Invalid op '{op}'; must be insert | update | delete")
    if op in ("insert", "update"):
        for field_name in ("title", "body"):
            if field_name not in event:
                raise ValidationError(f"Event op='{op}' missing required field '{field_name}'")
```

Define `ValidationError` as a simple subclass of `Exception` at the top of `cdc.py`.

**4. Implement `apply_event`.**

Use exactly this function (locked; do not alter):

```python
def apply_event(event, db_path, corpus_version=None, now_ts=None, conn=None) -> dict:
    validate_event(event)
    op, doc_id = event["op"], event["doc_id"]
    ...
    if op in ("insert", "update"):
        text = clean_text(event["title"], event["body"])
        version_id, is_new = merge_one_document(conn, doc_id, text, corpus_version, now_ts)  # the M2 MERGE, per event
        return {"doc_id": doc_id, "op": op, "version_id": version_id, "is_new": is_new, "skipped": not is_new}
    else:  # delete
        changed = soft_delete_document(conn, doc_id, now_ts)
        return {"doc_id": doc_id, "op": op, "version_id": None, "is_new": False, "skipped": not changed}
```

Wire the `conn` parameter: if the caller passes an open connection, use it; otherwise open one from `db_path`. This keeps `apply_event` testable without touching the file system.

**5. Write the pytest suite.**

Create `module4-streaming/tests/test_cdc.py`. The suite runs fully offline against an in-memory SQLite database. Write five tests:

- **insert creates a version**: apply an insert event, query `source_documents`, assert one row for that `doc_id` with `version_id = "v1"`.
- **update with changed body creates a new version**: apply an insert, then apply an update with a different `body`, assert two rows for the same `doc_id` (v1 and v2).
- **re-applying the same event is a no-op**: apply an insert event twice, assert `source_documents` still has exactly one row for that `doc_id` and `apply_event` returns `skipped: True` on the second call.
- **delete soft-deletes**: apply an insert then a delete; assert `soft_delete_document` returns `True` and the row's `deleted_at` is set.
- **malformed event raises ValidationError without corrupting the store**: call `apply_event` with a missing `doc_id`; assert `ValidationError` is raised and `source_documents` has zero rows.

**6. Run the full test suite.**

```
python -m pytest module4-streaming/tests/
```

All prior tests must pass. The five new tests must pass. No network calls; `sqlite3` and `pytest` only.

---

## Done When

- `python -m pytest module4-streaming/tests/` exits 0.
- Applying an insert event creates a `source_documents` version with `version_id = "v1"`.
- Applying an update with a changed body creates a second version (`v2`); the first is retained.
- Re-applying the same insert event creates zero new versions and returns `skipped: True`.
- Applying a delete event sets `deleted_at` on the row; `soft_delete_document` returns `True`.
- Applying a malformed event (missing `doc_id`) raises `ValidationError` and leaves the store empty.
- No external dependencies: stdlib `sqlite3`, `hashlib`, `json`, and `pytest` only.

---

## Stretch

Assert that an update event whose `body` is identical to the current version is a no-op: `apply_event` returns `skipped: True` and `source_documents` still has exactly one version for that `doc_id`. This proves the content-hash check absorbs redundant upstream updates the same way it absorbs batch re-runs.
