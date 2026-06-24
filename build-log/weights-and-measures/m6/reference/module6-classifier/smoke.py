The user wants me to generate smoke.py for the M6 module. Let me think through the requirements carefully.

The smoke.py needs to:
1. Run train.py on a 50-sample fixture
2. Run eval.py on a 20-sample fixture
3. All 20+ assertions pass in < 30 seconds on CPU
4. Test the negative case: untrained model must fail the gate
5. Exit 0 on all assertions including the negative case
6. Fixed random seeds

Let me design this. The smoke test needs to:
- Create fixtures (50 train samples, 20 test samples)
- Run training
- Run eval (should PASS)
- Run eval with untrained/random model (should BLOCK / exit 1)
- Verify both behaviors

Since the smoke test needs to verify exit codes, I'll use subprocess to invoke train.py and eval.py, OR import them and call functions. The spec says "runs train.py on a 50-sample fixture, then eval.py on a 20-sample fixture" - this suggests subprocess invocation.

Let me think about the structure:

1. Create fixture files in a temp directory (or under outputs/)
2. Run `python train.py --train fixture_50.jsonl --output outputs/smoke_model.pt` 
3. Run `python eval.py --model outputs/smoke_model.pt --test fixture_20.jsonl` - expect exit 0
4. For negative case: create an untrained model or use a fresh one. Run eval against it - expect exit 1
5. All assertions check exit codes

Let me write this carefully.

The fixtures should be synthetic sentiment/topic data - 5 classes. Something like:
- positive, negative, neutral, mixed, question? Or topics: sports, politics, tech, health, entertainment

Let me use sentiment with clear keywords so the model can learn quickly:
- class 0: positive (contains "great", "love", "amazing")
- class 1: negative (contains "terrible", "hate", "awful")
- class 2: neutral (contains "okay", "fine", "average")
- class 3: tech (contains "code", "computer", "software")
- class 4: sports (contains "game", "team", "player")

For 50 samples train + 20 test, with strong signal patterns, a small model should beat majority baseline easily.

Let me write smoke.py:

```python
"""
smoke.py — End-to-end smoke test for Module 6 artifact.

Runs train.py on a 50-sample fixture, then eval.py on a 20-sample fixture.
Verifies:
  - Positive case: tuned model passes the eval gate (exit 0)
  - Negative case: untrained/random model fails the eval gate (exit 1)

Exits 0 iff all assertions hold (including the negative-case assertion).
"""
from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"

# ---- Reproducibility ----
torch.manual_seed(42)
random.seed(42)

# ---- Fixture generation ----
# 5 classes with strong lexical signal so a tiny classifier learns fast on CPU.
TEMPLATES = {
    "positive": [
        "this is great and i love it",
        "amazing work really wonderful",
        "i am so happy with this",
        "fantastic experience would recommend",
        "good quality and well made",
    ],
    "negative": [
        "this is terrible and awful",
        "i hate this so much",
        "worst experience ever do not buy",
        "broken and useless really bad",
        "disappointing quality very poor",
    ],
    "neutral": [
        "it is okay nothing special",
        "average product works fine",
        "received the item as described",
        "neutral opinion no strong feeling",
        "standard and unremarkable overall",
    ],
    "tech": [
        "new software update released today",
        "the code runs on the server",
        "computer hardware is fast",
        "programming language feature added",
        "data pipeline processes records",
    ],
    "sports": [
        "the team won the game",
        "player scored in final match",
        "championship victory for club",
        "athlete broke the record",
        "season opener starts tonight",
    ],
}
LABELS = sorted(TEMPLATES.keys())  # consistent ordering


def make_fixture(path: Path, n_per_class: int, seed: int = 42) -> None:
    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for idx, label in enumerate(LABELS):
            templates = TEMPLATES[label]
            for i in range(n_per_class):
                base = templates[i % len(templates)]
                # add light noise so it's not pure duplication
                words = base.split()
                rng.shuffle(words)
                text = " ".join(words)
                f.write(f'{{"text": "{text}", "label": "{label}", "label_idx": {idx}}}\n')


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="m6_smoke_"))
    try:
        train_fixture = tmp / "train_50.jsonl"
        test_fixture = tmp / "test_20.jsonl"
        untrained_ckpt = tmp / "untrained.pt"
        trained_ckpt = OUTPUTS / "smoke_model.pt"
        OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 50 train = 10 per class, 20 test = 4 per class
        make_fixture(train_fixture, n_per_class=10)
        make_fixture(test_fixture, n_per_class=4, seed=7)

        assertions: list[tuple[str, bool, str]] = []

        # --- Step 1: train ---
        cp = run([sys.executable, str(ROOT / "train.py"),
                  "--train", str(train_fixture),
                  "--output", str(trained_ckpt),
                  "--epochs", "5",
                  "--seed", "42"])
        assertions.append(("train.py exits 0",
                           cp.returncode == 0,
                           cp.stdout + cp.stderr))
        assertions.append(("train.py produces checkpoint file",
                           trained_ckpt.exists() and trained_ckpt.stat().st_size > 0,
                           f"ckpt missing or empty at {trained_ckpt}"))

        # --- Step 2: eval on tuned model — expect PASS (exit 0) ---
        cp = run([sys.executable, str(ROOT / "eval.py"),
                  "--model", str(trained_ckpt),
                  "--test", str(test_fixture),
                  "--seed", "42"])
        assertions.append(("eval.py PASS exit 0 on tuned model",
                           cp.returncode == 0,
                           cp.stdout + cp.stderr))
        out = cp.stdout.lower()
        assertions.append(("eval log mentions exact_match",
                           "exact_match" in out or "exact-match" in out,
                           cp.stdout))
        assertions.append(("eval log mentions macro_f1",
                           "macro_f1" in out or "macro-f1" in out or "f1" in out,
                           cp.stdout))

        # --- Step 3: negative case — untrained random model must BLOCK ---
        # Build an untrained checkpoint with the same constructor signature
        # by importing train.py and saving a fresh model.
        build_untrained_script = tmp / "build_untrained.py"
        build_untrained_script.write_text(
            "import sys, torch; sys.path.insert(0, %r)\n"
            "import train as T\n"
            "torch.manual_seed(123)\n"
            "m, vocab = T.build_model()\n"
            "T.save_checkpoint(m, vocab, %r)\n"
            % (str(ROOT), str(untrained_ckpt))
        )
        cp = run([sys.executable, str(build_untrained_script)])
        assertions.append(("untrained checkpoint builds",
                           cp.returncode == 0 and untrained_ckpt.exists(),
                           cp.stdout + cp.stderr))

        cp = run([sys.executable, str(ROOT / "eval.py"),
                  "--model", str(untrained_ckpt),
                  "--test", str(test_fixture),
                  "--seed", "42"])
        assertions.append(("eval.py BLOCK exit 1 on untrained model",
                           cp.returncode == 1,
                           cp.stdout + cp.stderr))

        # --- Step 4: MLflow offline artifact emitted ---
        mlruns = OUTPUTS / "mlruns"
        assertions.append(("mlflow offline backend dir exists",
                           mlruns.exists(),
                           f"no mlruns at {mlruns}"))

        # --- Report ---
        print("\n=== smoke.py: %d assertions ===" % len(assertions))
        all_ok = True
        for name, ok, detail in assertions:
            tag = "PASS" if ok else "FAIL"
            print(f"  [{tag}] {name}")
            if not ok:
                print(f"        detail: {detail[:500]}")
                all_ok = False

        if not all_ok:
            print("\nsmoke.py: FAILURES present.")
            return 2  # real failure of smoke itself
        print("\nsmoke.py: ALL ASSERTIONS HOLD (including negative case).")
        return 0
    finally:
        # keep outputs/ artifacts; clean tmp
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
```

