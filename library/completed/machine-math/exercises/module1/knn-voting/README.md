# Exercise: k-Nearest Neighbors Voting

**Goal:** Build `exercises/ml/knn.py`, a from-scratch `KNNClassifier` that reuses the `METRICS`
dispatch table from `ml/distances.py`, then measure its accuracy on Iris and confirm that scaling
is not optional.

**Why:** Distance is a decision; a lazy learner that cannot swap metrics, or that receives
unscaled features, is a classifier whose votes are rigged before prediction even starts.

## The Shared Artifact

`exercises/ml/` is the throughline package for this book. You built `ml/__init__.py` and
`ml/distances.py` in the previous lesson; this lesson adds `ml/knn.py` beside them. The
`KNNClassifier` imports `METRICS` from `ml.distances` directly, real reuse rather than a copy.
Read the current state of `ml/distances.py` before touching anything, so you understand what
`METRICS` contains and what each metric's signature looks like.

## Steps

### 1. Implement `exercises/ml/knn.py`

The locked structure below is the contract the acceptance gate tests. Implement each method body;
do not alter signatures, docstrings, or the `ValueError` guard at the top of `__init__`.

```python
"""k-nearest neighbors, from scratch in NumPy.

A lazy learner: "training" is storing the data; all the work is at prediction time. Every line maps
to one of three steps -- measure distance to every training point, rank, vote. The metric is pluggable
because choosing it is a modeling decision, not a default.
"""
import numpy as np
from collections import Counter

from ml.distances import METRICS


class KNNClassifier:
    def __init__(self, k=5, metric="euclidean"):
        if metric not in METRICS:
            raise ValueError(f"Unknown metric: {metric!r}; choose one of {sorted(METRICS)}")
        self.k = k
        self.metric = metric

    def fit(self, X, y):
        """Store the labeled training set. No parameters are fit; this is the whole 'training' phase."""
        self.X_train = np.asarray(X, dtype=float)
        self.y_train = np.asarray(y)
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=float)
        return np.array([self._predict_one(x) for x in X])

    def _predict_one(self, x):
        distance = METRICS[self.metric]
        distances = [distance(x, row) for row in self.X_train]
        k_idx = np.argsort(distances)[: self.k]
        votes = Counter(self.y_train[i] for i in k_idx)
        return votes.most_common(1)[0][0]
```

### 2. Write the Acceptance Gate

Create `exercises/module1/knn-voting/test_knn.py` with the locked test suite below. scikit-learn
is the oracle; the algorithm is yours.

```python
"""Acceptance gate for the knn-voting exercise.

The from-scratch KNNClassifier must agree with scikit-learn on the same split, clear an accuracy floor
on scaled Iris, and -- the point of the module -- show that scaling is not optional: a distorted feature
sinks an unscaled model, and z-scoring recovers it. scikit-learn is the oracle; the algorithm is yours.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from ml.knn import KNNClassifier
from ml.distances import zscore


def _split():
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)


def _accuracy(pred, truth):
    return float(np.mean(np.asarray(pred) == np.asarray(truth)))


def test_matches_sklearn_on_iris():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s, X_te_s = zscore(X_tr), zscore(X_te)
    mine = KNNClassifier(k=5, metric="euclidean").fit(X_tr_s, y_tr).predict(X_te_s)
    ref = KNeighborsClassifier(n_neighbors=5, metric="euclidean").fit(X_tr_s, y_tr).predict(X_te_s)
    assert np.mean(mine == ref) >= 0.95


def test_accuracy_floor_on_scaled_iris():
    X_tr, X_te, y_tr, y_te = _split()
    pred = KNNClassifier(k=5, metric="euclidean").fit(zscore(X_tr), y_tr).predict(zscore(X_te))
    assert _accuracy(pred, y_te) >= 0.90


def test_scaling_makes_the_vote_fair():
    # Multiply a weak feature (sepal width) by 1000 so raw Euclidean distance is hijacked by it.
    X_tr, X_te, y_tr, y_te = _split()
    distort = np.array([1.0, 1000.0, 1.0, 1.0])
    X_tr_d, X_te_d = X_tr * distort, X_te * distort
    knn = KNNClassifier(k=5, metric="euclidean")
    unscaled = _accuracy(knn.fit(X_tr_d, y_tr).predict(X_te_d), y_te)
    scaled = _accuracy(knn.fit(zscore(X_tr_d), y_tr).predict(zscore(X_te_d)), y_te)
    assert scaled > unscaled


def test_unknown_metric_rejected():
    try:
        KNNClassifier(k=3, metric="hamming")
    except ValueError:
        return
    raise AssertionError("an unknown metric must raise ValueError")
```

## Done When

```
python -m pytest exercises/module1/knn-voting
```

All four tests pass. Your classifier agrees with scikit-learn's on the same split; scaled Iris
accuracy clears 0.90; z-scoring recovers accuracy that the distorted feature destroyed; an
unknown metric raises `ValueError`.

## Stretch

Run a k-sweep over {1, 3, 5, 11, 21} on z-scored Iris with Euclidean distance and print the
accuracy at each k. Then repeat at k=5 with Euclidean, Manhattan, and cosine. Report which k and
which metric wins, and write two sentences explaining the cosine result in terms of what Iris
features actually represent (spatial measurements, not frequency profiles). The numbers you get
should match the lesson table; if they do not, you have a bug in `_predict_one`.
