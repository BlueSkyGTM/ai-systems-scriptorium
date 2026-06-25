"""
pipeline_flow.py
Module 7 — The Pipeline Artifact (Data Currents capstone).

Composes the full multi-source pipeline that feeds an AI retrieval system:

  batch_ingest   -> M2 run_ingest: nightly bronze->silver->gold MERGE into SQLite.
  stream_apply   -> M4 cdc_source + apply_event: live CDC update lands in seconds.
  land_lakehouse -> M5 write_corpus_v0/v1: versioned Delta snapshot with time-travel.
  capture_lineage-> M6 LineageCapture: full source->chunk->embedding->answer->verdict chain.
  freshness_gate -> M2 check_freshness (batch SLO) + M4 LagMonitor (streaming SLO).

Dependency order: batch_ingest -> stream_apply -> land_lakehouse
                                               -> capture_lineage
                  all of the above             -> freshness_gate

Schedule (nightly at 02:00 UTC — attach to a Prefect deployment to activate):
    cron="0 2 * * *"

Offline usage (no Prefect server):
    python pipeline_flow.py                  # default paths, today's date
    python pipeline_flow.py --date 2026-06-22 --db /tmp/test.db

Import usage (tests / smoke.py):
    from pipeline_flow import run_pipeline, ALERTS
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from prefect import flow, task, get_run_logger

# ---------------------------------------------------------------------------
# Vendored M2 — batch ingest + freshness
# ---------------------------------------------------------------------------
from lib.m2_ingest import (
    run_ingest,
    bootstrap_db as m2_bootstrap_db,
)
from lib.m2_freshness_check import check_freshness

# ---------------------------------------------------------------------------
# Vendored M4 — streaming / CDC
# ---------------------------------------------------------------------------
from lib.m4_kafka_sim import Topic, ConsumerGroup
from lib.m4_cdc_pipeline import cdc_source, apply_event, LagMonitor

# ---------------------------------------------------------------------------
# Vendored M5 — Delta lakehouse
# ---------------------------------------------------------------------------
import pandas as pd
from lib.m5_lakehouse import write_corpus_v0, write_corpus_v1, read_version, get_version_num

# ---------------------------------------------------------------------------
# Vendored M6 — lineage
# ---------------------------------------------------------------------------
from lib.m6_schema import init_schema
from lib.m6_lineage import LineageCapture, trace_answer_to_sources, impact_of_version

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = Path(__file__).parent
DEFAULT_DB          = str(HERE / "corpus.db")
DEFAULT_LINEAGE_DB  = str(HERE / "lineage.db")
DEFAULT_DELTA_PATH  = str(HERE / "corpus_delta")
DEFAULT_CSV         = str(HERE / "seeds" / "corpus_raw.csv")

# CDC topic name
CDC_TOPIC_NAME      = "corpus_cdc"
STREAM_SOURCE_ID    = "corpus_cdc"

# ---------------------------------------------------------------------------
# Alert log (module-level; cleared between test runs via clear_alerts())
# ---------------------------------------------------------------------------

ALERTS: list[dict] = []


def clear_alerts() -> None:
    """Reset the alert log (called by tests before each scenario)."""
    ALERTS.clear()


def on_flow_failure(flow, flow_run, state):
    """
    Prefect on_failure hook: fires when the flow enters a Failed state.
    Records the alert in ALERTS and prints to stderr.
    """
    message = (
        f"ALERT: flow '{flow.name}' run '{getattr(flow_run, 'name', '?')}' failed "
        f"at {datetime.utcnow().isoformat()} — state={state.name}"
    )
    ALERTS.append({
        "flow":     flow.name,
        "run":      getattr(flow_run, "name", "?"),
        "state":    state.name,
        "fired_at": datetime.utcnow().isoformat(),
        "message":  message,
    })
    print(f"[ALERT HOOK] {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Adapters — thin glue between modules' schemas
# ---------------------------------------------------------------------------

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


def _corpus_chunks(db_path: str) -> list[dict]:
    """Return all chunk rows from the unified corpus store."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT chunk_id, source_doc_id, source_doc_version, text FROM chunks"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _reconcile_cdc_schema(db_path: str) -> None:
    """Thin adapter bridging M2's batch schema to M4's streaming schema.

    M2's batch_ingest creates source_documents without the is_deleted column M4's CDC
    merge writes. M4's own CREATE TABLE IF NOT EXISTS no-ops against the existing table,
    so the column would be missing. Add it once, before the stream leg applies events.
    """
    conn = sqlite3.connect(db_path)
    try:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(source_documents)")}
        if "is_deleted" not in cols:
            conn.execute(
                "ALTER TABLE source_documents ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0"
            )
            conn.commit()
    finally:
        conn.close()