Wait, I'm assuming train.py has `build_model()` and `save_checkpoint()` functions. Since I don't know exactly what train.py looks like, let me think about this differently.

The negative case approach: instead of depending on train.py internals, I can:
1. Create a fixture with a 0-epoch trained model by running train.py with --epochs 0, OR
2. Create a "random" checkpoint by initializing a fresh model

Actually, a cleaner approach: train.py with --epochs 0 or --epochs 1 with shuffled labels would create a bad model.

Let me use a simpler approach: train on shuffled/random labels to produce a "deficient" model. The spec says "Deficient run (model untrained) must fail the gate". So I can train with --epochs 0 (no training) or with --shuffle-labels flag, or just initialize without training.

Actually, the cleanest is to support --epochs 0 in train.py and use that. But since I can't modify train.py here, I'll make smoke.py flexible.

Let me think again. The smoke.py is one file. It's the orchestrator. It needs to:
1. Run train.py (assumes it works)
2. Run eval.py against trained (expect PASS)
3. Run eval.py against untrained (expect BLOCK)

For the untrained case, the cleanest way is to call train.py with --epochs 0. I'll assume train.py supports this (it's a reasonable assumption for this kind of artifact). If not, I'd need to construct an untrained checkpoint manually.

Let me make it more robust — try --epochs 0 first, and if that fails, construct a model directly. Actually, simpler: just assume train.py supports --epochs 0. This is a reasonable design.

Actually, looking again at the spec: "Deficient run (model untrained) must fail the gate — smoke.py tests this negative case." So "untrained" is the wording. --epochs 0 makes sense.

Let me also reconsider: train.py is not in my control here (I'm only generating smoke.py). But the spec says these scripts should work together. I'll write smoke.py assuming train.py has reasonable CLI:
- --train <path>
- --output <path>
- --epochs <int>
- --seed <int>

And eval.py:
- --model <path>
- --test <path>
- --seed <int>
- Exit 0 = PASS, 1 = BLOCK

This is the standard contract. Let me finalize.

Let me also reconsider the untrained model creation. If train.py supports --epochs 0, that's cleanest. But there's risk: what if --epochs 0 still does one optimizer step? Let me be more defensive.

Actually, the safest negative case is to create a model with mismatched weights. I can:
1. Take the trained checkpoint
2. Replace its weights with random initialization (preserving shape)
3. Save as untrained

This works regardless of train.py internals, as long as it's a torch checkpoint with state_dict.

But that requires knowing the checkpoint format. Standard PyTorch checkpoints are dicts with "state_dict" or similar.

Let me write smoke.py to be defensive — try --epochs 0 first; if that produces a model that doesn't BLOCK, then do the weight-shuffle approach.

Actually, let me keep it simpler and more robust. I'll generate the untrained model by:
1. Running train.py with --epochs 0 (most likely creates an untrained model)
2. If that doesn't exist or eval doesn't BLOCK, fall back to corrupting the trained checkpoint's weights

Let me write a clean version. I'll structure it to assume train.py supports --epochs 0 (it's a natural feature to add), and document this assumption.

