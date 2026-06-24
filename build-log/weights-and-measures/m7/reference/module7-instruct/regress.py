"""regress.py — M7 Behavioral Regression Suite.

Instruction-tuning adds capability. A regression suite is what proves it did not
remove any. This script runs a fixed set of behaviour checks against the base model
and the base+adapter model, then gates:

  PASS (exit 0) iff the tuned model matches or beats the base on EVERY case (no
  regression) AND strictly improves on at least one (the new skill was learned).
  BLOCK (exit 1) otherwise.

The checks are string-level exact matches on the greedy-decoded response, so they are
deterministic and an interviewer can read them at a glance.

MLflow logging is optional; pass --no-mlflow (or run without mlflow installed) to skip.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from tune import NAMES, load_base, load_tuned, generate_response

try:
    import mlflow  # optional
    HAS_MLFLOW = True
except ImportError:  # pragma: no cover - exercised only when mlflow absent
    HAS_MLFLOW = False

ROOT = Path(__file__).resolve().parent
MLFLOW_DB = ROOT / "outputs" / "mlruns.db"

# The behaviour suite: the new skill (greet) plus the two old skills the adapter must
# not break. Held-out names the model never trained on are included on purpose.
SUITE: List[Tuple[str, str, str]] = [
    # (verb, name, expected_response)
    ("greet", "alice", "hello alice"),
    ("greet", "ivan", "hello ivan"),
    ("greet", "judy", "hello judy"),
    ("thank", "bob", "thanks bob"),
    ("thank", "grace", "thanks grace"),
    ("bye", "carol", "goodbye carol"),
    ("bye", "heidi", "goodbye heidi"),
]


def score(model, suite: List[Tuple[str, str, str]]) -> List[int]:
    """1 if the model's response exactly matches the expected string, else 0."""
    results = []
    for verb, name, expected in suite:
        got = " ".join(generate_response(model, verb, name))
        results.append(int(got == expected))
    return results


def evaluate() -> dict:
    base = load_base()
    tuned = load_tuned()
    base_scores = score(base, SUITE)
    tuned_scores = score(tuned, SUITE)

    regressions = [
        SUITE[i][:2] for i in range(len(SUITE)) if tuned_scores[i] < base_scores[i]
    ]
    improved = sum(int(t > b) for t, b in zip(tuned_scores, base_scores))
    no_regression = len(regressions) == 0
    passed = no_regression and improved > 0

    return {
        "base_pass": sum(base_scores),
        "tuned_pass": sum(tuned_scores),
        "n_cases": len(SUITE),
        "improved": improved,
        "regressions": regressions,
        "no_regression": no_regression,
        "passed": bool(passed),
        "per_case": list(zip([f"{v} {n}" for v, n, _ in SUITE], base_scores, tuned_scores)),
    }


def log_to_mlflow(m: dict) -> None:
    if not HAS_MLFLOW:
        return
    MLFLOW_DB.parent.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB}")
    mlflow.set_experiment("m7-instruct-regression")
    with mlflow.start_run():
        mlflow.log_metric("base_pass", m["base_pass"])
        mlflow.log_metric("tuned_pass", m["tuned_pass"])
        mlflow.log_metric("improved", m["improved"])
        mlflow.log_param("no_regression", m["no_regression"])
        mlflow.log_param("passed", m["passed"])


def format_report(m: dict) -> str:
    lines = [f"[regress] {m['n_cases']} behaviour checks (base vs tuned)"]
    for label, b, t in m["per_case"]:
        flag = "  " if t >= b else "REGRESSION"
        lines.append(f"  {label:14} base={b} tuned={t} {flag}")
    lines.append(
        f"  base={m['base_pass']}/{m['n_cases']}  tuned={m['tuned_pass']}/{m['n_cases']}  "
        f"improved={m['improved']}  regressions={len(m['regressions'])}"
    )
    lines.append(f"  GATE: {'PASS' if m['passed'] else 'BLOCK'}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="M7 behavioral regression gate.")
    parser.add_argument("--no-mlflow", action="store_true")
    args = parser.parse_args()

    m = evaluate()
    print(format_report(m))
    if not args.no_mlflow:
        log_to_mlflow(m)
    return 0 if m["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
