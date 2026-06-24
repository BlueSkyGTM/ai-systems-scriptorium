# Module 6: Artifact: Tuned Classifier with Eval Gate

> The first piece in your portfolio. A fine-tuned text classifier that **proves** it beats its baseline, behind a gate that fails loudly when it doesn't.

---

## The Business Problem

Every ML interview ends the same way: *"Show me something you shipped."*

Notebooks don't count. Leaderboards don't count. What counts is a self-contained artifact that:

1. Trains a model from data.
2. Evaluates it against a sensible baseline.
3. **Refuses to ship** if it doesn't clear the bar.
4. Leaves an auditable trail (metrics, params).

This module produces exactly that. The domain is deliberately small: 5-class support-ticket routing (`billing`, `bug`, `feature`, `praise`, `security`) on synthetic data, so the whole loop runs on a laptop CPU in seconds. The discipline is the same one you would apply to a 7B-parameter fine-tune:

> **No model leaves the door without beating its baseline by a margin you pre-committed to.**

---

## What's in the Box

```
module6-classifier/
├── train.py                  # Fine-tune a tiny text classifier -> outputs/checkpoint.pt
├── eval.py                   # Gated eval: tuned vs. majority-class baseline
├── smoke.py                  # End-to-end smoke test (incl. negative case)
├── tests/
│   └── test_classifier.py    # pytest subset of the smoke assertions
├── outputs/                  # checkpoint.pt, train.jsonl, test.jsonl, mlruns.db
│   └── skill-classifier.md   # Portfolio write-up stub
└── README.md                 # This file
```

**Stack:** Python 3.11+, PyTorch, MLflow (optional, offline sqlite). No HuggingFace, no GPU required.

---

## One-Command Run

```bash
python smoke.py
```

That single command:

1. Trains the classifier on a 300-sample fixture.
2. Evaluates the trained checkpoint against the majority-class baseline on the 120-sample held-out fixture.
3. Verifies the gate **passes** (model beats baseline by at least 5pp on both accuracy and macro-F1).
4. Re-runs eval against an **untrained** model and verifies the gate **blocks** (exit code 1).
5. Exits `0` only if every assertion, including the negative case, holds.

Expected wall-clock: a few seconds on CPU.

---

## The Eval Gate

`eval.py` implements a binary ship/no-ship decision:

| Outcome | Condition | Exit Code |
|---------|-----------|-----------|
| **PASS** | Tuned model beats majority-class baseline by at least 5pp on *both* exact-match accuracy **and** macro-F1 | `0` |
| **BLOCK** | Otherwise | `1` |

Both metrics must clear the bar. A model that gains accuracy by collapsing into the majority class will lose macro-F1, and the gate will catch it.

The majority-class baseline is stored in the checkpoint as `train_majority_class`, so the gate reconstructs it without re-parsing the training data. Metrics are logged to MLflow (optional, offline sqlite backend); pass `--no-mlflow` to skip logging.

---

## Running the Pieces

### Train

```bash
python train.py --n-train 600 --n-test 200 --epochs 25
```

Saves a self-contained checkpoint to `outputs/checkpoint.pt` and writes `outputs/train.jsonl` + `outputs/test.jsonl`.

### Evaluate (the gate)

```bash
python eval.py --checkpoint outputs/checkpoint.pt --test outputs/test.jsonl
echo $?   # 0 = PASS, 1 = BLOCK
```

### Test

```bash
python -m pytest tests/ -q
```

---

## Reproducibility

All randomness is pinned in `train.py`:

```python
SEED = 42
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
random.seed(SEED)
torch.manual_seed(SEED)
```

Same seed, same data, same checkpoint, on any machine. The held-out test set uses a disjoint seed (`SEED + 1000`), so it never overlaps with training.

---

## Why This Belongs in Your Portfolio

Recruiters and hiring managers skim. They want to see, in 60 seconds:

- **A training loop** you wrote, not imported from `transformers`.
- **A baseline** you chose and justified: majority-class, the cheapest non-trivial comparator.
- **A gate** with a pre-committed threshold, not a post-hoc rationalization.
- **A negative case** you test: the gate *must* block an untrained model.

That's the whole pitch. The rest is details, which is what `outputs/skill-classifier.md` is for: a write-up stub you flesh out and link from your resume.

---

## Module Context

This is **Module 6** of *Weights and Measures*. It applies the pieces built in M1 through M5: the PyTorch training loop, train/val discipline, the JSONL dataset contract, checkpointing, and the eval gate. M6 is where those become **one shippable thing**.

---

## Requirements

```bash
pip install torch
pip install mlflow   # optional, for the metrics trail
```

Python 3.11+. CPU-only. No CUDA, no HuggingFace.

---

## License

MIT. This is your artifact. Put your name on it.
