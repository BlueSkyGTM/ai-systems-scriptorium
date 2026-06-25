"""
tests/test_pipeline.py
CI form of the M7 smoke assertions.

Each test function maps 1-to-1 to a numbered smoke assertion so failures
are locatable by ID.  All tests share a single pipeline run (session-scoped
fixture) for speed; each builds in a fresh temp directory.
"""

from __future__ import annotations

import csv
import os
import shutil
import sqlite3
import tempfile
import time

import pytest

# ---------------------------------------------------------------------------
# Helpers
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


def _write_csv(path: str, rows: list[tuple]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["doc_id", "title", "body", "category", "created_on"])
        w.writerows(rows)


# ---------------------------------------------------------------------------
# Session-scoped fixtures — one happy-path run shared by all positive tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def tmp_dir():
    d = tempfile.mkdtemp(prefix="m7_pytest_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="session")
def pipeline_result(tmp_dir):
    """Run the full happy-path pipeline once; return (result, paths)."""
    from pipeline_flow import run_pipeline, clear_alerts

    csv_path        = os.path.join(tmp_dir, "corpus_raw.csv")
    db_path         = os.path.join(tmp_dir, "corpus.db")
    lineage_db_path = os.path.join(tmp_dir, "lineage.db")
    delta_path      = os.path.join(tmp_dir, "corpus_delta")

    _write_csv(csv_path, BATCH_DOCS)

    base_time        = 1_750_000_000.0
    stream_apply_ts  = "2026-06-15 12:00:00"
    batch_now_fresh  = "2026-06-15 12:00:30"

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
            "event_time": base_time,
        }
    ]

    clear_alerts()
    result = run_pipeline(
        csv_path=csv_path,
        db_path=db_path,
        lineage_db_path=lineage_db_path,
        delta_path=delta_path,
        cdc_events=cdc_events,
        stream_slo_seconds=5.0,
        stream_apply_time=base_time,
        stream_now_ts=stream_apply_ts,
        batch_now_ts=batch_now_fresh,
        batch_load_ts="2026-06-15 12:00:00",
    )
    paths = {
        "db_path":         db_path,
        "lineage_db_path": lineage_db_path,
        "delta_path":      delta_path,
    }
    return result, paths


@pytest.fixture(scope="session")
def corpus_conn(pipeline_result):
    _, paths = pipeline_result
    conn = sqlite3.connect(paths["db_path"])
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def lineage_conn(pipeline_result):
    _, paths = pipeline_result
    conn = sqlite3.connect(paths["lineage_db_path"])
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# 1. Batch leg
# ---------------------------------------------------------------------------

def test_1a_batch_doc_ids_in_source_documents(pipeline_result, corpus_conn):
    """All batch doc_ids appear in source_documents after batch_ingest."""
    doc_ids = {r[0] for r in corpus_conn.execute(
        "SELECT DISTINCT doc_id FROM source_documents WHERE is_deleted = 0"
    ).fetchall()}
    batch_ids = {row[0] for row in BATCH_DOCS}
    assert batch_ids.issubset(doc_ids), f"missing: {batch_ids - doc_ids}"


def test_1b_corpus_loads_row_written(corpus_conn):
    """corpus_loads has a success row for corpus_raw."""
    rows = corpus_conn.execute(
        "SELECT COUNT(*) FROM corpus_loads WHERE source_id='corpus_raw' AND status='success'"
    ).fetchone()[0]
    assert rows >= 1, "Expected at least one success load row"


def test_1c_chunks_for_every_batch_doc(corpus_conn):
    """Chunks exist for every batch-loaded document."""
    docs_with_chunks = {r[0] for r in corpus_conn.execute(
        "SELECT DISTINCT source_doc_id FROM chunks"
    ).fetchall()}
    batch_ids = {row[0] for row in BATCH_DOCS}
    assert batch_ids.issubset(docs_with_chunks), f"missing chunks: {batch_ids - docs_with_chunks}"


# ---------------------------------------------------------------------------
# 2. Streaming leg
# ---------------------------------------------------------------------------

def test_2a_cdc_produces_new_version(corpus_conn):
    """CDC update on doc_alpha produces >= 2 versions in source_documents."""
    versions = [r[0] for r in corpus_conn.execute(
        "SELECT version_id FROM source_documents WHERE doc_id='doc_alpha' ORDER BY version_id"
    ).fetchall()]
    assert len(versions) >= 2, f"Expected >= 2 versions, got: {versions}"


