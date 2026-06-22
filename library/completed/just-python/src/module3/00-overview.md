# Module 3: Pandas for AI Pipelines

## What This Module Covers

Module 2 drove the raw NumPy buffer: ufuncs, broadcasting, indexing, layout. Module 3 puts a labeled, heterogeneous table on top of that buffer, the DataFrame, and the operations that turn raw rows into a training or evaluation set. A DataFrame column is a NumPy-backed Series, so everything M1 and M2 taught about memory and vectorization carries straight in; what is new is the labeled structure and the four data-prep moves built on it.

This is the Pandas surface a hiring screen tests. A take-home that hands you a messy CSV, a corpus of JSONL, or a predictions file to score is asking whether you can load it with the right dtypes, join it, group it, and clean it without dropping to a Python loop. Module 3 is also where the book's data layer begins: the load and clean patterns you write here are the ones the Module 6 wrangling artifact reuses off disk.

The work stays grounded in the Sans Python ecosystem and the made-with-ml data pipeline: the eval tables, corpora, and prediction outputs you already know are the data you now wrangle at speed.

## Arc of Lessons

| Lesson | Title | What It Teaches |
|--------|-------|-----------------|
| 1 | Series and DataFrame | The DataFrame as a dict of NumPy-backed Series sharing one index; per-column dtypes, and the object-dtype string tax M1 predicted, measured with `memory_usage(deep=True)` |
| 2 | Reading and Writing AI Formats | CSV (eval interchange), JSONL (corpora), Parquet (typed, columnar, at scale); controlling dtypes on load and knowing what survives each round trip |
| 3 | Groupby, Merge, and Apply | Split-apply-combine with `groupby` + agg, `merge` to join predictions to labels, and why `apply` is a disguised loop you vectorize away |
| 4 | Cleaning and Missing Data | Dedup, handle `NaN` (drop vs fill), reshape with melt/pivot, and clean text with the vectorized `.str` accessor; the operations that make raw rows a dataset |

## Throughline Artifact

You extend `measure.py` once more. Lesson 1 adds `frame_bytes`, which reports a DataFrame's true memory with `memory_usage(deep=True)` and compares it to the equivalent contiguous ndarray, making the object-dtype string overhead (M1's boxed-object model, now in Pandas) measurable. The load, join, and clean patterns in Lessons 2 through 4 are the data-prep moves the Module 6 wrangling pipeline imports and extends. The reuse is real: you open the existing file and add to it, you do not start over.

## Prerequisites

- Module 1 (the object model, dtypes, the contiguous buffer) and Module 2 (vectorized column operations). Module 3 builds on both: a numeric column is a NumPy buffer, and `apply` is the Python loop M2 taught you to avoid. It does not re-teach them.
- The `measure.py` you have been building, at `exercises/module1/the-cost-of-a-python-list/measure.py`. You extend it here.
- A Python 3.11+ environment with pandas and NumPy installed (`pip install pandas numpy`); `pyarrow` for the Parquet lesson (`pip install pyarrow`).