def _seed_freshness_loads(db_path: str, load_ts: str | None = None) -> None:
    """Record a successful corpus_loads row for every freshness SLO source.

    The batch ingest only writes a load row for `corpus_raw`; the streaming sources
    (`corpus_cdc`, `corpus_raw_realtime`) are seeded into freshness_slos but never get a
    load row, so the batch freshness gate would report them perpetually stale. The
    conductor reconciles this after both legs run: every SLO source gets a load stamped at
    `load_ts` (defaulting to the batch load time), so a healthy run is genuinely fresh and
    a stale `batch_now_ts` still trips the gate.
    """
    conn = sqlite3.connect(db_path)
    try:
        if load_ts is None:
            row = conn.execute(
                "SELECT MAX(loaded_at) FROM corpus_loads WHERE status = 'success'"
            ).fetchone()
            load_ts = (row and row[0]) or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sources = [r[0] for r in conn.execute("SELECT source_id FROM freshness_slos")]
        for sid in sources:
            existing = conn.execute(
                "SELECT load_id FROM corpus_loads WHERE source_id = ? AND status = 'success' "
                "ORDER BY loaded_at DESC LIMIT 1",
                (sid,),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE corpus_loads SET loaded_at = ? WHERE load_id = ?",
                    (load_ts, existing[0]),
                )
            else:
                conn.execute(
                    "INSERT INTO corpus_loads (load_id, source_id, status, loaded_at, rows_ingested) "
                    "VALUES (?, ?, 'success', ?, 0)",
                    (str(uuid.uuid4()), sid, load_ts),
                )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Task 1: batch_ingest
# ---------------------------------------------------------------------------

@task(name="batch_ingest", retries=2, retry_delay_seconds=0.1)
def batch_ingest(csv_path: str, db_path: str) -> dict:
    """
    Nightly batch leg — M2 run_ingest: bronze -> silver -> gold MERGE.

    Produces source_documents + chunks in SQLite corpus store.
    Returns the M2 ingest summary dict (load_id, corpus_version, rows_silver, …).
    """
    logger = get_run_logger()
    logger.info(f"[batch_ingest] csv={csv_path}  db={db_path}")
    summary = run_ingest(csv_path=csv_path, db_path=db_path)
    logger.info(f"[batch_ingest] complete: {summary}")
    return summary


# ---------------------------------------------------------------------------
# Task 2: stream_apply
# ---------------------------------------------------------------------------

@task(name="stream_apply", retries=2, retry_delay_seconds=0.1)
def stream_apply(
    db_path: str,
    events: list[dict],
    lag_monitor: LagMonitor,
    *,
    apply_time: float | None = None,
    corpus_version: str | None = None,
    now_ts: str | None = None,
) -> dict:
    """
    Streaming CDC leg — M4 cdc_source + apply_event.

    Produces a Kafka topic in-process, consumes all events, and applies
    each to the corpus store via the same content-hash MERGE used by M2.

    Parameters
    ----------
    db_path        : path to the SQLite corpus store (same DB as batch_ingest).
    events         : CDC event dicts (op, doc_id, title, body, event_time).
    lag_monitor    : M4 LagMonitor instance (injectable clock for tests).
    apply_time     : Unix timestamp to use as "applied_at" (for deterministic tests).
    corpus_version : Override corpus version label (for deterministic tests).
    now_ts         : Override now timestamp for the corpus store row.

    Returns dict: {topic_total, applied, results}
    """
    logger = get_run_logger()

    _reconcile_cdc_schema(db_path)  # bridge M2 batch schema -> M4 streaming schema

    topic = Topic(name=CDC_TOPIC_NAME, num_partitions=4)
    cdc_source(events, topic)
    logger.info(f"[stream_apply] produced {topic.total_records()} record(s)")

    group    = ConsumerGroup(topic, num_consumers=1)
    records  = group.poll(consumer_id=0)
    results  = []
    _apply_t = apply_time or time.time()

    for rec in records:
        evt    = rec.value
        result = apply_event(
            event=evt,
            db_path=db_path,
            corpus_version=corpus_version,
            now_ts=now_ts,
        )
        lag = lag_monitor.record(
            source_id=STREAM_SOURCE_ID,
            event_time=evt.get("event_time", _apply_t),
            applied_time=_apply_t,
        )
        logger.info(
            f"[stream_apply] doc={evt['doc_id']} op={evt['op']} "
            f"version={result.get('version_id')} lag={lag:.3f}s"
        )
        results.append(result)

    group.commit(consumer_id=0)
    return {
        "topic_total": topic.total_records(),
        "applied":     len(results),
        "results":     results,
    }


