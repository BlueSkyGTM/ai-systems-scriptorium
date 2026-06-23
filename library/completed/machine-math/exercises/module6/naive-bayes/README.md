# Exercise: Naive Bayes

**Goal:** Create `exercises/ml/naive_bayes.py` and add the `GaussianNB` class to it. The class fits a Gaussian distribution per class per feature, then at prediction time sums log-likelihoods across features and returns the argmax class. Verify against scikit-learn on the Iris dataset.

**Why:** After this exercise you have built a complete probabilistic classifier from scratch and confirmed it matches scikit-learn's output label for label. More importantly, you will understand exactly where the naive independence assumption enters (the product of per-feature likelihoods in `_log_posteriors`) and can reason about what happens when features are correlated or uninformative.

## The Shared Artifact

Before touching any file, list the contents of `exercises/ml/` and read each file that exists. Earlier modules placed the following in that package:

```
exercises/ml/
  __init__.py        (empty, marks the package)
  distances.py       (M1: Euclidean, Manhattan, Cosine; zscore; minmax_scale)
  knn.py             (M1: KNNClassifier importing from ml.distances)
  tree.py            (M3: entropy, gini, information_gain, DecisionTreeClassifier,
                          DecisionTreeRegressor)
  ensemble.py        (M4: RandomForestClassifier, GradientBoostingRegressor)
  metrics.py         (M5: confusion_matrix, accuracy, precision, recall, f1,
                          roc_curve, roc_auc, mae, rmse, r2, slice_metric)
  features.py        (M6 lesson 1: one_hot_encode, ordinal_encode;
                                   imports zscore, minmax_scale from ml.distances)
```

You are adding:

```
exercises/ml/
  naive_bayes.py     (M6 lesson 2: GaussianNB)
```

The throughline: `ml/naive_bayes.py` is a standalone module with no imports from the rest of `ml/`. It uses only NumPy. The capstone imports `ml.naive_bayes` alongside `ml.features` and `ml.metrics`. Do not move the file or rename the class.

## Steps

### 1. Confirm the Current Package State

Open `exercises/ml/` and verify which files exist. The `features.py` from the previous lesson should already be present. You are not modifying any existing file.

### 2. Create `exercises/ml/naive_bayes.py`

The file begins with the module docstring, then the imports, then the `GaussianNB` class with `__init__`, `fit`, `predict_proba`, `predict`, and `_log_posteriors`. Add them exactly as shown in the lesson:

```python
"""ml/naive_bayes.py -- Gaussian Naive Bayes classifier, from scratch in NumPy.

One idea: if you assume features are independent given the class (the "naive"
assumption), the joint likelihood factorizes into a product of per-feature
likelihoods. Model each feature as Gaussian: estimate a per-class mean and
variance from training data, then at inference multiply the Gaussian densities
(in log space to avoid underflow) and pick the class with the highest
log-posterior = log-prior + sum of log-likelihoods.

No sklearn inside the algorithm. Pure NumPy.
"""
from __future__ import annotations

from typing import Optional

import numpy as np


class GaussianNB:
    """Gaussian Naive Bayes classifier.

    Stores per-class class priors, feature means, and feature variances at
    fit time. Prediction applies the log-sum-exp trick for numerically stable
    posterior normalization.

    Parameters
    ----------
    var_smoothing : float
        Tiny variance floor added to every per-class per-feature variance to
        prevent division-by-zero when a feature is (nearly) constant within a
        class. Default 1e-9 (matches sklearn's default).
    """

    def __init__(self, var_smoothing: float = 1e-9):
        self.var_smoothing = var_smoothing
        # Fitted attributes
        self.classes_: Optional[np.ndarray] = None
        self.log_priors_: Optional[np.ndarray] = None   # shape (n_classes,)
        self.means_: Optional[np.ndarray] = None        # shape (n_classes, n_features)
        self.vars_: Optional[np.ndarray] = None         # shape (n_classes, n_features)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "GaussianNB":
        """Estimate priors, per-class per-feature means and variances."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        n_samples, n_features = X.shape

        self.classes_ = np.unique(y)
        n_classes = len(self.classes_)

        self.means_ = np.zeros((n_classes, n_features))
        self.vars_ = np.zeros((n_classes, n_features))
        self.log_priors_ = np.zeros(n_classes)

        for i, cls in enumerate(self.classes_):
            X_cls = X[y == cls]
            self.log_priors_[i] = np.log(len(X_cls) / n_samples)
            self.means_[i] = X_cls.mean(axis=0)
            raw_var = X_cls.var(axis=0)
            self.vars_[i] = raw_var + self.var_smoothing

        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return normalized class posterior probabilities."""
        log_posts = self._log_posteriors(X)
        row_max = log_posts.max(axis=1, keepdims=True)
        shifted = log_posts - row_max
        exp_shifted = np.exp(shifted)
        proba = exp_shifted / exp_shifted.sum(axis=1, keepdims=True)
        return proba

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return the class with the highest log-posterior for each sample."""
        log_posts = self._log_posteriors(X)
        best_class_idx = np.argmax(log_posts, axis=1)
        return self.classes_[best_class_idx]

    def _log_posteriors(self, X: np.ndarray) -> np.ndarray:
        """Compute log-unnormalized posteriors for all classes and samples."""
        X = np.asarray(X, dtype=float)
        n_samples = X.shape[0]
        n_classes = len(self.classes_)
        log_posts = np.zeros((n_samples, n_classes))

        for i in range(n_classes):
            mu = self.means_[i]
            var = self.vars_[i]
            log_likelihood = (
                -0.5 * np.sum(np.log(2.0 * np.pi * var))
                - 0.5 * np.sum((X - mu) ** 2 / var, axis=1)
            )
            log_posts[:, i] = self.log_priors_[i] + log_likelihood

        return log_posts
```

