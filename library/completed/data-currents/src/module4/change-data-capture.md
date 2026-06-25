# Change Data Capture

A nightly batch reload re-reads the entire table to find what changed. CDC just tells you, as it happens, exactly which rows changed and how.

The difference is not just speed. A batch job wakes up, reads 500,000 rows, hashes each one, and discards 499,987 because nothing moved. CDC emits an event the moment the database writes a row: one insert, one update, or one delete, delivered as a structured record to whoever is listening. The work scales with the change rate, not the table size.

## How CDC Works

A CDC system hooks into the database's write-ahead log or change tracking mechanism. Every committed insert, update, or delete produces a change event and puts it on a stream. A consumer reads the stream and applies each event to a downstream store.

The event carries a fixed schema:

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

Three operation types cover every mutation a relational table can produce. `insert` and `update` carry the full new row; `delete` carries only the key, because the row is gone.

Microsoft Fabric Eventstream provides CDC source connectors for Azure SQL DB and PostgreSQL that take an initial snapshot of the table, then stream every subsequent row-level change as events in this format. In the open-source world, Debezium over Kafka Connect does the same: snapshot once, stream forward. The consumer's job is identical in both cases. [MS-Learn Eventstream (CDC sources): https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/overview]

## Validation at the Boundary

Bad events corrupt the store, and corruption compounds. You reject a malformed event before it enters the pipeline, not after.

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

`validate_event` raises on the first violation it finds. The consumer calls it before any write, so a malformed event never reaches the database. A missing `doc_id` is caught at the boundary; a delete event without `title` or `body` passes because a delete legitimately omits the row's content.

## Applying the Event With the M2 MERGE

The consumer applies one event at a time:

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

`merge_one_document` is `merge_gold` from M2, applied to a single document. The logic is unchanged: hash the text, check `(doc_id, content_hash)`, insert a new version only if the content moved. An insert event on a document that already exists in the store with identical text produces no new version, because the hash matches. The correctness guarantee you established in M2 holds per event, not just per batch.

The delete path calls `soft_delete_document`: it marks the row as deleted rather than removing it, so the version history is intact. A delete event followed by an insert event on the same `doc_id` produces a new version rather than resurrecting the old one.

## Idempotency Carries Over

The M2 MERGE is idempotent on `(doc_id, content_hash)`. `apply_event` inherits that property. Apply the same insert event twice; the second call finds the `(doc_id, content_hash)` pair already in `source_documents` and returns `skipped: True`. No duplicate version, no error.

This matters because streams deliver at-least-once. An event may arrive more than once: a consumer restart, a network hiccup during acknowledgment, a redelivery after a timeout. Without idempotency, a redelivered insert doubles the version count. With it, the second delivery is a quiet no-op. The M2 MERGE was designed for a batch that might re-run; here it silently absorbs stream redelivery.

## Core Concepts

- CDC captures every insert, update, and delete from a source database as a structured event and streams it to a consumer; the consumer's work scales with the change rate, not the table size.
- A CDC event carries an `op` field (`insert`, `update`, or `delete`) and a `doc_id`; insert and update also carry the full new row; validation at the boundary rejects malformed events before they reach the store.
- `apply_event` applies one CDC event using the same content-hash MERGE as the batch load: the correctness guarantee is identical; only the latency differs.
- Because the M2 MERGE is idempotent on `(doc_id, content_hash)`, applying the same event twice is a no-op; the at-least-once delivery guarantee of a stream is absorbed without duplicating versions.

<div class="claude-handoff" data-exercise="exercises/module4/change-data-capture/">

**Build It in Claude Code**: Extend `module4-streaming/` by defining the CDC event schema (op/doc_id/title/body/event_time), a `validate_event` guard that raises `ValidationError` on a missing doc_id, an unknown op, or a missing title/body on insert/update, and an `apply_event` function that validates the event then applies insert/update via `merge_one_document` (the M2 content-hash MERGE, one document at a time) and delete via `soft_delete_document`; prove that applying an insert event creates a new `source_documents` version, that applying the same event a second time creates zero new versions, and that a malformed event raises `ValidationError` without touching the store.

</div>
