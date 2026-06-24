"""smoke.py — end-to-end smoke test for the Module 7 instruction-tuned artifact.

Pipeline:
  1. Build a 10-sample JSONL fixture.
  2. Run tune.py on that fixture (must finish on CPU).
  3. Run regress.py on the resulting adapter -> expects PASS (exit 0).
  4. Swap the adapter file with random weights of identical shapes.
  5. Run regress.py on the corrupted adapter -> expects BLOCK (exit 1).
  6. Restore the real adapter.

smoke.py exits 0 only if every one of those expected outcomes was observed,
including the negative case (random adapter must BLOCK). The negative-case
assertion is the regression-suite's "fuse": it proves regress.py is capable
of failing, so a green run is meaningful.

Constraints honored:
  * stdlib + torch only (no HuggingFace, no sklearn needed here).
  * Fixed seeds (random, torch).
  * CPU-runnable, designed to finish in < 45 s on a laptop CPU.
  * MLflow offline sqlite backend for child processes.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path

import torch

# ----------------------------------------------------------------------------
# Paths and constants
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
ADAPTER_DIR = OUTPUTS / "adapter"
ADAPTER_FILE = ADAPTER_DIR / "adapter.pt"
DATA_DIR = ROOT / "data"
FIXTURE = DATA_DIR / "smoke_fixture.jsonl"

MLFLOW_URI = "sqlite:///outputs/mlruns.db"
SMOKE_BUDGET_SECONDS = 45.0


# ----------------------------------------------------------------------------
# Seed control
# ----------------------------------------------------------------------------
def set_seeds() -> None:
    random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)
    try:
        import numpy as np  # optional, only if available
        np.random.seed(42)
    except ImportError:
        pass


# ----------------------------------------------------------------------------
# Subprocess runner (inherits env so MLFLOW_TRACKING_URI flows downstream)
# ----------------------------------------------------------------------------
def run(cmd: list[str]) -> int:
    env = os.environ.copy()
    env.setdefault("CUDA_VISIBLE_DEVICES", "")  # force CPU
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    print(f"[smoke] $ {' '.join(cmd)}", flush=True)
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.stdout:
        print(proc.stdout, end="", flush=True)
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr, flush=True)
    return proc.returncode


# ----------------------------------------------------------------------------
# Fixture creation (deterministic 10-sample chat-format JSONL)
# ----------------------------------------------------------------------------
def build_fixture() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    samples = [
        {"instruction": "Say hello.", "response": "Hello there!"},
        {"instruction": "What is 2+2?", "response": "4"},
        {"instruction": "Name a primary color.", "response": "Blue"},
        {"instruction": "Capitalize the word cat.", "response": "CAT"},
        {"instruction": "What sound does a dog make?", "response": "Woof"},
        {"instruction": "Say goodbye.", "response": "Goodbye!"},
        {"instruction": "What is 1+1?", "response": "2"},
        {"instruction": "Name a fruit.", "response": "Apple"},
        {"instruction": "What is the opposite of hot?", "response": "Cold"},
        {"instruction": "Spell the word red.", "response": "R-E-D"},
    ]
    assert len(samples) == 10, "smoke fixture must have exactly 10 samples"
    with FIXTURE.open("w") as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")
    return FIXTURE


# ----------------------------------------------------------------------------
# Negative-case helpers: swap adapter with random weights of identical shapes
# ----------------------------------------------------------------------------
def corrupt_adapter_with_random_weights(path: Path) -> Path:
    """Overwrite the LoRA adapter file with random tensors of identical
    shapes/dtypes. Returns the backup path so the real adapter can be restored.
    """
    backup = path.with_suffix(".bak.pt")
    shutil.copy2(path, backup)

    state = torch.load(path, map_location="cpu")
    corrupted: dict[str, object] = {}
    for key, value in state.items():
        if isinstance(value, torch.Tensor):
            # randn_like preserves dtype/shape; LoRA deltas are small float tensors
            corrupted[key] = torch.randn_like(value) * 0.1
        else:
            corrupted[key] = value
    torch.save(corrupted, path)
    return backup


def restore_adapter(path: Path, backup: Path) -> None:
    shutil.copy2(backup, path)
    try:
        backup.unlink()
    except FileNotFoundError:
        pass


# ----------------------------------------------------------------------------
# Main smoke flow
# ----------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    set_seeds()

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_URI

    # -------- Step 1: build fixture --------
    fixture = build_fixture()
    assert fixture.exists() and fixture.stat().st_size > 0

    # Clean slate: remove stale adapter if present so we test a fresh tune.
    if ADAPTER_FILE.exists():
        ADAPTER_FILE.unlink()

    # -------- Step 2: tune on the 10-sample fixture --------
    rc = run([
        sys.executable, "tune.py",
        "--data", str(fixture),
        "--adapter-out", str(ADAPTER_FILE),
        "--epochs", "1",
    ])
    assert rc == 0, f"tune.py exited with rc={rc} (expected 0)"
    assert ADAPTER_FILE.exists(), "tune.py did not produce adapter.pt"

    # Sanity: adapter must contain tensors, not be empty.
    adapter_state = torch.load(ADAPTER_FILE, map_location="cpu")
    tensor_keys = [k for k, v in adapter_state.items() if isinstance(v, torch.Tensor)]
    assert len(tensor_keys) > 0, "adapter.pt contains no tensors"
    print(f"[smoke] tune.py OK ({len(tensor_keys)} tensor params)", flush=True)

    # -------- Step 3: regress on real adapter -> must PASS --------
    rc = run([sys.executable, "regress.py", "--adapter", str(ADAPTER_FILE)])
    assert rc == 0, (
        f"regress.py BLOCKED the real adapter (rc={rc}); expected PASS (0)"
    )
    print("[smoke] regress.py PASS on real adapter OK", flush=True)

    # -------- Step 4: negative case — random adapter must BLOCK --------
    backup = corrupt_adapter_with_random_weights(ADAPTER_FILE)
    try:
        rc = run([sys.executable, "regress.py", "--adapter", str(ADAPTER_FILE)])
        assert rc == 1, (
            f"regress.py PASSED a random-weight adapter (rc={rc}); "
            "expected BLOCK (1) — regression suite is not sensitive enough"
        )
        print("[smoke] regress.py BLOCK on random adapter OK", flush=True)
    finally:
        restore_adapter(ADAPTER_FILE, backup)

    # -------- Final adapter sanity check --------
    restored_state = torch.load(ADAPTER_FILE, map_location="cpu")
    for k in tensor_keys:
        assert torch.equal(
            restored_state[k], adapter_state[k]
        ), f"adapter param '{k}' changed during negative-case dance"

    elapsed = time.time() - t0
    print(f"[smoke] ALL SMOKE CHECKS PASSED in {elapsed:.1f}s", flush=True)
    assert elapsed < SMOKE_BUDGET_SECONDS, (
        f"smoke exceeded budget: {elapsed:.1f}s > {SMOKE_BUDGET_SECONDS}s"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as e:
        print(f"[smoke] FAIL: {e}", file=sys.stderr, flush=True)
        sys.exit(1)