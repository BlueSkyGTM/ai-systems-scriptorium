"""m5_eval.py — the eval gate (M5's technique).

Scores the trained classifier against a majority-class baseline on exact-match accuracy
and macro-F1, and gates: PASS only if the model beats the baseline by at least 5
percentage points on BOTH metrics. The model is rebuilt from the checkpoint via m6_train,
so the gate never re-implements the architecture.
"""
from __future__ import annotations

from typing import Dict, List

import torch

import m6_train

MARGIN_PP = 0.05


def accuracy(preds: List[int], golds: List[int]) -> float:
    return sum(int(p == g) for p, g in zip(preds, golds)) / len(golds) if golds else 0.0


def macro_f1(preds: List[int], golds: List[int], num_classes: int = m6_train.NUM_CLASSES) -> float:
    f1s = []
    for c in range(num_classes):
        tp = sum(int(p == c and g == c) for p, g in zip(preds, golds))
        fp = sum(int(p == c and g != c) for p, g in zip(preds, golds))
        fn = sum(int(p != c and g == c) for p, g in zip(preds, golds))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return sum(f1s) / len(f1s) if f1s else 0.0


def gate(checkpoint: dict, test: List[dict]) -> Dict[str, float]:
    model, vocab = m6_train.load_model(checkpoint)
    golds = [m6_train.CLASS_NAMES.index(r["label"]) for r in test]

    ids, lengths = [], []
    for r in test:
        i, ln = vocab.encode(r["text"])
        ids.append(i)
        lengths.append(ln)
    with torch.no_grad():
        preds = model(torch.tensor(ids), torch.tensor(lengths)).argmax(1).tolist()

    base_class = checkpoint["train_majority_class"]
    base_preds = [base_class] * len(golds)

    tuned_acc, tuned_f1 = accuracy(preds, golds), macro_f1(preds, golds)
    base_acc, base_f1 = accuracy(base_preds, golds), macro_f1(base_preds, golds)
    passed = (tuned_acc >= base_acc + MARGIN_PP) and (tuned_f1 >= base_f1 + MARGIN_PP)

    return {
        "tuned_acc": tuned_acc, "tuned_f1": tuned_f1,
        "baseline_acc": base_acc, "baseline_f1": base_f1,
        "passed": bool(passed), "n_test": len(golds),
    }
