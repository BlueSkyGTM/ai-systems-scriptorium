"""smoke.py — end-to-end smoke test for the Module 8 pipeline.

Runs ``pipeline.py`` on synthetic fixtures, then ``rubric.py``.

Two scenarios are exercised and BOTH outcomes are asserted:
  1. Happy path     : full pipeline (data → train → eval gate → regress → log)
                      rubric.py MUST exit 0 (READY).
  2. Deficient path : eval gate skipped.
                      rubric.py MUST exit 1 (NEEDS WORK).

The smoke test itself exits 0 iff both assertions hold.

CPU-only, < 60s total, fixed seeds. No HuggingFace.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import torch

# ---------------------------------------------------------------------------
# Determinism — set BEFORE any work happens.
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
os.environ.setdefault("PYTHONHASHSEED", str(SEED))

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

MLFLOW_URI = "sqlite:///outputs/mlruns.db"
os.environ.setdefault("MLFLOW_TRACKING_URI", MLFLOW_URI)

PIPELINE = ROOT / "pipeline.py"
RUBRIC = ROOT / "rubric.py"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def write_synthetic_fixtures(fixture_dir: Path, n_train: int = 24,
                             n_val: int = 8) -> Path:
    """Write tiny JSONL train/val fixtures understood by M3 curate + M5 eval.

    Each record carries ``text``, ``label``, and ``answer`` so the same fixture
    can serve the classifier head (M6) and the exact-match eval gate (M5).
    """
    fixture_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    def make_records(k: int, prefix: str) -> list[dict]:
        rows = []
        for i in range(k):
            label = "A" if i % 2 == 0 else "B"
            text = f"{prefix} sample {i} token {rng.randint(0, 99)} marker {label.lower()}"
            rows.append({
                "id": f"{prefix}-{i:03d}",
                "text": text,
                "label": label,
                "answer": label.lower(),
            })
        return rows

    train = make_records(n_train, "train")
    val = make_records(n_val, "val")
    (fixture_dir / "train.jsonl").write_text(
        "\n".join(json.dumps(r) for r in train), encoding="utf-8")
    (fixture_dir / "val.jsonl").write_text(
        "\n".join(json.dumps(r) for r in val), encoding="utf-8")
    return fixture_dir


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------
def build_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(SEED)
    env["MLFLOW_TRACKING_URI"] = MLFLOW_URI
    if extra:
        env.update(extra)
    return env


def run(cmd: list[str], env: dict[str, str], timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
def scenario_happy(tmp_root: Path) -> None:
    """Full pipeline runs end-to-end; rubric returns 0 (READY)."""
    fixtures = write_synthetic_fixtures(tmp_root / "fixtures_happy")
    workdir = tmp_root / "run_happy"
    workdir.mkdir(parents=True, exist_ok=True)

    env = build_env({
        "M8_FIXTURE_DIR": str(fixtures),
        "M8_WORKDIR": str(workdir),
        "M8_SKIP_EVAL_GATE": "0",
        "M8_SKIP_REGRESS": "0",
        "M8_EPOCHS": "1",
        "M8_BATCH": "4",
        "M8_SEED": str(SEED),
    })

    proc = run([sys.executable, str(PIPELINE)], env)
    assert proc.returncode == 0, (
        f"[happy] pipeline.py exited {proc.returncode}\n"
        f"--- STDOUT ---\n{proc.stdout}\n"
        f"--- STDERR ---\n{proc.stderr}\n"
    )

    manifest = workdir / "manifest.json"
    assert manifest.exists(), f"[happy] manifest missing: {manifest}"

    rub = run([sys.executable, str(RUBRIC), str(workdir)], env)
    assert rub.returncode == 0, (
        f"[happy] rubric.py should exit 0 (READY) but exited {rub.returncode}\n"
        f"--- STDOUT ---\n{rub.stdout}\n"
        f"--- STDERR ---\n{rub.stderr}\n"
    )
    print(f"[smoke] happy path OK  (rubric exit 0)  -> {workdir}")


def scenario_deficient(tmp_root: Path) -> None:
    """Eval gate skipped -> rubric MUST return 1 (NEEDS WORK)."""
    fixtures = write_synthetic_fixtures(tmp_root / "fixtures_bad")
    workdir = tmp_root / "run_bad"
    workdir.mkdir(parents=True, exist_ok=True)

    env = build_env({
        "M8_FIXTURE_DIR": str(fixtures),
        "M8_WORKDIR": str(workdir),
        "M8_SKIP_EVAL_GATE": "1",   # the deficient behavior under test
        "M8_SKIP_REGRESS": "0",
        "M8_EPOCHS": "1",
        "M8_BATCH": "4",
        "M8_SEED": str(SEED),
    })

    proc = run([sys.executable, str(PIPELINE)], env)
    # Pipeline may legitimately block on the skipped gate; accept 0 or 1.
    assert proc.returncode in (0, 1), (
        f"[bad] pipeline.py unexpected exit {proc.returncode}\n"
        f"--- STDOUT ---\n{proc.stdout}\n"
        f"--- STDERR ---\n{proc.stderr}\n"
    )

    rub = run([sys.executable, str(RUBRIC), str(workdir)], env)
    assert rub.returncode == 1, (
        f"[bad] rubric.py should exit 1 (NEEDS WORK) but exited {rub.returncode}\n"
        f"--- STDOUT ---\n{rub.stdout}\n"
        f"--- STDERR ---\n{rub.stderr}\n"
    )
    print(f"[smoke] deficient path OK  (rubric exit 1)  -> {workdir}")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main() -> int:
    # Re-seed deterministically at the top of each driver invocation.
    random.seed(SEED)
    torch.manual_seed(SEED)

    # Pre-flight: required files exist.
    for required in (PIPELINE, RUBRIC):
        assert required.exists(), f"[smoke] missing required file: {required}"

    with tempfile.TemporaryDirectory(prefix="m8_smoke_") as td:
        tmp_root = Path(td)

        scenario_happy(tmp_root)

        # Reset RNG between scenarios so the two runs are independent.
        random.seed(SEED)
        torch.manual_seed(SEED)

        scenario_deficient(tmp_root)

    print("[smoke] ALL ASSERTIONS PASSED  (happy=READY, deficient=NEEDS WORK)")
    return 0


if __name__ == "__main__":
    sys.exit(main())