### 3. Run the Acceptance Gate

The locked test suite is at `exercises/module6/naive-bayes/test_naive_bayes.py`. Do not modify it.

```python
"""Acceptance gate: GaussianNB on Iris.

Tests
-----
1. GaussianNB on Iris (stratified 80/20, random_state=0) clears 0.90 test accuracy.
2. GaussianNB label agreement with sklearn.naive_bayes.GaussianNB >= 0.93.
3. predict_proba rows sum to 1 and shape is (n_samples, n_classes).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB as SklearnGNB

from ml.naive_bayes import GaussianNB


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def iris_split():
    iris = load_iris()
    X, y = iris.data, iris.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=0
    )
    return X_train, X_test, y_train, y_test


@pytest.fixture(scope="module")
def fitted_gnb(iris_split):
    X_train, X_test, y_train, y_test = iris_split
    gnb = GaussianNB()
    gnb.fit(X_train, y_train)
    return gnb


@pytest.fixture(scope="module")
def fitted_sk_gnb(iris_split):
    X_train, _, y_train, _ = iris_split
    sk = SklearnGNB()
    sk.fit(X_train, y_train)
    return sk


# ---------------------------------------------------------------------------
# 1. Accuracy floor
# ---------------------------------------------------------------------------

def test_accuracy_floor(iris_split, fitted_gnb):
    _, X_test, _, y_test = iris_split
    y_pred = fitted_gnb.predict(X_test)
    acc = float(np.mean(y_pred == y_test))
    assert acc >= 0.90, f"Expected accuracy >= 0.90, got {acc:.4f}"


# ---------------------------------------------------------------------------
# 2. Label agreement with sklearn
# ---------------------------------------------------------------------------

def test_label_agreement_sklearn(iris_split, fitted_gnb, fitted_sk_gnb):
    _, X_test, _, _ = iris_split
    our_pred = fitted_gnb.predict(X_test)
    sk_pred = fitted_sk_gnb.predict(X_test)
    agreement = float(np.mean(our_pred == sk_pred))
    assert agreement >= 0.93, (
        f"Expected label agreement with sklearn >= 0.93, got {agreement:.4f}"
    )


# ---------------------------------------------------------------------------
# 3. predict_proba shape and row-sum
# ---------------------------------------------------------------------------

def test_predict_proba_shape(iris_split, fitted_gnb):
    _, X_test, _, _ = iris_split
    proba = fitted_gnb.predict_proba(X_test)
    assert proba.shape == (X_test.shape[0], 3), (
        f"Expected shape ({X_test.shape[0]}, 3), got {proba.shape}"
    )


def test_predict_proba_sums_to_one(iris_split, fitted_gnb):
    _, X_test, _, _ = iris_split
    proba = fitted_gnb.predict_proba(X_test)
    row_sums = proba.sum(axis=1)
    np.testing.assert_allclose(row_sums, np.ones(len(row_sums)), atol=1e-9)
```

## Done When

```
python -m pytest exercises/module6/naive-bayes
```

All four tests pass: test accuracy on Iris clears 0.90; label agreement with scikit-learn's GaussianNB is at least 0.93 on the 30-test-sample split; `predict_proba` returns shape `(30, 3)`; every row of `predict_proba` sums to 1.

## Stretch

After the tests pass, add one experiment to understand where the naive assumption breaks. Generate a dataset with two features that are perfectly correlated (feature 2 = feature 1 + small noise) and two classes. Fit `GaussianNB` and scikit-learn's `LogisticRegression` on the same data. Compare test accuracy and calibration (how close `predict_proba` is to the true class rates). Does the double-counting of correlated features hurt the ranking, or only the probability magnitudes? Write your finding in a comment at the bottom of your experiment script.