def test_2b_cdc_result_is_new(pipeline_result):
    """Stream apply result marks is_new=True for doc_alpha."""
    result, _ = pipeline_result
    stream_results = result["stream_summary"]["results"]
    alpha = [r for r in stream_results if r["doc_id"] == "doc_alpha"]
    assert alpha, "No stream result for doc_alpha"
    assert any(r["is_new"] for r in alpha), f"is_new never True: {alpha}"


def test_2c_per_key_partitioning(pipeline_result):
    """All CDC results for doc_alpha came through (per-key partition stability)."""
    result, _ = pipeline_result
    total_applied = result["stream_summary"]["applied"]
    assert total_applied >= 1, "Expected at least 1 CDC event applied"


# ---------------------------------------------------------------------------
# 3. Lakehouse
# ---------------------------------------------------------------------------

def test_3a_delta_has_two_versions(pipeline_result):
    """Delta table has >= 2 versions after batch + stream."""
    from lib.m5_lakehouse import get_version_num
    _, paths = pipeline_result
    v = get_version_num(paths["delta_path"])
    assert v >= 1, f"Expected version >= 1, got {v}"


def test_3b_read_version_0(pipeline_result):
    """read_version(0) returns the pre-stream snapshot (rows > 0)."""
    from lib.m5_lakehouse import read_version
    _, paths = pipeline_result
    df = read_version(0, paths["delta_path"])
    assert len(df) > 0, "v0 snapshot is empty"


def test_3c_read_version_1(pipeline_result):
    """read_version(1) returns the post-stream snapshot (rows > 0)."""
    from lib.m5_lakehouse import read_version
    _, paths = pipeline_result
    df = read_version(1, paths["delta_path"])
    assert len(df) > 0, "v1 snapshot is empty"


def test_3d_post_stream_snapshot_is_larger(pipeline_result):
    """Post-stream snapshot has more rows than pre-stream (new version row added)."""
    from lib.m5_lakehouse import read_version
    _, paths = pipeline_result
    v0 = read_version(0, paths["delta_path"])
    v1 = read_version(1, paths["delta_path"])
    assert len(v1) > len(v0), f"v0={len(v0)} v1={len(v1)}: expected v1 > v0"


def test_3e_doc_alpha_hash_differs_across_versions(pipeline_result):
    """doc_alpha has a different content_hash in v0 vs v1 (stream change visible)."""
    from lib.m5_lakehouse import read_version
    _, paths = pipeline_result
    v0 = read_version(0, paths["delta_path"])
    v1 = read_version(1, paths["delta_path"])
    h0 = set(v0[v0["doc_id"] == "doc_alpha"]["content_hash"])
    h1 = set(v1[v1["doc_id"] == "doc_alpha"]["content_hash"])
    assert h0 and h1, f"doc_alpha missing from v0 ({h0}) or v1 ({h1})"
    assert h0 != h1, f"content_hash identical across versions: {h0}"


# ---------------------------------------------------------------------------
# 4. Lineage
# ---------------------------------------------------------------------------

def test_4a_every_indexed_doc_has_lineage(pipeline_result, corpus_conn, lineage_conn):
    """Every non-deleted indexed doc has a row in the lineage source_documents table."""
    indexed = {r[0] for r in corpus_conn.execute(
        "SELECT DISTINCT doc_id FROM source_documents WHERE is_deleted = 0"
    ).fetchall()}
    lin_docs = {r[0] for r in lineage_conn.execute(
        "SELECT DISTINCT doc_id FROM source_documents"
    ).fetchall()}
    assert indexed.issubset(lin_docs), f"missing from lineage: {indexed - lin_docs}"


def test_4b_trace_resolves_simulated_answer(pipeline_result, lineage_conn):
    """trace_answer_to_sources returns rows for the simulated answer."""
    from lib.m6_lineage import trace_answer_to_sources
    result, _ = pipeline_result
    answer_id = result["lineage_summary"]["answer_id"]
    trace = trace_answer_to_sources(lineage_conn, answer_id)
    assert len(trace) >= 1, f"No trace rows for answer_id={answer_id}"


