# Exercise: Bagging and Random Forests

**Goal:** Create `exercises/ml/ensemble.py` and add `RandomForestClassifier` to it,
reusing `DecisionTreeClassifier` from `ml.tree`. Verify the forest against scikit-learn
on breast cancer classification.

**Why:** Building the forest yourself locks in exactly what bootstrap sampling means in
code: sample rows with replacement, restrict features at each tree, collect majority
votes. After this exercise you can read any random forest implementation and recognize
the three mechanical steps (bootstrap, train, aggregate) in whatever form they take.
The acceptance gate compares your forest against scikit-learn's on the same data; if
they agree on 90% or more of the test labels, the algorithm is correct.

## The Shared Artifact

Before touching any file, list the contents of `exercises/ml/` and read each file.
Module 3 placed `DecisionTreeClassifier` in `exercises/ml/tree.py`. You are creating a
new file, `exercises/ml/ensemble.py`, and adding `RandomForestClassifier` to it.

The reuse is real and must stay real: `RandomForestClassifier.fit` instantiates
`DecisionTreeClassifier` objects imported from `ml.tree`. Do not copy the tree class.
Do not re-implement the split logic. The throughline: `ml/tree.py` holds all tree
building; `ml/ensemble.py` holds all ensemble logic that wraps those trees.

Current package state entering this exercise:

```
exercises/ml/
  __init__.py        (empty, marks the package)
  distances.py       (M1: Euclidean, Manhattan, Cosine; two scalers)
  knn.py             (M1: KNNClassifier importing from ml.distances)
  tree.py            (M3: entropy, gini, information_gain, _Node, DecisionTreeClassifier)
```

You are adding:

```
exercises/ml/
  ensemble.py        (M4 lesson 1: RandomForestClassifier)
```

## Steps

### 1. Confirm the Current Package State

Open `exercises/ml/tree.py` and verify that `DecisionTreeClassifier` is present and
exports `predict`. Understand the module-level imports already in place.

### 2. Create `exercises/ml/ensemble.py`

The file starts with the module docstring and imports. Then add `RandomForestClassifier`
exactly as shown in the lesson. The complete file for this lesson:

