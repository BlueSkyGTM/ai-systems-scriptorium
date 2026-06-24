"""
tests/test_exam.py
Reference test suite for Module 8 — "The Diagnostic Exam".

These tests pin the contract of the exam artifact:
  * broken_pipeline.py contains the three deliberately injected defects.
  * broken_pipeline.py runs and emits lineage.db + corpus_store.db.
  * diagnose.py exposes >= 6 find_* functions, each returning a non-None
    finding when run against the *broken* artifacts, and None against the
    *fixed* artifacts.
  * fix.py removes every defect.
  * rubric.py exits 1 on broken_pipeline.py and 0 on fix.py.
  * smoke.py exits 0 (the negative case is itself part of the suite).

Run:
    pytest tests/test_exam.py -v
"""
from __future__ import annotations

import inspect
import importlib.util
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]  # module8-exam/
EXAM_DIR = ROOT

BROKEN_PIPELINE = EXAM_DIR / "broken_pipeline.py"
DIAGNOSE = EXAM_DIR / "diagnose.py"
FIX = EXAM_DIR / "fix.py"
RUBRIC = EXAM_DIR / "rubric.py"
SMOKE = EXAM_DIR / "smoke.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _run(script: Path, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run a python script as a subprocess; capture stdout/stderr."""
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=180,
    )


def _import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot import {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _call_finder(fn, lineage_conn, corpus_conn):
    """Invoke a diagnose.find_* function tolerating multiple signatures."""
    sig = inspect.signature(fn)
    kwargs: dict = {}
    params = sig.parameters
    if "lineage_conn" in params:
        kwargs["lineage_conn"] = lineage_conn
    elif "lineage" in params:
        kwargs["lineage"] = lineage_conn
    if "corpus_conn" in params:
        kwargs["corpus_conn"] = corpus_conn
    elif "corpus" in params:
        kwargs["corpus"] = corpus_conn
    if not kwargs and len(params) == 0:
        return fn()
    return fn(**kwargs)


def _finder_names(mod) -> list[str]:
    return sorted(n for n in dir(mod) if n.startswith("find_"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def workdir(tmp_path: Path) -> Path:
    (tmp_path / "outputs").mkdir(exist_ok=True)
    return tmp_path


@pytest.fixture(scope="module")
def broken_workdir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    d = tmp_path_factory.mktemp("broken_run")
    (d / "outputs").mkdir()
    proc = _run(BROKEN_PIPELINE, cwd=d)
    assert proc.returncode == 0, (
        f"broken_pipeline.py should run (it emits corrupted artifacts, "
        f"not crash):\n{proc.stderr}"
    )
    return d


@pytest.fixture()
def fixed_workdir(tmp_path: Path) -> Path:
    (tmp_path / "outputs").mkdir(exist_ok=True)
    proc = _run(FIX, cwd=tmp_path)
    assert proc.returncode == 0, f"fix.py crashed:\n{proc.stderr}"
    return tmp_path


# ---------------------------------------------------------------------------
# Defect presence in broken_pipeline.py (source-level checks)
# ---------------------------------------------------------------------------
def test_broken_pipeline_defect1_batch_now_ts_2099():
    """Defect 1: batch_now_ts hardcoded to a far-future date."""
    src = BROKEN_PIPELINE.read_text()
    assert "2099" in src, "Defect 1 missing: no '2099' literal in broken_pipeline.py"
    hits = [
        line for line in src.splitlines()
        if "batch_now_ts" in line and "2099" in line
    ]
    assert hits, (
        "Defect 1 missing: expected an assignment like "
        "batch_now_ts = ... '2099-01-01' ..."
    )


def test_broken_pipeline_defect2_record_verdict_skipped():
    """Defect 2: capture_lineage skips the record_verdict call."""
    src = BROKEN_PIPELINE.read_text()
    assert "capture_lineage" in src, "capture_lineage not defined"
    # The broken version must not thread record_verdict through lineage capture.
    assert "record_verdict" not in src, (
        "Defect 2 missing: broken_pipeline.py still references record_verdict"
    )


def test_broken_pipeline_defect3_freshness_gate_retries_two():
    """Defect 3: freshness_gate has retries=2 (should be 0)."""
    src = BROKEN_PIPELINE.read_text()
    lines = src.splitlines()
   