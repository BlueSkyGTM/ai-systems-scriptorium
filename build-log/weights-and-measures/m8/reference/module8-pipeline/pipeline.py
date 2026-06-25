"""pipeline.py — Module 8: The Full Fine-Tune Pipeline (the conductor).

Composes five vendored modules into one gated, end-to-end run:

    curate_data  -> m3_curate : validate, dedupe, split the raw tickets
    train_model  -> m6_train  : train the classifier (via the m4_tune loop)
    eval_gate    -> m5_eval   : accuracy + macro-F1 vs baseline; BLOCK if it fails
    regress      -> m7_regress: pinned golden tickets must route correctly; BLOCK if not
    log_artifact -> write outputs/manifest.json (+ optional MLflow)

The conductor is the only new code; every stage is a vendored module. Each gate raises
PipelineBlocked on failure, so the pipeline fails loud rather than shipping a bad model.
rubric.py then grades the run from the manifest.

Usage:
    python pipeline.py                 # full run -> outputs/manifest.json
    from pipeline import run_pipeline   # tests / smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIB = ROOT / "lib"
sys.path.insert(0, str(LIB))

import m3_curate  # noqa: E402
import m5_eval  # noqa: E402
import m6_train  # noqa: E402
import m7_regress  # noqa: E402

import torch  # noqa: E402

OUTPUTS = ROOT / "outputs"
MANIFEST_PATH = OUTPUTS / "manifest.json"
CHECKPOINT_PATH = OUTPUTS / "checkpoint.pt"
MLFLOW_DB = OUTPUTS / "mlruns.db"

try:
    import mlflow  # optional
    HAS_MLFLOW = True
except ImportError:  # pragma: no cover
    HAS_MLFLOW = False


class PipelineBlocked(RuntimeError):
    """Raised when a gate stage fails; the pipeline must not continue."""


def run_pipeline(*, n_raw: int = 400, seed: int = 42, skip_eval: bool = False,
                 write: bool = True) -> dict:
    """Run the full pipeline. `skip_eval=True` deliberately omits the eval gate so the
    rubric can demonstrate it catches a deficient run."""
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    # 1. curate ------------------------------------------------------------
    raw = m3_curate.generate_raw(n_raw, seed=seed)
    curated = m3_curate.curate(raw, seed=seed)

    # 2. train -------------------------------------------------------------
    trained = m6_train.build_and_train(curated)
    checkpoint = trained["checkpoint"]
    if write:
        torch.save(checkpoint, CHECKPOINT_PATH)

    # 3. eval gate ---------------------------------------------------------
    eval_summary = None
    if not skip_eval:
        eval_summary = m5_eval.gate(checkpoint, curated["test"])
        if not eval_summary["passed"]:
            raise PipelineBlocked(
                f"eval gate BLOCK: tuned_acc={eval_summary['tuned_acc']:.3f} "
                f"baseline_acc={eval_summary['baseline_acc']:.3f}"
            )

    # 4. regression gate ---------------------------------------------------
    regress_summary = m7_regress.check(checkpoint)
    if not regress_summary["passed"]:
        raise PipelineBlocked(
            f"regression BLOCK: {regress_summary['n_passed']}/{regress_summary['n_cases']} "
            f"golden cases passed"
        )

    # 5. log artifact ------------------------------------------------------
    manifest = {
        "curated": {
            "n_raw": curated["n_raw"],
            "n_deduped": curated["n_deduped"],
            "dupes_removed": curated["dupes_removed"],
            "disjoint": curated["disjoint"],
        },
        "trained": {
            "train_acc": trained["train_acc"],
            "final_loss": trained["final_loss"],
        },
        "eval": (None if eval_summary is None else {
            "passed": eval_summary["passed"],
            "tuned_acc": eval_summary["tuned_acc"],
            "baseline_acc": eval_summary["baseline_acc"],
        }),
        "regress": {
            "passed": regress_summary["passed"],
            "n_passed": regress_summary["n_passed"],
            "n_cases": regress_summary["n_cases"],
        },
        "logged": True,
    }
    if write:
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        _log_mlflow(manifest)

    return {"manifest": manifest, "checkpoint": checkpoint,
            "eval": eval_summary, "regress": regress_summary, "curated": curated}


def _log_mlflow(manifest: dict) -> None:
    if not HAS_MLFLOW:
        return
    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB}")
    mlflow.set_experiment("m8-pipeline")
    with mlflow.start_run():
        mlflow.log_metric("train_acc", manifest["trained"]["train_acc"])
        if manifest["eval"]:
            mlflow.log_metric("tuned_acc", manifest["eval"]["tuned_acc"])
        mlflow.log_param("regress_passed", manifest["regress"]["passed"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the M8 full fine-tune pipeline.")
    parser.add_argument("--skip-eval", action="store_true",
                        help="omit the eval gate (deficient run; the rubric will catch it)")
    args = parser.parse_args()
    try:
        result = run_pipeline(skip_eval=args.skip_eval)
    except PipelineBlocked as exc:
        print(f"[pipeline] BLOCKED: {exc}", file=sys.stderr)
        return 1
    m = result["manifest"]
    print(f"[pipeline] curated {m['curated']['n_deduped']} rows "
          f"(removed {m['curated']['dupes_removed']} dupes); "
          f"train_acc={m['trained']['train_acc']:.3f}; "
          f"regress {m['regress']['n_passed']}/{m['regress']['n_cases']}; "
          f"manifest -> {MANIFEST_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
