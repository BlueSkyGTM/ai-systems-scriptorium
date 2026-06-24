The user wants me to generate `tests/test_classifier.py` for Module 6. This is a pytest suite that should be a subset of smoke.py assertions.

Let me think about what this file needs to test:
1. Training produces a checkpoint
2. Eval produces PASS exit code on the tuned model
3. Eval produces BLOCK exit code when model is untrained
4. Accuracy and F1 metrics are computed
5. Baseline comparison works
6. Seeds are fixed
7. MLflow logs are created

Since this is a pytest subset of smoke.py assertions, I need to test components that are reasonable to test in pytest. I shouldn't just call smoke.py - I should test individual pieces.

Let me think about the structure of the system:
- `train.py` has a training function that takes config and produces a checkpoint
- `eval.py` has an eval function that loads checkpoint and test set, computes metrics, returns results dict and pass/block
- There's likely a shared model definition, dataset loader

Let me design this as testing:
1. Test that a model can be instantiated and forwarded
2. Test that the dataset loader works
3. Test that training improves loss/accuracy
4. Test that eval returns correct structure with metrics
5. Test that the gate logic works (PASS when tuned beats baseline, BLOCK otherwise)
6. Test that seeds are reproducible
7. Test MLflow artifact creation

I'll write a focused pytest suite. Since I don't have access to the actual train.py/eval.py source, I'll make reasonable assumptions about their interfaces based on the spec.

Let me assume the following interface:
- `train.py`: 
  - `main(config)` or callable functions
  - saves checkpoint to `outputs/classifier.pt`
- `eval.py`:
  - `evaluate(checkpoint_path, test_path)` returns dict with keys: `tuned_acc`, `baseline_acc`, `tuned_f1`, `baseline_f1`, `delta_acc`, `delta_f1`, `pass`
  - exit code 0 = PASS, 1 = BLOCK

Let me also assume there's a shared module for the model and data, perhaps `model.py` and `data.py`, or maybe everything is in train.py.

I'll write tests that exercise:
1. Dataset loading and shape
2. Model forward pass
3. Training reduces loss
4. Checkpoint exists and loads
5. Eval metrics structure
6. Gate logic
7. Reproducibility
8. MLflow logs

Let me write this carefully. I'll use pytest fixtures and import the modules being tested.

I'll be conservative about the exact interfaces and use try/except or reasonable assumptions. Let me write this assuming there are clean function-level interfaces in train.py and eval.py.

Actually, looking at typical implementations of such artifacts, I'll structure tests around:
- `import train` and `import eval` as modules
- These modules expose class/function interfaces

Let me write a comprehensive but focused test file:

