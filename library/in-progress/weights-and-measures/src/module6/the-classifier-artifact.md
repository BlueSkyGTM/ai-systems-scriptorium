# The Classifier Artifact

A checkpoint is not an artifact. A checkpoint with a gate that proves it beats the baseline is.

Three scripts, one hierarchy. `eval.py` owns the PASS/BLOCK decision. `train.py` exists to produce a checkpoint `eval.py` can grade. `smoke.py` exists to prove both paths work. Nothing else ships.

## The Dataset Contract

The data is synthetic 5-class text: `billing`, `bug`, `feature`, `praise`, `security`. Each class carries signal words so a small embedding model can separate them. The format is JSONL, one record per line:

```json
{"text": "...", "label": "..."}
```

The seed is fixed before any RNG use. `train.py` sets `SEED = 42`. `eval.py` consumes a held-out test set seeded at `SEED + 1000`, guaranteeing deterministic, disjoint splits. The checkpoint stores the majority class from training so the baseline is reconstructable without re-parsing the training file.

## The Three Scripts

`train.py` fine-tunes a tiny PyTorch classifier and saves a self-contained checkpoint. The seed block at the top of the file is mandatory:

```python
SEED = 42
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
random.seed(SEED)
torch.manual_seed(SEED)
```

The checkpoint it produces carries everything the evaluator needs:

```python
Checkpoint contract (produced by train.py):
    state_dict, vocab (stoi), class_names, config, train_majority_class
```

`eval.py` loads that checkpoint, runs the tuned model against a majority-class baseline on two metrics, and exits:

```python
The GATE passes (exit code 0) iff the tuned model beats the baseline by
≥ 5 percentage points on BOTH metrics. Otherwise the gate BLOCKS (exit 1).
```

Exit 0 means the model ships. Exit 1 means it stops. No middle ground, no warnings, no "close enough."

`smoke.py` orchestrates the full loop on a 300-sample train fixture and a 120-sample test fixture, running 20 assertions in a few seconds. It asserts the trained model clears the gate (exit 0). Then it asserts the untrained model fails it (exit 1). Both assertions must hold. If a broken model passes or a good model blocks, `smoke.py` fails before your CI pipeline does.

## The README Contract

The README declares the artifact in plain terms:

```
module6-classifier/
├── train.py                  # Fine-tune a tiny text classifier -> outputs/checkpoint.pt
├── eval.py                   # Gated eval: tuned vs. majority-class baseline
├── smoke.py                  # End-to-end smoke test (incl. negative case)
├── tests/
│   └── test_classifier.py    # pytest subset of the smoke assertions
├── outputs/                  # checkpoint.pt, train.jsonl, test.jsonl, mlruns.db
│   └── skill-classifier.md   # portfolio write-up
└── README.md
```

A reviewer clones the repo, runs one command, and watches the loop execute: train, evaluate, gate. The README frames the stakes without apology:

> Notebooks don't count. Leaderboards don't count. What counts is a self-contained artifact that:
> 1. Trains a model from data.
> 2. Evaluates it against a sensible baseline.
> 3. **Refuses to ship** if it doesn't clear the bar.
> 4. Leaves an auditable trail (metrics, params, artifacts).

## Core Concepts

1. `eval.py` owns the only decision that matters: PASS (exit 0) or BLOCK (exit 1). `train.py` and `smoke.py` exist to serve that decision.

2. The gate passes iff the tuned model beats the majority-class baseline by at least 5 percentage points on both exact-match accuracy and macro-F1.

3. The seed split (`SEED = 42` for training, `SEED + 1000` for evaluation) guarantees the held-out test set is deterministic and disjoint from the training set.

4. `smoke.py` must assert both the happy path (trained model clears the gate) and the deficient path (untrained model blocks it). One without the other proves nothing.

<div class="claude-handoff" data-exercise="exercises/module6/the-classifier-artifact/">
**Build It in Claude Code** · Exercise · exercises/module6/the-classifier-artifact/
</div>

Ship a checkpoint without a gate and you ship a file nobody can trust at review time.