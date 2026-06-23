# Deduplication and Leakage

A validation number computed on data the model already saw is not a number; it is a
rumor. Module 2's early-stopping policy trusts `valid_loss` to tell the truth about
what the model has learned. If a training example leaked into the validation set, that
truth is corrupted before the first epoch completes.

This lesson is about two defects that corrupt it: duplicate examples that bloat the
apparent dataset without adding information, and cross-split leakage that makes the
model's validation performance look better than it is. Both are preventable at curation
time, with a content hash and six lines of stdlib code.

## Exact Deduplication by Content Hash

A duplicate is not a repeated topic; it is a repeated example. Two chat examples that
ask about gravity in slightly different words are distinct. Two examples whose messages
are byte-for-byte identical in content are the same signal delivered twice, and the
second copy earns nothing.

The detection method is a content hash: normalize each message (lowercase the role,
strip whitespace from the content), concatenate the result, and SHA-256 the bytes. Two
examples with the same hash are, for training purposes, the same example. The first
one stays; every subsequent copy is dropped.

`curate.py` implements this pass verbatim:

```python
h = _example_hash(msgs)
if h in seen_hashes:
    deduped += 1
    continue
seen_hashes[h] = len(valid_examples)
valid_examples.append(raw)
```

The `_example_hash` function normalizes and hashes in one pass, so the dedup loop
holds no decoded objects, only strings and a dict. Stdlib `hashlib.sha256`, no
dependencies.

This is the same principle as `made-with-ml`'s
`expect_compound_columns_to_be_unique(["title", "description"])`: a compound-uniqueness
constraint that no example should repeat across the key columns. Here the "columns" are
the message contents, and the constraint is implemented as a stdlib content hash rather
than a Great Expectations assertion. Same invariant, zero new dependencies.

`check_dataset.py` enforces the same constraint as a gate. Its `validate` function
maintains a `seen_hashes` dict across every line of a JSONL file:

```
[FAIL] BAD exact duplicate
    - line 3: duplicate (matches line 1)
```

An exact copy on any line fails with a named reason and an exit code of 1. The gate
catches post-curation regressions; the dedup pass in `curate.py` prevents them from
forming in the first place.

## Leakage: The Silent Metric Inflation

Deduplication within a file is not enough. The subtler defect is cross-split leakage:
the same example, or a trivially paraphrased version, appearing in both `train.jsonl`
and `val.jsonl`.

When a model is evaluated on an example it trained on, the validation loss for that
example reflects memorization, not generalization. With enough shared examples, the
aggregate `valid_loss` metric M2 reads to decide early stopping becomes optimistic.
The training run stops at the right epoch relative to a corrupted baseline, the shipped
checkpoint is promoted, and the production model underperforms. The data defect is
invisible inside the training logs.

The gate is `check_dataset.py --check-leak`:

```
python check_dataset.py --check-leak train.jsonl val.jsonl
```

It hashes every valid example in both files and checks the intersection. If any hash
appears in both, the gate fails:

```
[FAIL] BAD train/val leak
    - leak: 1 example(s) appear in both .../train_leak.jsonl and .../val_leak.jsonl
```

A clean split returns no output and exits 0. The selftest confirms both failure and
success cases against known inputs, so the gate itself is verifiable:

```
[PASS] GOOD no train/val leak
```

## Held-Out Design: The Seeded Split

