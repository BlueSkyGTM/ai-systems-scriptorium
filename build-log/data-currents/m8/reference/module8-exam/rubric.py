"""
rubric.py
The Module 8 grader. Six criteria, each worth one point.

The grader works by:
  1. Static inspection of the student's fix.py (text + AST)
  2. Dynamic execution of fix.py against a fresh tempdir
  3. Execution of diagnose.py against the resulting lineage + corpus DBs
  4. Direct inspection of the lineage DB for the previously-broken edge

Exit codes:
  0  PASS  (all 6 criteria satisfied)
  1  FAIL  (one or more criteria failed; stderr lists which)

Usage:
  python rubric.py
  python rubric.py --fix ./broken_pipeline.py   # negative-case self-check
  python rubric.py --skip-runtime               # static-only grade

Contract honored for smoke.py:
  - rubric.py against the *broken* pipeline exits 1 (negative case)
  - rubric.py against a correct fix.py exits 0 (positive case)
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_FIX = Path(__file__).resolve().parent / "fix.py"
DEFAULT_DIAGNOSE = Path(__file__).resolve().parent / "diagnose.py"
DEFAULT_LIB = Path(__file__).resolve().parent.parent / "lib"

PASS = 0
FAIL = 1


# ---------------------------------------------------------------------------
# Small reporting helper
# ---------------------------------------------------------------------------
def _criterion(name: str, ok: bool, detail: str = "") -> tuple[str, bool, str]:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line, file=sys.stderr)
    return (name, ok, detail)


# ---------------------------------------------------------------------------
# Source loading + AST helpers
# ---------------------------------------------------------------------------
def _source(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {path}")
    return path.read_text(encoding="utf-8")


def _keyword_value(call: ast.Call, kwname: str) -> ast.expr | None:
    for kw in call.keywords:
        if kw.arg == kwname:
            return kw.value
    return None


# ---------------------------------------------------------------------------
# Criterion 1 — Defect 1 fixed:
#   batch_now_ts must NOT be hardcoded to a far-future date like "2099-01-01".
# ---------------------------------------------------------------------------
def crit_batch_now_ts(src: str) -> tuple[str, bool, str]:
    far_future = re.compile(r'"(209\d