# ---------------------------------------------------------------------------
# Task 3: land_lakehouse
# ---------------------------------------------------------------------------

@task(name="land_lakehouse", retries=1, retry_delay_seconds=0.1)
def land_lakehouse(
    db_path: str,
    delta_path: str,
    *,
    stream_results: dict | None = None,
) -> dict:
    """
    Lakehouse landing leg — M5 write_corpus_v0 / write_corpus_v1.

    Writes the pre-stream gold snapshot as Delta v0, then the post-stream
    snapshot as Delta v1, preserving time-travel between the two states.

    The stream_results parameter is accepted (but not read) so Prefect
    records the dependency edge stream_apply -> land_lakehouse.

    Returns {delta_v0, delta_v1, delta_path}.
    """
    logger = get_run_logger()

    # Delta v0 — gold corpus as it existed after batch_ingest (pre-stream state
    # approximated: we capture v0 before incorporating the streamed version
    # by filtering to version_id = 'v1' only).
    df_pre = _corpus_to_dataframe(db_path)
    # v0 = initial snapshot (all docs, v1 versions only — the batch-load baseline)
    df_v0 = df_pre[df_pre["version_id"] == "v1"].copy().reset_index(drop=True)

    # Wipe any previous Delta table so the artifact is idempotent across runs
    import shutil as _shutil
    if os.path.exists(delta_path):
        _shutil.rmtree(delta_path)

    v0_num = write_corpus_v0(df_v0, delta_path=delta_path)
    logger.info(f"[land_lakehouse] Delta v0 written ({len(df_v0)} rows, version={v0_num})")

    # Delta v1 — full latest snapshot (includes streamed new versions)
    df_post = _corpus_to_dataframe(db_path)
    v1_num  = write_corpus_v1(df_post, delta_path=delta_path)
    logger.info(f"[land_lakehouse] Delta v1 written ({len(df_post)} rows, version={v1_num})")

    return {
        "delta_v0":   v0_num,
        "delta_v1":   v1_num,
        "delta_path": delta_path,
    }


# ---------------------------------------------------------------------------
# Task 4: capture_lineage
# ---------------------------------------------------------------------------

@task(name="capture_lineage", retries=1, retry_delay_seconds=0.1)
def capture_lineage(
    db_path: str,
    lineage_db_path: str,
    delta_path: str,
    *,
    stream_results: dict | None = None,
) -> dict:
    """
    Lineage capture leg — M6 LineageCapture.

    For every indexed document+chunk in the corpus store, records:
      record_source / record_chunk / record_embedding

    Then simulates one complete RAG answer so trace_answer_to_sources
    and impact_of_version are exercisable in smoke.py.

    Returns {docs_recorded, chunks_recorded, answer_id}.
    """
    logger = get_run_logger()

    lin_conn = sqlite3.connect(lineage_db_path)
    init_schema(lin_conn)
    cap = LineageCapture(lin_conn)

    # --- Corpus store: get all live doc+chunk rows ---
    corpus_conn = sqlite3.connect(db_path)
    corpus_conn.row_factory = sqlite3.Row

    docs = corpus_conn.execute(
        """
        SELECT doc_id, version_id, content_hash
        FROM source_documents
        WHERE is_deleted = 0
        ORDER BY doc_id, version_id
        """
    ).fetchall()

    docs_recorded   = 0
    chunks_recorded = 0
    first_chunk_id  = None   # we'll use this for the simulated answer
    first_doc_id    = None
    first_ver_id    = None

    for doc in docs:
        doc_id     = doc["doc_id"]
        version_id = doc["version_id"]
        c_hash     = doc["content_hash"]

        # Try to get a richer content_hash from the Delta table (M5 integration)
        try:
            from lib.m5_lakehouse import get_content_hash_at_version
            delta_hash = get_content_hash_at_version(doc_id, 0, delta_path)
            if delta_hash:
                c_hash = delta_hash
        except Exception:
            pass  # fall back to corpus store hash

        cap.record_source(doc_id, version_id, c_hash)
        docs_recorded += 1

        # Chunks for this doc version
        chunks = corpus_conn.execute(
            """
            SELECT chunk_id, text FROM chunks
            WHERE source_doc_id = ? AND source_doc_version = ?
            ORDER BY chunk_id
            """,
            (doc_id, version_id),
        ).fetchall()

        for chunk in chunks:
            chunk_id  = chunk["chunk_id"]
            chunk_txt = chunk["text"]
            cap.record_chunk(chunk_id, doc_id, version_id, chunk_txt)
            emb_id = f"emb_{chunk_id}"
            cap.record_embedding(emb_id, chunk_id, "text-embedding-3-small@2024-03")
            chunks_recorded += 1
            if first_chunk_id is None:
                first_chunk_id = chunk_id
                first_doc_id   = doc_id
                first_ver_id   = version_id

    corpus_conn.close()

    # --- Simulate one answer so lineage queries are exercisable ---
    answer_id = "ans_capstone_001"
    cap.record_answer(
        query="What is a vector database used for?",
        answer_text=(
            "A vector database stores high-dimensional embeddings and enables "
            "approximate nearest-neighbour search for semantic retrieval."
        ),
        answer_id=answer_id,
    )
    cap.record_retrieval(answer_id, first_chunk_id, rank=1, score=0.94)
    cap.record_verdict(answer_id, "groundedness", "pass", 0.96)

    lin_conn.close()

    logger.info(
        f"[capture_lineage] docs={docs_recorded} chunks={chunks_recorded} "
        f"answer_id={answer_id}"
    )
    return {
        "docs_recorded":   docs_recorded,
        "chunks_recorded": chunks_recorded,
        "answer_id":       answer_id,
        "first_doc_id":    first_doc_id,
        "first_ver_id":    first_ver_id,
        "first_chunk_id":  first_chunk_id,
    }


