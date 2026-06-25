"""smoke.py — end-to-end oracle for the Module 8 diagnostic exam.

Proves the exam works in both directions:
  1. The broken pipeline runs to false 'success' while diagnose.py lights up all three defects.
  2. The fixed pipeline is clean: diagnose finds nothing, a healthy corpus passes, and a
     stale corpus raises FreshnessBreach.
  3. The rubric grades the fix PASS and the broken pipeline FAIL.

Exits 0 only if every assertion holds, including the negative cases.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import broken_pipeline
import diagnose
import fix
import rubric

LOADED = "2026-06-24 12:00:00"
NOW_FRESH = "2026-06-24 12:05:00"
NOW_STALE = "2026-06-26 18:00:00"

_PASS = 0
_FAIL = 0


def check(label: str, cond: bool) -> None:
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ok   {label}")
    else:
        _FAIL += 1
        print(f"  FAIL {label}")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        broken_db = str(Path(tmp) / "broken.db")
        fixed_db = str(Path(tmp) / "fixed.db")
        stale_db = str(Path(tmp) / "stale.db")

        # --- Broken pipeline: runs to false success, diagnose finds all 3 defects ----
        print("[smoke] running the broken pipeline...")
        b = broken_pipeline.run(broken_db, LOADED, NOW_FRESH)
        bf = {f["name"]: f for f in diagnose.diagnose(broken_db, b)}

        check("broken: ran to 'success' with no exception", b["raised"] is False)
        check("broken: freshness used a future 'now' (defect 1)", bf["q1_future_now"]["found"])
        check("broken: source flagged stale despite a fresh load", bf["q2_stale_despite_load"]["found"])
        check("broken: an answer has no verdict (defect 2)", bf["q3_missing_verdict"]["found"])
        check("broken: lineage chain is incomplete", bf["q4_chain_incomplete"]["found"])
        check("broken: gate did not block the stale source (defect 3)", bf["q5_silent_gate"]["found"])
        check("broken: summary reports defects present", bf["q6_summary"]["found"])

        # --- Fixed pipeline: healthy run is clean, diagnose finds nothing ------------
        print("[smoke] running the fixed pipeline (healthy)...")
        f = fix.run(fixed_db, LOADED, NOW_FRESH)
        ff = {x["name"]: x for x in diagnose.diagnose(fixed_db, f)}

        check("fixed: healthy run not stale", f["fresh"]["is_stale"] is False)
        check("fixed: no future-now defect", not ff["q1_future_now"]["found"])
        check("fixed: verdict recorded", not ff["q3_missing_verdict"]["found"])
        check("fixed: lineage chain complete", not ff["q4_chain_incomplete"]["found"])
        check("fixed: no silent-gate defect", not ff["q5_silent_gate"]["found"])
        check("fixed: summary reports no defects", not ff["q6_summary"]["found"])

        # --- Fixed pipeline: stale corpus must fail loud -----------------------------
        print("[smoke] running the fixed pipeline (stale)...")
        raised = False
        try:
            fix.run(stale_db, LOADED, NOW_STALE)
        except fix.FreshnessBreach:
            raised = True
        check("fixed: stale corpus raises FreshnessBreach", raised)

    # --- Rubric grades fix PASS, broken FAIL -----------------------------------------
    print("[smoke] grading...")
    graded = rubric.grade()
    check("rubric: fix scores all six criteria", graded["score"] == graded["total"])
    check("rubric: fix verdict PASS", graded["passed"] is True)
    check("rubric: broken pipeline FAILs the grade", rubric.grade("broken_pipeline")["passed"] is False)
    check("rubric.py exits 0 on the fix", _run("rubric.py") == 0)
    check("rubric.py exits 1 on broken_pipeline", _run("rubric.py", "--pipeline", "broken_pipeline") == 1)

    total = _PASS + _FAIL
    print(f"\n[smoke] {_PASS}/{total} assertions passed")
    if _FAIL:
        print(f"[smoke] FAILED ({_FAIL} failures)")
        return 1
    print("[smoke] PASS")
    return 0


def _run(script: str, *args: str) -> int:
    import subprocess
    return subprocess.run([sys.executable, script, *args],
                          cwd=str(Path(__file__).resolve().parent),
                          capture_output=True, text=True).returncode


if __name__ == "__main__":
    sys.exit(main())
