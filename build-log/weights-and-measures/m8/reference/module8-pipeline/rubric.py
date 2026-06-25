"""rubric.py — the Module 8 grader, expressed in code.

A rubric in prose can be argued with. A rubric in code cannot: it reads the pipeline's
manifest and scores five criteria, then exits READY (0) or NEEDS WORK (1). The grade is
the deliverable.

    1. data curated      - duplicates were removed and the split is disjoint
    2. model trained     - training accuracy cleared the floor
    3. eval gate enforced- the eval gate actually ran and passed
    4. regression enforced- every pinned golden case passed
    5. artifact logged   - the manifest was written

Criterion 3 is the one a deficient run trips: skip the eval gate and the rubric blocks,
even though the pipeline itself ran to completion.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "outputs" / "manifest.json"

TRAIN_ACC_FLOOR = 0.80


def grade(manifest: dict) -> dict:
    curated = manifest.get("curated", {})
    trained = manifest.get("trained", {})
    eval_s = manifest.get("eval")
    regress = manifest.get("regress")

    criteria = {
        "data_curated": bool(curated.get("dupes_removed", 0) > 0 and curated.get("disjoint")),
        "model_trained": bool(trained.get("train_acc", 0.0) >= TRAIN_ACC_FLOOR),
        "eval_gate_enforced": bool(eval_s is not None and eval_s.get("passed")),
        "regression_enforced": bool(regress is not None and regress.get("passed")),
        "artifact_logged": bool(manifest.get("logged")),
    }
    ready = all(criteria.values())
    return {"criteria": criteria, "ready": ready,
            "score": sum(criteria.values()), "total": len(criteria)}


def run_rubric(manifest_path: Path = MANIFEST_PATH) -> dict:
    if not manifest_path.exists():
        return {"criteria": {}, "ready": False, "score": 0, "total": 5,
                "error": f"no manifest at {manifest_path}"}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return grade(manifest)


def format_report(r: dict) -> str:
    lines = ["[rubric] grading the pipeline run"]
    if r.get("error"):
        lines.append(f"  ERROR: {r['error']}")
    for name, ok in r.get("criteria", {}).items():
        lines.append(f"  [{'x' if ok else ' '}] {name}")
    lines.append(f"  score {r['score']}/{r['total']} -> "
                 f"{'READY' if r['ready'] else 'NEEDS WORK'}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade the M8 pipeline run.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args()
    r = run_rubric(args.manifest)
    print(format_report(r))
    return 0 if r["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
