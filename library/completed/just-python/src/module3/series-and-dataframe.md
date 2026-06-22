# Series and DataFrame

A DataFrame column is a NumPy-backed Series. That one fact closes the loop on everything M1 and M2 taught: the memory model is the same, the vectorized column operations are the same, and the dtype tax on a string column is exactly what M1 predicted for boxed Python objects.

## The Two Structures

A `Series` is a one-dimensional labeled array: a single typed buffer (the values) paired with an index (the row labels). Build one from a list and you get a `RangeIndex` for free:

```python
import pandas as pd
import numpy as np

scores = pd.Series([0.91, 0.87, 0.94, 0.73], name="f1")
print(scores)
# 0    0.91
# 1    0.87
# 2    0.94
# 3    0.73
# Name: f1, dtype: float64

print(scores.dtype)    # float64
print(scores.nbytes)   # 32  (4 values × 8 bytes each)
```

`scores.nbytes` reports the backing buffer directly, the same as `ndarray.nbytes`. The M2 vectorized operations apply to a Series column-by-column for the same reason: each column is a contiguous typed buffer, and NumPy ufuncs operate on it without a Python loop.

A `DataFrame` is a dict of Series objects sharing one index. The columns can carry different dtypes; the index is the common row spine.

```python
df = pd.DataFrame({
    "model":  ["gpt-4o",  "claude-3", "llama-3",  "mistral"],
    "f1":     [0.91,      0.87,       0.94,        0.73],
    "tokens": [4096,      8192,       8192,        32768],
    "open":   [False,     False,      True,         True],
})
print(df)
#      model    f1  tokens   open
# 0    gpt-4o  0.91    4096  False
# 1  claude-3  0.87    8192  False
# 2   llama-3  0.94    8192   True
# 3   mistral  0.73   32768   True
```

## Inspecting dtypes and Layout

`df.dtypes` returns a Series mapping column name to dtype:

```python
print(df.dtypes)
# model      object
# f1        float64
# tokens      int64
# open         bool
# dtype: object
```

Three columns hold contiguous NumPy buffers (`float64`, `int64`, `bool`). The `model` column shows `object`. That is the dtype from M1's "every value is a box" lesson: each entry is a Python `str` object on the heap, and the column stores 8-byte pointers to those objects, not the characters themselves.

`df.info()` confirms the layout and reports a memory estimate in one call:

```python
df.info()
# <class 'pandas.core.frame.DataFrame'>
# RangeIndex: 4 entries, 0 to 3
# Data columns (total 4 columns):
#  #   Column  Non-Null Count  Dtype
# ---  ------  --------------  -----
#  0   model   4 non-null      object
#  1   f1      4 non-null      float64
#  2   tokens  4 non-null      int64
#  3   open    4 non-null      bool
# dtypes: bool(1), float64(1), int64(1), object(1)
# memory usage: 196.0+ bytes
```

The `+` on the memory figure is the tell: pandas knows the `object` column's real cost is not yet counted. Pass `deep=True` to follow the pointers.

## Measuring the Object-dtype Tax

`df.memory_usage(deep=True)` returns a Series of byte counts per column, including the index:

```python
usage = df.memory_usage(deep=True)
print(usage)
# Index      132
# model      224
# f1          32
# tokens      32
# open         4
# dtype: int64

print(f"total: {usage.sum():,} bytes")
# total: 424 bytes
```

The `model` column costs 224 bytes for four short strings (your pandas version may print a slightly different figure for the object column), against 32 bytes for the numeric columns holding the same four rows. That is M1's object overhead in column form: four Python `str` objects, each individually heap-allocated, each carrying a type pointer and reference count, their addresses stored in the object-dtype column.

Compare directly to the equivalent numeric ndarray to see the ratio:

```python
numeric_col = np.array([0.91, 0.87, 0.94, 0.73], dtype=np.float64)
print(f"numeric ndarray:  {numeric_col.nbytes:>6} bytes")  # 32 bytes
print(f"object column:    {usage['model']:>6} bytes")       # 224 bytes
```

The string column is roughly 7x heavier per row. At production scale, a model-name column on a million-row eval table is not a footnote: it is tens of megabytes of pointer overhead on top of the character data itself.

Microsoft Learn's "Explore and Analyze Data with Python" module introduces the DataFrame as the core structure for exploring tabular data with Pandas ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

## When the Column Is Tight

The numeric columns pay no object tax. `df["f1"]` is a `float64` Series backed by a 32-byte buffer; `df["tokens"]` is an `int64` Series backed by the same. M2's broadcasting applies per-column without any pointer-chasing:

```python
# Normalize f1 scores to [0, 1] range, vectorized, no loop
min_f1 = df["f1"].min()
max_f1 = df["f1"].max()
df["f1_norm"] = (df["f1"] - min_f1) / (max_f1 - min_f1)
print(df[["model", "f1", "f1_norm"]])
#      model    f1   f1_norm
# 0    gpt-4o  0.91  0.857143
# 1  claude-3  0.87  0.666667
# 2   llama-3  0.94  1.000000
# 3   mistral  0.73  0.000000
```

The arithmetic runs on the `float64` buffer directly. No Python objects enter the loop.

## The Shared Index

Every Series in a DataFrame shares the same index object. When you select a column, you get back a Series whose index is the DataFrame's row index. When you assign a new column from a computation, pandas aligns it to that same index automatically. The alignment guarantee is what lets you mix columns freely without tracking row position by hand.

```python
# Selecting a column returns a Series; its index matches the DataFrame's
col = df["f1"]
print(type(col))           # <class 'pandas.core.series.Series'>
print(col.index.tolist())  # [0, 1, 2, 3]
```

The shared index is what separates a DataFrame from a raw dict of arrays. It is also what makes joins, groupbys, and reindexing safe: pandas uses the labels, not integer position, to align data.

Every eval table you will build in production is a DataFrame: columns for model names (object dtype), columns for metric scores (float64), columns for flags (bool). Knowing before you load which columns carry the object-dtype tax is what keeps that table from silently doubling your memory budget.

## Core Concepts

- A DataFrame is a dict of NumPy-backed Series sharing one index; each column carries its own dtype, so a numeric column is a tight contiguous buffer while an object/string column stores Python-object pointers and pays M1's full per-element heap overhead.
- `df.dtypes` reveals the dtype per column; `df.info()` confirms shape and prints a memory estimate, flagging the object column cost with a `+`; `df.memory_usage(deep=True)` follows the pointers and returns the true byte count per column.
- A numeric Series column is a contiguous `ndarray` buffer; M2's vectorized column operations apply directly and run without a Python loop.
- The object dtype is the string column's cost signal: an `object`-dtype column on a large eval table can outweigh all the numeric columns combined because each entry is a separately allocated, reference-counted Python object.

<div class="claude-handoff" data-exercise="exercises/module3/series-and-dataframe/">

**Inspect It in Claude Code:** Extend `measure.py` with `frame_bytes`, a function that measures the true memory cost of a DataFrame, compares a numeric column to its equivalent ndarray, and proves the object-dtype overhead against a string column.

</div>