```python
"""Pytest suite for the tuned text classifier artifact.

This is a subset of the smoke-test assertions; it focuses on
unit-level invariants that can be checked quickly on CPU.
"""
from __future__ import annotations

import os
import sys
import json
import random
import shutil
import subprocess
from pathlib import Path

import pytest
import torch

# Ensure repo root is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

torch.manual_seed(42)
random.seed(42)

OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


# ---------- Fixtures ----------

@pytest.fixture(scope="session")
def tiny_fixture_dir(tmp_path_factory):
    """Build a tiny JSONL dataset for testing."""
    d = tmp_path_factory.mktemp("data")
    labels = ["positive", "negative", "neutral", "tech", "sports"]
    rows = []
    for i, lab in enumerate(labels * 12):  # 60 rows
        rows.append({"text": f"sample {i} about {lab}", "label": lab})
    train_p = d / "train.jsonl"
    with train_p.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    test_rows = []
    for i, lab in enumerate(labels * 4):  # 20 rows
        test_rows.append({"text": f"holdout {i} {lab} sample", "label": lab})
    test_p = d / "test.jsonl"
    with test_p.open("w") as f:
        for r in test_rows:
            f.write(json.dumps(r) + "\n")
    return d


@pytest.fixture(scope="session")
def trained_checkpoint(tiny_fixture_dir):
    """Run train.py end-to-end and yield the checkpoint path."""
    ckpt = OUT / "classifier.pt"
    if ckpt.exists():
        ckpt.unlink()
    import train
    train.main(
        data_path=str(tiny_fixture_dir / "train.jsonl"),
        out_path=str(ckpt),
        epochs=3,
        batch_size=8,
        seed=42,
    )
    assert ckpt.exists(), "train.py did not produce a checkpoint"
    return ckpt


# ---------- Model / data unit tests ----------

def test_dataset_loader_yields_tensors(tiny_fixture_dir):
    from data import load_dataset  # noqa
    ds = load_dataset(str(tiny_fixture_dir / "train.jsonl"))
    assert len(ds) > 0
    x, y = ds[0]
    assert torch.is_tensor(x)
    assert torch.is_tensor(y) or isinstance(y, int)


def test_model_forward_shape():
    from model import TextClassifier
    net = TextClassifier(vocab_size=200, num_classes=5)
    x = torch.randint(0, 200, (4, 16))
    logits = net(x)
    assert logits.shape == (4, 5)


def test_training_reduces_loss(tiny_fixture_dir, tmp_path):
    import train
    ckpt = tmp_path / "ckpt.pt"
    # Train one step and ensure final loss < initial loss on a held batch.
    metrics = train.main(
        data_path=str(tiny_fixture_dir / "train.jsonl"),
        out_path=str(ckpt),
        epochs=2,
        batch_size=8,
        seed=42,
        return_metrics=True,
    )
    assert metrics["final_loss"] < metrics["initial_loss"]


# ---------- Checkpoint / eval tests ----------

def test_checkpoint_loads_with_state_dict(trained_checkpoint):
    ck = torch.load(trained_checkpoint, map_location="cpu")
    assert "state_dict" in ck or "model" in ck
    # Validate keys are tensor-valued.
    sd = ck.get("state_dict", ck.get("model"))
    assert all(isinstance(v, torch.Tensor) for v in sd.values())


def test_eval_returns_required_metrics(trained_checkpoint, tiny_fixture_dir):
    import eval as eval_mod
    res = eval_mod.evaluate(
        checkpoint_path=str(trained_checkpoint),
        test_path=str(tiny_fixture_dir / "test.jsonl"),
    )
    for key in ["tuned_acc", "baseline_acc", "tuned_f1", "baseline_f1"]:
        assert key in res, f"missing metric: {key}"
    assert 0.0 <= res["tuned_acc"] <= 1.0
    assert 0.0 <= res["tuned_f1"] <= 1.0


def test_gate_passes_for_trained_model(trained_checkpoint, tiny_fixture_dir):
    import eval as eval_mod
    res = eval_mod.evaluate(
        checkpoint_path=str(trained_checkpoint),
        test_path=str(tiny_fixture_dir / "test.jsonl"),
    )
    assert res["tuned_acc"] >= res["baseline_acc"] + 0.05 - 1e-6
    assert res["tuned_f1"] >= res["baseline_f1"] + 0.05 - 1e-6
    assert res["passed"] is True


def test_gate_blocks_for_untrained_model(tiny_fixture_dir, tmp_path):
    """An untrained (random-init) checkpoint must fail the gate."""
    from model import TextClassifier
    net = TextClassifier(vocab_size=200, num_classes=5)
    untrained = tmp_path / "untrained.pt"
    torch.save(
        {
            "state_dict": net.state_dict(),
            "config": {"vocab_size": 200, "num_classes": 5},
        },
        untrained,
    )
    import eval as eval_mod
    res = eval_mod.evaluate(
        checkpoint_path=str(untrained),
        test_path=str(tiny_fixture_dir / "test.jsonl"),
        allow_block=True,
    )
    # Untrained should not clear the +5pp bar on both metrics.
    assert res["passed"] is False


# ---------- Reproducibility ----------

def test_seeds_are_deterministic(tiny_fixture_dir, tmp_path):
    import train
    a = tmp_path / "a.pt"
    b = tmp_path / "b.pt"
    train.main(data_path=str(tiny_fixture_dir / "train.jsonl"),
               out_path=str(a), epochs=1, batch_size=8, seed=42)
    train.main(data_path=str(tiny_fixture_dir / "train.jsonl"),
               out_path=str(b), epochs=1, batch_size=8, seed=42)
    sa = torch.load(a, map_location="cpu")
    sb = torch.load(b, map_location="cpu")
    sda = sa.get("state_dict", sa.get("model"))
    sdb = sb.get("state_dict", sb.get("model"))
    for k in sda:
        assert torch.allclose(sda[k], sdb[k]), f"weights diverged for {k}"


# ---------- MLflow artifacts ----------

def test_mlflow_run_logged(trained_checkpoint, tiny_fixture_dir):
    import eval as eval_mod
    eval_mod.evaluate(
        checkpoint_path=str(trained_checkpoint),
        test_path=str(tiny_fixture_dir / "test.jsonl"),
        log_mlflow=True,
    )
    assert (OUT / "mlruns.db").exists() or (OUT / "mlruns").exists()
```

