"""
rubric.py — Module 8 pipeline grading rubric.

Grades the M8 fine-tune pipeline artifact on 5 hard criteria:
    1. Data quality gate   — dataset curation ran, dedupe + split recorded
    2. Train reproducible  — seed pinned, run hash recorded, deterministic
    3. Eval gate enforced  — M5 exact-match + F1 gate recorded as PASS
    4. Regression enforced — M7 behavioral regression recorded as PASS
    5. MLflow logged       — offline sqlite backend has >=1 run

Exit codes:
    0 = READY         (all 5 criteria pass)
    1 = NEEDS WORK    (one or more criteria failed)

The rubric is the deliverable: it grades by code, not prose.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

CRITERIA: Tuple[str, ...] = (
    "data_quality",
    "train_reproducible",
    "eval_gate_enforced",
    "regression_gate_enforced",
    "mlflow_logged",
)

DEFAULT_OUTPUTS = Path(__file__).resolve().parent / "outputs"

SEED = 42

# Minimum thresholds the gate must explicitly record and meet.
EVAL_EM_THRESHOLD = 0.50
EVAL_F1_THRESHOLD = 0.60
REGRESSION_MAX_DELTA = 0.10  # abs drift allowed vs baseline


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def _load_json(path: Path) -> Dict:
    if not path.is_file():
        raise FileNotFoundError(f"missing artifact: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# Criterion 1: Data quality gate (M3 curation ran)
# --------------------------------------------------------------------------- #

def check_data_quality(outputs: Path) -> Tuple[bool, str]:
    """M3 must have: validated, deduped, and split the JSONL dataset.

    Looks for `data_quality.json` produced by pipeline step 1 and verifies
    the recorded counters are internally consistent.
    """
    try:
        rep = _load_json(outputs / "data_quality.json")
    except FileNotFoundError as e:
        return False, str(e)

    required_keys = {"raw", "validated", "deduped", "train", "val", "test", "seed"}
    missing = required_keys - rep.keys()
    if missing:
        return False, f"data_quality.json missing keys: {sorted(missing)}"

    # Internal consistency: deduped <= validated <= raw
    if not (rep["deduped"] <= rep["validated"] <= rep["raw"]):
        return False, (
            f"counts inconsistent: raw={rep['raw']} validated={rep['validated']} "
            f"deduped={rep['deduped']}"
        )

    # Split must sum to deduped and each split must be positive.
    total_split = rep["train"] + rep["val"] + rep["test"]
    if total_split != rep["deduped"]:
        return False, (
            f"split sum {total_split} != deduped {rep['deduped']}"
        )
    if min(rep["train"], rep["val"], rep["test"]) <= 0:
        return False, "one or more splits is empty"

    if rep.get("seed") != SEED:
        return False, f"seed != {SEED} (got {rep.get('seed')})"

    return True, (
        f"raw={rep['raw']} validated={rep['validated']} "
        f"deduped={rep['deduped']} splits={rep['train']}/{rep['val']}/{rep['test']}"
    )


# --------------------------------------------------------------------------- #
# Criterion 2: Train reproducibility (M4/M6)
# --------------------------------------------------------------------------- #

def check_train_reproducible(outputs: Path) -> Tuple[bool, str]:
    """Train step must record a fixed seed and a deterministic checkpoint hash."""
    try:
        rep = _load_json(outputs / "train_report.json")
    except FileNotFoundError as e:
        return False, str(e)

    required = {"seed", "adapter_hash", "epochs", "final_loss"}
    missing = required - rep.keys()
    if missing:
        return False, f"train_report.json missing keys: {sorted(missing)}"

    if rep["seed"] != SEED:
        return False, f"seed != {SEED} (got {rep['seed']})"

    if not isinstance(rep["adapter_hash"], str) or len(rep["adapter_hash"]) < 8:
        return False, "adapter_hash missing or too short"

    adapter_path = outputs / "adapter.pt"
    if adapter_path.is_file():
        actual = _sha256(adapter_path)[:16]
        recorded = rep["adapter_hash"][:16]
        if actual != recorded:
            return False, (
                f"adapter hash mismatch: file={actual} report={recorded}"
            )

    if not isinstance(rep["epochs"], int) or rep["epochs"] < 1:
        return False, f"epochs must be >=1 (got {rep['epochs']})"

    if not isinstance(rep["final_loss"], (int, float)) or rep["final_loss"] <= 0:
        return False, f"final_loss looks wrong: {rep['final_loss']}"

    return True, (
        f"seed={rep['seed']} epochs={rep['epochs']} "
        f"final_loss={rep['final_loss']:.4f} adapter={rep['adapter_hash'][:8]}"
    )


# --------------------------------------------------------------------------- #
# Criterion 3: Eval gate enforced (M5)
# --------------------------------------------------------------------------- #

def check_eval_gate_enforced(outputs: Path) -> Tuple[bool, str]:
    """M5 gate must be explicitly recorded as PASS over required thresholds."""
    try:
        rep = _load_json(outputs / "eval_report.json")
    except FileNotFoundError as e:
        return False, str(e)

    required = {"exact_match", "f1", "em_threshold", "f1_threshold", "gate"}
    missing = required - rep.keys()
    if missing:
        return False, f"eval_report.json missing keys: {sorted(missing)}"

    em = rep["exact_match"]
    f1 = rep["f1"]
    em_t = rep["em_threshold"]
    f1_t = rep["f1_threshold"]

    # Thresholds recorded in the report must meet or exceed the rubric floor.
    if em_t < EVAL_EM_THRESHOLD:
        return False, f"em_threshold {em_t} below floor {EVAL_EM_THRESHOLD}"
    if f1_t < EVAL_F1_THRESHOLD:
        return False, f"f1_threshold {f1_t} below floor {EVAL_F1_THRESHOLD}"

    if not (em >= em_t and f1 >= f1_t):
        return False, (
            f"metrics below thresholds: EM={em:.3f} (>={em_t}) F1={f1:.3f} (>={f1_t})"
        )

    if rep["gate"] != "PASS":
        return False, f"gate field = {rep['gate']!r}, expected 'PASS'"

    return True, f"gate=PASS EM={em:.3f} F1={f1:.3f}"


# --------------------------------------------------------------------------- #
# Criterion 4: Regression gate enforced (M7)
# --------------------------------------------------------------------------- #

def check_regression_gate_enforced(outputs: Path) -> Tuple[bool, str]:
    """M7 regression must run against a baseline and PASS a drift bound."""
    try:
        rep = _load_json(outputs / "regression_report.json")
    except FileNotFoundError as e:
        return False, str(e)

    required = {"cases", "passed", "failed", "max_delta", "max_delta_allowed", "gate"}
    missing = required - rep.keys()
    if missing:
        return False, f"regression_report.json missing keys: {sorted(missing)}"

    if rep["cases"] <= 0:
        return False, "no regression cases recorded"

    if rep["failed"] > 0:
        return False, f"{rep['failed']} regression case(s) failed"

    if rep["max_delta"] > rep["max_delta_allowed"]:
        return False, (
            f"drift {rep['max_delta']:.3f} exceeds "
            f"allowed {rep['max_delta_allowed']:.3f}"
        )

    if rep["max_delta_allowed"] > REGRESSION_MAX_DELTA:
        return False, (
            f"allowed drift {rep['max_delta_allowed']} looser than "
            f"rubric max {REGRESSION_MAX_DELTA}"
        )

    if rep["gate"] != "PASS":
        return False, f"gate field = {rep['gate']!r}, expected 'PASS'"

    return True, (
        f"gate=PASS cases={rep['cases']} max_delta={rep['max_delta']:.3f} "
        f"(<= {rep['max_delta_allowed']:.3f})"
    )


# --------------------------------------------------------------------------- #
# Criterion 5: MLflow logged (offline sqlite backend)
# --------------------------------------------------------------------------- #

def check_mlflow_logged(outputs: Path) -> Tuple[bool, str]:
    """Pipeline must have written to the offline sqlite tracking backend."""
    db_path = outputs / "mlruns.db"
    if not db_path.is_file():
        return False, f"missing mlflow db: {db_path}"

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error as e:
        return False, f"cannot open mlflow db: {e}"

    try:
        cur = conn.cursor()
        # MLflow schema: experiments, runs, metrics, params.
        cur.execute(
            "SELECT count(*) FROM runs WHERE status='FINISHED'"
        )
        row = cur.fetchone()
        n_runs = row[0] if row else 0
        if n_runs < 1:
            return False, "0 FINISHED runs in mlruns.db"

        cur.execute("SELECT count(*) FROM metrics")
        n_metrics = cur.fetchone()[0]
        if n_metrics < 1:
            return False, "0 metrics logged to mlruns.db"

        cur.execute("SELECT count(*) FROM params")
        n_params = cur.fetchone()[0]
        if n_params < 1:
            return False, "0 params logged to mlruns.db"
    except sqlite3.Error as e:
        return False, f"mlflow db query failed: {e}"
    finally:
        conn.close()

    return True, f"runs={n_runs} metrics={n_metrics} params={n_params}"


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #

CHECKS: Dict[str, Callable[[Path], Tuple[bool, str]]] = {
    "data_quality": check_data_quality,
    "train_reproducible": check_train_reproducible,
    "eval_gate_enforced": check_eval_gate_enforced,
    "regression_gate_enforced": check_regression_gate_enforced,
    "mlflow_logged": check_mlflow_logged,
}


def run_rubric(outputs: Path) -> int:
    print("=" * 68)
    print(f"Module 8 Pipeline Rubric — outputs: {outputs}")
    print("=" * 68)

    results: List[Tuple[str, bool, str]] = []
    for key in CRITERIA:
        check = CHECKS[key]
        try:
            ok, detail = check(outputs)
        except Exception as e:  # never crash the rubric
            ok, detail = False, f"check raised: {type(e).__name__}: {e}"
        results.append((key, ok, detail))

    width = max(len(k) for k in CRITERIA)
    print(f"\n{'Criterion':<{width}}   Verdict   Detail")
    print("-" * 68)
    n_pass = 0
    for key, ok, detail in results:
        verdict = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        print(f"{key:<{width}}   {verdict:<6}   {detail}")

    print("-" * 68)
    total = len(CRITERIA)
    print(f"Score: {n_pass}/{total}")

    if n_pass == total:
        print("Verdict: READY")
        return 0
    print("Verdict: NEEDS WORK")
    return 1


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Module 8 pipeline rubric.")
    p.add_argument(
        "--outputs",
        type=Path,
        default=DEFAULT_OUTPUTS,
        help="pipeline outputs directory (default: ./outputs)",
    )
    args = p.parse_args(argv)
    return run_rubric(args.outputs)


if __name__ == "__main__":
    sys.exit(main())