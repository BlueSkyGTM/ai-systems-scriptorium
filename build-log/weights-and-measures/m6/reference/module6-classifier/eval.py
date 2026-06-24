"""eval.py — M6 Eval Gate for the tuned skill classifier.

Loads a checkpoint and the held-out test set, then scores the tuned model against
a majority-class baseline on two metrics:

  * exact-match accuracy
  * macro-F1

The GATE passes (exit 0) iff the tuned model beats the baseline by at least 5
percentage points on BOTH metrics. Otherwise it BLOCKS (exit 1). The exit code is
the deliverable: a tune that cannot prove it beats the cheapest possible model
does not ship.

MLflow logging is optional. If mlflow is installed it logs to an offline sqlite
backend; if not, the gate still runs (the logging is a convenience, not the gate).

Checkpoint contract (produced by train.py):
    state_dict, vocab (stoi), class_names, config, train_majority_class

Test JSONL row contract: {"text": "...", "label": "<class name>"}
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import torch

# Import the architecture + tokenizer from train.py so the two can never drift.
from train import (
    CLASS_NAMES,
    MAX_LEN,
    NUM_CLASSES,
    TextClassifier,
    Vocab,
)

try:
    import mlflow  # optional
    HAS_MLFLOW = True
except ImportError:  # pragma: no cover - exercised only when mlflow absent
    HAS_MLFLOW = False

ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT / "outputs"
DEFAULT_CHECKPOINT = OUTPUTS_DIR / "checkpoint.pt"
DEFAULT_TEST = OUTPUTS_DIR / "test.jsonl"
MLFLOW_DB = OUTPUTS_DIR / "mlruns.db"

MARGIN_PP = 0.05  # gate requires >= 5 percentage points on BOTH metrics


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def accuracy(preds: List[int], golds: List[int]) -> float:
    if not golds:
        return 0.0
    return sum(int(p == g) for p, g in zip(preds, golds)) / len(golds)


def macro_f1(preds: List[int], golds: List[int], num_classes: int = NUM_CLASSES) -> float:
    f1s = []
    for c in range(num_classes):
        tp = sum(int(p == c and g == c) for p, g in zip(preds, golds))
        fp = sum(int(p == c and g != c) for p, g in zip(preds, golds))
        fn = sum(int(p != c and g == c) for p, g in zip(preds, golds))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        f1s.append(f1)
    return sum(f1s) / len(f1s) if f1s else 0.0


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
def load_jsonl(path: Path) -> List[Tuple[str, str]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            rows.append((obj["text"], obj["label"]))
    return rows


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
def evaluate(checkpoint_path: Path, test_path: Path) -> Dict[str, float]:
    """Score the tuned model vs the majority-class baseline. Returns a dict of
    metrics plus the two boolean margin checks and the overall gate result."""
    checkpoint = torch.load(checkpoint_path, weights_only=False)
    vocab = Vocab(checkpoint["vocab"])
    config = checkpoint["config"]

    model = TextClassifier(
        len(vocab),
        config["num_classes"],
        config["embed_dim"],
        config["hidden_dim"],
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    test = load_jsonl(test_path)
    golds = [CLASS_NAMES.index(label) for _, label in test]

    token_ids, lengths = [], []
    for text, _ in test:
        ids, length = vocab.encode(text, config.get("max_len", MAX_LEN))
        token_ids.append(ids)
        lengths.append(length)
    x = torch.tensor(token_ids, dtype=torch.long)
    lens = torch.tensor(lengths, dtype=torch.long)

    with torch.no_grad():
        tuned_preds = model(x, lens).argmax(dim=1).tolist()

    baseline_class = checkpoint["train_majority_class"]
    baseline_preds = [baseline_class] * len(golds)

    tuned_acc = accuracy(tuned_preds, golds)
    tuned_f1 = macro_f1(tuned_preds, golds)
    base_acc = accuracy(baseline_preds, golds)
    base_f1 = macro_f1(baseline_preds, golds)

    acc_ok = tuned_acc >= base_acc + MARGIN_PP
    f1_ok = tuned_f1 >= base_f1 + MARGIN_PP

    return {
        "tuned_acc": tuned_acc,
        "tuned_f1": tuned_f1,
        "baseline_acc": base_acc,
        "baseline_f1": base_f1,
        "acc_margin": tuned_acc - base_acc,
        "f1_margin": tuned_f1 - base_f1,
        "acc_ok": acc_ok,
        "f1_ok": f1_ok,
        "passed": bool(acc_ok and f1_ok),
        "n_test": len(golds),
    }


def log_to_mlflow(metrics: Dict[str, float]) -> None:
    """Log metrics to an offline MLflow sqlite backend. No-op if mlflow absent."""
    if not HAS_MLFLOW:
        return
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB}")
    mlflow.set_experiment("m6-classifier-eval")
    with mlflow.start_run():
        for key, value in metrics.items():
            if isinstance(value, bool):
                mlflow.log_param(key, value)
            else:
                mlflow.log_metric(key, float(value))


def format_report(m: Dict[str, float]) -> str:
    verdict = "PASS" if m["passed"] else "BLOCK"
    return (
        f"[eval] n_test={m['n_test']}\n"
        f"  tuned    : acc={m['tuned_acc']:.3f}  macro_f1={m['tuned_f1']:.3f}\n"
        f"  baseline : acc={m['baseline_acc']:.3f}  macro_f1={m['baseline_f1']:.3f}\n"
        f"  margins  : acc={m['acc_margin']:+.3f} ({'ok' if m['acc_ok'] else 'FAIL'})  "
        f"f1={m['f1_margin']:+.3f} ({'ok' if m['f1_ok'] else 'FAIL'})\n"
        f"  GATE     : {verdict} (needs >= {MARGIN_PP:.0%} on both)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M6 eval gate: tuned vs baseline.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--test", type=Path, default=DEFAULT_TEST)
    parser.add_argument("--no-mlflow", action="store_true", help="skip MLflow logging")
    args = parser.parse_args()

    metrics = evaluate(args.checkpoint, args.test)
    print(format_report(metrics))
    if not args.no_mlflow:
        log_to_mlflow(metrics)

    return 0 if metrics["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

