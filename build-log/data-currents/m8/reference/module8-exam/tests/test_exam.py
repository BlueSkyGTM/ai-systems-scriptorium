"""pytest suite for the Module 8 diagnostic exam.

Pins the exam contract: the broken pipeline carries three diagnosable defects, the fix
corrects them, and the rubric grades the fix PASS.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

EXAM_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXAM_DIR))

import broken_pipeline  # noqa: E402
import diagnose  # noqa: E402
import fix  # noqa: E402
import rubric  # noqa: E402

LOADED = "2026-06-24 12:00:00"
NOW_FRESH = "2026-06-24 12:05:00"
NOW_STALE = "2026-06-26 18:00:00"


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "exam.db")


def _findings(db_path, result):
    return {f["name"]: f for f in diagnose.diagnose(db_path, result)}


def test_broken_runs_to_false_success(tmp_db):
    r = broken_pipeline.run(tmp_db, LOADED, NOW_FRESH)
    assert r["raised"] is False
    assert r["gate"]["blocked"] is False  # stale but not blocked


def test_broken_has_all_three_defects(tmp_db):
    r = broken_pipeline.run(tmp_db, LOADED, NOW_FRESH)
    f = _findings(tmp_db, r)
    assert f["q1_future_now"]["found"]       # defect 1
    assert f["q3_missing_verdict"]["found"]  # defect 2
    assert f["q5_silent_gate"]["found"]      # defect 3


def test_fix_clears_all_defects(tmp_db):
    r = fix.run(tmp_db, LOADED, NOW_FRESH)
    f = _findings(tmp_db, r)
    assert not f["q1_future_now"]["found"]
    assert not f["q3_missing_verdict"]["found"]
    assert not f["q4_chain_incomplete"]["found"]
    assert not f["q5_silent_gate"]["found"]


def test_fix_healthy_run_is_clean(tmp_db):
    r = fix.run(tmp_db, LOADED, NOW_FRESH)
    assert r["fresh"]["is_stale"] is False
    assert r["raised"] is False


def test_fix_stale_run_raises(tmp_db):
    with pytest.raises(fix.FreshnessBreach):
        fix.run(tmp_db, LOADED, NOW_STALE)


def test_lineage_chain_complete_after_fix(tmp_db):
    r = fix.run(tmp_db, LOADED, NOW_FRESH)
    assert not _findings(tmp_db, r)["q4_chain_incomplete"]["found"]


def test_diagnose_exposes_six_checks():
    assert len(diagnose.ALL_CHECKS) == 6


def test_rubric_passes_the_fix():
    r = rubric.grade()
    assert r["passed"] is True
    assert r["score"] == r["total"] == 6