```python
"""Ensemble methods, from scratch in NumPy.

Two ideas housed here:

1. Bagging + random feature subsets -> RandomForestClassifier.
   Each tree sees a bootstrap sample of rows and a random subset of features.
   Prediction is majority vote. Variance falls; bias stays flat.

2. Gradient boosting -> GradientBoostingRegressor.
   Fit weak regressors (shallow trees) sequentially to the residuals of the
   ensemble so far. Each stage nudges the prediction in the direction of
   steepest descent of MSE. The ensemble is additive:
       F_m(x) = base + lr * sum_{i=1}^{m} h_i(x)
   where h_i is trained on y - F_{i-1}(x).

No sklearn inside the algorithms. Pure NumPy + ml.tree.
"""
from __future__ import annotations

from typing import List, Optional, Union

import numpy as np

from ml.tree import DecisionTreeClassifier, DecisionTreeRegressor


# ---------------------------------------------------------------------------
# RandomForestClassifier
# ---------------------------------------------------------------------------

class RandomForestClassifier:
    """Bootstrap-aggregated ensemble of DecisionTreeClassifiers with random
    feature subsets.

    Parameters
    ----------
    n_estimators : int
        Number of trees in the forest.
    max_depth : int or None
        Maximum depth for each tree.
    max_features : "sqrt" or int
        Number of features to consider at each tree. "sqrt" -> int(sqrt(n_features)).
    min_samples_split : int
        Passed through to each tree.
    random_state : int or None
        Seeds a numpy Generator for reproducibility.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        max_features: Union[str, int] = "sqrt",
        min_samples_split: int = 2,
        random_state: Optional[int] = None,
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.max_features = max_features
        self.min_samples_split = min_samples_split
        self.random_state = random_state

        self.estimators_: List[DecisionTreeClassifier] = []
        self.feature_indices_: List[np.ndarray] = []
        self.n_classes_: int = 0

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestClassifier":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        n_samples, n_features = X.shape
        self.n_classes_ = int(y.max()) + 1

        rng = np.random.default_rng(self.random_state)

        # Resolve max_features to an integer count
        if self.max_features == "sqrt":
            k = max(1, int(np.sqrt(n_features)))
        elif isinstance(self.max_features, int):
            k = min(self.max_features, n_features)
        else:
            raise ValueError(f"max_features must be 'sqrt' or int, got {self.max_features!r}")

        self.estimators_ = []
        self.feature_indices_ = []

        for _ in range(self.n_estimators):
            # Bootstrap sample (rows with replacement)
            row_idx = rng.integers(0, n_samples, size=n_samples)
            # Random feature subset (without replacement)
            feat_idx = rng.choice(n_features, size=k, replace=False)
            feat_idx.sort()   # stable column order; purely cosmetic

            X_boot = X[row_idx][:, feat_idx]
            y_boot = y[row_idx]

            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
            )
            tree.fit(X_boot, y_boot)

            self.estimators_.append(tree)
            self.feature_indices_.append(feat_idx)

        return self

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        # Collect votes: shape (n_estimators, n_samples)
        votes = np.stack(
            [
                tree.predict(X[:, feat_idx])
                for tree, feat_idx in zip(self.estimators_, self.feature_indices_)
            ],
            axis=0,
        )   # shape: (n_estimators, n_samples)

        n_samples = X.shape[0]
        # Majority vote per sample
        preds = np.zeros(n_samples, dtype=int)
        for i in range(n_samples):
            counts = np.bincount(votes[:, i], minlength=self.n_classes_)
            preds[i] = int(np.argmax(counts))
        return preds
```

Note the import line imports `DecisionTreeRegressor` as well. That class does not exist
in `ml/tree.py` yet; it will be added in the next lesson. The import does not fail now
because `GradientBoostingRegressor` (which uses `DecisionTreeRegressor`) is also not
present yet. Add both classes together in the next lesson; for this exercise the import
line is there to avoid modifying the file again later.

### 3. Run the Acceptance Gate

The locked test suite is at
`exercises/module4/bagging-and-random-forests/test_forest.py`. It is already in place;
do not modify it.

