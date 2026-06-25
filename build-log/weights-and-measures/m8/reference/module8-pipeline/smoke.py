"""smoke.py — end-to-end oracle for the Module 8 pipeline artifact.

Proves the composition and the grader, in both directions:
  1. Full pipeline run: every stage produces its summary; the manifest is written.
  2. rubric.py grades that run READY (all five criteria pass).
  3. Deficient run (eval gate skipped): the pipeline still completes...
  4. ...but rubric.py grades it NEEDS WORK, tripping exactly the eval-gate criterion.

A green run means the conductor composes the vendored modules correctly AND the rubric
catches a deficient run. Exits 0 only if every assertion holds.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pipeline as pipeline_mod
import rubric as rubric_mod

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


def run(args: list[str]) -> int:
    return subprocess.run([sys.executable, *args], cwd=str(ROOT),
                          capture_output=True, text=True).returncode


def main() -> int:
    print("[smoke] full pipeline run...")
    result = pipeline_mod.run_pipeline()
    m = result["manifest"]

    # -- Composition: every stage produced its summary -----------------------
    check("curation removed duplicates", m["curated"]["dupes_removed"] > 0)
    check("train/test split is disjoint", m["curated"]["disjoint"] is True)
    check("model trained above the floor", m["trained"]["train_acc"] >= 0.80)
    check("eval gate ran and passed", m["eval"] is not None and m["eval"]["passed"])
    check("eval beats the baseline", m["eval"]["tuned_acc"] > m["eval"]["baseline_acc"])
    check("every golden case passed", m["regress"]["n_passed"] == m["regress"]["n_cases"])
    check("manifest marked logged", m["logged"] is True)
    check("manifest.json written", (ROOT / "outputs" / "manifest.json").exists())
    check("checkpoint written", (ROOT / "outputs" / "checkpoint.pt").exists())

    # -- Rubric grades the good run READY ------------------------------------
    graded = rubric_mod.run_rubric()
    check("rubric: all five criteria pass", graded["score"] == graded["total"])
    check("rubric verdict READY", graded["ready"] is True)
    check("rubric.py exits 0 on a good run", run(["rubric.py"]) == 0)

    # -- Deficient run: eval gate skipped ------------------------------------
    print("[smoke] deficient run (eval gate skipped)...")
    deficient = pipeline_mod.run_pipeline(skip_eval=True)
    check("deficient manifest has no eval", deficient["manifest"]["eval"] is None)

    bad_grade = rubric_mod.grade(deficient["manifest"])
    check("rubric fails the eval-gate criterion",
          bad_grade["criteria"]["eval_gate_enforced"] is False)
    check("rubric verdict NEEDS WORK", bad_grade["ready"] is False)
    check("rubric.py exits 1 on the deficient run (via written manifest)",
          run(["rubric.py"]) == 1)

    total = _PASS + _FAIL
    print(f"\n[smoke] {_PASS}/{total} assertions passed")
    if _FAIL:
        print(f"[smoke] FAILED ({_FAIL} failures)")
        return 1
    print("[smoke] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
