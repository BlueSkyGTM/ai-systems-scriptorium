# Exercise: Training the Classifier

## Goal

Write `train.py` so it trains the classifier deterministically and saves a
self-contained checkpoint that `eval.py` can load without re-parsing the training data.

## Why

A checkpoint that carries only weights forces every consumer to guess the architecture,
the vocab, and the baseline. A checkpoint that carries its own metadata is a contract.
Fixing the seed before any RNG call is what makes the run reproducible on another machine.

## What You Are Building

A `train.py` with a `train_model()` function that builds the vocab, trains an
embedding-plus-mean-pool MLP, and writes `outputs/checkpoint.pt` plus the
`train.jsonl` and `test.jsonl` fixtures.

## Steps

1. Pin the seed at the top of the file, before any randomness:

   ```python
   SEED = 42
   os.environ.setdefault("PYTHONHASHSEED", str(SEED))
   random.seed(SEED)
   torch.manual_seed(SEED)
   ```

2. Generate the training set at `SEED` and the held-out test set at `SEED + 1000` so the
   two never overlap.

3. Build the vocab from the training tokens only. Reserve ids 0 and 1 for `<pad>` and `<unk>`.

4. Train the `TextClassifier` (embedding, masked mean-pool, two linear layers) with Adam
   and cross-entropy for a fixed number of epochs.

5. Save the checkpoint with all five keys: `state_dict`, `vocab`, `class_names`,
   `config`, and `train_majority_class`. Write `train.jsonl` and `test.jsonl`.

6. Confirm training accuracy is high (at least 0.80) on the synthetic set, so the gate has
   real signal to grade.