Hmm, but I'm guessing at too many interface details. Let me be more careful and defensive. The tests should be reasonably robust to different reasonable interfaces.

Actually, looking back at the spec, it says train.py and eval.py are scripts, and the tests should be "a subset of smoke assertions". The cleanest approach is to:
1. Run train.py as a subprocess or via main()
2. Run eval.py as a subprocess (to check exit codes)
3. Assert on the artifacts and outputs

But pytest tests that subprocess-call full scripts are slow. Better to have function-level interfaces.

Let me write this assuming train.py and eval.py have:
- `train.main(args=None)` - parses args or uses defaults, runs training
- `eval.main(args=None)` - parses args, runs eval, returns exit code
- Possibly internal functions like `evaluate(...)`

Actually for robustness, let me design tests that work whether the modules expose function interfaces or only script-level behavior. I'll test what's reasonable:

1. Module imports work
2. Training script produces checkpoint
3. Eval script exits 0 on trained model
4. Eval script exits 1 on untrained model
5. MLflow artifacts exist after eval
6. Seeds are deterministic

Let me use subprocess for the eval tests since exit code is critical.

Let me revise:

```python
"""Pytest suite for the tuned text classifier artifact (M6).

Subset of smoke.py assertions; focused on CPU-fast unit checks.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

torch.manual_seed(42)
random.seed(42)

PYTHON = sys.executable


# ---------- Fixtures ----------

@pytest.fixture()
def tiny_data(tmp_path):
    labels = ["positive", "negative", "neutral", "tech", "sports"]
    train = tmp_path / "train.jsonl"
    test = tmp_path / "test.jsonl"
    with train.open("w") as f:
        for i in range(60):
            lab = labels[i % len(labels)]
            f.write(json.dumps({"text": f"sample {i} about {lab} content", "label": lab}) + "\n")
    with test.open("w") as f:
        for i in range(20):
            lab = labels[i % len(labels)]
            f.write(json.dumps({"text": f"holdout {i} {lab} sample", "label": lab}) + "\n")
    return train, test


@pytest.fixture()
def trained_checkpoint(tiny_data, tmp_path):
    train_p, _ = tiny_data
    ckpt = tmp_path / "classifier.pt"
    rc = subprocess.run(
        [PYTHON, str(ROOT / "train.py"),
         "--data", str(train_p),
         "--out", str(ckpt),
         "--epochs", "5",
         "--seed", "42"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert ckpt.exists()
    return ckpt


# ---------- Tests ----------

def test_train_produces_checkpoint(tiny_data, tmp_path):
    train_p, _ = tiny_data
    ckpt = tmp_path / "classifier.pt"
    rc = subprocess.run(
        [PYTHON, str(ROOT / "train.py"),
         "--data", str(train_p),
         "--out", str(ckpt),
         "--epochs", "3",
         "--seed", "42"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert rc.returncode == 0, rc.stderr
    assert ckpt.exists()
    state = torch.load(ckpt, map_location="cpu")
    assert "state_dict" in state or "model_state_dict" in state


def test_eval_passes_on_trained_model(trained_checkpoint, tiny_data):
    _, test_p = tiny_data
    rc = subprocess.run(
        [PYTHON, str(ROOT / "eval.py"),
         "--checkpoint", str(trained_checkpoint),
         "--test", str(test_p),
         "--seed", "42"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert rc.returncode == 0, f"Expected PASS, got BLOCK:\n{rc.stdout}\n{rc.stderr}"


def test_eval_blocks_on_untrained_model(tiny_data, tmp_path):
    _, test_p = tiny_data
    untrained = tmp_path / "untrained.pt"
    # Save an untrained model with the same architecture.
    # We rely on train.py exposing a model factory, or we save a trivially
    # poor checkpoint by training 0 epochs.
    rc = subprocess.run(
        [PYTHON, str(ROOT / "train.py"),
         "--data", str(tiny_data[0]),
         "--out", str(untrained),
         "--epochs", "0",
         "--seed", "42"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    if rc.returncode != 0 or not untrained.exists():
        pytest.skip("train.py does not support epochs=0 for untrained baseline")
    rc = subprocess.run(
        [PYTHON, str(ROOT / "eval.py"),
         "--checkpoint", str(untrained),
         "--test", str(test_p),
         "--seed", "42"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert rc.returncode == 1, "Expected BLOCK for untrained model"


def test_mlflow_artifacts_created(trained_checkpoint, tiny_data):
    _, test_p = tiny_data
    # Wipe mlruns to detect fresh creation.
    mlruns_db = OUT / "mlruns.db"
    mlruns_dir = OUT / "mlruns"
    if mlruns_db.exists():
        mlruns_db.unlink()
    if mlruns_dir.exists():
        shutil.rmtree(mlruns_dir)
    subprocess.run(
        [PYTHON, str(ROOT / "eval.py"),
         "--checkpoint", str(trained_checkpoint),
         "--test", str(test_p),
         "--seed", "42"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert mlruns_db.exists() or mlruns_dir.exists()


def test_determinism_same_seed(tiny_data, tmp_path):
    train_p, _ = tiny_data
    a = tmp_path / "a.pt"
    b = tmp_path / "b.pt"
    for ckpt in (a, b):
        rc = subprocess.run(
            [PYTHON, str(ROOT / "train.py"),
             "--data", str(train_p),
             "--out", str(ckpt),
             "--epochs", "2",
             "--seed", "42"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert rc.returncode == 0, rc.stderr
    sa = torch.load(a, map_location="cpu")
    sb = torch.load(b, map_location="cpu")
    sa_sd = sa.get("state_dict", sa.get("model_state_dict", sa))
    sb_sd = sb.get("state_dict", sb.get("model_state_dict", sb))
    assert set(sa_sd.keys()) == set(sb_sd.keys())
    for k in sa_sd:
        assert torch.allclose(sa_sd[k], sb_sd[k]), f"non-deterministic weights at {k}"
```

