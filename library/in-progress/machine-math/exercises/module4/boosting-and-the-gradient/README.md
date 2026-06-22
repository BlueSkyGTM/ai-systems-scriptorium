# Exercise: Boosting and the Gradient

**Goal:** Append `_NodeReg` and `DecisionTreeRegressor` to `exercises/ml/tree.py`, then
add `GradientBoostingRegressor` to `exercises/ml/ensemble.py`. Verify both against
scikit-learn on the Friedman-1 regression dataset.

**Why:** Building the booster yourself makes the gradient-descent-in-function-space
connection tangible. You will write the line `residuals = y - current` and watch what
happens round by round: the residuals shrink, the training MSE falls monotonically, and
the final ensemble produces predictions within 0.07% of scikit-learn's. That number
tells you the algorithm is mechanically correct before you ever open a tuning dashboard.

## The Shared Artifact

Before touching any file, read `exercises/ml/tree.py` and `exercises/ml/ensemble.py`
in their current state. The previous lesson left the package here:

```
exercises/ml/
  __init__.py        (empty, marks the package)
  distances.py       (M1: Euclidean, Manhattan, Cosine; two scalers)
  knn.py             (M1: KNNClassifier importing from ml.distances)
  tree.py            (M3 + M4 lesson 1: entropy, gini, information_gain,
                      _Node, DecisionTreeClassifier)
  ensemble.py        (M4 lesson 1: RandomForestClassifier)
```

You are adding:

```
exercises/ml/
  tree.py            (append: _NodeReg, DecisionTreeRegressor)
  ensemble.py        (append: GradientBoostingRegressor)
```

The `ml/ensemble.py` file already contains the import line
`from ml.tree import DecisionTreeClassifier, DecisionTreeRegressor`. Once you add
`DecisionTreeRegressor` to `ml/tree.py`, that import resolves and
`GradientBoostingRegressor` can use it. Do not modify the import line.

## Steps

### 1. Append to `exercises/ml/tree.py`

Add `_NodeReg` and `DecisionTreeRegressor` after `DecisionTreeClassifier`, at the end of
the file. Do not alter anything already there.

```python
# ---------------------------------------------------------------------------
# Regressor node + tree (added M4)
# ---------------------------------------------------------------------------

@dataclass
class _NodeReg:
    """A node in a regression tree. Either an internal split or a leaf."""
    feature: Optional[int] = None
    threshold: Optional[float] = None
    left: Optional["_NodeReg"] = None
    right: Optional["_NodeReg"] = None
    # Leaf value: mean of target in the region
    value: Optional[float] = None

    @property
    def is_leaf(self) -> bool:
        return self.value is not None


class DecisionTreeRegressor:
    """Greedy, axis-aligned decision tree regressor.

    Split criterion: variance reduction (weighted MSE). A leaf predicts the mean
    of the training targets that fell into it.

    Parameters
    ----------
    max_depth : int or None
        Maximum depth of the tree. None means grow until too few samples remain.
    min_samples_split : int
        Do not split a node that has fewer than this many samples.
    """

    def __init__(
        self,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
    ):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root_: Optional[_NodeReg] = None

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DecisionTreeRegressor":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        self.root_ = self._grow(X, y, depth=0)
        return self

    def _grow(self, X: np.ndarray, y: np.ndarray, depth: int) -> _NodeReg:
        n_samples, n_features = X.shape

        # Stopping conditions -> leaf
        too_small = n_samples < self.min_samples_split
        at_max = (self.max_depth is not None) and (depth >= self.max_depth)

        if too_small or at_max:
            return _NodeReg(value=float(np.mean(y)))

        # Find the best split by maximum variance reduction
        parent_var = float(np.var(y)) * n_samples   # proportional to MSE * n

        best_reduction = -1.0
        best_feat: Optional[int] = None
        best_thresh: Optional[float] = None

        for feat in range(n_features):
            col = X[:, feat]
            unique_vals = np.unique(col)
            if len(unique_vals) < 2:
                continue
            thresholds = (unique_vals[:-1] + unique_vals[1:]) / 2.0

            for thresh in thresholds:
                mask = col <= thresh
                left_y, right_y = y[mask], y[~mask]
                if len(left_y) == 0 or len(right_y) == 0:
                    continue
                # Weighted MSE of children
                child_var = (
                    float(np.var(left_y)) * len(left_y)
                    + float(np.var(right_y)) * len(right_y)
                )
                reduction = parent_var - child_var
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_feat = feat
                    best_thresh = thresh

        # No beneficial split -> leaf
        if best_feat is None or best_reduction <= 0.0:
            return _NodeReg(value=float(np.mean(y)))

        mask = X[:, best_feat] <= best_thresh
        left_node = self._grow(X[mask], y[mask], depth + 1)
        right_node = self._grow(X[~mask], y[~mask], depth + 1)

        return _NodeReg(
            feature=best_feat,
            threshold=best_thresh,
            left=left_node,
            right=right_node,
        )

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return np.array([self._traverse(self.root_, row) for row in X])

    def _traverse(self, node: _NodeReg, row: np.ndarray) -> float:
        if node.is_leaf:
            return node.value
        if row[node.feature] <= node.threshold:
            return self._traverse(node.left, row)
        return self._traverse(node.right, row)
```

The gain criterion is the only structural change from `DecisionTreeClassifier`. The
split loop is identical in shape; only the impurity computation differs: weighted variance
reduction instead of Gini or entropy. The leaf stores a float mean instead of an int
majority class.

### 2. Append to `exercises/ml/ensemble.py`

Add `GradientBoostingRegressor` after `RandomForestClassifier` in the same file. Do not
touch `RandomForestClassifier` or the imports.

