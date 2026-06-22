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