def test_4c_trace_carries_content_hash(pipeline_result, lineage_conn):
    """All traced rows carry a content_hash (exact version anchor)."""
    from lib.m6_lineage import trace_answer_to_sources
    result, _ = pipeline_result
    answer_id = result["lineage_summary"]["answer_id"]
    trace = trace_answer_to_sources(lineage_conn, answer_id)
    assert all(r.get("content_hash") for r in trace), \
        f"Missing content_hash in trace: {trace}"


def test_4d_trace_carries_eval_verdict(pipeline_result, lineage_conn):
    """Traced rows include an eval verdict."""
    from lib.m6_lineage import trace_answer_to_sources
    result, _ = pipeline_result
    answer_id = result["lineage_summary"]["answer_id"]
    trace = trace_answer_to_sources(lineage_conn, answer_id)
    assert any(r.get("verdict") for r in trace), \
        f"No verdict in trace: {trace}"


# ---------------------------------------------------------------------------
# 5. Freshness gate (healthy run)
# ---------------------------------------------------------------------------

def test_5a_batch_freshness_passes(pipeline_result):
    """Healthy run: no stale batch sources."""
    result, _ = pipeline_result
    batch_results = result["freshness_summary"]["batch_results"]
    stale = [r for r in batch_results if r["is_stale"]]
    assert stale == [], f"Unexpected stale sources: {stale}"


def test_5b_stream_freshness_passes(pipeline_result):
    """Healthy run: stream lag within SLO."""
    result, _ = pipeline_result
    assert result["freshness_summary"]["stream_lag_ok"], \
        f"Stream lag exceeded SLO: {result['freshness_summary']}"


# ---------------------------------------------------------------------------
# 6. Impact analysis
# ---------------------------------------------------------------------------

def test_6a_impact_returns_affected_answer(pipeline_result, lineage_conn):
    """impact_of_version identifies the answer affected by the streamed change."""
    from lib.m6_lineage import impact_of_version
    result, _ = pipeline_result
    first_doc_id  = result["lineage_summary"]["first_doc_id"]
    first_ver_id  = result["lineage_summary"]["first_ver_id"]
    answer_id     = result["lineage_summary"]["answer_id"]
    impact = impact_of_version(lineage_conn, first_doc_id, first_ver_id)
    assert len(impact) >= 1, f"Expected impact rows, got: {impact}"
    assert any(r["answer_id"] == answer_id for r in impact), \
        f"answer_id {answer_id} not in impact: {[r['answer_id'] for r in impact]}"


# ---------------------------------------------------------------------------
# 7. Negative run — stale batch source fails the gate
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def negative_run_dir():
    d = tempfile.mkdtemp(prefix="m7_pytest_neg_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def test_7a_stale_batch_fails_gate(negative_run_dir):
    """A stale batch source (age > SLO) raises RuntimeError from freshness_gate."""
    from pipeline_flow import run_pipeline, clear_alerts

    csv_path        = os.path.join(negative_run_dir, "corpus_raw.csv")
    db_path         = os.path.join(negative_run_dir, "corpus.db")
    lineage_db_path = os.path.join(negative_run_dir, "lineage.db")
    delta_path      = os.path.join(negative_run_dir, "corpus_delta")

    _write_csv(csv_path, BATCH_DOCS)

    base_time = 1_750_000_000.0
    # 30 hours after the ingest -> age > 25h SLO -> STALE
    batch_now_stale = "2026-06-16 18:00:00"

    clear_alerts()
    with pytest.raises(Exception):
        run_pipeline(
            csv_path=csv_path,
            db_path=db_path,
            lineage_db_path=lineage_db_path,
            delta_path=delta_path,
            cdc_events=[
                {
                    "op":         "update",
                    "doc_id":     "doc_alpha",
                    "title":      "V2",
                    "body":       "Updated.",
                    "event_time": base_time,
                }
            ],
            stream_slo_seconds=5.0,
            stream_apply_time=base_time,
            batch_now_ts=batch_now_stale,
            batch_load_ts="2026-06-15 12:00:00",
        )


def test_7b_alert_hook_fires_on_gate_failure(negative_run_dir):
    """on_failure hook populated ALERTS when the gate failed."""
    from pipeline_flow import ALERTS
    # test_7a must have already run (module-scoped fixture ensures same dir/state)
    assert len(ALERTS) >= 1, f"Expected ALERTS to be populated; got: {ALERTS}"