This is more robust. But I'm not sure about the exact CLI args of train.py/eval.py. Let me make reasonable assumptions that match common conventions and that smoke.py would likely also use.

Actually let me think again - the spec mentions `outputs/` directory for checkpoints and `outputs/mlruns/` for MLflow. Let me make the tests flexible and not too prescriptive about exact CLI flags. But subprocess calls need exact args.

I'll go with a reasonable, conventional CLI design. The book's train.py and eval.py will be designed to match. The smoke.py likely has the same structure.

Let me finalize the tests. I want it to be CPU-fast, so I'll keep epoch counts small and dataset sizes small.

One concern: the determinism test creates models multiple times - need to make sure subprocess seeds work. Setting `--seed 42` should propagate `torch.manual_seed(42)`.

Let me also think about edge cases:
- The untrained test - if train.py doesn't support `--epochs 0`, we should skip. I have that.
- MLflow: the spec says sqlite backend `outputs/mlruns.db`, but also mentions `outputs/mlruns/` directory. I'll check for either.

I think this is solid. Let me also add a test for the JSONL contract:
- The dataset is in JSONL format with `text` and `label` fields.

And a test for the model forward shape if there's a separate model module. But since the spec says "no HuggingFace required, but may use torchtext-style approach or pure torch", there might not be a separate model module. Better to skip that and focus on the artifacts.

Let me clean up the final version and ensure correctness.

Final structure:
1. test_train_produces_checkpoint
2