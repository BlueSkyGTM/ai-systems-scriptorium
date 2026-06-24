"""pytest suite for the M6 tuned classifier — a subset of smoke.py's assertions.

Trains once per session on a small fixture, then checks the checkpoint shape, the
metrics, and the gate's two-sided behaviour (PASS on trained, BLOCK on untrained).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
import torch

# Make the artifact root importable (train.py / eval.py live one level up).
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import eval as eval_mod  # noqa: E402
import train as train_mod  # noqa: E402


@pytest.fixture(scope="session")
def trained():
    summary = train_mod.train_model(n_train=300, n_test=120, epochs=20)
    return summary


def test_checkpoint_written(trained):
    assert Path(trained["checkpoint"]).exists()
    assert Path(trained["test_jsonl"]).exists()


def test_checkpoint_contract(trained):
    blob = torch.load(trained["checkpoint"], weights_only=False)
    for key in ("state_dict", "vocab", "class_names", "config", "train_majority_class"):
        assert key in blob, f"missing checkpoint key: {key}"
    assert len(blob["class_names"]) == 5


def test_train_accuracy_high(trained):
    assert trained["train_acc"] >= 0.80


def test_tuned_beats_baseline(trained):
    m = eval_mod.evaluate(Path(trained["checkpoint"]), Path(trained["test_jsonl"]))
    assert m["tuned_acc"] > m["baseline_acc"]
    assert m["tuned_f1"] > m["baseline_f1"]


def test_gate_passes_on_trained(trained):
    m = eval_mod.evaluate(Path(trained["checkpoint"]), Path(trained["test_jsonl"]))
    assert m["acc_ok"] and m["f1_ok"]
    assert m["passed"] is True


def test_baseline_is_weak(trained):
    m = eval_mod.evaluate(Path(trained["checkpoint"]), Path(trained["test_jsonl"]))
    assert m["baseline_acc"] < 0.5  # 5 classes, majority-class baseline


def test_gate_blocks_on_untrained(trained):
    blob = torch.load(trained["checkpoint"], weights_only=False)
    cfg = blob["config"]
    torch.manual_seed(0)
    untrained = train_mod.TextClassifier(
        len(train_mod.Vocab(blob["vocab"])),
        cfg["num_classes"], cfg["embed_dim"], cfg["hidden_dim"],
    )
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "untrained.pt"
        torch.save(
            {
                "state_dict": untrained.state_dict(),
                "vocab": blob["vocab"],
                "class_names": blob["class_names"],
                "config": cfg,
                "train_majority_class": blob["train_majority_class"],
            },
            bad,
        )
        m = eval_mod.evaluate(bad, Path(trained["test_jsonl"]))
        assert m["passed"] is False


def test_metrics_helpers():
    assert eval_mod.accuracy([0, 1, 2], [0, 1, 2]) == 1.0
    assert eval_mod.accuracy([0, 0, 0], [0, 1, 2]) == pytest.approx(1 / 3)
    assert eval_mod.macro_f1([0, 1], [0, 1], num_classes=2) == pytest.approx(1.0)