```python
"""Acceptance gate for DecisionTreeRegressor and RandomForestClassifier.

DecisionTreeRegressor on a seeded 1-D signal:
- reduces test MSE vs the constant-mean baseline.
- agrees with sklearn.tree.DecisionTreeRegressor within tolerance.

RandomForestClassifier on breast_cancer (stratified 80/20, random_state=0):
- clears >= 0.93 test accuracy.
- beats a single DecisionTreeClassifier of the same max_depth on the same split.
- agrees with sklearn.ensemble.RandomForestClassifier on >= 90% of test labels.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier as SklearnRF
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as SklearnDTC
from sklearn.tree import DecisionTreeRegressor as SklearnDTR

from ml.ensemble import RandomForestClassifier
from ml.tree import DecisionTreeClassifier, DecisionTreeRegressor


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TREE_MAX_DEPTH = 4
FOREST_N_ESTIMATORS = 100
FOREST_MAX_DEPTH = 6
RANDOM_STATE = 0


def _regression_split():
    """Seeded 1-D regression signal: noisy sine wave."""
    rng = np.random.default_rng(42)
    n = 200
    X = rng.uniform(0, 2 * np.pi, size=(n, 1))
    y = np.sin(X[:, 0]) + rng.normal(0, 0.1, size=n)
    return train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)


def _cancer_split():
    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)


# ---------------------------------------------------------------------------
# DecisionTreeRegressor tests
# ---------------------------------------------------------------------------

def test_regressor_beats_mean_baseline():
    """From-scratch regressor must reduce MSE below the constant-mean baseline."""
    X_tr, X_te, y_tr, y_te = _regression_split()

    reg = DecisionTreeRegressor(max_depth=TREE_MAX_DEPTH).fit(X_tr, y_tr)
    preds = reg.predict(X_te)

    baseline_mse = float(np.mean((y_te - np.mean(y_tr)) ** 2))
    tree_mse = float(np.mean((y_te - preds) ** 2))

    assert tree_mse < baseline_mse, (
        f"Tree MSE {tree_mse:.4f} is not better than mean baseline {baseline_mse:.4f}"
    )


def test_regressor_agrees_with_sklearn():
    """From-scratch regressor must agree with sklearn's on held-out predictions.

    Agreement is measured as Pearson correlation >= 0.98 (exact values diverge
    only due to tie-breaking; structure should be nearly identical).
    """
    X_tr, X_te, y_tr, y_te = _regression_split()

    scratch = DecisionTreeRegressor(max_depth=TREE_MAX_DEPTH).fit(X_tr, y_tr)
    sk = SklearnDTR(max_depth=TREE_MAX_DEPTH, random_state=RANDOM_STATE).fit(X_tr, y_tr)

    p_scratch = scratch.predict(X_te)
    p_sk = sk.predict(X_te)

    corr = float(np.corrcoef(p_scratch, p_sk)[0, 1])
    assert corr >= 0.98, (
        f"Prediction correlation with sklearn = {corr:.4f} (below 0.98)"
    )


# ---------------------------------------------------------------------------
# RandomForestClassifier tests
# ---------------------------------------------------------------------------

def test_forest_clears_accuracy_floor():
    """From-scratch RandomForest must reach >= 0.93 test accuracy on breast_cancer."""
    X_tr, X_te, y_tr, y_te = _cancer_split()
    rf = RandomForestClassifier(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)
    acc = float(np.mean(rf.predict(X_te) == y_te))
    assert acc >= 0.93, f"Forest test accuracy {acc:.4f} is below 0.93 floor"


def test_forest_beats_single_tree():
    """RandomForest must be >= the single tree accuracy on the same split."""
    X_tr, X_te, y_tr, y_te = _cancer_split()

    single = DecisionTreeClassifier(max_depth=FOREST_MAX_DEPTH).fit(X_tr, y_tr)
    forest = RandomForestClassifier(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)

    acc_single = float(np.mean(single.predict(X_te) == y_te))
    acc_forest = float(np.mean(forest.predict(X_te) == y_te))

    assert acc_forest >= acc_single, (
        f"Forest acc {acc_forest:.4f} < single tree acc {acc_single:.4f}"
    )


def test_forest_agrees_with_sklearn():
    """From-scratch and sklearn forests must agree on >= 90% of test labels."""
    X_tr, X_te, y_tr, y_te = _cancer_split()

    scratch_rf = RandomForestClassifier(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)
    sk_rf = SklearnRF(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)

    p_scratch = scratch_rf.predict(X_te)
    p_sk = sk_rf.predict(X_te)

    agreement = float(np.mean(p_scratch == p_sk))
    assert agreement >= 0.90, (
        f"Label agreement with sklearn = {agreement:.4f} (below 0.90)"
    )
```

## Done When

```
python -m pytest exercises/module4/bagging-and-random-forests
```

All four tests pass: `DecisionTreeRegressor` beats the mean baseline and correlates
with scikit-learn at or above 0.98; `RandomForestClassifier` clears 0.93 accuracy,
beats the single tree, and agrees with scikit-learn on 90% or more of breast cancer
test labels.

## Stretch

After the tests pass, instrument the forest to track out-of-bag (OOB) accuracy. For
each bootstrap sample, the rows not drawn (the 36.8% of unique samples that were left
out) are the OOB set for that tree. Average the OOB predictions across all trees that
did not see each sample. Compare the OOB accuracy to the held-out test accuracy. If they
are close, you have a free validation estimate that required no separate split.
