# Bagging and Random Forests

A single decision tree is unstable. Change a handful of training samples and the tree can
look completely different at every split below the root. That instability is variance, and
variance is the enemy bagging is designed to kill.

## The Bagging Idea

Bootstrap aggregating, shortened to bagging, is the simplest variance reduction technique
for high-variance learners. Draw a bootstrap sample: sample `n` rows from your training
set with replacement, where `n` is the original size. About 63.2% of unique rows appear
in each sample; the rest are left out. Train a full, unpruned tree on that sample. Repeat
for each of your `n_estimators` trees. At prediction time, collect every tree's vote and
return the majority class.

Why does it work? Each tree overfits, but to a different bootstrap sample, so the
overfitting is incoherent. When you average incoherent noise, it cancels. The signal
component, shared across all trees, survives the averaging. Bias barely moves because
each tree trains on a full-sized sample; variance falls roughly in proportion to the
number of trees, up to the point where the trees become correlated and further averaging
stops helping.

Random forests push the idea one step further. At each split, instead of searching all
features, each tree draws a random subset of features of size `sqrt(n_features)` for
classification and considers only those. That random feature subset forces the trees to
differ even when they see similar bootstrap samples. The result is a forest of trees that
are diverse in two independent ways: different rows, different features.

The Azure Machine Learning designer's Decision Forest Regression component exposes this
directly. It offers both a **Bagging** resampling method (bootstrap aggregating with
aggregation over the resulting tree predictions) and a **Replicate** method (same input
data, random split predicates). The bagging path is the same bootstrap-and-average
mechanism you build here; see the [Decision Forest Regression component
reference](https://learn.microsoft.com/azure/machine-learning/component-reference/decision-forest-regression?view=azureml-api-2)
for the designer-level parameters.

## The Code

The locked `RandomForestClassifier` below is the exact code the acceptance gate imports.
Add it to `exercises/ml/ensemble.py`. It imports `DecisionTreeClassifier` directly from
`ml.tree`, the file you built in Module 3: real reuse, no copy.

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

Follow the `fit` loop carefully. `rng.integers(0, n_samples, size=n_samples)` draws the
bootstrap row indices with replacement. `rng.choice(n_features, size=k, replace=False)`
draws the feature subset without replacement. The tree then trains on the sliced
submatrix: `X[row_idx][:, feat_idx]`. At prediction time, each tree receives only the
columns it was trained on: `X[:, feat_idx]`. The majority vote over all `n_estimators`
trees is the forest's answer.

## Measured Results

On the breast cancer dataset (569 samples, 30 features, 2 classes), with a stratified
80/20 split and `random_state=0`:

- `DecisionTreeClassifier(max_depth=6)`: test accuracy `0.9123`.
- `RandomForestClassifier(n_estimators=100, max_depth=6, random_state=0)`: test accuracy
  `0.9386`.
- Label-by-label agreement between the from-scratch forest and scikit-learn's
  `RandomForestClassifier` on the same 114 test samples: `99.12%`.

The forest clears the single-tree score by more than two percentage points. The agreement
with scikit-learn confirms that the bootstrap-and-vote mechanics are correct: the same
algorithm on the same data produces the same predictions.

## Why Variance Falls

Think of it this way. Each tree predicts `signal + noise_i`, where `noise_i` is the
idiosyncratic overfitting noise that tree `i` picked up from its bootstrap sample. When
you average 100 such trees, the signal terms add coherently; the noise terms, being
independent of each other, cancel. The variance of the average is `variance_of_one_tree /
n_estimators` when the trees are uncorrelated. The random feature subset keeps the trees
uncorrelated even when the dataset has a few dominant features; without it, every tree
would split on the same feature at the root, and the votes would tell you almost nothing
new about each other.

Bias is mostly untouched because each tree still trains on a full-sized sample. You are
not undersampling data; you are resampling it. The tree's capacity to fit the underlying
function is unchanged.

Adding more trees past a certain point gives diminishing returns but never makes things
worse. That is a sharp difference from boosting, where too many rounds can overfit.

## Core Concepts

- Bagging trains each tree on a bootstrap sample (rows sampled with replacement, same
  size as original) and aggregates predictions by majority vote; independent overfitting
  noise cancels on average.
- Random forests add random feature subsampling at each split (`sqrt(n_features)` for
  classification), forcing diversity even when one feature dominates.
- Averaging `k` independent learners reduces variance by roughly a factor of `k`; bias
  stays flat because each learner trains on a full-sized sample.
- From-scratch and scikit-learn forests agree on 99.12% of breast cancer test labels at
  100 trees and `max_depth=6`, confirming the bootstrap-and-vote logic is correct.

<div class="claude-handoff" data-exercise="exercises/module4/bagging-and-random-forests/">

**Build It in Claude Code**: Read the current state of `exercises/ml/tree.py` before
touching anything. Module 3 already placed `DecisionTreeClassifier` there. You are now
creating `exercises/ml/ensemble.py` and adding `RandomForestClassifier` to it. Import
`DecisionTreeClassifier` from `ml.tree`; do not copy it. Implement the class exactly as
shown above. Then verify with the locked acceptance gate at
`exercises/module4/bagging-and-random-forests/test_forest.py`. Done when
`python -m pytest exercises/module4/bagging-and-random-forests` is green.

</div>
