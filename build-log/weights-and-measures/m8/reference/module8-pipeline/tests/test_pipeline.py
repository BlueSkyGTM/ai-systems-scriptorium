"""tests/test_pipeline.py — pytest suite for module8-pipeline.

Covers:
  - Individual stage functions (curate, train, eval_gate, regress, log_artifact)
  - End-to-end pipeline orchestration (happy path)
  - Negative path: eval gate failure -> pipeline blocks
  - Negative path: regression gate failure -> pipeline blocks
  - Reproducibility under fixed seed
  - rubric.py: READY (exit 0) on full run; NEEDS WORK (exit 1) when gate skipped
  - MLflow artifacts persisted to sqlite backend

All tests are CPU-only and run in well under 60s on synthetic fixtures.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import torch

# Make the project root importable. tests/ sits one level under module8-pipeline/.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pipeline  # noqa: E402
import rubric  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _seed():
    """Determinism for every test."""
    random.seed(42)
    torch.manual_seed(42)
    yield


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Isolated working directory with synthetic fixtures."""
    work = tmp_path / "work"
    work.mkdir()

    # Synthetic raw data (M3-style: prompt/completion JSONL).
    raw = work / "raw.jsonl"
    rows = [
        {"prompt": f"q{i}", "completion": f"a{i % 4}"}
        for i in range(40)
    ]
    # Inject a few exact duplicates so the dedupe gate has something to do.
    rows += rows[:4]
    raw.write_text("\n".join(json.dumps(r) for r in raw_lines(rows)))

    # MLflow sqlite backend inside the workspace.
    mlruns = work / "mlruns.db"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{mlruns}")

    yield {
        "root": work,
        "raw": raw,
        "data_dir": work / "data",
        "model_dir": work / "model",
        "eval_dir": work / "eval",
        "regress_dir": work / "regress",
        "outputs_dir": work / "outputs",
        "mlruns": mlruns,
    }


def raw_lines(rows):
    return [json.dumps(r) for r in rows]


def _write_config(workspace, **overrides):
    cfg = {
        "raw_path": str(workspace["raw"]),
        "data_dir": str(workspace["data_dir"]),
        "model_dir": str(workspace["model_dir"]),
        "eval_dir": str(workspace["eval_dir"]),
        "regress_dir": str(workspace["regress_dir"]),
        "outputs_dir": str(workspace["outputs_dir"]),
        "seed": 42,
        "epochs": 1,
        "batch_size": 8,
        "eval_threshold": 0.25,   # tiny threshold so synthetic passes
        "regress_threshold": 0.20,
        "vocab_size": 64,
        "d_model": 16,
        "n_pairs": 8,
    }
    cfg.update(overrides)
    p = workspace["root"] / "config.json"
    p.write_text(json.dumps(cfg))
    return p


# ---------------------------------------------------------------------------
# Stage 1: curate_data
# ---------------------------------------------------------------------------

def test_curate_data_dedupes_and_splits(workspace):
    cfg = _write_config(workspace)
    out = pipeline.curate_data(json.loads(cfg.read_text()))

    train = (workspace["data_dir"] / "train.jsonl").read_text().splitlines()
    val = (workspace["data_dir"] / "val.jsonl").read_text().splitlines()
    test = (workspace["data_dir"] / "test.jsonl").read_text().splitlines()

    # Dedupe: 44 raw -> 40 unique.
    total = len(train) + len(val) + len(test)
    assert total == 40, f"dedupe failed: {total} rows"
    assert out["unique"] == 40
    assert out["duplicate_dropped"] == 4
    # Splits roughly present.
    assert len(train) >= len(val) >= 1
    assert len(test) >= 1


def test_curate_data_validates_schema(workspace):
    bad = workspace["root"] / "bad.jsonl"
    bad.write_text("\n".join(raw_lines([
        {"prompt": "ok", "completion": "ok"},
        {"prompt": "missing_completion"},  # invalid
    ])))
    workspace["raw"] = bad
    cfg = _write_config(workspace)
    with pytest.raises((ValueError, RuntimeError)):
        pipeline.curate_data(json.loads(cfg.read_text()))


# ---------------------------------------------------------------------------
# Stage 2: train_model
# ---------------------------------------------------------------------------

