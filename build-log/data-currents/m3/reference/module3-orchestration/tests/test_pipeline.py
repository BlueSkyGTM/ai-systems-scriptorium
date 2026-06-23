"""
tests/test_pipeline.py
pytest CI suite for Module 3 — Orchestration.

Mirrors the six smoke assertions but in pytest style with fixtures and
isolated temp directories so tests are fully parallelisable.

Run:
    python -m pytest tests/ -v
"""

import os
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta

import pytest

# ---------------------------------------------------------------------------
# Make sure the repo root is on sys.path so we can import our modules
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pipeline_flow as pf
from pipeline_flow import pipeline_flow
from ingest import run_ingest, bootstrap_db

SEEDS_CSV = os.path.join(ROOT, "seeds", "corpus_raw.csv")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Yield a path to a fresh SQLite corpus DB in a temp directory."""
    return str(tmp_path / "corpus.db")


@pytest.fixture(autouse=True)
def clear_alerts():
    """Reset the global ALERTS list before every test."""
    pf.ALERTS.clear()
    yield
    pf.ALERTS.clear()


def count_source_docs(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    n = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    conn.close()
    return n


# ---------------------------------------------------------------------------
# 1. Structure
# ---------------------------------------------------------------------------

class TestStructure:
    def test_extract_is_prefect_task(self):
        from prefect import Task
        assert isinstance(pf.extract, Task)

    def test_ingest_is_prefect_task(self):
        from prefect import Task
        assert isinstance(pf.ingest, Task)

    def test_transform_is_prefect_task(self):
        from prefect import Task
        assert isinstance(pf.transform, Task)

    def test_freshness_gate_is_prefect_task(self):
        from prefect import Task
        assert isinstance(pf.freshness_gate, Task)

    def test_pipeline_flow_is_prefect_flow(self):
        from prefect import Flow
        assert isinstance(pf.pipeline_flow, Flow)

    def test_on_failure_hook_registered(self):
        # In Prefect 3.x hooks live in on_failure_hooks (a list),
        # not on_failure (which is a bound method for registering hooks).
        from prefect import Flow
        flow_obj = pf.pipeline_flow
        assert isinstance(flow_obj, Flow)
        hooks = getattr(flow_obj, "on_failure_hooks", None)
        assert hooks is not None and len(hooks) > 0, (
            f"Expected on_failure_hooks to be non-empty, got: {hooks}"
        )

    def test_task_names_correct(self):
        """Each task has the expected Prefect name."""
        assert pf.extract.name == "extract"
        assert pf.ingest.name == "ingest"
        assert pf.transform.name == "transform"
        assert pf.freshness_gate.name == "freshness_gate"


# ---------------------------------------------------------------------------
# 2. Topological run
# ---------------------------------------------------------------------------

class TestTopologicalRun:
    def test_flow_returns_expected_keys(self, tmp_db):
        result = pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        for key in ("run_date", "csv_path", "ingest_summary", "transform_status",
                    "freshness_results"):
            assert key in result, f"Missing key: {key}"

    def test_ingest_summary_success(self, tmp_db):
        result = pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        assert result["ingest_summary"]["status"] == "success"

    def test_source_documents_populated(self, tmp_db):
        pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        assert count_source_docs(tmp_db) > 0

    def test_transform_returns_known_status(self, tmp_db):
        result = pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        assert result["transform_status"] in ("dbt_success", "transform_skipped")

    def test_freshness_results_not_empty(self, tmp_db):
        result = pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        assert isinstance(result["freshness_results"], list)
        assert len(result["freshness_results"]) > 0

    def test_tasks_execute_in_dependency_order(self, tmp_db):
        """
        Verify that data flows: extract emits a path, ingest uses that path,
        transform receives ingest output, freshness_gate receives db_path.
        We assert end state: source_documents populated AND freshness gate passed.
        """
        result = pipeline_flow(
            run_date="2026-01-15",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        # If order were wrong, ingest would have a missing/wrong CSV and fail.
        assert result["ingest_summary"]["status"] == "success"
        stale = [r for r in result["freshness_results"] if r["is_stale"]]
        assert stale == [], f"Unexpected stale sources: {stale}"


# ---------------------------------------------------------------------------
# 3. Retry
# ---------------------------------------------------------------------------

class TestRetry:
    def test_transient_failure_recovers(self, tmp_db, monkeypatch):
        """Patch run_ingest to fail on the first call, succeed on the second."""
        call_count = {"n": 0}
        original = pf.run_ingest

        def flaky(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("Injected transient failure")
            return original(*args, **kwargs)

        monkeypatch.setattr(pf, "run_ingest", flaky)

        result = pipeline_flow(
            run_date="2026-01-16",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        assert result["ingest_summary"]["status"] == "success"

    def test_retry_fires_more_than_once(self, tmp_db, monkeypatch):
        """The task should be called at least twice when the first attempt fails."""
        call_count = {"n": 0}
        original = pf.run_ingest

        def flaky(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("Injected transient failure")
            return original(*args, **kwargs)

        monkeypatch.setattr(pf, "run_ingest", flaky)

        pipeline_flow(
            run_date="2026-01-16",
            corpus_csv=SEEDS_CSV,
            db_path=tmp_db,
        )
        assert call_count["n"] >= 2, (
            f"Expected at least 2 calls (1 fail + 1 retry), got {call_count['n']}"
        )


# ---------------------------------------------------------------------------
# 4. Alert on freshness breach
# ---------------------------------------------------------------------------

class TestAlertOnBreach:
    def test_flow_raises_on_stale_source(self, tmp_db):
        """Flow must raise (not silently succeed) when the freshness gate detects staleness."""
        run_ingest(csv_path=SEEDS_CSV, db_path=tmp_db)
        far_future = (datetime.utcnow() + timedelta(hours=1000)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        with pytest.raises(Exception):
            pipeline_flow(
                run_date="2026-01-17",
                corpus_csv=SEEDS_CSV,
                db_path=tmp_db,
                freshness_now_ts=far_future,
            )

    def test_alerts_populated_after_breach(self, tmp_db):
        """ALERTS list must be non-empty after a freshness breach."""
        run_ingest(csv_path=SEEDS_CSV, db_path=tmp_db)
        far_future = (datetime.utcnow() + timedelta(hours=1000)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            pipeline_flow(
                run_date="2026-01-17",
                corpus_csv=SEEDS_CSV,
                db_path=tmp_db,
                freshness_now_ts=far_future,
            )
        except Exception:
            pass

        assert len(pf.ALERTS) > 0, "Expected ALERTS to be non-empty after breach"

    def test_alert_contains_failure_info(self, tmp_db):
        """Alert record must reference the failed flow."""
        run_ingest(csv_path=SEEDS_CSV, db_path=tmp_db)
        far_future = (datetime.utcnow() + timedelta(hours=1000)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            pipeline_flow(
                run_date="2026-01-17",
                corpus_csv=SEEDS_CSV,
                db_path=tmp_db,
                freshness_now_ts=far_future,
            )
        except Exception:
            pass

        assert len(pf.ALERTS) > 0
        alert = pf.ALERTS[0]
        assert "flow" in alert
        assert "state" in alert


# ---------------------------------------------------------------------------
# 5. Backfill idempotency
# ---------------------------------------------------------------------------

class TestBackfillIdempotency:
    def test_second_run_adds_zero_new_versions(self, tmp_db):
        """Re-ingesting identical content must not create new source_document rows."""
        pipeline_flow(run_date="2026-01-18", corpus_csv=SEEDS_CSV, db_path=tmp_db)
        count_1 = count_source_docs(tmp_db)

        result2 = pipeline_flow(
            run_date="2026-01-19", corpus_csv=SEEDS_CSV, db_path=tmp_db
        )
        count_2 = count_source_docs(tmp_db)

        assert count_2 == count_1, (
            f"Expected no new rows after identical re-run; "
            f"before={count_1}, after={count_2}"
        )
        assert result2["ingest_summary"]["new_versions"] == 0

    def test_three_runs_stable(self, tmp_db):
        """Belt-and-suspenders: three identical runs are all stable."""
        for date in ("2026-01-20", "2026-01-21", "2026-01-22"):
            pipeline_flow(run_date=date, corpus_csv=SEEDS_CSV, db_path=tmp_db)
        # All three should have the same row count as after the first
        count = count_source_docs(tmp_db)
        pipeline_flow(run_date="2026-01-23", corpus_csv=SEEDS_CSV, db_path=tmp_db)
        assert count_source_docs(tmp_db) == count


# ---------------------------------------------------------------------------
# 6. Negative: stale / missing state causes hard failure
# ---------------------------------------------------------------------------

class TestNegative:
    def test_never_loaded_db_freshness_gate_raises(self, tmp_db):
        """
        A never-loaded DB has NULL load timestamps -> check_freshness marks them
        as stale.  Call check_freshness directly (same logic that freshness_gate
        wraps) to isolate the gate without needing a Prefect run context.
        """
        from freshness_check import check_freshness
        bootstrap_db(tmp_db)  # schema + SLOs, no load rows
        results = check_freshness(db_path=tmp_db)
        stale = [r for r in results if r["is_stale"]]
        assert len(stale) > 0, (
            f"Expected at least one stale source for never-loaded DB, got: {results}"
        )

    def test_missing_csv_fails(self, tmp_db):
        """extract() should fail fast if the CSV doesn't exist."""
        with pytest.raises(Exception):
            pipeline_flow(
                run_date="2026-01-25",
                corpus_csv="/nonexistent/path/corpus.csv",
                db_path=tmp_db,
            )

    def test_freshness_gate_breach_is_not_a_warning(self, tmp_db):
        """
        Freshness breach must be a HARD failure (raises), not a logged warning.
        This is the 'no silent staleness' contract.
        """
        run_ingest(csv_path=SEEDS_CSV, db_path=tmp_db)
        future = (datetime.utcnow() + timedelta(hours=500)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        raised = False
        try:
            pipeline_flow(
                run_date="2026-01-26",
                corpus_csv=SEEDS_CSV,
                db_path=tmp_db,
                freshness_now_ts=future,
            )
        except Exception:
            raised = True
        assert raised, "Freshness breach must raise; it must not be a no-op"
