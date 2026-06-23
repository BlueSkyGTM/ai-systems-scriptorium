# Exercise: Deduplication and Leakage

## Goal

Plant an exact duplicate and a cross-split leak in a raw JSONL file. Run `curate.py` to remove
them and produce clean splits. Run `check_dataset.py --check-leak` across the splits and confirm
it passes.

## Why

Two failures corrupt a fine-tune dataset without throwing an error: exact duplicates, and
leakage. An exact duplicate trains the model to weight one pattern disproportionately. Cross-
split leakage means a training example appears in the validation set; the validation loss M2
depends on will look better than it is, and you will not know until the model underperforms in
production. Neither failure is visible to the eye in a file of hundreds of lines. Both are
detectable by a hash. This exercise makes you plant both failures deliberately, then confirm
the tooling catches and removes them.

## What You Are Building

A raw JSONL file with known problems, and the clean splits that prove `curate.py` fixed them.

## Steps

1. Create `exercises/module3/deduplication-and-leakage/raw.jsonl` with at least 12 examples.
   Include two deliberate problems:

   - **An exact duplicate**: repeat one example verbatim on a second line.
   - **A cross-split leak**: add a second copy of a different example at the end of the file.
     Because `curate.py` will deduplicate before splitting, the simplest way to simulate leakage
     for this exercise is to note which example you intend to appear in both splits, then verify
     after the split that it was deduplicated and therefore cannot leak. A true post-split leak
     is what `--check-leak` is designed to catch; you will plant it in step 4.

2. Run `curate.py` on the raw file:

   ```
   python exercises/spine/curate.py raw.jsonl out/ --seed 0
   ```

   This writes `out/train.jsonl`, `out/val.jsonl`, and `out/manifest.json`. Read the manifest.
   Confirm `deduped` is at least 1 (the planted duplicate was removed).

3. Run `check_dataset.py` on each output:

   ```
   python exercises/spine/check_dataset.py out/train.jsonl
   python exercises/spine/check_dataset.py out/val.jsonl
   ```

   Both must exit 0.

4. Now plant a real cross-split leak. Create `out/val_with_leak.jsonl` by copying `out/val.jsonl`
   and appending one line from `out/train.jsonl` verbatim. Then run:

   ```
   python exercises/spine/check_dataset.py --check-leak out/train.jsonl out/val_with_leak.jsonl
   ```

   Confirm the output names the leak failure. Then delete `out/val_with_leak.jsonl`.

5. Run the leakage gate on the clean splits:

   ```
   python exercises/spine/check_dataset.py --check-leak out/train.jsonl out/val.jsonl
   ```

   It must exit 0.

## Done When

All of the following are true:

- `out/manifest.json` shows `deduped` >= 1 and `dropped` >= 0.
- `check_dataset.py out/train.jsonl` exits 0.
- `check_dataset.py out/val.jsonl` exits 0.
- `check_dataset.py --check-leak out/train.jsonl out/val.jsonl` exits 0.
- `check_dataset.py --check-leak out/train.jsonl out/val_with_leak.jsonl` exits 1 with a
  named `leak` failure (before you delete the leak file).

## Estimated Time

35 to 50 minutes.

## Stretch

Open `out/manifest.json` and verify the `seed` field matches what you passed to `curate.py`.
Run `curate.py` again with `--seed 99` and confirm the split sizes are the same but the
assignment of examples to train vs. val changes. Write one sentence explaining why recording
the seed in the manifest matters for reproducing a training run later.
