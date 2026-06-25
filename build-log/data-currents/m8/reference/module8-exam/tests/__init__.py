"""Test package for the Module 8 Diagnostic Exam.

Side-effect-light: it only wires the exam directory onto sys.path so the scripts
(broken_pipeline, diagnose, fix, rubric) import cleanly from every test module.
"""
from __future__ import annotations

import sys
from pathlib import Path

_EXAM_DIR = Path(__file__).resolve().parent.parent
if str(_EXAM_DIR) not in sys.path:
    sys.path.insert(0, str(_EXAM_DIR))

EXAM_DIR = _EXAM_DIR
