# Exercise: Feature Vectors and Distance Metrics From Scratch

## Goal

Load the Iris dataset, represent it as a NumPy matrix, and compute pairwise Euclidean and cosine
distances between the first five rows using only NumPy arithmetic; no `sklearn.metrics.pairwise` or
`scipy.spatial.distance`. Print both 5x5 matrices and write one sentence per metric explaining
which pair is most similar and why the two metrics disagree on at least one pair.

## Why

The ability to implement a distance metric from its formula, without reaching for a library wrapper,
is the test that you understand the geometry rather than just calling it. Every production vector
search system, from Azure AI Search to Cosmos DB vector indexes, is computing one of these formulas
at scale. Knowing the formula makes the library call legible.

## Steps

1. Load the dataset:
   ```python
   from sklearn.datasets import load_iris
   import numpy as np
   iris = load_iris()
   X = iris.data          # shape (150, 4), dtype float64
   y = iris.target        # shape (150,)
   X5 = X[:5]             # the five rows you will work with
   ```

2. Implement `euclidean_distance(a, b)` using `np.sqrt` and `np.sum`. Do not use `np.linalg.norm`.
   Compute a 5x5 matrix `D_euc` where `D_euc[i, j]` is the Euclidean distance between `X5[i]`
   and `X5[j]`. The diagonal must be zero.

3. Implement `cosine_distance(a, b)` as `1 - dot(a, b) / (norm(a) * norm(b))`. You may use
   `np.dot` and `np.linalg.norm` here. Compute a 5x5 matrix `D_cos` with the same shape.
   Note: this gives distance, not similarity; zero means identical direction.

4. Print both matrices with two decimal places:
   ```python
   np.set_printoptions(precision=2, suppress=True)
   print("Euclidean:\n", D_euc)
   print("Cosine:\n", D_cos)
   ```

5. Inspect the matrices. Find the pair `(i, j)` with the smallest non-diagonal Euclidean distance
   and the pair with the smallest non-diagonal cosine distance. Check whether they are the same
   pair. Write a one-sentence comment in your script explaining why they agree or disagree; the
   answer will depend on whether the closest Euclidean pair differs in magnitude from what their
   directional angle would suggest.

6. (Optional: run a quick sanity check.) Verify your `euclidean_distance` against `np.linalg.norm`
   on one pair:
   ```python
   i, j = 0, 1
   assert abs(euclidean_distance(X5[i], X5[j]) - np.linalg.norm(X5[i] - X5[j])) < 1e-10
   ```

## Done When

- `D_euc` and `D_cos` are printed and both have zeros on the diagonal.
- You can identify one pair where Euclidean and cosine distance give different similarity rankings,
  and you can state in one sentence why.
- The sanity check passes (no assertion error).

## Stretch

Add a third matrix `D_man` (Manhattan distance). For each of the three metrics, find the top-3
closest pairs (excluding the diagonal). Report which pairs appear in all three lists, which appear
in only one, and what that tells you about the structure of the Iris feature space near those five
points.
