# Vectorized Math and ufuncs

Computing cosine similarity for a batch of 512 embedding vectors is the wrong place to discover that Python `for` loops serialize what a CPU wants to parallelize. A ufunc runs one typed C loop across the entire buffer; a reduction collapses an axis in the same stroke.

## What You Build

You build a batch cosine-similarity script that computes dot products, norms, and similarity scores for a matrix of embedding rows against a query vector, using ufuncs and reductions, with no Python loop over the batch dimension.

## The Typed C Loop

Module 1 established that a NumPy array is a contiguous typed buffer. A ufunc exploits that layout directly: it selects a compiled C inner loop matched to the array's dtype and steps through every element without returning to the Python interpreter between iterations. Microsoft Learn's "Explore and Analyze Data with Python" module makes the same point at the pattern level: operations on typed NumPy arrays run far more efficiently than the equivalent work over Python sequences ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

You can see the available type signatures on any ufunc:

```python
import numpy as np

print(np.multiply.types)
# ['bb->b', 'BB->B', 'hh->h', ..., 'dd->d', 'gg->g', 'FF->F', 'DD->D', ...]
```

Each entry is a type signature for one compiled loop. When you call `np.multiply(a, b)`, NumPy matches the arrays' dtype to the right entry and runs that loop end-to-end. No Python objects cross the boundary per element.

## Element-Wise Operations

Start with a batch of embeddings and a query vector:

```python
rng = np.random.default_rng(42)

batch = rng.standard_normal((512, 128)).astype(np.float32)  # 512 rows, 128 dims
query = rng.standard_normal(128).astype(np.float32)         # 1 query vector

# Element-wise multiply each row by the query (broadcast: (512, 128) * (128,))
products = np.multiply(batch, query)
print(products.shape)   # (512, 128)
print(products.dtype)   # float32
```

Broadcasting handles the shape mismatch: the `(128,)` query is treated as `(1, 128)` and multiplied across all 512 rows. The ufunc runs one `ff->f` C loop over the whole `(512 * 128)`-element buffer.

## Reductions With `axis`

A reduction collapses an axis by applying a ufunc's accumulation logic across it. `arr.sum(axis=1)` calls `np.add.reduce` along axis 1, turning `(512, 128)` into `(512,)`.

Dot products for all 512 rows:

```python
dot_products = products.sum(axis=1)      # (512,)
print(dot_products.shape)                # (512,)
print(dot_products[:4])
# e.g. [-2.31  1.07  0.44 -0.89]
```

Norms follow the same pattern:

```python
batch_norms = np.sqrt((batch ** 2).sum(axis=1))   # (512,)
query_norm  = np.sqrt((query ** 2).sum())          # scalar
```

Or use `np.linalg.norm` as a convenience, which maps to the same ufunc machinery:

```python
batch_norms = np.linalg.norm(batch, axis=1)   # (512,)
query_norm  = np.linalg.norm(query)            # scalar
```

Cosine similarity is now three lines with no loop:

```python
cosine_sim = dot_products / (batch_norms * query_norm)
print(cosine_sim.shape)   # (512,)
print(cosine_sim[:4])
# e.g. [-0.18  0.09  0.04 -0.07]
```

## `argmax`: Finding the Top Match

`np.argmax` is a reduction that returns the index of the maximum value along an axis:

```python
top_idx = np.argmax(cosine_sim)           # scalar index
print(f"top match: row {top_idx}, score {cosine_sim[top_idx]:.4f}")
# e.g. top match: row 217, score 0.2841
```

No Python loop over 512 scores. The ufunc walks the `(512,)` buffer once in C and hands back one integer.

## `np.where`: The Vectorized Conditional

`np.where(condition, x, y)` is the vectorized `if/else`. It replaces every element where `condition` is `False` with `y`:

```python
threshold = 0.0
# Keep scores above threshold; zero out the rest
filtered = np.where(cosine_sim > threshold, cosine_sim, 0.0)
print(filtered.shape)            # (512,)
print((filtered > 0).sum())      # number of positive-similarity matches
```

One ufunc call replaces a loop that would read each score, branch, and write a result.

## `arr.mean(axis=0)`: Collapsing the Batch

`mean(axis=0)` collapses the batch dimension, producing the per-dimension mean across all rows:

```python
col_means = batch.mean(axis=0)
print(col_means.shape)   # (128,)
print(col_means[:4])
# e.g. [-0.002  0.011 -0.008  0.003]  -- near zero for standard normal
```

Axis 0 walks the buffer in strides of `128 * 4 bytes` (the row stride you established in Module 1), summing down each column. The scalar 512 never appears in your code; it collapses inside the C loop.

Reach for a Python `for` loop over a batch dimension and you have already conceded the performance argument; in production the ufunc is the default, and the loop is the exception you justify. Module 4 turns that instinct into a measured decision rule.

## Core Concepts

- A ufunc selects a compiled C inner loop matched to the array's dtype and steps through the buffer without returning to the Python interpreter per element; the type signatures on `ufunc.types` tell you exactly which loops exist.
- The `axis` argument on reductions (`sum`, `mean`, `argmax`) names which dimension collapses; `axis=0` collapses rows into a single row, `axis=1` collapses columns into a single column.
- `np.argmax` returns the index of the maximum value in one C pass; no Python comparison loop is needed to find the top result in a batch.
- `np.where(condition, x, y)` is a vectorized conditional that replaces an element-by-element `if/else` loop; it belongs in every score-filtering and masking pipeline.

<div class="claude-handoff" data-exercise="exercises/module2/vectorized-math-and-ufuncs/">

**Build It in Claude Code:** Build a cosine-similarity script that ranks 512 embedding rows against a query vector using ufuncs and reductions, with no Python loop, then assert the result matches a reference loop.

</div>