def test_train_model_produces_checkpoint(workspace):
    cfg = _write_config(workspace)
    pipeline.curate_data(json.loads(cfg.read_text()))
    out = pipeline.train_model(json.loads(cfg.read_text()))

    ckpt = workspace["model_dir"] / "model.pt"
    assert ckpt.exists(), "checkpoint not written"
    assert out["checkpoint"].endswith("model.pt")
    # LoRA-style adapter manifest present.
    assert (workspace["model_dir"] / "adapter.json").exists()


def test_train_model_is_reproducible(workspace):
    cfg = _write_config(workspace)
    pipeline.curate_data(json.loads(cfg.read_text()))

    torch.manual_seed(42); random.seed(42)
    a = pipeline.train_model(json.loads(cfg.read_text()))
    # Re-train into a second dir from the same seed.
    cfg2 = json.loads(cfg.read_text())
    cfg2["model_dir"] = str(workspace["root"] / "model2")
    torch.manual_seed(42); random.seed(42)
    b = pipeline.train_model(cfg2)

    sd_a = torch.load(a["checkpoint"], map_location="cpu")
    sd_b = torch.load(b["checkpoint"], map_location="cpu")
    for k in sd_a:
        assert torch.allclose(sd_a[k], sd_b[k]), f"non-reproducible at {k}"


# ---------------------------------------------------------------------------
# Stage 3: eval_gate
# ---------------------------------------------------------------------------

def test_eval_gate_passes_when_above_threshold(workspace):
    cfg = _write_config(workspace, eval_threshold=0.0)
    pipeline.curate_data(json.loads(cfg.read_text()))
    pipeline.train_model(json.loads(cfg.read_text()))
    out = pipeline.eval_gate(json.loads(cfg.read_text()))
    assert out["passed"] is True
    assert out["exact_match"] >= 0.0
    assert out["f1"] >= 0.0
    assert (workspace["eval_dir"] / "metrics.json").exists()


def test_eval_gate_blocks_when_below_threshold(workspace):
    cfg = _write_config(workspace, eval_threshold=2.0)  # impossible
    pipeline.curate_data(json.loads(cfg.read_text()))
    pipeline.train_model(json.loads(cfg.read_text()))
    out = pipeline.eval_gate(json.loads(cfg.read_text()))
    assert out["passed"] is False


# ---------------------------------------------------------------------------
# Stage 4: regress
# ---------------------------------------------------------------------------

def test_regress_runs_and_emits_report(workspace):
    cfg = _write_config(workspace)
    pipeline.curate_data(json.loads(cfg.read_text()))
    pipeline.train_model(json.loads(cfg.read_text()))
    pipeline.eval_gate(json.loads(cfg.read_text()))
    out = pipeline.regress(json.loads(cfg.read_text()))
    assert "passed" in out
    assert (workspace["regress_dir"] / "regression.json").exists()


def test_regress_blocks_when_below_threshold(workspace):
    cfg = _write_config(workspace, regress_threshold=2.0)
    pipeline.curate_data(json.loads(cfg.read_text()))
    pipeline.train_model(json.loads(cfg.read_text()))
    pipeline.eval_gate(json.loads(cfg.read_text()))
    out = pipeline.regress(json.loads(cfg.read_text()))
    assert out["passed"] is False


# ---------------------------------------------------------------------------
# Stage 5: log_artifact (MLflow)
# ---------------------------------------------------------------------------

def test_log_artifact_writes_manifest_and_mlflow(workspace):
    cfg = _write_config(workspace)
    pipeline.curate_data(json.loads(cfg.read_text()))
    pipeline.train_model(json.loads(cfg.read_text()))
    pipeline.eval_gate(json.loads(cfg.read_text()))
    pipeline.regress(json.loads(cfg.read_text()))
    out = pipeline.log_artifact(json.loads(cfg.read_text()))

    manifest = workspace["outputs_dir"] / "manifest.json"
    assert manifest.exists()
    m = json.loads(manifest.read_text())
    assert m["stages"] == ["curate", "train", "eval", "regress", "log"]
    assert out["mlflow_run_id"]

    # MLflow sqlite DB must now exist with at least one run.
    assert workspace["mlruns"].exists()
    conn = sqlite3.connect(str(workspace["mlruns"]))
    try:
        rows = conn.execute(
            "SELECT COUNT(*) FROM experiments"
        ).fetchone()
        assert rows[0] >= 1
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# End-to-end orchestration
# ---------------------------------------------------------------------------

