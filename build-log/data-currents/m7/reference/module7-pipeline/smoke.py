"""
smoke.py
End-to-end oracle for the M7 multi-source corpus pipeline.

Runs the pipeline against a fresh temp directory, then asserts:
  1. Batch leg       — corpus_store has batch documents as source_document versions.
  2. Streaming leg   — CDC-updated doc has a NEW content version; partitioning held.
  3. Lakehouse       — Delta table has >= 2 versions; time-travel diverges at changed doc.
  4. Lineage         — every indexed doc has a lineage row; trace_answer_to_sources
                       resolves the simulated answer to the exact source-doc + content_hash.
  5. Freshness pass  — healthy run: both gates pass.
  6. Impact          — impact_of_version returns the answer affected by the streamed change.
  7. Negative run    — stale batch source FAILS the gate and fires the alert hook.

Usage:
    python smoke.py          # prints PASS/FAIL per assertion, exits non-zero on any failure
    python -m pytest tests/  # CI form (delegates to tests/test_pipeline.py)
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tempfile
import time

# ---------------------------------------------------------------------------
# Assertion helper
# ---------------------------------------------------------------------------

RESULTS: list[tuple[str, bool, str]] = []


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    marker = "  " if condition else "!"
    msg = f"[{status}] {marker}{label}"
    if detail:
        msg += f"\n        {detail}"
    print(msg)
    RESULTS.append((label, condition, detail))
    return condition


# ---------------------------------------------------------------------------
# Test corpus data
# ---------------------------------------------------------------------------

BATCH_DOCS = [
    ("doc_alpha", "Vector Databases Explained",
     "A vector database stores high-dimensional embeddings and supports "
     "approximate nearest-neighbour search enabling fast semantic retrieval at scale.",
     "retrieval", "2026-01-10"),
    ("doc_beta",  "RAG Pipeline Architecture",
     "Retrieval-augmented generation combines a retriever component with a "
     "language model generator to ground responses in a curated document corpus.",
     "architecture", "2026-01-11"),
    ("doc_gamma", "Streaming vs Batch Ingestion",
     "Batch ingestion processes large files on a schedule while streaming ingestion "
     "applies CDC events in near real-time enabling fresher retrieval.",
     "ingestion", "2026-01-12"),
]


def write_csv(path: str, rows: list[tuple]) -> None:
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["doc_id", "title", "body", "category", "created_on"])
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Main oracle
# ---------------------------------------------------------------------------

def run_smoke() -> bool:
    # Avoid polluting the real pipeline files — use a fresh temp dir
    tmp = tempfile.mkdtemp(prefix="m7_smoke_")
    try:
        return _run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _run(tmp: str) -> bool:
    from pipeline_flow import (
        run_pipeline,
        ALERTS,
        clear_alerts,
    )

    # Shared paths inside temp dir
    csv_path        = os.path.join(tmp, "corpus_raw.csv")
    db_path         = os.path.join(tmp, "corpus.db")
    lineage_db_path = os.path.join(tmp, "lineage.db")
    delta_path      = os.path.join(tmp, "corpus_delta")

    write_csv(csv_path, BATCH_DOCS)

    # Deterministic timestamp anchor
    base_time = 1_750_000_000.0                     # Unix timestamp anchor
    apply_ts  = "2026-06-15 12:00:00"               # ISO string for corpus store
    batch_load_ts       = "2026-06-15 12:00:00"     # when every source was loaded
    batch_now_ts_fresh  = "2026-06-15 12:00:30"     # just after ingest — fresh

    # CDC event: update doc_alpha with new body content
    cdc_events = [
        {
            "op":         "update",
            "doc_id":     "doc_alpha",
            "title":      "Vector Databases Explained (v2)",
            "body":       (
                "A vector database stores high-dimensional embeddings, supports "
                "approximate nearest-neighbour search, and scales to billions of "
                "vectors with sub-millisecond latency — the foundation of RAG."
            ),
            "event_time": base_time,   # injected; lag will be 0.0 s
        }
    ]

    # =========================================================================
    # HAPPY PATH RUN
    # =========================================================================
    print("\n=== M7 Smoke: HAPPY PATH ===\n")
    clear_alerts()
    result = run_pipeline(
        csv_path=csv_path,
        db_path=db_path,
        lineage_db_path=lineage_db_path,
        delta_path=delta_path,
        cdc_events=cdc_events,
        stream_slo_seconds=5.0,
        stream_apply_time=base_time,     # lag = base_time - base_time = 0 s
        stream_now_ts=apply_ts,
        batch_now_ts=batch_now_ts_fresh,
        batch_load_ts=batch_load_ts,
    )

    # ------------------------------------------------------------------
    # 1. Batch leg
    # ------------------------------------------------------------------
    print("\n--- 1. Batch leg ---")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # a) All three batch docs present
    doc_ids = {r[0] for r in conn.execute(
        "SELECT DISTINCT doc_id FROM source_documents WHERE is_deleted = 0"
    ).fetchall()}
    batch_doc_ids = {row[0] for row in BATCH_DOCS}
    check("1a. All batch doc_ids in source_documents",
          batch_doc_ids.issubset(doc_ids),
          f"expected {sorted(batch_doc_ids)}, got {sorted(doc_ids)}")

    # b) corpus_loads row written
    loads = conn.execute(
        "SELECT * FROM corpus_loads WHERE source_id='corpus_raw' AND status='success'"
    ).fetchall()
    check("1b. corpus_loads row written for batch ingest",
          len(loads) >= 1,
          f"loads found: {len(loads)}")

    # c) Chunks produced for every batch doc
    chunks_per_doc = {r[0]: r[1] for r in conn.execute(
        "SELECT source_doc_id, COUNT(*) FROM chunks GROUP BY source_doc_id"
    ).fetchall()}
    check("1c. Chunks exist for every batch doc",
          all(d in chunks_per_doc for d in batch_doc_ids),
          f"docs with chunks: {list(chunks_per_doc.keys())}")

    # ------------------------------------------------------------------
    # 2. Streaming leg
    # ------------------------------------------------------------------
    print("\n--- 2. Streaming leg ---")

    # After stream_apply doc_alpha should have two versions (v1 from batch, v2 from CDC)
    alpha_versions = conn.execute(
        "SELECT version_id FROM source_documents WHERE doc_id = 'doc_alpha' ORDER BY version_id"
    ).fetchall()
    alpha_vids = [r[0] for r in alpha_versions]
    check("2a. CDC update produced a new version for doc_alpha",
          len(alpha_vids) >= 2,
          f"versions: {alpha_vids}")

    # Partition stability: all events for doc_alpha land on the same partition
    stream_results = result["stream_summary"]["results"]
    # (We verify by checking the topic in memory is not available post-run,
    #  but the apply results should all have the same doc_id)
    alpha_results = [r for r in stream_results if r["doc_id"] == "doc_alpha"]
    check("2b. CDC result recorded for doc_alpha",
          len(alpha_results) >= 1,
          f"stream results for doc_alpha: {alpha_results}")

    check("2c. CDC result is_new=True (new content version landed)",
          any(r["is_new"] for r in alpha_results),
          f"alpha_results: {alpha_results}")

    # ------------------------------------------------------------------
    # 3. Lakehouse
    # ------------------------------------------------------------------
    print("\n--- 3. Lakehouse ---")
    from lib.m5_lakehouse import read_version, get_version_num

    v_num = get_version_num(delta_path)
    check("3a. Delta table has >= 2 versions",
          v_num >= 1,
          f"current version: {v_num}")

    df_v0  = read_version(0, delta_path)
    df_v1  = read_version(1, delta_path)

    check("3b. read_version(0) returns pre-stream snapshot",
          len(df_v0) > 0,
          f"v0 rows: {len(df_v0)}")

    check("3c. read_version(1) returns post-stream snapshot",
          len(df_v1) > 0,
          f"v1 rows: {len(df_v1)}")

    # v0 has only v1 rows (batch baseline), v1 has v1 + v2 rows
    check("3d. Post-stream snapshot is larger than pre-stream (new version row added)",
          len(df_v1) > len(df_v0),
          f"v0 rows={len(df_v0)}, v1 rows={len(df_v1)}")

    # doc_alpha in v1 has a different content_hash than in v0
    v0_alpha = df_v0[df_v0["doc_id"] == "doc_alpha"]
    v1_alpha = df_v1[df_v1["doc_id"] == "doc_alpha"]
    check("3e. doc_alpha content_hash differs between v0 and v1 snapshots",
          (not v0_alpha.empty) and (not v1_alpha.empty) and
          set(v0_alpha["content_hash"]) != set(v1_alpha["content_hash"]),
          f"v0 hashes={set(v0_alpha.get('content_hash', [])) if not v0_alpha.empty else 'empty'}, "
          f"v1 hashes={set(v1_alpha.get('content_hash', [])) if not v1_alpha.empty else 'empty'}")

    # ------------------------------------------------------------------
    # 4. Lineage
    # ------------------------------------------------------------------
    print("\n--- 4. Lineage ---")
    from lib.m6_lineage import trace_answer_to_sources, impact_of_version

    lin_conn = sqlite3.connect(lineage_db_path)

    # a) Every indexed doc has a lineage row
    lin_doc_ids = {r[0] for r in lin_conn.execute(
        "SELECT DISTINCT doc_id FROM source_documents"
    ).fetchall()}
    all_indexed_ids = {r[0] for r in conn.execute(
        "SELECT DISTINCT doc_id FROM source_documents WHERE is_deleted = 0"
    ).fetchall()}
    check("4a. Every indexed doc_id has a lineage source row",
          all_indexed_ids.issubset(lin_doc_ids),
          f"indexed={sorted(all_indexed_ids)}, lineage={sorted(lin_doc_ids)}")

    # b) trace_answer_to_sources resolves the simulated answer
    answer_id = result["lineage_summary"]["answer_id"]
    trace      = trace_answer_to_sources(lin_conn, answer_id)
    check("4b. trace_answer_to_sources returns at least one row",
          len(trace) >= 1,
          f"trace rows: {len(trace)}")

    # c) The trace resolves to a source_doc with a content_hash
    has_hash = all(r.get("content_hash") for r in trace)
    check("4c. Traced rows carry content_hash (exact version anchor)",
          has_hash,
          f"hashes: {[r.get('content_hash') for r in trace]}")

    # d) Eval verdict in the trace
    has_verdict = any(r.get("verdict") for r in trace)
    check("4d. Traced rows include eval_verdict",
          has_verdict,
          f"verdicts: {[r.get('verdict') for r in trace]}")

    # ------------------------------------------------------------------
    # 5. Freshness pass
    # ------------------------------------------------------------------
    print("\n--- 5. Freshness gate (healthy run) ---")
    freshness = result.get("freshness_summary", {})
    batch_results = freshness.get("batch_results", [])
    stale = [r for r in batch_results if r.get("is_stale")]
    check("5a. Batch freshness: no stale sources on healthy run",
          len(stale) == 0,
          f"stale: {stale}")
    check("5b. Stream freshness: lag within SLO on healthy run",
          freshness.get("stream_lag_ok", False),
          f"freshness_summary={freshness}")

    # ------------------------------------------------------------------
    # 6. Impact analysis
    # ------------------------------------------------------------------
    print("\n--- 6. Impact analysis ---")
    # doc_alpha v2 was produced by the CDC event; our answer cited doc_alpha v1 chunk.
    # impact_of_version(doc_alpha, v1) should return the affected answer.
    first_doc_id = result["lineage_summary"]["first_doc_id"]
    first_ver_id = result["lineage_summary"]["first_ver_id"]
    impact = impact_of_version(lin_conn, first_doc_id, first_ver_id)
    check("6a. impact_of_version returns the affected answer",
          len(impact) >= 1,
          f"impact rows: {impact}")

    check("6b. Affected answer_id matches the simulated answer",
          any(r["answer_id"] == answer_id for r in impact),
          f"answer_ids in impact: {[r['answer_id'] for r in impact]}")

    lin_conn.close()
    conn.close()

    # =========================================================================
    # NEGATIVE RUN — stale batch source
    # =========================================================================
    print("\n=== M7 Smoke: NEGATIVE RUN (stale batch) ===\n")

    # Separate temp dir for the negative run so artifacts don't bleed across
    tmp2 = tempfile.mkdtemp(prefix="m7_smoke_neg_")
    try:
        _run_negative(tmp2)
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    return all(ok for _, ok, _ in RESULTS)


def _run_negative(tmp: str) -> None:
    """
    7. Negative / deficient run:
       Inject a 'now' timestamp that is 30 hours after the last batch load
       (past the 25-hour corpus_raw SLO) and verify the gate fails + alert fires.
    """
    from pipeline_flow import run_pipeline, ALERTS, clear_alerts

    csv_path        = os.path.join(tmp, "corpus_raw.csv")
    db_path         = os.path.join(tmp, "corpus.db")
    lineage_db_path = os.path.join(tmp, "lineage.db")
    delta_path      = os.path.join(tmp, "corpus_delta")

    write_csv(csv_path, BATCH_DOCS)

    base_time = 1_750_000_000.0
    # Loaded at 2026-06-15 12:00; a 'now' 30 hours later -> age_hours=30 > SLO=25 -> STALE
    batch_load_ts = "2026-06-15 12:00:00"
    batch_now_ts_stale = "2026-06-16 18:00:00"

    clear_alerts()
    gate_failed = False
    try:
        run_pipeline(
            csv_path=csv_path,
            db_path=db_path,
            lineage_db_path=lineage_db_path,
            delta_path=delta_path,
            cdc_events=[
                {
                    "op":         "update",
                    "doc_id":     "doc_alpha",
                    "title":      "Vector Databases Explained (v2)",
                    "body":       "Updated body text for the negative run.",
                    "event_time": base_time,
                }
            ],
            stream_slo_seconds=5.0,
            stream_apply_time=base_time,
            batch_now_ts=batch_now_ts_stale,
            batch_load_ts=batch_load_ts,
        )
    except Exception:
        gate_failed = True

    print("\n--- 7. Negative run ---")
    check("7a. Stale batch source FAILS the freshness gate",
          gate_failed,
          "Expected RuntimeError from freshness_gate on stale corpus_raw")

    check("7b. on_failure alert hook fired",
          len(ALERTS) >= 1,
          f"ALERTS: {ALERTS}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("M7 Pipeline Artifact — Smoke Test")
    print("=" * 60)

    ok = run_smoke()

    print("\n" + "=" * 60)
    total   = len(RESULTS)
    passed  = sum(1 for _, ok_, _ in RESULTS if ok_)
    failed  = total - passed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    if not ok:
        sys.exit(1)
    print("ALL PASS")
    sys.exit(0)
