# Exercise: Confusion Counts with NumPy

**Goal:** Add `confusion_counts` to the shared `exercises/module7/eval_engine.py`. Load the
sample predictions and assert the per-class TP/FP/FN counts for all three classes. Print
the counts and exit with code 0.

**Why:** Precision, recall, and F1 are all derived from these three numbers. If you can
compute them by hand in NumPy, you own the metric. If you can only call `f1_score`, you
own the output.

## Setup

L1 created `exercises/module7/eval_engine.py` with `EvalConfig` and `load_predictions`, and
`exercises/module7/predictions.csv` with 10 rows. Open `eval_engine.py` and read its current
state before adding anything. You are continuing a build, not starting one.

The locked `EvalConfig` looks like this:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class EvalConfig:
    input_path: str
    output_path: str
    pred_col: str = "prediction"
    label_col: str = "label"
```

The `predictions.csv` has two columns: `prediction` and `label`. Ten rows, three classes:
`cat`, `dog`, `bird`.

## Steps

1. **Read `eval_engine.py` first.** Print its current state in your head. Locate `EvalConfig`
   and `load_predictions`. Understand what `load_predictions` returns before you add anything.

2. **Add `confusion_counts` to `eval_engine.py`.** The function signature is fixed:

   ```python
   def confusion_counts(df: pd.DataFrame, cls: str, config: EvalConfig) -> tuple[int, int, int]:
       # your implementation here
       ...
   ```

   Inside:
   - Pull `pred` and `label` as NumPy arrays from `df[config.pred_col]` and `df[config.label_col]`.
   - Build `predicted_pos = (pred == cls)` and `actual_pos = (label == cls)`.
   - Compute `tp`, `fp`, `fn` using `&` and `~` on those masks. Wrap each sub-condition in
     parentheses (operator precedence, covered in M2).
   - Return `(int(tp), int(fp), int(fn))`.

   No sklearn. No loop over rows.

3. **Run the pipeline and assert correctness.**

   ```python
   import pandas as pd
   from eval_engine import EvalConfig, load_predictions, confusion_counts

   config = EvalConfig(
       input_path="exercises/module7/predictions.csv",
       output_path="exercises/module7/outputs/",
   )

   df = load_predictions(config.input_path, config)

   cat_counts  = confusion_counts(df, "cat",  config)
   dog_counts  = confusion_counts(df, "dog",  config)
   bird_counts = confusion_counts(df, "bird", config)

   print(f"cat  -> tp={cat_counts[0]}, fp={cat_counts[1]}, fn={cat_counts[2]}")
   print(f"dog  -> tp={dog_counts[0]}, fp={dog_counts[1]}, fn={dog_counts[2]}")
   print(f"bird -> tp={bird_counts[0]}, fp={bird_counts[1]}, fn={bird_counts[2]}")

   assert cat_counts  == (3, 1, 1), f"cat:  expected (3,1,1) got {cat_counts}"
   assert dog_counts  == (2, 1, 2), f"dog:  expected (2,1,2) got {dog_counts}"
   assert bird_counts == (2, 1, 0), f"bird: expected (2,1,0) got {bird_counts}"

   print("[PASS] cat  (3, 1, 1)")
   print("[PASS] dog  (2, 1, 2)")
   print("[PASS] bird (2, 1, 0)")
   ```

## Done When

All three assertions pass, the `[PASS]` lines print, and the script exits with code 0. Run it with:

```sh
python exercises/module7/confusion-counts-with-numpy/smoke.py
```

No dependencies beyond pandas and numpy.

## Stretch

The three classes share 10 rows. Verify two invariants that hold for any exhaustive label set:

1. **Every row contributes exactly once to either TP, FP, or FN for the class it was predicted
   as.** Sum TP + FP across all three classes and confirm the total equals the number of rows (10).

2. **Every ground-truth positive row is counted as either TP or FN.** For each class, confirm
   `tp + fn` equals the number of rows where `label == cls`.

```python
classes = ["cat", "dog", "bird"]
counts = {cls: confusion_counts(df, cls, config) for cls in classes}

total_tp_fp = sum(tp + fp for tp, fp, fn in counts.values())
assert total_tp_fp == len(df), f"TP+FP should sum to row count, got {total_tp_fp}"

for cls, (tp, fp, fn) in counts.items():
    actual_positives = int((df[config.label_col] == cls).sum())
    assert tp + fn == actual_positives, (
        f"{cls}: tp+fn={tp+fn} but actual positives={actual_positives}"
    )

print("[PASS] TP+FP sums to row count across all classes")
print("[PASS] TP+FN equals ground-truth positives for each class")
```

These two checks confirm `confusion_counts` is correct by structure, not just by matching a
hard-coded expected value.