The split that avoids leakage is `curate.py`'s seeded random split. Chat examples are
unlabeled, so stratified splitting by label (the labeled-data analogue in
`made-with-ml`'s `stratify_split(test_size=0.2, seed=...)`) does not apply. A seeded
shuffle achieves the same property that matters: reproducibility. Given the same seed,
the same raw corpus produces the same train and val sets every time.

The mechanism:

```python
rng = random.Random(seed)
rng.shuffle(valid_examples)

val_size = math.ceil(n * val_frac)
train_examples = valid_examples[: n - val_size]
val_examples   = valid_examples[n - val_size :]
```

The `manifest.json` records the seed and fraction alongside the counts:

```json
{
  "raw_count": 7,
  "dropped": 1,
  "deduped": 1,
  "valid_unique": 5,
  "train_count": 4,
  "val_count": 1,
  "seed": 42,
  "val_frac": 0.2,
  "train_path": "...",
  "val_path": "..."
}
```

`seed: 42`, `val_frac: 0.2`, the exact counts. Anyone who can read the manifest can
reproduce the split from the raw corpus, audit which examples landed where, and verify
that the `val_count` matches `ceil(5 * 0.2) = 1`. Reproducibility is not a nicety here:
if the split changes between curation runs, the leak gate could pass one day and fail
the next on identical data.

## The Cleaner Feeds the Gate

The design is two-stage by intent. `curate.py` is the cleaner: it drops invalid lines,
removes duplicates, shuffles with a seed, and writes the split files. `check_dataset.py`
is the gate: it validates each file independently, then checks the cross-split hash
intersection. Neither step substitutes for the other.

The selftest for `curate.py` confirms the pipeline end-to-end. Seven raw lines in (5
valid, 1 invalid JSON, 1 exact duplicate of line A), five unique examples out, split
4/1, and `check_dataset.check_leak` passes the output:

```
[PASS] duplicate removed (valid_unique=5)
[PASS] invalid line dropped (dropped=1)
[PASS] dedup count correct (deduped=1)
[PASS] split sizes correct (train=4, val=1)
[PASS] check_dataset.validate passes train.jsonl
[PASS] check_dataset.validate passes val.jsonl
[PASS] check_dataset.check_leak finds no leak
```

The cleaner's selftest calls the gate as its final assertion. A curate run that does
not pass the leak check has not finished.

Skip this lesson and Module 2's `valid_loss` curve becomes a mirror that shows the
model its own training data and calls it validation. The metric looks good. The model is not.

## Core Concepts

- Exact deduplication hashes the normalized message contents with SHA-256; two examples
  with the same hash are the same training signal, and the second copy is dropped before
  the split runs.
- The `made-with-ml` compound-uniqueness constraint (`expect_compound_columns_to_be_unique`)
  is the same invariant, reimplemented in stdlib: no example should repeat across its key
  content fields.
- Cross-split leakage inflates `valid_loss` by letting the model evaluate on examples it
  trained on; the validation signal M2 trusts to stop training early becomes optimistic.
- The leak gate is `check_dataset.py --check-leak train.jsonl val.jsonl`; it hashes every
  valid example in both files and fails on any intersection, with a named reason and exit 1.
- A seeded random split is the unlabeled-data analogue of a stratified split: the seed
  makes the split reproducible, the manifest records it, and anyone with the raw corpus and
  the manifest can reconstruct the exact train/val partition.
- The cleaner (`curate.py`) and the gate (`check_dataset.py`) are distinct by design:
  the cleaner builds the split, the gate verifies it, and the cleaner's selftest calls the
  gate as its final assertion.

<div class="claude-handoff" data-exercise="exercises/module3/deduplication-and-leakage/">

**Build It in Claude Code**: Start from a small raw JSONL file of ten chat examples, then deliberately plant one exact duplicate (copy a line verbatim) and one cross-split leak (add the same line to both the train and val files after splitting). Run `python curate.py raw.jsonl out/ --seed 42 --val-frac 0.2` to deduplicate and split the raw file; inspect `manifest.json` and confirm the `deduped` count is 1. Then run `python check_dataset.py --check-leak out/train.jsonl out/val.jsonl` and confirm it exits 0, meaning the seeded split introduced no leak. Finally, introduce a manual leak by copying one line from `train.jsonl` into `val.jsonl` and re-run the gate to confirm it catches the overlap with a named failure and exit code 1.

</div>