```python
# ---------------------------------------------------------------------------
# GradientBoostingRegressor
# ---------------------------------------------------------------------------

class GradientBoostingRegressor:
    """Gradient boosting for regression (MSE loss), from scratch.

    Builds an additive ensemble of shallow DecisionTreeRegressors:
        F_0(x) = mean(y)
        F_m(x) = F_{m-1}(x) + learning_rate * h_m(x)
    where h_m is fit to the residuals r_m = y - F_{m-1}(x).

    Parameters
    ----------
    n_estimators : int
        Number of boosting rounds.
    learning_rate : float
        Shrinkage applied to each tree's contribution.
    max_depth : int
        Maximum depth for each weak learner.
    """

    def __init__(
        self,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 3,
    ):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth

        self.base_: float = 0.0
        self.estimators_: List[DecisionTreeRegressor] = []
        self.train_losses_: List[float] = []

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GradientBoostingRegressor":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)

        # F_0: constant prediction = mean(y)
        self.base_ = float(np.mean(y))
        current = np.full_like(y, self.base_)

        self.estimators_ = []
        self.train_losses_ = []

        for _ in range(self.n_estimators):
            residuals = y - current

            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=2,
            )
            tree.fit(X, residuals)

            current = current + self.learning_rate * tree.predict(X)

            self.estimators_.append(tree)
            mse = float(np.mean((y - current) ** 2))
            self.train_losses_.append(mse)

        return self

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        result = np.full(X.shape[0], self.base_)
        for tree in self.estimators_:
            result = result + self.learning_rate * tree.predict(X)
        return result
```

Read the `fit` loop before you implement it: `self.base_` is `F_0`; `current` tracks
`F_m` on the training set; `residuals = y - current` computes the negative gradient;
`current = current + self.learning_rate * tree.predict(X)` is the update step.
`self.train_losses_` stores per-round training MSE; the acceptance gate asserts it
is monotonically non-increasing.

### 3. Run the Acceptance Gate

The locked test suite is at
`exercises/module4/boosting-and-the-gradient/test_boosting.py`. It is already in place;
do not modify it. The gate runs 100 boosting rounds on 400 training samples and repeats
the fit twice (for the monotone and correlation tests), so it builds several hundred
trees total. Expect one to two minutes on a laptop.

```python
"""Acceptance gate for GradientBoostingRegressor.

On a seeded regression dataset (make_friedman1):
- clears a test R^2 floor of >= 0.80.
- per-round TRAIN loss is monotonically non-increasing.
- agrees with sklearn.ensemble.GradientBoostingRegressor: Pearson correlation
  of predictions >= 0.97 (exact match is not expected due to tie-breaking in
  the underlying trees).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import make_friedman1
from sklearn.ensemble import GradientBoostingRegressor as SklearnGB
from sklearn.model_selection import train_test_split

from ml.ensemble import GradientBoostingRegressor


# ---------------------------------------------------------------------------
# Shared data
# ---------------------------------------------------------------------------

N_ESTIMATORS = 100
LEARNING_RATE = 0.1
MAX_DEPTH = 3
RANDOM_STATE = 0


def _friedman_split():
    X, y = make_friedman1(n_samples=500, n_features=10, noise=1.0, random_state=RANDOM_STATE)
    return train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)


def _r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / ss_tot)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_gbr_clears_r2_floor():
    """GradientBoostingRegressor must reach test R^2 >= 0.80 on friedman1."""
    X_tr, X_te, y_tr, y_te = _friedman_split()
    gbr = GradientBoostingRegressor(
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
    ).fit(X_tr, y_tr)

    r2 = _r2(y_te, gbr.predict(X_te))
    assert r2 >= 0.80, f"Test R^2 {r2:.4f} is below the 0.80 floor"


def test_gbr_train_loss_monotone():
    """Per-round training MSE must be non-increasing across all boosting rounds."""
    X_tr, X_te, y_tr, y_te = _friedman_split()
    gbr = GradientBoostingRegressor(
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
    ).fit(X_tr, y_tr)

    losses = np.array(gbr.train_losses_)
    # Allow tiny floating-point rounding (1e-10 tolerance)
    diffs = np.diff(losses)
    violating = np.sum(diffs > 1e-10)
    assert violating == 0, (
        f"{violating} rounds where train loss increased. "
        f"First few diffs: {diffs[:10]}"
    )


def test_gbr_agrees_with_sklearn():
    """From-scratch GBR must correlate >= 0.97 with sklearn's predictions."""
    X_tr, X_te, y_tr, y_te = _friedman_split()

    scratch = GradientBoostingRegressor(
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
    ).fit(X_tr, y_tr)
    sk = SklearnGB(
        n_estimators=N_ESTIMATORS,
        learning_rate=LEARNING_RATE,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)

    p_scratch = scratch.predict(X_te)
    p_sk = sk.predict(X_te)

    corr = float(np.corrcoef(p_scratch, p_sk)[0, 1])
    assert corr >= 0.97, (
        f"Prediction correlation with sklearn = {corr:.4f} (below 0.97)"
    )
```

## Done When

```
python -m pytest exercises/module4/boosting-and-the-gradient
```

All three tests pass: test R-squared clears 0.80 on Friedman-1; training MSE is
monotonically non-increasing across all 100 rounds; prediction correlation with
scikit-learn clears 0.97. Expect the run to take one to two minutes.

## Stretch

After the tests pass, print `gbr.train_losses_` at rounds 1, 10, 25, 50, and 100. How
much does the loss fall in the first 10 rounds versus the last 10? Then refit with
`learning_rate=0.5` and 20 rounds versus `learning_rate=0.01` and 500 rounds. Do both
configurations reach similar test R-squared? What does that tell you about the
learning-rate-times-rounds product as a budget?