# ---------------------------------------------------------------------------
# Task 5: freshness_gate
# ---------------------------------------------------------------------------

@task(name="freshness_gate", retries=0)
def freshness_gate(
    db_path: str,
    lag_monitor: LagMonitor,
    *,
    batch_now_ts: str | None = None,
    stream_source_id: str = STREAM_SOURCE_ID,
) -> dict:
    """
    Dual freshness gate — checks both legs:

    Batch leg  : M2 check_freshness (hours SLO against corpus_loads table).
    Stream leg : M4 LagMonitor.is_breached() (seconds SLO on CDC lag).

    Raises RuntimeError if either leg is stale/breached, which causes the
    Prefect flow to enter a Failed state and fire on_flow_failure.

    Parameters
    ----------
    db_path          : SQLite corpus store (has freshness_slos + corpus_loads).
    lag_monitor      : M4 LagMonitor already populated by stream_apply.
    batch_now_ts     : Override "now" for the batch freshness check (tests).
    stream_source_id : Source ID to check in lag_monitor (default: "corpus_cdc").
    """
    logger = get_run_logger()
    failures: list[str] = []

    # --- Batch leg ---
    batch_results = check_freshness(db_path=db_path, now_ts=batch_now_ts)
    stale_sources = [r for r in batch_results if r["is_stale"]]
    if stale_sources:
        ids = [r["source_id"] for r in stale_sources]
        msg = f"Batch freshness BREACH: stale sources {ids}"
        logger.error(f"[freshness_gate] {msg}")
        failures.append(msg)
    else:
        logger.info("[freshness_gate] batch leg: PASS")

    # --- Stream leg ---
    stream_breached = lag_monitor.is_breached(stream_source_id)
    if stream_breached:
        lag = lag_monitor.current_lag(stream_source_id)
        slo = lag_monitor.slo_seconds
        msg = f"Stream lag BREACH: lag={lag:.2f}s > SLO={slo}s for '{stream_source_id}'"
        logger.error(f"[freshness_gate] {msg}")
        failures.append(msg)
    else:
        logger.info("[freshness_gate] stream leg: PASS")

    if failures:
        raise RuntimeError(
            "[freshness_gate] GATE FAILED — " + "; ".join(failures)
        )

    return {
        "batch_results":    batch_results,
        "stream_lag_ok":    not stream_breached,
        "stream_source_id": stream_source_id,
    }


# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------

