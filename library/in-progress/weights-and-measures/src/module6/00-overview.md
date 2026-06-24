# Module 6: Artifact: Tuned Classifier with Eval Gate

Loss curves describe training; only the held-out gate decides if you ship. Module 6 is where the training loop from M1 through M4 and the eval gate from M5 fuse into a single GitHub-postable artifact that proves a tuned model is actually better.

## What This Module Covers

You build `module6-classifier/`, a self-contained project that trains a tiny 5-class text classifier, evaluates it against a majority-class baseline, and refuses to ship unless it wins by a margin you pre-committed to.

Six files do the work.

`train.py` fine-tunes a mean-pooled embedding model on synthetic JSONL and writes `outputs/checkpoint.pt`. Pure PyTorch, no HuggingFace, CPU in under 60 seconds.

`eval.py` loads that checkpoint plus a held-out test set, then exits zero only if the tuned model beats baseline by at least 5 percentage points on both exact-match accuracy and macro-F1. Otherwise the gate blocks with exit 1.

`smoke.py` runs the full loop on a 50-sample fixture, asserts the positive case passes, and asserts the negative case (an untrained model) blocks. Target under 30 seconds on CPU.

`tests/test_classifier.py` is the pytest subset of those smoke assertions.

`README.md` is the front door for any reviewer who clones the repo.

`outputs/skill-classifier.md` is the portfolio write-up: problem statement, approach, results, and the auditable trail that backs every claim.

## The Artifact

`module6-classifier/` imports nothing from M1 through M5. It applies every principle from them.

The training script fixes seeds before the first RNG call so eval's held-out test set is deterministic and disjoint from training:

```python
SEED = 42
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
random.seed(SEED)
torch.manual_seed(SEED)
```

The checkpoint it writes is a contract. The `state_dict`, `vocab`, `class_names`, `config`, and `train_majority_class` travel together so `eval.py` never re-parses training data.

The gate logs to MLflow with an offline sqlite backend, leaving a reviewer-readable trail. The README frames the discipline in one line:

> No model leaves the door without beating its baseline by a margin you pre-committed to.

## Who This Is For

You finished M5 and shipped an eval gate. Now you ship the first real artifact: something a hiring manager can clone, run, and verify in under a minute.

## Prerequisites

Modules 1 through 5 complete. Python 3.11 or newer. PyTorch installed; CPU is enough. `scikit-learn` optional if you want a stronger baseline.

## Time Estimate

60 to 90 minutes per lesson.

## Core Concepts

- A loss curve reports training progress; only held-out evaluation against a baseline reports shipping readiness.
- The eval gate exits zero only if the tuned model beats baseline by at least 5 percentage points on both exact-match accuracy and macro-F1.
- A checkpoint is a contract: it carries the `state_dict`, `vocab`, `class_names`, `config`, and `train_majority_class` so eval never re-parses training data.
- The artifact imports nothing from earlier modules but applies every principle from them: fixed seeds, disjoint test split, pre-committed margin, auditable trail.

A Production AI Engineer ships nothing a reviewer cannot re-run blind and reach the same verdict.