"""smoke.py — end-to-end oracle for the M6 tuned classifier artifact.

Runs the whole loop on small fixtures and asserts the artifact behaves like an
artifact: it trains, the checkpoint is well-formed, the tuned model beats the
baseline, the gate PASSES on a trained model, and the gate BLOCKS on an untrained
one. The negative case is the point: a gate that never fails is not a gate.

    python smoke.py        # exits 0 iff every assertion holds
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import torch

import eval as eval_mod
import train as train_mod

ROOT = Path(__file__).resolve().parent
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
    print("[smoke] training on small fixtures...")
    summary = train_mod.train_model(n_train=300, n_test=120, epochs=20)

    ckpt = Path(summary["checkpoint"])
    test_jsonl = Path(summary["test_jsonl"])

    # --- Artifact shape -----------------------------------------------------
    check("checkpoint written", ckpt.exists())
    check("train.jsonl written", Path(summary["train_jsonl"]).exists())
    check("test.jsonl written", test_jsonl.exists())
    check("train accuracy is high", summary["train_acc"] >= 0.80)

    blob = torch.load(ckpt, weights_only=False)
    for key in ("state_dict", "vocab", "class_names", "config", "train_majority_class"):
        check(f"checkpoint has '{key}'", key in blob)
    check("5 class names", len(blob["class_names"]) == 5)
    check("config has max_len", "max_len" in blob["config"])

    # --- Happy path: trained model beats baseline, gate PASSES --------------
    m = eval_mod.evaluate(ckpt, test_jsonl)
    check("tuned acc > baseline acc", m["tuned_acc"] > m["baseline_acc"])
    check("tuned f1 > baseline f1", m["tuned_f1"] > m["baseline_f1"])
    check("acc margin >= 5pp", m["acc_ok"])
    check("f1 margin >= 5pp", m["f1_ok"])
    check("gate result PASS", m["passed"] is True)
    check("baseline acc < 0.5 (5 classes)", m["baseline_acc"] < 0.5)

    rc = subprocess.run(
        [sys.executable, str(ROOT / "eval.py"), "--no-mlflow"],
        cwd=str(ROOT), capture_output=True, text=True,
    ).returncode
    check("eval.py exits 0 on trained model", rc == 0)

    # --- Negative case: untrained model must BLOCK --------------------------
    with tempfile.TemporaryDirectory() as tmp:
        bad_ckpt = Path(tmp) / "untrained.pt"
        vocab = train_mod.Vocab(blob["vocab"])
        cfg = blob["config"]
        torch.manual_seed(0)
        untrained = train_mod.TextClassifier(
            len(vocab), cfg["num_classes"], cfg["embed_dim"], cfg["hidden_dim"]
        )
        torch.save(
            {
                "state_dict": untrained.state_dict(),
                "vocab": blob["vocab"],
                "class_names": blob["class_names"],
                "config": cfg,
                "train_majority_class": blob["train_majority_class"],
            },
            bad_ckpt,
        )
        bad = eval_mod.evaluate(bad_ckpt, test_jsonl)
        check("untrained model fails the margin", bad["passed"] is False)

        rc_bad = subprocess.run(
            [sys.executable, str(ROOT / "eval.py"),
             "--checkpoint", str(bad_ckpt), "--test", str(test_jsonl), "--no-mlflow"],
            cwd=str(ROOT), capture_output=True, text=True,
        ).returncode
        check("eval.py exits 1 on untrained model", rc_bad == 1)

    # --- Summary ------------------------------------------------------------
    total = _PASS + _FAIL
    print(f"\n[smoke] {_PASS}/{total} assertions passed")
    if _FAIL:
        print(f"[smoke] FAILED ({_FAIL} failures)")
        return 1
    print("[smoke] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
