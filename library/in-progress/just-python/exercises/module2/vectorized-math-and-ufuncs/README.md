# Exercise: Vectorized Math and ufuncs

**Goal:** Build a script that computes cosine similarity for a batch of embedding rows against a query vector using ufuncs and reductions, finds the top match with `argmax`, masks low scores with `np.where`, and asserts the vectorized result matches a reference loop.

**Why:** Every metric aggregation pipeline in production runs on batches, not scalars; knowing how to collapse an axis without a Python loop is the skill that keeps inference from stalling.

## Steps

1. Create deterministic arrays with a fixed seed. Use shape `(256, 64)` for the batch and `(64,)` for the query, dtype `np.float32`:

   ```python
   import numpy as np
   import sys

   rng = np.random.default_rng(7)
   batch = rng.standard_normal((256, 64)).astype(np.float32)
   query = rng.standard_normal(64).astype(np.float32)
   ```

2. Compute dot products for all 256 rows in one operation. Multiply the batch by the query (broadcast handles `(256, 64) * (64,)`) and sum along axis 1:

   ```python
   dot_products = (batch * query).sum(axis=1)   # shape: (256,)
   ```

3. Compute L2 norms for the batch rows and for the query:

   ```python
   batch_norms = np.linalg.norm(batch, axis=1)  # shape: (256,)
   query_norm  = np.linalg.norm(query)           # scalar
   ```

4. Compute cosine similarity and find the top match:

   ```python
   cosine_sim = dot_products / (batch_norms * query_norm)   # shape: (256,)
   top_idx    = np.argmax(cosine_sim)
   ```

5. Mask scores at or below zero using `np.where`:

   ```python
   filtered = np.where(cosine_sim > 0.0, cosine_sim, 0.0)
   ```

6. Build a reference result with a Python loop (this is the slow path you are replacing):

   ```python
   ref = np.zeros(256, dtype=np.float32)
   for i in range(256):
       dot = float(np.dot(batch[i], query))
       norm_i = float(np.linalg.norm(batch[i]))
       ref[i] = dot / (norm_i * float(query_norm))
   ```

7. Assert correctness and print a structured report:

   ```python
   assert np.allclose(cosine_sim, ref, atol=1e-5), \
       "Vectorized cosine similarity must match the reference loop"
   assert cosine_sim[top_idx] == cosine_sim.max(), \
       "argmax index must point to the highest score"
   assert filtered[filtered < 0].size == 0, \
       "np.where must zero out all negative scores"
   assert (filtered > 0).sum() == (cosine_sim > 0).sum(), \
       "np.where must preserve all positive scores"

   print(f"[PASS] vectorized vs loop: max diff {np.abs(cosine_sim - ref).max():.2e}")
   print(f"[PASS] top match: row {top_idx}, score {cosine_sim[top_idx]:.4f}")
   print(f"[PASS] positive matches after threshold: {(filtered > 0).sum()} / 256")
   ```

## Done When

All four assertions pass, the three `[PASS]` lines print, and the script exits with code 0. Run it with:

```sh
python cosine_batch.py
```

No external dependencies beyond NumPy.

## Stretch

Replace `np.linalg.norm(batch, axis=1)` with the explicit ufunc form: `np.sqrt((batch ** 2).sum(axis=1))`. Assert the two norms agree to `atol=1e-5`. Print a line confirming they match. This makes the ufunc chain explicit rather than delegating to a convenience function.
