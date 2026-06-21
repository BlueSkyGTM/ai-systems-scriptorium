# Exercise: Boolean Masks and Fancy Indexing

**Goal:** Build `filter_eval.py`, a script that filters a simulated eval table to its failing rows and retrieves the top-k rows by score, then asserts both results are copies.

**Why:** The ability to cut an eval set to its failures and surface the top-k candidates is the operational core of any eval-driven workflow; knowing the results are copies means you can modify them without corrupting the source table.

## Steps

1. Create a deterministic eval table with a fixed seed:

   ```python
   import numpy as np

   rng = np.random.default_rng(42)
   n = 20

   scores = rng.uniform(0.0, 1.0, n).astype(np.float32)
   labels = rng.integers(0, 2, n)
   preds  = rng.integers(0, 2, n)

   table = np.column_stack([scores, labels, preds])  # shape (20, 3)
   ```

2. Build a boolean mask for failing rows (score below 0.4 AND label mismatch):

   ```python
   failing = (scores < 0.4) & (labels != preds)
   ```

   Print the number of failing rows and the count of `True` entries in the mask.

3. Select the failing rows and confirm the result is a copy:

   ```python
   failing_rows = table[failing]

   assert failing_rows.flags['OWNDATA'], "mask result must own its buffer"
   assert not np.shares_memory(table, failing_rows), "mask result must not share memory"
   assert failing_rows.shape[0] == failing.sum(), "row count must match True count in mask"
   ```

4. Fancy-index three specific rows by position (use `[3, 17, 5]`) and confirm the gather is also a copy:

   ```python
   chosen = table[np.array([3, 17, 5])]

   assert chosen.flags['OWNDATA'], "fancy-indexed result must own its buffer"
   assert not np.shares_memory(table, chosen), "fancy-indexed result must not share memory"
   assert chosen.shape == (3, 3), "shape must be (3, 3)"
   ```

5. Retrieve the top-3 rows by score with `argsort` and assert they are the three highest scores:

   ```python
   k = 3
   top_k_idx = np.argsort(scores)[-k:]
   top_k_rows = table[top_k_idx]

   top_k_scores = scores[top_k_idx]
   ref_top3 = np.sort(scores)[-k:]
   assert np.allclose(np.sort(top_k_scores), ref_top3), "top-k scores must match the three highest"
   assert not np.shares_memory(table, top_k_rows), "top-k result must not share memory"
   ```

6. Repeat the top-3 retrieval with `argpartition` and assert the same three highest scores appear (order may differ):

   ```python
   part_idx = np.argpartition(scores, -k)[-k:]
   part_scores = scores[part_idx]
   assert np.allclose(np.sort(part_scores), ref_top3), "argpartition top-k must match argsort top-k"
   ```

7. Print a structured report and exit with code 0:

   ```
   [PASS] mask: 1 of 20 rows failing
   [PASS] mask result is a copy (OWNDATA True, shares_memory False)
   [PASS] fancy index result is a copy
   [PASS] argsort top-3 scores: [0.859 0.927 0.976]
   [PASS] argpartition top-3 matches argsort top-3
   ```

   (Exact counts and scores depend on the fixed seed; the seed guarantees they are deterministic.)

## Done When

All six assertion groups pass, the structured `[PASS]` report prints, and the script exits with code 0. Run it with:

```sh
python filter_eval.py
```

No external dependencies beyond NumPy. The fixed seed `np.random.default_rng(42)` makes every run deterministic.

## Stretch

Add a combined filter: use `np.where` to get the indices of rows where the score exceeds 0.7 AND the label matches the prediction (the high-confidence correct rows). Fancy-index those rows, assert the result is a copy, and print the count. Then assert that the high-confidence set and the failing set have no rows in common:

```python
hc_idx = np.where((scores > 0.7) & (labels == preds))[0]
hc_rows = table[hc_idx]
assert not np.shares_memory(table, hc_rows)
assert len(np.intersect1d(hc_idx, np.nonzero(failing)[0])) == 0, \
    "high-confidence correct rows must not overlap with failing rows"
```
