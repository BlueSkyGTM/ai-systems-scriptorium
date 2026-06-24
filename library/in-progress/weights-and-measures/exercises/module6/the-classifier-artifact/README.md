# Exercise: The Classifier Artifact

## Goal

Stand up the `module6-classifier/` skeleton and prove the three-script contract holds:
`train.py` produces a checkpoint, `eval.py` grades it, `smoke.py` orchestrates both.

## Why

An artifact is not a model file; it is a directory whose scripts agree on a contract.
The fastest way to internalize that contract is to build the skeleton and watch one
command drive the whole loop. If the scripts disagree on the checkpoint shape or the
data location, nothing runs.

## What You Are Building

The artifact directory with `train.py`, `eval.py`, `smoke.py`, a `tests/` package, an
`outputs/` directory, and a `README.md`, wired so `python smoke.py` runs end to end.

## Steps

1. Create the directory layout:

   ```
   module6-classifier/
   ├── train.py
   ├── eval.py
   ├── smoke.py
   ├── tests/__init__.py
   ├── tests/test_classifier.py
   ├── outputs/
   └── README.md
   ```

2. Define the synthetic 5-class dataset (`billing`, `bug`, `feature`, `praise`,
   `security`) with per-class signal words, seeded at `SEED = 42`.

3. Confirm the JSONL row contract: each row is `{"text": "...", "label": "<class name>"}`.

4. Write a one-paragraph README that states the one-command run (`python smoke.py`) and
   the PASS/BLOCK exit-code meaning.

5. Run `python smoke.py`. It will fail until the next exercises fill in training and the
   gate; confirm the failure is "not implemented yet," not a structural error.