Final design:

```python
def main():
    # 1. Setup fixtures
    # 2. Run train.py (positive training)
    # 3. Run eval.py on trained model -> expect exit 0
    # 4. Run train.py --epochs 0 to create untrained model
    # 5. Run eval.py on untrained -> expect exit 1
    # 6. Verify MLflow output exists
    # 7. Report and exit
```

Let me write the final version cleanly. I'll aim for 20+ assertions as required.

Let me count assertions needed: "All 20+ assertions pass" — at least 20 assertions.

Let me brainstorm:
1. Fixture creation succeeds (train file exists, > 0 bytes)
2. Fixture train has 50 lines
3. Fixture test has 20 lines
4. Train balanced across classes (5x10)
5. Test balanced (5x4)
6. train.py exits 0
7. Checkpoint file exists
8. Checkpoint file > 0 bytes
9. Checkpoint loadable by torch
10. eval.py PASS exits 0
11. eval.py stdout contains "exact_match"
12. eval.py stdout contains "macro_f1"
13. eval.py stdout contains "baseline"
14. eval.py stdout contains PASS or pass
15. eval.py BLOCK on untrained exits 1
16. eval.py stdout for negative contains BLOCK or fail
17. MLflow directory exists
18. MLflow has at least one run directory
19. Total time < 30s (track timing)
20. All seeds set (just check our own seeding happened)
21. Trained beats baseline by >=5pp (parse from stdout)

That's plenty. Let me code this up properly.

Actually, parsing exact numbers from stdout is brittle. I'll keep assertions that don't depend on exact text. But some text-based assertions are necessary to verify behavior.

Let me also think about timing. The smoke test should run in < 30s on CPU. Training 5 epochs on 50 samples should be very fast (~5s). Eval is fast. So total ~10-15s, well within budget.

Let me write the final version:

```python
"""smoke.py — End-to-end smoke test for Module 6 artifact."""
from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import torch

# Reproducibility before anything else.
torch.manual_seed(42)
random.seed(42)
os.environ.setdefault("PYTHONHASHSEED", "42")

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
TIME_BUDGET_S = 30.0

# 5 classes with strong lexical signal so a tiny classifier learns fast on CPU.
_TEMPLATES: dict[str, list[str]] = {
    "positive": [
        "this is great and i love it",
        "amazing work really wonderful",
        "i am so happy with this",
        "fantastic experience would recommend",
        "good quality and well made",
    ],
    "negative": [
        "this is terrible and awful",
        "i hate this so much",
        "worst experience ever do not buy",
        "broken and useless really bad",
        "disappointing quality very poor",
    ],
    "neutral": [
        "it is okay nothing special",
        "average product works fine",
        "received the item as described",
        "neutral opinion no strong feeling",
        "standard and unremarkable overall",
    ],
    "tech": [
        "new software update released today",
        "the code runs on the server",
        "computer hardware is fast",
        "programming language feature added",
        "data pipeline processes records",
    ],
    "sports": [
        "the team won the game",
        "player scored in final match",
        "championship victory for club",
        "athlete broke the record",
        "season opener starts tonight",
    ],
}
LABELS = sorted(_TEMPLATES.keys())


def make_fixture(path: Path, n_per_class: int, seed: int) -> int:
    rng = random.Random(seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for idx, label in enumerate(LABELS):
            templates = _TEMPLATES[label]
            for i in range(n_per_class):
                base = templates[i % len(templates)]
                words = base.split()
                rng.shuffle(words)
                text = " ".join(words)
                f.write('{"text": "%s", "label": "%s", "label_idx": %d}\n' % (text, label, idx))
                count += 1
    return count


def run(cmd: list[str], timeout: float = 60.0) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def assert_check(name: str, cond: bool, detail: str, results: list[tuple[str, bool, str]]) -> None:
    results.append((name, bool(cond), detail))


def main() -> int:
    t0 = time.monotonic()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="m6_smoke_"))
    results: list[tuple[str, bool, str]] = []

    try:
        train_fixture = tmp / "train_50.jsonl"
        test_fixture = tmp / "test_20.jsonl"
        trained_ckpt = OUTPUTS / "smoke_model.pt"
        untrained_ckpt = OUTPUTS / "smoke_model_untrained.pt"

        # 1. Fixtures
        n_train = make_fixture(train_fixture, n_per_class=10, seed=42)
        n_test