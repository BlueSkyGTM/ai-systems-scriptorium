# Confusion Counts with NumPy

The confusion matrix is the foundation of every classification metric, and it is three boolean masks plus a sum. If you have called `sklearn.metrics.f1_score` without ever writing those masks yourself, you are trusting a number you cannot explain in an interview.

## What You Build

You build `confusion_counts`, the stage in `eval_engine.py` that takes a DataFrame and a class name and returns `(tp, fp, fn)` as integers, using NumPy boolean operations and no library metrics.

## The Two Source Arrays

The stage starts by pulling the prediction and label columns from the DataFrame using the config:

```python
pred  = df[config.pred_col].to_numpy()
label = df[config.label_col].to_numpy()
```

From these two arrays, two boolean masks fall out of a single comparison each:

```python
predicted_pos = (pred  == cls)   # True where the model said "cls"
actual_pos    = (label == cls)   # True where the ground truth is "cls"
```

Every count the confusion matrix cares about is built from these two masks combined.

## Three Masks, Three Counts

Module 2 introduced boolean masks and `&` on NumPy arrays. Here you use them on a real metric, not a synthetic score column.

Combine the two source masks to get the three per-class counts:

```python
tp = (predicted_pos  &  actual_pos).sum()    # model said cls AND ground truth is cls
fp = (predicted_pos  & ~actual_pos).sum()    # model said cls BUT ground truth is not cls
fn = (~predicted_pos &  actual_pos).sum()    # model missed cls AND ground truth is cls
```

The parentheses around each condition are not optional. Python's operator precedence ranks `&` above `==`, so without them `pred == cls & label == cls` parses as `pred == (cls & label) == cls`, which is wrong and silent. Wrap every condition; it is a one-time cost the M2 lesson already flagged.

## Convert to int Before Returning

NumPy's `.sum()` on a boolean array returns a NumPy scalar (`numpy.intp`), not a Python `int`. Return plain Python ints so the tuple is portable and prints cleanly:

```python
return (int(tp), int(fp), int(fn))
```

## The Full Stage

```python
def confusion_counts(df: pd.DataFrame, cls: str, config: EvalConfig) -> tuple[int, int, int]:
    pred  = df[config.pred_col].to_numpy()
    label = df[config.label_col].to_numpy()

    predicted_pos = (pred  == cls)
    actual_pos    = (label == cls)

    tp = (predicted_pos  &  actual_pos).sum()
    fp = (predicted_pos  & ~actual_pos).sum()
    fn = (~predicted_pos &  actual_pos).sum()

    return (int(tp), int(fp), int(fn))
```

One function. No loop over rows. No import from sklearn.

## Concrete Example: Class "cat"

The locked sample in `exercises/module7/predictions.csv` has 10 rows. Walk through class "cat":

| row | prediction | label | predicted_pos | actual_pos | TP | FP | FN |
|-----|-----------|-------|--------------|-----------|----|----|-----|
| 0   | cat       | cat   | T | T | 1 | | |
| 1   | dog       | cat   | F | T | | | 1 |
| 2   | cat       | cat   | T | T | 1 | | |
| 3   | bird      | bird  | F | F | | | |
| 4   | cat       | cat   | T | T | 1 | | |
| 5   | dog       | dog   | F | F | | | |
| 6   | cat       | dog   | T | F | | 1 | |
| 7   | bird      | bird  | F | F | | | |
| 8   | dog       | cat   | F | T | | | 1 |
| 9   | bird      | bird  | F | F | | | |

`confusion_counts(df, "cat", config)` returns `(3, 1, 1)`. Three masks, no loop.

Azure AI Language's evaluation-metrics reference defines these three cells in identical terms for per-class evaluation of custom classifiers: the diagonal value is TP, the row sum excluding the diagonal is FP, and the column sum excluding the diagonal is FN ([learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics](https://learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics#confusion-matrix)).

## Where This Fits in eval_engine.py

`confusion_counts` is the data layer for the module's shared artifact. `load_predictions` (L1, given) loads the CSV into a DataFrame. `per_class_metrics` (L3, given) calls `confusion_counts` for each class and derives precision, recall, and F1. `to_markdown_table` (L3, given) formats the result. `run` (L4, given) wires all stages together. You build this one stage; the others assume it works.

The engineer who can write per-class confusion counts from two boolean arrays understands what precision and recall are measuring. The one who only calls `f1_score` is trusting a wrapper to stay correct when the label set changes, the multiclass averaging shifts, or the column names drift.

## Core Concepts

- For one class, TP, FP, and FN are three boolean mask combinations of two source arrays; `.sum()` counts each in a single NumPy pass.
- `predicted_pos & actual_pos` is TP; `predicted_pos & ~actual_pos` is FP; `~predicted_pos & actual_pos` is FN. Parentheses on each sub-condition are required because `&` has higher precedence than `==`.
- NumPy's `.sum()` on a boolean array returns a NumPy scalar; convert to `int()` before returning so the tuple is portable.
- This is the per-class slice of the confusion matrix, computed by hand: diagonal = TP, row-excluding-diagonal = FP, column-excluding-diagonal = FN.

<div class="claude-handoff" data-exercise="exercises/module7/confusion-counts-with-numpy/">

**Build It in Claude Code:** Add `confusion_counts` to the shared `eval_engine.py`, load the sample predictions, assert the per-class counts for cat, dog, and bird, and exit 0.

</div>