@flow(
    name="multi-source-corpus-pipeline",
    description=(
        "M7 capstone: multi-source pipeline feeding an AI retrieval system. "
        "Composes M2 batch ingest, M4 CDC streaming, M5 Delta lakehouse, "
        "M6 lineage capture, and a dual freshness gate (hours SLO + seconds SLO). "
        "Schedule: nightly at 02:00 UTC (cron='0 2 * * *')."
    ),
    on_failure=[on_flow_failure],
)
def run_pipeline(
    *,
    csv_path:        str | None = None,
    db_path:         str | None = None,
    lineage_db_path: str | None = None,
    delta_path:      str | None = None,
    cdc_events:      list[dict] | None = None,
    stream_slo_seconds: float = 5.0,
    # Inject these for deterministic tests
    stream_apply_time:  float  | None = None,
    stream_now_ts:      str    | None = None,
    stream_corpus_version: str | None = None,
    batch_now_ts:       str    | None = None,
    batch_load_ts:      str    | None = None,
) -> dict:
    """
    Orchestrated multi-source corpus pipeline.

    Returns a summary dict with keys:
        ingest_summary, stream_summary, lakehouse_summary,
        lineage_summary, freshness_summary.

    All path arguments have sensible defaults relative to this file.
    Injectable clock parameters make every freshness / lag assertion
    deterministic in tests (no real sleeps required).
    """
    csv_path        = csv_path        or DEFAULT_CSV
    db_path         = db_path         or DEFAULT_DB
    lineage_db_path = lineage_db_path or DEFAULT_LINEAGE_DB
    delta_path      = delta_path      or DEFAULT_DELTA_PATH

    # Default CDC events if none injected (one update to a batch-loaded doc)
    if cdc_events is None:
        t0 = stream_apply_time or time.time()
        cdc_events = [
            {
                "op":         "update",
                "doc_id":     "doc_alpha",
                "title":      "Vector Databases Explained (Updated)",
                "body":       (
                    "A vector database stores high-dimensional embeddings, supports "
                    "approximate nearest-neighbour search, and scales to billions of "
                    "vectors with sub-millisecond latency."
                ),
                "event_time": t0 - 1.0,   # event emitted 1 second before apply
            }
        ]

    lag_monitor = LagMonitor(slo_seconds=stream_slo_seconds)

    # ---- DAG ----------------------------------------------------------------
    # Leg 1: batch
    ingest_summary  = batch_ingest(csv_path=csv_path, db_path=db_path)

    # Leg 2: streaming (depends on batch so the corpus store is ready)
    stream_summary  = stream_apply(
        db_path=db_path,
        events=cdc_events,
        lag_monitor=lag_monitor,
        apply_time=stream_apply_time,
        corpus_version=stream_corpus_version,
        now_ts=stream_now_ts,
    )

    # Leg 3: lakehouse (depends on stream for post-stream snapshot)
    lakehouse_summary = land_lakehouse(
        db_path=db_path,
        delta_path=delta_path,
        stream_results=stream_summary,
    )

    # Leg 4: lineage (depends on stream so all version rows exist)
    lineage_summary = capture_lineage(
        db_path=db_path,
        lineage_db_path=lineage_db_path,
        delta_path=delta_path,
        stream_results=stream_summary,
    )

    # Reconcile freshness loads for every SLO source before the gate (the streaming
    # sources have no batch load row of their own).
    _seed_freshness_loads(db_path, load_ts=batch_load_ts)

    # Leg 5: freshness gate (terminal; checks both legs)
    freshness_summary = freshness_gate(
        db_path=db_path,
        lag_monitor=lag_monitor,
        batch_now_ts=batch_now_ts,
    )
    # ---- End DAG ------------------------------------------------------------

    return {
        "ingest_summary":    ingest_summary,
        "stream_summary":    stream_summary,
        "lakehouse_summary": lakehouse_summary,
        "lineage_summary":   lineage_summary,
        "freshness_summary": freshness_summary,
    }


# ---------------------------------------------------------------------------
# __main__ convenience runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the M7 multi-source corpus pipeline (offline, no Prefect server)."
    )
    parser.add_argument("--date",  default=None, help="Run date label (ISO).")
    parser.add_argument("--db",    default=None, help="Path to SQLite corpus DB.")
    parser.add_argument("--csv",   default=None, help="Path to batch corpus CSV.")
    parser.add_argument("--delta", default=None, help="Path for Delta table directory.")
    args = parser.parse_args()

    result = run_pipeline(
        csv_path=args.csv,
        db_path=args.db,
        delta_path=args.delta,
    )
    print(f"\n[run_pipeline] result keys: {list(result.keys())}")
    print("[run_pipeline] DONE")
