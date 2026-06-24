# The Eval Gate

Every model looks fine in training; the gate is the first honest opinion.

The deliverable is not the checkpoint. It is the exit code. When your CI pipeline calls `eval.py`, it reads one thing: zero or one. Zero means the tuned model beat the baseline by the margin you pre-committed to. One means it did not, and nothing downstream runs.

## What The Gate Checks

The gate loads a fine-tuned checkpoint and a held-out JSONL test set, then evaluates the tuned model against a majority-class baseline on two metrics. Here is the contract, verbatim from the top of `eval.py`:

```python
"""eval.py — M6 Eval Gate for the tuned skill classifier.

Loads a fine-tuned checkpoint and a held-out JSONL test set, then evaluates
the tuned model against a majority-class baseline on two metrics:

  * exact-match accuracy
  * macro-F1

The GATE passes (exit code 0) iff the tuned model beats the baseline by
≥ 5 percentage points on BOTH metrics. Otherwise the gate BLOCKS (exit 1).

Logging goes to MLflow with an offline sqlite backend.
"""
```

Both metrics must clear the margin. "Both" does the work. A model that lifts accuracy but collapses on macro-F1 for a minority class gets blocked. That is the design.

## The Majority-Class Baseline

The baseline predicts the most frequent label for every input. No training, no weights, no inference cost. It is the cheapest classifier that exists. If your fine-tuned model cannot beat it by five points on both metrics, you shipped nothing.

The checkpoint carries everything `eval.py` needs to reconstruct that baseline without touching the training data:

```python
Checkpoint contract (produced by train.py):
    {
        "vocab":   Dict[str, int],         # word -> id; must contain <pad>, <unk>
        "label_map": Dict[str, int],       # label string -> id (5 classes)
        "config":  {embed_dim, hidden_dim, max_len, ...},
        "state_dict": OrderedDict,         # TextClassifier weights
    }
```

## MLflow Without A Server

The gate logs metrics, parameters, and artifacts to MLflow using an offline sqlite backend. No server, no network, no infrastructure to stand up. The import is optional and gated so CI does not break when MLflow is absent:

```python
try:
    import mlflow  # optional; gated by --mlflow-off flag for CI
    HAS_MLFLOW = True
except ImportError:  # pragma: no cover
    HAS_MLFLOW = False
```

## Disjoint Seeds

Training and evaluation use separate, deterministic seeds. The held-out test set never overlaps with training data. From the `train.py` design notes:

```python
All randomness is seeded (SEED = 42) so eval.py's held-out test set
(seed = SEED + 1000) is deterministic and disjoint from training.
```

`eval.py` pins its own seeds at module load:

```python
# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
torch.manual_seed(42)
random.seed(42)
```

This is the same gate pattern from Module 5, now pointed at a real model with a real baseline and real consequences.

## Core Concepts

- **Exit code is the deliverable.** `eval.py` returns 0 iff the tuned model beats the majority-class baseline by at least 5 percentage points on both exact-match accuracy and macro-F1. Any other result exits 1.
- **Majority-class baseline.** The cheapest classifier: predict the most frequent label for every input. The checkpoint stores it so `eval.py` never re-parses training data.
- **Offline MLflow.** The sqlite backend logs runs without a server. The import is optional, gated by a flag, so CI works with or without MLflow installed.
- **Disjoint seeds.** Training uses seed 42; the test set uses seed 1042. The split is deterministic and non-overlapping.

<div class="claude-handoff" data-exercise="exercises/module6/the-eval-gate/">
**Build It in Claude Code** · Exercise · exercises/module6/the-eval-gate/
</div>

If your test set leaks or your baseline is too weak, exit 0 becomes the most expensive lie in your pipeline: a gate that blesses a broken model for production.