# Exercise: Feature Vectors

**Goal:** Build `exercises/ml/distances.py`, a NumPy module of three distance metrics and two
feature scalers that every later algorithm in the `ml/` package reuses.

**Why:** The distance function is the only geometry assumption a distance-based algorithm makes;
getting it right, and scaling features so no single column hijacks it, is the precondition for
anything in this book to work correctly.

## The Shared Artifact

`exercises/ml/` is the throughline package for this book. Before you add anything, create
`exercises/ml/__init__.py` once (an empty file is fine). Every lesson in Modules 1 through 7
adds one module to this package; the capstone imports them all off disk.

Check whether `exercises/ml/__init__.py` already exists. If it does, read the package before
touching it. If not, create it now, then create `exercises/ml/distances.py` with the locked
structure below.

## Steps

### 1. Create the Package Root (Once Only)

```
exercises/ml/__init__.py    <- empty file; makes ml/ an importable package
```

### 2. Implement `exercises/ml/distances.py`

The locked structure below is the contract every later module imports. Implement each function
body; do not alter signatures, docstrings, or the `METRICS` dict at the bottom.

```python
"""Distance metrics and feature scaling, from scratch in NumPy.

The three metrics answer three different "how far apart?" questions; the two scalers put every
feature on a common footing so the metric is not hijacked by the largest-range column. These are the
geometry primitives every later algorithm in the package reuses.
"""
import numpy as np


def euclidean(a, b):
    """Straight-line (L2) distance. Use when magnitude matters and features are comparably scaled."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.sqrt(np.sum((a - b) ** 2)))


def manhattan(a, b):
    """Sum of absolute per-axis differences (L1). More robust to a single outlier dimension."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.sum(np.abs(a - b)))


def cosine_distance(a, b):
    """1 - cosine similarity. Use when direction (proportional pattern) matters and magnitude is noise."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0.0:
        raise ValueError("cosine distance is undefined for a zero-magnitude vector")
    return float(1.0 - np.dot(a, b) / denom)


def minmax_scale(X):
    """Linearly rescale each column to [0, 1]. Constant columns map to 0 (no range to stretch)."""
    X = np.asarray(X, dtype=float)
    lo = X.min(axis=0)
    hi = X.max(axis=0)
    span = np.where(hi - lo == 0.0, 1.0, hi - lo)
    return (X - lo) / span


def zscore(X):
    """Center each column at mean 0, scale to unit standard deviation. Constant columns map to 0."""
    X = np.asarray(X, dtype=float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd = np.where(sd == 0.0, 1.0, sd)
    return (X - mu) / sd


# Name -> function, so an algorithm can take a metric by string (a hypothesis about the data).
METRICS = {
    "euclidean": euclidean,
    "manhattan": manhattan,
    "cosine": cosine_distance,
}
```

### 3. Write the Acceptance Gate

Create `exercises/module1/feature-vectors/test_distances.py` with the locked test suite below.
scikit-learn is the oracle only; the math under test is yours, in `ml/distances.py`.

```python
"""Acceptance gate for the feature-vectors exercise.

The from-scratch metrics must agree with scikit-learn's reference implementations, and the two scalers
must do what they claim. scikit-learn is the oracle only; the math under test is yours, in ml/distances.py.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.metrics.pairwise import (
    euclidean_distances,
    manhattan_distances,
    cosine_distances,
)

from ml.distances import euclidean, manhattan, cosine_distance, minmax_scale, zscore

A = np.array([5.1, 3.5, 1.4, 0.2])
B = np.array([6.7, 3.0, 5.2, 2.3])


def test_euclidean_matches_sklearn():
    assert np.isclose(euclidean(A, B), euclidean_distances([A], [B])[0, 0])


def test_manhattan_matches_sklearn():
    assert np.isclose(manhattan(A, B), manhattan_distances([A], [B])[0, 0])


def test_cosine_matches_sklearn():
    assert np.isclose(cosine_distance(A, B), cosine_distances([A], [B])[0, 0])


def test_cosine_zero_vector_raises():
    try:
        cosine_distance(np.zeros(4), B)
    except ValueError:
        return
    raise AssertionError("cosine_distance must raise ValueError on a zero-magnitude vector")


def test_minmax_scale_hits_unit_interval():
    X = np.array([[20.0, 20000.0], [80.0, 200000.0], [50.0, 110000.0]])
    Xs = minmax_scale(X)
    assert np.allclose(Xs.min(axis=0), 0.0)
    assert np.allclose(Xs.max(axis=0), 1.0)


def test_zscore_standardizes():
    X = np.random.RandomState(0).rand(64, 3) * 100.0
    Xs = zscore(X)
    assert np.allclose(Xs.mean(axis=0), 0.0, atol=1e-9)
    assert np.allclose(Xs.std(axis=0), 1.0, atol=1e-9)
```

## Done When

```
python -m pytest exercises/module1/feature-vectors
```

All six tests pass. scikit-learn agrees with your three metrics; min-max output is bounded to
[0, 1]; z-score output has mean 0 and standard deviation 1 per column; a zero-magnitude vector
raises `ValueError`.

## Stretch

Add a `chebyshev(a, b)` function to `ml/distances.py`: the L-infinity distance, defined as the
maximum absolute difference across all axes (`max(|a_i - b_i|)`). Add it to `METRICS` under the
key `"chebyshev"`. Write a test that verifies it equals `scipy.spatial.distance.chebyshev` on the
same A, B pair. Then fit a `KNNClassifier` (from the next lesson) with `metric="chebyshev"` on
z-scored Iris and report its accuracy at k=5. Chebyshev is the metric a chessboard king
uses; it is the right choice when you want the single worst-case axis to dominate, not the
aggregate distance.
