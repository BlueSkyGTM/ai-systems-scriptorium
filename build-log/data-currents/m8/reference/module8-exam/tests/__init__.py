"""
tests package for the Module 8 Diagnostic Exam.

Initializes the test namespace and wires up import paths so that the
vendored M7 ``lib/`` package and the module8-exam scripts (broken_pipeline,
diagnose, fix, rubric, smoke) are importable from every test module without
requiring an editable install.

This file is intentionally side-effect-light: it only mutates ``sys.path``
and exposes a handful of constants. The real grading work lives in
``test_smoke.py``, ``test_rubric.py``, and ``test_diagnose.py``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path wiring
# ---------------------------------------------------------------------------
# tests/__init__.py -> tests/  -> module8-exam/  -> <repo_root>
_THIS_DIR = Path(__file__).resolve().parent
_EXAM_DIR = _THIS_DIR.parent
_REPO_ROOT = _EXAM_DIR.parent

# Ensure the exam directory itself is on sys.path so that
# `import broken_pipeline`, `import diagnose`, `import fix`, etc. work.
for _candidate in (_EXAM_DIR, _REPO_ROOT):
    _candidate_str = str(_candidate)
    if _candidate_str not in sys.path:
        sys.path.insert(0, _candidate_str)

# Vendored M7 lib lives at <repo_root>/lib per the M7 reference layout.
_LIB_DIR = _REPO_ROOT / "lib"
if _LIB_DIR.is_dir() and str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------
EXAM_DIR: Path = _EXAM_DIR
REPO_ROOT: Path = _REPO_ROOT
LINEAGE_DB: Path = _EXAM_DIR / "outputs" / "lineage.db"
CORPUS_DB: Path = _EXAM_DIR / "outputs" / "corpus_store.db"

# The three deliberate defects injected into broken_pipeline.py. Tests in this
# package assert against these symbols so the defect identifiers stay in one
# place even if a student's fix.py is regenerated.
DEFECT_FRESHNESS_TS = "freshness.batch_now_ts_hardcoded"
DEFECT_LINEAGE_SKIP = "lineage.capture_skips_record_verdict"
DEFECT_GATE_RETRIES = "gate.retries_nonzero"

EXPECTED_GATE_RETRIES = 0
HARDCODED_BAD_TS = "2099-01-01"

# Determinism knobs — keep tests reproducible on CPU.
RANDOM_SEED = 42

__all__ = [
    "EXAM_DIR",
    "REPO_ROOT",
    "LINEAGE_DB",
    "CORPUS_DB",
    "DEFECT_FRESHNESS_TS",
    "DEFECT_LINEAGE_SKIP",
    "DEFECT_GATE_RETRIES",
    "EXPECTED_GATE_RETRIES",
    "HARDCODED_BAD_TS",
    "RANDOM_SEED",
]
