"""smoke.py — end-to-end oracle for the Module 7 instruction-tuned artifact.

Pipeline:
  1. Run tune.py: pretrain the base, LoRA-tune the new skill, save base + adapter.
  2. Run regress.py on the real adapter -> expects PASS (exit 0).
  3. Swap the adapter file with random weights of identical shapes.
  4. Run regress.py on the corrupted adapter -> expects BLOCK (exit 1).
  5. Restore the real adapter and confirm it is byte-for-byte intact.

smoke.py exits 0 only if every expected outcome holds, including the negative case.
The negative case is the regression suite's fuse: it proves regress.py can fail, so a
green run means something.

Constraints: stdlib + torch only, fixed seeds, CPU-runnable in a few seconds.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

import torch

import regress as regress_mod
import tune as tune_mod

ROOT = Path(__file__).resolve().parent
ADAPTER_FILE = ROOT / "outputs" / "adapter" / "adapter.pt"
BASE_FILE = ROOT / "outputs" / "base.pt"
BUDGET_S = 45.0

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


def run(args: list[str]) -> int:
    return subprocess.run(
        [sys.executable, *args], cwd=str(ROOT), capture_output=True, text=True
    ).returncode


def main() -> int:
    t0 = time.time()

    # -- Step 1: tune (pretrain base + LoRA-tune the new skill) ---------------
    print("[smoke] tuning...")
    summary = tune_mod.build()
    check("base checkpoint written", BASE_FILE.exists())
    check("adapter written", ADAPTER_FILE.exists())
    check("adapter is a small fraction of the model",
          summary["adapter_params"] < summary["total_params"] // 10)
    check("adapter has trainable params", summary["adapter_params"] > 0)

    adapter_state = torch.load(ADAPTER_FILE, weights_only=False)
    tensor_keys = [k for k, v in adapter_state.items() if isinstance(v, torch.Tensor)]
    check("adapter file holds LoRA tensors", len(tensor_keys) > 0)

    # -- Step 2: behavioural evaluation (in-process) -------------------------
    m = regress_mod.evaluate()
    check("base fails at least one case (the new skill)", m["base_pass"] < m["n_cases"])
    check("tuned passes every case", m["tuned_pass"] == m["n_cases"])
    check("tuned improves on the base", m["improved"] > 0)
    check("no behavioural regression", m["no_regression"])
    check("gate result PASS", m["passed"] is True)

    # -- Step 3: regress.py PASS on real adapter -----------------------------
    check("regress.py exits 0 on real adapter", run(["regress.py", "--no-mlflow"]) == 0)

    # -- Step 4: negative case — random adapter must BLOCK -------------------
    backup = ADAPTER_FILE.with_suffix(".bak.pt")
    shutil.copy2(ADAPTER_FILE, backup)
    try:
        corrupted = {
            k: (torch.randn_like(v) if isinstance(v, torch.Tensor) else v)
            for k, v in adapter_state.items()
        }
        torch.save(corrupted, ADAPTER_FILE)
        check("regress.py exits 1 on random adapter", run(["regress.py", "--no-mlflow"]) == 1)
    finally:
        shutil.copy2(backup, ADAPTER_FILE)
        backup.unlink(missing_ok=True)

    restored = torch.load(ADAPTER_FILE, weights_only=False)
    check("real adapter restored intact",
          all(torch.equal(restored[k], adapter_state[k]) for k in tensor_keys))

    elapsed = time.time() - t0
    check(f"finished within budget ({elapsed:.1f}s < {BUDGET_S}s)", elapsed < BUDGET_S)

    total = _PASS + _FAIL
    print(f"\n[smoke] {_PASS}/{total} assertions passed")
    if _FAIL:
        print(f"[smoke] FAILED ({_FAIL} failures)")
        return 1
    print("[smoke] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