def test_pipeline_main_happy_path_returns_zero(workspace):
    cfg = _write_config(workspace)
    rc = pipeline.main(str(cfg))
    assert rc == 0
    # Every stage produced its artifact.
    assert (workspace["data_dir"] / "train.jsonl").exists()
    assert (workspace["model_dir"] / "model.pt").exists()
    assert (workspace["eval_dir"] / "metrics.json").exists()
    assert (workspace["regress_dir"] / "regression.json").exists()
    assert (workspace["outputs_dir"] / "manifest.json").exists()


def test_pipeline_main_blocks_on_eval_gate(workspace):
    cfg = _write_config(workspace, eval_threshold=2.0)
    rc = pipeline.main(str(cfg))
    assert rc == 2, f"expected eval-gate block (rc=2), got {rc}"
    # Regression stage should NOT have run on a blocked pipeline.
    assert not (workspace["regress_dir"] / "regression.json").exists()


def test_pipeline_main_blocks_on_regression_gate(workspace):
    cfg = _write_config(workspace, regress_threshold=2.0)
    rc = pipeline.main(str(cfg))
    assert rc == 3, f"expected regress-gate block (rc=3), got {rc}"
    # Eval metrics must exist (regression gate runs after eval).
    assert (workspace["eval_dir"] / "metrics.json").exists()


# ---------------------------------------------------------------------------
# rubric.py
# ---------------------------------------------------------------------------

def test_rubric_ready_on_full_run(workspace):
    cfg = _write_config(workspace)
    assert pipeline.main(str(cfg)) == 0
    rc, criteria = rubric.grade(str(workspace["root"]), str(cfg))
    assert rc == 0, f"expected READY, got NEEDS WORK: {criteria}"
    # Five criteria, all passed.
    assert len(criteria) == 5
    assert all(c["passed"] for c in criteria)
    names = {c["name"] for c in criteria}
    assert names == {
        "data_quality_gate",
        "train_reproducibility",
        "eval_gate_enforced",
        "regression_gate_enforced",
        "mlflow_logged",
    }


def test_rubric_fails_when_eval_gate_skipped(workspace):
    """Deficient run: simulate skipping the eval gate. Rubric must grade
    NEEDS WORK (exit 1) and flag the eval-gate criterion as failed."""
    cfg = _write_config(workspace)
    # Run pipeline normally first to populate artifacts.
    assert pipeline.main(str(cfg)) == 0

    # Tamper: delete the eval metrics to simulate skipping.
    (workspace["eval_dir"] / "metrics.json").unlink()
    # Manifest also reflects stages; remove eval entry to simulate skip.
    manifest = workspace["outputs_dir"] / "manifest.json"
    m = json.loads(manifest.read_text())
    m["stages"] = [s for s in m["stages"] if s != "eval"]
    manifest.write_text(json.dumps(m))

    rc, criteria = rubric.grade(str(workspace["root"]), str(cfg))
    assert rc == 1
    eval_criterion = next(c for c in criteria if c["name"] == "eval_gate_enforced")
    assert eval_criterion["passed"] is False


def test_rubric_fails_when_mlflow_missing(workspace):
    cfg = _write_config(workspace)
    assert pipeline.main(str(cfg)) == 0
    workspace["mlruns"].unlink()
    rc, criteria = rubric.grade(str(workspace["root"]), str(cfg))
    assert rc == 1
    mlflow_criterion = next(c for c in criteria if c["name"] == "mlflow_logged")
    assert mlflow_criterion["passed"] is False


# ---------------------------------------------------------------------------
# Smoke-test entry-point parity (smoke.py is the canonical driver)
# ---------------------------------------------------------------------------

def test_smoke_py_exits_zero(workspace, monkeypatch):
    """smoke.py must exit 0 including the negative case."""
    smoke = ROOT / "smoke.py"
    if not smoke.exists():
        pytest.skip("smoke.py not present in this layout")
    # Point smoke at the temp workspace by chdir'ing there.
    monkeypatch.chdir(workspace["root"])
    env = os.environ.copy()
    env["MLFLOW_TRACKING_URI"] = f"sqlite:///{workspace['mlruns']}"
    proc = subprocess.run(
        [sys.executable, str(smoke)],
        cwd=str(workspace["root"]),
        env=env,
        capture_output=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"smoke.py failed: {proc.returncode}\n"
        f"STDOUT:\n{proc.stdout.decode(errors='replace')}\n"
        f"STDERR:\n{proc.stderr.decode(errors='replace')}"
    )


if __name__ == "__main__":
    # Allow direct execution for quick local sanity.
    raise SystemExit(pytest.main([__file__, "-v", "-x"]))