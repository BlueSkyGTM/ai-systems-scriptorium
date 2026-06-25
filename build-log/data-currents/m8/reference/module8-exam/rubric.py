"""rubric.py — the Module 8 grader. Six criteria, each worth one point.

Grades the submitted fix by running it and diagnosing the result:
  1. Defect 1 fixed   - the freshness check uses the real 'now', not a future date.
  2. Defect 2 fixed   - capture_lineage records the eval verdict.
  3. Defect 3 fixed   - the freshness gate fails loud (raises) on a stale source.
  4. Lineage complete - the answer -> verdict chain can be walked end to end.
  5. Healthy run      - a freshly loaded corpus passes the gate and runs clean.
  6. Stale run blocks - a stale corpus raises FreshnessBreach (no silent success).

Exit 0 = PASS (all six), 1 = FAIL. The grade is the deliverable.
"""
from __future__ import annotations

import argparse
import importlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagnose

LOADED = "2026-06-24 12:00:00"
NOW_FRESH = "2026-06-24 12:05:00"          # 5 minutes later -> fresh
NOW_STALE = "2026-06-26 18:00:00"          # ~54 hours later -> stale (> 25h SLO)


def grade(pipeline_name: str = "fix") -> dict:
    """Grade a candidate pipeline module (default: the submitted fix.py).

    Running it against `broken_pipeline` fails (the defects are present); running it
    against a correct `fix` passes.
    """
    pipeline = importlib.import_module(pipeline_name)
    with tempfile.TemporaryDirectory() as tmp:
        healthy_db = str(Path(tmp) / "healthy.db")
        stale_db = str(Path(tmp) / "stale.db")

        healthy = pipeline.run(healthy_db, LOADED, NOW_FRESH)
        findings = {f["name"]: f for f in diagnose.diagnose(healthy_db, healthy)}

        # A correct gate must stop the run on a stale corpus (any raised exception).
        stale_blocks = False
        try:
            pipeline.run(stale_db, LOADED, NOW_STALE)
        except Exception:
            stale_blocks = True

        criteria = {
            "defect1_freshness_now_fixed": not findings["q1_future_now"]["found"],
            "defect2_verdict_recorded": not findings["q3_missing_verdict"]["found"],
            "defect3_gate_fails_loud": stale_blocks,
            "lineage_chain_complete": not findings["q4_chain_incomplete"]["found"],
            "healthy_run_clean": (not healthy["fresh"]["is_stale"]) and healthy["raised"] is False,
            "stale_run_blocks": stale_blocks,
        }
    passed = all(criteria.values())
    return {"criteria": criteria, "passed": passed,
            "score": sum(criteria.values()), "total": len(criteria)}


def format_report(r: dict) -> str:
    lines = ["[rubric] grading the fix"]
    for name, ok in r["criteria"].items():
        lines.append(f"  [{'x' if ok else ' '}] {name}")
    lines.append(f"  score {r['score']}/{r['total']} -> {'PASS' if r['passed'] else 'FAIL'}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade a candidate pipeline.")
    parser.add_argument("--pipeline", default="fix",
                        help="module to grade (default: fix; use broken_pipeline for the self-check)")
    args = parser.parse_args()
    r = grade(args.pipeline)
    print(format_report(r))
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
