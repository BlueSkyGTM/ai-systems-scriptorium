# Module 2: NumPy in Depth

## What This Module Covers

Module 1 built the *why*: the array exists because Python's boxed containers waste memory bandwidth, and a contiguous typed buffer is the fix. This module builds the *how*. You drive that buffer with the four operations that make it pay off: vectorized math (ufuncs and reductions), broadcasting, advanced indexing, and the memory layout that decides whether any of them is actually fast.

This is the NumPy surface a hiring screen tests. A take-home that asks you to score a batch of embeddings, filter an evaluation set, or normalize a feature matrix is asking whether you can replace a Python loop with an array operation and know what it costs. Module 2 is also the rung Module 4 stands on: you cannot reason about when to vectorize until you can vectorize fluently, and you cannot explain a slow reduction until you can read its memory layout.

The work stays grounded in the Sans Python ecosystem: the embedding rows, query vectors, and evaluation tables you already built are the data you now operate on at speed.

## Arc of Lessons

| Lesson | Title | What It Teaches |
|--------|-------|-----------------|
| 1 | Vectorized Math and ufuncs | A ufunc runs one compiled C loop across the whole buffer; reductions collapse an axis. You build batch cosine similarity with `sum`, `argmax`, and `np.where`, no Python loop |
| 2 | Broadcasting | The alignment rule that stretches a smaller array across a larger one with no copy; `keepdims` and `np.newaxis` to place the size-1 axis, and when arithmetic forces materialization |
| 3 | Boolean Masks and Fancy Indexing | Selection by condition and by position; both trigger advanced indexing and both copy, unlike M1's slice-view; `argsort` and `argpartition` for top-k |
| 4 | Memory Layout and Contiguity | C order versus Fortran order, why a strided reduction is slower than a contiguous one, and the `ascontiguousarray` and `reshape` copy rules that govern the fix |

## Throughline Artifact

You keep extending `measure.py`, the benchmark helper from Module 1. Lesson 2 adds `broadcast_allocates`, which proves a broadcast view stays near zero bytes until arithmetic forces the full output buffer. Lesson 4 adds `time_contiguous_vs_strided`, which times a reduction over contiguous data against the same reduction over a transposed view and prints the gap in milliseconds. By the end of the module the helper measures not just memory but layout cost, and Module 4 imports it off disk to prove a vectorized op beats a loop. The reuse is real: you open the existing file and add to it, you do not start over.

## Prerequisites

- Module 1 in full: the contiguous array, the dtype contract, and the shape-and-strides descriptor, including which operations return a view and which copy. Module 2 uses that view-versus-copy distinction; it does not re-teach it.
- The `measure.py` you built in Module 1, at `exercises/module1/the-cost-of-a-python-list/measure.py`. You extend it here.
- A Python 3.11+ environment with NumPy installed (`pip install numpy`).
