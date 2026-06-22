# Groupby, Merge, and Apply

Your model ran overnight. You have a predictions frame and a labels frame sitting in two separate CSVs, and the question you need to answer is: how accurate was it per class? That question has three steps: join the frames, split by class, and reduce to a number. Pandas has a primitive for each step.

## The Artifact

You build `score_pipeline.py`: a script that merges a predictions frame to a labels frame by example id, groups the merged result by class to compute per-class counts and accuracy, and contrasts `apply` with its vectorized equivalent so you can see the difference in one run.

## Split-Apply-Combine

The mental model behind `groupby` is three moves: split the frame into groups by a key, apply a function to each group independently, then combine the results back into a single frame. Pandas does the split and combine automatically; you supply only the apply step.

Start with a merged frame where each row is one prediction (you build the merge in the next section; here, focus on the grouping):

```python
import pandas as pd

# After merging predictions to labels on 'id' (next section)
# merged has columns: id, class_label, correct (1 or 0)
per_class = (
    merged
    .groupby("class_label")
    .agg(
        count=pd.NamedAgg(column="correct", aggfunc="count"),
        accuracy=pd.NamedAgg(column="correct", aggfunc="mean"),
    )
)
print(per_class)
```

Named aggregations keep the output column names explicit. The alternative (`grouped["correct"].agg(["count", "mean"])`) works but names the columns after the function strings, which is harder to read downstream. Named aggregation is the form that survives code review. Microsoft Learn's "Explore and Analyze Data with Python" module groups and aggregates DataFrame data this way ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

`groupby` does not execute until you call the aggregation. The `grouped` object is lazy: it holds the split plan, not the split result. Calling `.agg(...)` materializes it.

## Merge: Joining Predictions to Labels

You rarely receive predictions and ground truth in the same frame. Scoring starts with a join.

```python
import numpy as np

rng = np.random.default_rng(42)
n = 20
classes = ["cat", "dog", "bird"]

labels_df = pd.DataFrame({
    "id":          range(n),
    "class_label": rng.choice(classes, n),
    "true_label":  rng.integers(0, 2, n),
})

preds_df = pd.DataFrame({
    "id":         range(n - 2),       # two predictions missing on purpose
    "pred_label": rng.integers(0, 2, n - 2),
})

merged = pd.merge(preds_df, labels_df, on="id", how="inner")
print(f"labels: {len(labels_df)}, preds: {len(preds_df)}, merged: {len(merged)}")
# labels: 20, preds: 18, merged: 18
```

`how="inner"` keeps only rows where the id appears in both frames. Two labels dropped because no prediction matched. That is not a bug; it is the join telling you your prediction run was incomplete.

Now build the `correct` column and group:

```python
merged["correct"] = (merged["pred_label"] == merged["true_label"]).astype(int)

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

`how="left"` would keep all predictions even when no label exists, filling the label columns with `NaN`. That leaks phantom rows into your metrics: `mean()` on a column with `NaN` silently skips them, but `count()` counts non-null values only, so the two aggregations would count different rows. An unchecked `left` join is a silent accuracy inflation. Inner join, then check `len(merged)` against `len(preds_df)`: that gap is the real signal.

## apply: The Escape Hatch You Reach For Last

Module 2 taught that `df.apply(func, axis=1)` is a disguised per-row Python loop. Pandas calls your function once per row, passing a `Series`; it never vectorizes across the batch. The column operation is always preferred when one exists.

Here is the pattern to recognize and replace:

```python
# Slow: apply is a Python loop over rows
merged["correct_apply"] = merged.apply(
    lambda row: int(row["pred_label"] == row["true_label"]),
    axis=1,
)

# Fast: vectorized column comparison
merged["correct_vec"] = (merged["pred_label"] == merged["true_label"]).astype(int)

assert (merged["correct_apply"] == merged["correct_vec"]).all(), \
    "apply and vectorized must agree"
print("Both methods agree:", merged[["correct_apply", "correct_vec"]].head())
```

Both produce identical results. The vectorized version runs as one pandas operation across the entire column; the `apply` version calls Python once per row. At 20 rows the difference is noise. At two million rows it is the reason a batch scoring job times out.

`apply` earns its place only when the logic requires data from multiple rows of the same group, or when you need an external library that has no vectorized pandas equivalent. For a two-column comparison, reach for the column expression first.

## Per-Class Precision Starts Here

The `groupby` above is the first step in computing per-class precision, recall, and F1. Made-with-ml's `data.py` does a stratified split on the label column before training, a groupby-shaped operation that ensures each class appears in both train and validation sets at the right ratio. The same idea scales up: any metric you want to slice by class, by time window, or by data source is a `groupby` followed by an `agg`. The merge that precedes it is the seam where predictions meet ground truth, and the NaN count after that merge is where your data quality lives.

A scoring pipeline that skips the merge sanity check is guessing at its own denominator.

## Core Concepts

- `groupby(col).agg(name=pd.NamedAgg(column=..., aggfunc=...))` splits a frame by key, applies an aggregation to each group, and returns a frame with explicit output column names; named aggregation is the production form.
- `pd.merge(..., how="inner")` keeps only rows matched on both sides; `how="left"` preserves unmatched left rows as `NaN`, which silently corrupts per-class metrics if you do not check the row count after the join.
- `df.apply(func, axis=1)` is a per-row Python loop; replace it with a vectorized column expression whenever the logic touches only values in the same row.
- Per-class accuracy starts with a merge of predictions to labels on a shared key, then a `groupby` on the class column.

<div class="claude-handoff" data-exercise="exercises/module3/groupby-merge-apply/">

**Build It in Claude Code:** Build `score_pipeline.py`, a script that merges a predictions frame to a labels frame, groups by class to compute per-class accuracy, and asserts that `apply` and a vectorized column expression produce identical results.

</div>
