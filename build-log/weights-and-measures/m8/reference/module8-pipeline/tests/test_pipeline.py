"""pytest suite for module8-pipeline.

Covers the vendored stages (curate, train, eval gate, regression), the conductor's
two-sided gating, and the rubric's READY / NEEDS WORK verdict.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lib"))

import m3_curate  # noqa: E402
import m5_eval  # noqa: E402
import m6_train  # noqa: E402
import m7_regress  # noqa: E402
import pipeline as pipeline_mod  # noqa: E402
import rubric as rubric_mod  # noqa: E402


@pytest.fixture(scope="session")
def run():
    return pipeline_mod.run_pipeline(write=True)


# -- vendored stages ---------------------------------------------------------
def test_curate_removes_dupes_and_splits():
    raw = m3_curate.generate_raw(200, seed=1)
    curated = m3_curate.curate(raw, seed=1)
    assert curated["dupes_removed"] > 0
    assert curated["disjoint"] is True
    assert len(curated["train"]) > len(curated["test"]) > 0


def test_curate_drops_invalid_rows():
    raw = [{"text": "", "label": "billing"}, {"text": "no label"},
           {"text": "refund invoice", "label": "billing"}]
    curated = m3_curate.curate(raw)
    assert curated["n_valid"] == 1


def test_train_produces_checkpoint(run):
    ckpt = run["checkpoint"]
    for key in ("state_dict", "vocab", "class_names", "config", "train_majority_class"):
        assert key in ckpt
    assert run["manifest"]["trained"]["train_acc"] >= 0.80


def test_eval_gate_beats_baseline(run):
    e = run["eval"]
    assert e["passed"] is True
    assert e["tuned_acc"] > e["baseline_acc"]


def test_regression_all_golden_pass(run):
    r = run["regress"]
    assert r["passed"] is True
    assert r["n_passed"] == r["n_cases"]


# -- conductor gating --------------------------------------------------------
def test_pipeline_blocks_on_regression_failure(monkeypatch):
    # Force the regression check to fail; the conductor must raise PipelineBlocked.
    monkeypatch.setattr(
        m7_regress, "check",
        lambda ckpt, golden=None: {"passed": False, "n_passed": 0, "n_cases": 5,
                                   "failures": [("x", "billing", "bug")], "results": []},
    )
    with pytest.raises(pipeline_mod.PipelineBlocked):
        pipeline_mod.run_pipeline(write=False)


# -- rubric ------------------------------------------------------------------
def test_rubric_ready_on_good_run(run):
    graded = rubric_mod.grade(run["manifest"])
    assert graded["ready"] is True
    assert graded["score"] == graded["total"]


def test_rubric_blocks_deficient_run():
    deficient = pipeline_mod.run_pipeline(skip_eval=True, write=False)
    graded = rubric_mod.grade(deficient["manifest"])
    assert graded["criteria"]["eval_gate_enforced"] is False
    assert graded["ready"] is False
