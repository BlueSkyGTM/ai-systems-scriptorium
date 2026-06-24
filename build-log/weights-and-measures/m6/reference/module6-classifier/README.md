# Module 6 — Artifact: Tuned Classifier with Eval Gate

> The first piece in your portfolio. A fine-tuned text classifier that **proves** it beats its baseline, behind a gate that fails loudly when it doesn't.

---

## The Business Problem

Every ML interview ends the same way: *"Show me something you shipped."*

Notebooks don't count. Leaderboards don't count. What counts is a self-contained artifact that:

1. Trains a model from data.
2. Evaluates it against a sensible baseline.
3. **Refuses to ship** if it doesn't clear the bar.
4. Leaves an auditable trail (metrics, params, artifacts).

This module produces exactly that. The domain is deliberately small — 5-class sentiment/topic classification on synthetic data — so the whole loop runs on a laptop CPU in under a minute. The discipline, however, is the same one you'd apply to a 7B-parameter fine-tune:

> **No model leaves the door without beating its baseline by a margin you pre-committed to.**

---

## What's in the Box

```
m6-artifact/
├── train.py                  # Fine-tune a tiny text classifier → outputs/model.pt
├── eval.py                   # Gated eval: tuned vs. majority-class baseline
├── smoke.py                  # End-to-end smoke test (incl. negative case)
├── tests/
│   └── test_classifier.py    # pytest subset of the smoke assertions
├── data/                     # Synthetic JSONL fixtures (train/val/test)
├── outputs/                  # Checkpoints, MLflow runs, write-up
│   └── skill-classifier.md   # Portfolio write-up stub
└── README.md                 # This file
```

**Stack:** Python 3.11+, PyTorch, scikit-learn (baseline only), MLflow (offline, sqlite). No HuggingFace, no GPU required.

---

## One-Command Run

```bash
python smoke.py
```

That single command:

1. Trains the classifier on a 50-sample fixture.
2. Evaluates the trained checkpoint against the majority-class baseline on a 20-sample fixture.
3. Verifies the gate **passes** (model beats baseline by ≥ 5pp on both accuracy and macro-F1).
4. Re-runs eval against an **untrained** model and verifies the gate **blocks** (exit code 1).
5. Exits `0` only if every assertion — including the negative case — holds.

Expected wall-clock: **< 30 seconds on CPU**.

---

## The Eval Gate

`eval.py` implements a binary ship/no-ship decision:

| Outcome | Condition | Exit Code |
|---------|-----------|-----------|
| **PASS** | Tuned model beats majority-class baseline by ≥ 5pp on *both* exact-match accuracy **and** macro-F1 | `0` |
| **BLOCK** | Otherwise | `1` |

Both metrics must clear the bar. A model that gains accuracy by collapsing into the majority class will lose macro-F1 — and the gate will catch it.

Results are logged to **MLflow** (offline sqlite backend):

```python
mlflow.set_tracking_uri("sqlite:///outputs/mlruns.db")
```

Every run records params, metrics, and the gate verdict. Open it with:

```bash
mlflow ui --backend-store-uri sqlite:///outputs/mlruns.db
```

---

## Running the Pieces

### Train

```bash
python train.py \
    --train data/train.jsonl \
    --val   data/val.jsonl \
    --epochs 8 \
    --output outputs/model.pt
```

Saves a PyTorch checkpoint to `outputs/model.pt`.

### Evaluate (the gate)

```bash
python eval.py \
    --checkpoint outputs/model.pt \
    --test data/test.jsonl \
    --baseline majority
echo $?   # 0 = PASS, 1 = BLOCK
```

### Test

```bash
pytest -q
```

---

## Reproducibility

All randomness is pinned:

```python
torch.manual_seed(42)
random.seed(42)
```

Same seed, same data, same checkpoint — on any machine.

---

## Why This Belongs in Your Portfolio

Recruiters and hiring managers skim. They want to see, in 60 seconds:

- **A training loop** you wrote (not imported from `transformers`).
- **A baseline** you chose and justified (majority-class — the cheapest non-trivial comparator).
- **A gate** with a pre-committed threshold — not a post-hoc rationalization.
- **A negative case** you test: the gate *must* block an untrained model.
- **An artifact trail** (MLflow) that survives a repo re-clone.

That's the whole pitch. The rest is details, which is exactly what `outputs/skill-classifier.md` is for — a write-up stub you'll flesh out and link from your résumé.

---

## Module Context

This is **Module 6** of *Weights and Measures*. It builds directly on:

- **M1** — the PyTorch training loop (`trainer.py` spine).
- **M2** — train/val discipline and early stopping.
- **M3** — the JSONL dataset contract.
- **M4** — checkpointing (LoRA/QLoRA/PEFT in later modules).
- **M5** — the eval gate (`eval_gate.py`: exact-match, token-F1, perplexity, LLM-as-judge mock).

M6 is where those pieces become **one shippable thing**.

---

## Requirements

```bash
pip install torch scikit-learn mlflow
```

Python 3.11+. CPU-only. No CUDA, no HuggingFace, no excuses.

---

## License

MIT — this is your artifact. Put your name on it.