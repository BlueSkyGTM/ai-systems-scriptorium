# Exercise: Groupby, Merge, and Apply

**Goal:** Build `score_pipeline.py`, a script that merges a predictions frame to a labels frame by example id, groups the merged result by class to compute per-class count and accuracy, and proves that `apply` and a vectorized column expression produce identical results.

**Why:** Per-class metrics are the first thing a reviewer asks for after a model run. Knowing how to merge, group, and aggregate in one clean pipeline, and knowing when `apply` is costing you, is the practical foundation of every scoring workflow.

## Steps

1. Build two deterministic frames with a fixed seed:

   ```python
   import pandas as pd
   import numpy as np

   rng = np.random.default_rng(42)
   n = 30
   classes = ["cat", "dog", "bird"]

   labels_df = pd.DataFrame({
       "id":          range(n),
       "class_label": rng.choice(classes, n),
       "true_label":  rng.integers(0, 2, n),
   })

   preds_df = pd.DataFrame({
       "id":         range(n - 3),          # 3 predictions missing
       "pred_label": rng.integers(0, 2, n - 3),
   })
   ```

2. Merge predictions to labels on `"id"` with an inner join. Print the row counts before and after and assert the merged frame has exactly `n - 3` rows:

   ```python
   merged = pd.merge(preds_df, labels_df, on="id", how="inner")
   assert len(merged) == n - 3, f"expected {n - 3}, got {len(merged)}"
   print(f"labels: {len(labels_df)}, preds: {len(preds_df)}, merged: {len(merged)}")
   ```

3. Add a `correct` column using a vectorized comparison:

   ```python
   merged["correct"] = (merged["pred_label"] == merged["true_label"]).astype(int)
   ```

4. Group by `class_label` and compute per-class count and accuracy with named aggregation:

   ```python
   per_class = (
       merged
       .groupby("class_label")
       .agg(
           count=pd.NamedAgg(column="correct", aggfunc="count"),
           accuracy=pd.NamedAgg(column="correct", aggfunc="mean"),
       )
       .round(3)
   )
   print(per_class)
   ```

5. Add a second column using `apply` and assert it matches the vectorized result:

   ```python
   merged["correct_apply"] = merged.apply(
       lambda row: int(row["pred_label"] == row["true_label"]),
       axis=1,
   )

   assert (merged["correct"] == merged["correct_apply"]).all(), \
       "vectorized and apply results must agree"
   print("[PASS] apply and vectorized column agree")
   ```

6. Print a structured report and exit with code 0:

   ```
   [PASS] merge: 27 rows (30 labels, 27 preds, 3 dropped)
   [PASS] per-class accuracy computed (3 classes)
   [PASS] apply and vectorized column agree
   ```

   (Exact counts depend on the fixed seed; the seed guarantees they are deterministic.)

## Done When

All three assertion groups pass, the structured `[PASS]` report prints, and the script exits with code 0. Run it with:

```sh
python score_pipeline.py
```

No external dependencies beyond pandas and numpy. The fixed seed `np.random.default_rng(42)` makes every run deterministic.

## Stretch

Swap the frame order and use `how="left"` to keep all 30 label rows, including the three with no matching prediction. The `pred_label` column for those three rows will be `NaN`, which means your `correct` computation breaks for those rows. Build a `correct_left` column that handles the missing predictions explicitly, then group and assert the total `count` differs from the inner-join result:

```python
merged_left = pd.merge(labels_df, preds_df, on="id", how="left")
assert len(merged_left) == n, f"left join should keep all {n} label rows"

# NaN pred_label must not silently become a match; fill with -1 before comparing
merged_left["correct_left"] = (
    merged_left["pred_label"].fillna(-1).astype(int) == merged_left["true_label"]
).astype(int)

left_per_class = (
    merged_left
    .groupby("class_label")
    .agg(
        count=pd.NamedAgg(column="correct_left", aggfunc="count"),
        accuracy=pd.NamedAgg(column="correct_left", aggfunc="mean"),
    )
    .round(3)
)
print(left_per_class)

# The total count in the left join is n (30); the inner join counted n-3 (27)
assert left_per_class["count"].sum() == n, "left join count should be n"
assert per_class["count"].sum() == n - 3, "inner join count should be n-3"
print("[PASS] left join includes all labels; inner join drops unmatched predictions")
```
