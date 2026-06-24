# Exercise: The Eval Gate

## Goal

Write `eval.py` so its exit code is the deliverable: 0 when the tuned model beats the
majority-class baseline by at least 5 percentage points on both metrics, 1 otherwise.

## Why

Every model looks fine in training. The gate is the first honest opinion. A gate that
cannot fail is decoration; the exit code is what a CI pipeline reads to decide whether
anything downstream runs.

## What You Are Building

An `eval.py` that imports the model from `train.py`, scores the tuned model and the
majority-class baseline on exact-match accuracy and macro-F1, and exits 0 (PASS) or 1
(BLOCK).

## Steps

1. Import the architecture and tokenizer from `train.py` so the two scripts can never
   drift on the model definition:

   ```python
   from train import CLASS_NAMES, MAX_LEN, NUM_CLASSES, TextClassifier, Vocab
   ```

2. Load the checkpoint, rebuild the model from `config`, and load the `state_dict`.

3. Read the held-out `test.jsonl`. Score the tuned model's predictions.

4. Reconstruct the baseline from `train_majority_class`: predict that class for every
   input. Score it on the same test set.

5. Compute both margins. The gate passes only if `tuned >= baseline + 0.05` on **both**
   exact-match accuracy and macro-F1. Return 0 on PASS, 1 on BLOCK.

6. Make MLflow logging optional (guard the import) and add a `--no-mlflow` flag so the
   gate runs with or without MLflow installed.

7. Verify by hand: `python eval.py` then `echo $?`. A trained checkpoint should print 0.
