"""
cdc_pipeline.py
Change-Data-Capture streaming pipeline.

Components:
  cdc_source(events, topic)   — producer: emit CDC events to a Kafka topic
  apply_event(event, db_path) — consumer: apply one event to the corpus store
  LagMonitor                  — per-event lag tracking with injectable clock

CDC event schema:
  {
    "op":        "insert" | "update" | "delete",
    "doc_id":    str,            # required for all ops
    "title":     str,            # required for insert/update
    "body":      str,            # required for insert/update
    "event_time": float,         # Unix timestamp (injected by source/test)
  }

Idempotency contract (inherited from M2 merge_gold):
  - insert/update: keyed on (doc_id, content_hash); replaying the same
    event cannot create a duplicate source_documents version.
  - delete: soft-delete is idempotent; re-applying to an already-deleted
    doc is a no-op.
"""

from __future__ import annotations

import sqlite3
import time
import uuid
from typing import Callable

from kafka_sim import Topic, Producer
from corpus_store import (
    CORPUS_VERSION_PREFIX,
    bootstrap_db,
    clean_text,
    content_hash,
    merge_one_document,
    soft_delete_document,
)


# ---------------------------------------------------------------------------
# CDC Source (producer side)
# ---------------------------------------------------------------------------

class ValidationError(ValueError):
    """Raised when a CDC event is malformed."""


def validate_event(event: dict) -> None:
    """
    Validate a CDC event dict before producing it to the topic.
    Raises ValidationError on failure.
    """
    if "doc_id" not in event or not event.get("doc_id"):
        raise ValidationError(f"Event missing required field 'doc_id': {event!r}")
    op = event.get("op")
    if op not in ("insert", "update", "delete"):
        raise ValidationError(
            f"Invalid op '{op}' for doc_id={event.get('doc_id')!r}; "
            f"must be insert | update | delete"
        )
    if op in ("insert", "update"):
        for field_name in ("title", "body"):
            if field_name not in event:
                raise ValidationError(
                    f"Event op='{op}' missing required field '{field_name}': {event!r}"
                )


def cdc_source(events: list[dict], topic: Topic) -> list[tuple[int, int]]:
    """
    Emit a list of CDC events to the topic, keyed by doc_id.

    Each event is validated before producing.  ValidationError is raised
    immediately; events before the bad one are already on the topic.

    Returns: list of (partition, offset) for each produced event.
    """
    producer = Producer(topic)
    addresses = []
    for event in events:
        validate_event(event)
        part, offset = producer.produce(value=event, key=event["doc_id"])
        addresses.append((part, offset))
    return addresses


# ---------------------------------------------------------------------------
# Consumer: apply one event to the corpus store
# ---------------------------------------------------------------------------

def apply_event(
    event: dict,
    db_path: str,
    corpus_version: str | None = None,
    now_ts: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> dict:
    """
    Apply a single CDC event to the SQLite corpus store.

    Parameters
    ----------
    event        : CDC event dict (must pass validate_event).
    db_path      : path to the SQLite corpus DB.
    corpus_version: label for this streaming batch (defaults to today's date).
    now_ts       : ISO timestamp for last_modified_at (injectable for tests).
    conn         : optional open connection (used by tests for isolation;
                   caller is responsible for commit/close).

    Returns a result dict:
      {
        "doc_id":     str,
        "op":         str,
        "version_id": str | None,   # None for deletes
        "is_new":     bool,
        "skipped":    bool,         # True if event was a no-op (idempotent)
      }
    """
    validate_event(event)

    op     = event["op"]
    doc_id = event["doc_id"]

    import datetime as _dt
    if now_ts is None:
        now_ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if corpus_version is None:
        corpus_version = CORPUS_VERSION_PREFIX + _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d")

    _own_conn = conn is None
    if _own_conn:
        conn = bootstrap_db(db_path)

    try:
        if op in ("insert", "update"):
            text = clean_text(event["title"], event["body"])
            version_id, is_new = merge_one_document(
                conn, doc_id, text, corpus_version, now_ts
            )
            skipped = not is_new
            result = {
                "doc_id":     doc_id,
                "op":         op,
                "version_id": version_id,
                "is_new":     is_new,
                "skipped":    skipped,
            }
        else:  # delete
            changed = soft_delete_document(conn, doc_id, now_ts)
            result = {
                "doc_id":     doc_id,
                "op":         op,
                "version_id": None,
                "is_new":     False,
                "skipped":    not changed,
            }

        # Append to event log (idempotent via event_id primary key)
        event_id = event.get("event_id") or str(uuid.uuid4())
        c_hash = content_hash(
            clean_text(event.get("title", ""), event.get("body", ""))
        ) if op != "delete" else None
        try:
            conn.execute(
                "INSERT OR IGNORE INTO cdc_event_log "
                "(event_id, doc_id, op, content_hash, applied_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (event_id, doc_id, op, c_hash, now_ts),
            )
        except Exception:
            pass  # event_log is audit-only; don't fail the pipeline for it

        if _own_conn:
            conn.commit()
            conn.close()

    except Exception:
        if _own_conn:
            conn.close()
        raise

    return result


# ---------------------------------------------------------------------------
# Lag Monitor
# ---------------------------------------------------------------------------

class LagMonitor:
    """
    Tracks per-source streaming lag: applied_time - event_time.

    Clocks are injectable so tests are deterministic (no wall-clock sleeps).

    SLO: if lag_seconds > slo_seconds the source is considered 'breached'.
    """

    def __init__(self, slo_seconds: float = 5.0) -> None:
        self.slo_seconds = slo_seconds
        # source_id -> list of lag samples (seconds)
        self._samples: dict[str, list[float]] = {}

    def record(
        self,
        source_id: str,
        event_time: float,
        applied_time: float | None = None,
    ) -> float:
        """
        Record a lag sample for source_id.

        Parameters
        ----------
        source_id    : logical name of the CDC source (e.g. "corpus_cdc").
        event_time   : Unix timestamp when the event was emitted (from event dict).
        applied_time : Unix timestamp when the event was applied to the store.
                       Defaults to time.time() (wall clock) if not injected.

        Returns the lag in seconds.
        """
        if applied_time is None:
            applied_time = time.time()
        lag = applied_time - event_time
        self._samples.setdefault(source_id, []).append(lag)
        return lag

    def current_lag(self, source_id: str) -> float | None:
        """Most recent lag sample for source_id, or None if no samples."""
        samples = self._samples.get(source_id)
        return samples[-1] if samples else None

    def max_lag(self, source_id: str) -> float | None:
        """Maximum lag recorded for source_id."""
        samples = self._samples.get(source_id)
        return max(samples) if samples else None

    def is_breached(self, source_id: str) -> bool:
        """True if the most recent lag exceeds the SLO."""
        lag = self.current_lag(source_id)
        if lag is None:
            return False
        return lag > self.slo_seconds

    def status(self, source_id: str) -> str:
        """Human-readable status: 'ok', 'breached', or 'no_data'."""
        lag = self.current_lag(source_id)
        if lag is None:
            return "no_data"
        return "breached" if lag > self.slo_seconds else "ok"

    def report(self) -> dict[str, dict]:
        """Return a full status report for all monitored sources."""
        out = {}
        for src, samples in self._samples.items():
            cur = samples[-1]
            out[src] = {
                "current_lag_s": cur,
                "max_lag_s":     max(samples),
                "sample_count":  len(samples),
                "slo_seconds":   self.slo_seconds,
                "status":        "breached" if cur > self.slo_seconds else "ok",
            }
        return out
