# Boolean Masks and Fancy Indexing

Your eval run finished. Now you need the rows that failed: score below threshold, label wrong, confidence suspect. A Python loop over the table would work, but it is slow and clears nothing. Two NumPy operations cut straight to those rows: a boolean mask that selects by condition, and an integer array that gathers by position. Both return a copy.

## The Artifact

You build `filter_eval.py`: a script that filters a simulated eval table to its failing rows and retrieves the top-k rows by score.

## Build a Boolean Mask

Start with a score column and a threshold:

```python
import numpy as np

rng = np.random.default_rng(42)
n = 12

scores  = rng.uniform(0.0, 1.0, n).astype(np.float32)  # shape (12,)
labels  = rng.integers(0, 2, n)                          # 0 or 1
preds   = rng.integers(0, 2, n)

print("scores:", np.round(scores, 3))
```

A comparison on an array returns a boolean array of the same shape:

```python
low_score = scores < 0.4          # shape (12,), dtype bool
wrong_label = labels != preds      # shape (12,), dtype bool
```

Combine conditions with `&` (element-wise AND) or `|` (element-wise OR). Wrap each condition in parentheses: Python's operator precedence treats `&` and `|` as bitwise, and without parentheses the comparison operators bind more loosely than you expect.

```python
failing = low_score & wrong_label  # rows that are both low-confidence AND mislabeled
```

## Select Rows by Mask

Build a table where rows are examples and columns are `[score, label, pred]`:

```python
table = np.column_stack([scores, labels, preds])   # shape (12, 3)

failing_rows = table[failing]                       # shape (k, 3), k = number of True entries
print(f"failing rows: {failing_rows.shape[0]} of {n}")
print(failing_rows)
```

`table[failing]` is boolean indexing: NumPy walks the mask, collects the matching rows, and writes them into a fresh buffer. Unlike M1's slice-view, the mask result owns its buffer; `failing_rows.flags['OWNDATA']` is `True` and `np.shares_memory(table, failing_rows)` is `False`. [MS-Learn: "Explore and Analyze Data with Python" covers boolean filtering on NumPy arrays as the standard pattern for subsetting evaluation data in ML pipelines: learn.microsoft.com/training/modules/explore-analyze-data-with-python/]

`np.nonzero(failing)` gives you the integer indices of the `True` positions when you need them as a list rather than a mask:

```python
idx = np.nonzero(failing)[0]
print("failing indices:", idx)
assert np.array_equal(table[idx], failing_rows)
```

## Gather Rows by Integer Array

Fancy indexing takes an integer array and gathers the rows at those positions, in that order. The order is yours to choose:

```python
specific = np.array([7, 2, 11, 0])
subset = table[specific]           # shape (4, 3): rows 7, 2, 11, 0 in that exact order
print("gathered:", subset)
```

This is a gather: you pick, you reorder, you get a copy. The source table is untouched.

## Top-k via argsort and argpartition

To retrieve the top 3 rows by score, sort the score column and take the last three indices:

```python
k = 3
top_k_idx = np.argsort(scores)[-k:]          # indices of k highest scores, ascending order
top_k_rows = table[top_k_idx]

print("top-k scores:", scores[top_k_idx])
```

`argsort` returns all indices sorted; for large tables where you need only k winners, `argpartition` is faster: it guarantees the k-th element is in its sorted position without sorting the rest:

```python
part_idx = np.argpartition(scores, -k)[-k:]  # k highest, unordered among themselves
top_k_unordered = table[part_idx]
print("top-k (partition):", scores[part_idx])
```

Surfacing the top-scoring predictions for review is the front end of model evaluation; Microsoft Learn documents the precision, recall, and F1 metrics computed over those predictions in its Evaluate Model reference ([learn.microsoft.com/azure/machine-learning/component-reference/evaluate-model](https://learn.microsoft.com/azure/machine-learning/component-reference/evaluate-model?view=azureml-api-2#metrics)).

Both `argsort` and `argpartition` return integer arrays; passing them back into `table[...]` is fancy indexing, so the result is a copy.

## The Copy Confirmation

The rule from M1 holds for both operations: boolean indexing and fancy indexing both trigger advanced indexing, and advanced indexing always copies.

```python
assert failing_rows.flags['OWNDATA'],              "mask result must own its buffer"
assert not np.shares_memory(table, failing_rows),  "mask result must not share memory"
assert top_k_rows.flags['OWNDATA'],                "fancy-indexed top-k must own its buffer"
assert not np.shares_memory(table, top_k_rows),    "fancy-indexed top-k must not share memory"
```

Run the check once per pipeline: the cost of an unintended copy in a thousand-row loop is a thousand allocations. Knowing which operation copies is not a footnote; it is the memory budget.

The eval table that looked like a table is now something you can cut with a single expression: mask the failures, gather the top candidates, hand each to the next stage.

## Core Concepts

- A boolean mask built from a comparison (`scores < 0.4`) selects rows by condition; combine multiple masks with `&` and `|`, wrapping each condition in parentheses.
- Fancy indexing with an integer array (`table[np.array([7, 2, 11])]`) gathers rows by position in any order you specify; this is the primitive behind top-k retrieval.
- Both boolean indexing and fancy indexing trigger NumPy's advanced indexing, which always returns a copy: `arr.flags['OWNDATA']` is `True` and `np.shares_memory` is `False`.
- `argsort` gives all indices in sorted order; `argpartition` gives the k-th partition boundary without a full sort, which is faster when you need only the top or bottom k from a large score column.

<div class="claude-handoff" data-exercise="exercises/module2/advanced-indexing/">

**Build It in Claude Code:** Build `filter_eval.py`, a script that masks failing rows from a simulated eval table and retrieves the top-k rows by score, then asserts both results are copies.

</div>
