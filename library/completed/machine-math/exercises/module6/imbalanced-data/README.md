# Exercise: Imbalanced Data

**Goal:** Add `random_oversample`, `random_undersample`, and `class_weights` to
`exercises/ml/features.py`. The gate asserts that logistic regression trained on raw
95/5 imbalanced data has low minority recall (the problem), and that after
`random_oversample` balances the training classes, minority recall rises materially (the
fix).

**Why:** A model that predicts the majority class on every sample achieves 0.95 accuracy
and 0.0 minority recall. That number, not the accuracy, is what determines whether a
fraud-detection or medical-diagnosis model is useful. This exercise makes you produce
both numbers, prove the gap, and confirm that resampling closes it.

## The Shared Artifact

This exercise adds three functions to `exercises/ml/features.py`. Before writing
anything, list `exercises/ml/` and read `features.py` to see what is already there from
earlier modules. Do not duplicate any function that exists. The three new functions are
the M6 additions to that package.

The gate also imports `ml.logreg.LogisticRegression` and `ml.metrics.recall`. Confirm
both exist in the package before writing the test file.

## Steps

### 1. Add the Resampling Functions

Open `exercises/ml/features.py` and append the following three functions. Do not alter
any code already in the file.

```python
def random_oversample(
    X: np.ndarray,
    y: np.ndarray,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Duplicate minority-class rows (with replacement) until classes are balanced.

    All majority-class samples are kept. The minority class is upsampled
    (bootstrap draw) to match the majority count. If more than two classes
    are present, every class below the maximum count is oversampled to the
    maximum count.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    random_state : int or None

    Returns
    -------
    X_res, y_res : balanced arrays (order: original rows first, then synthetic)
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    rng = np.random.default_rng(random_state)

    classes, counts = np.unique(y, return_counts=True)
    max_count = int(counts.max())

    X_parts = [X]
    y_parts = [y]

    for cls, cnt in zip(classes, counts):
        deficit = max_count - cnt
        if deficit > 0:
            idx = np.where(y == cls)[0]
            extra = rng.choice(idx, size=deficit, replace=True)
            X_parts.append(X[extra])
            y_parts.append(y[extra])

    return np.vstack(X_parts), np.concatenate(y_parts)


def random_undersample(
    X: np.ndarray,
    y: np.ndarray,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Drop majority-class rows until all classes have the minority count.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    random_state : int or None

    Returns
    -------
    X_res, y_res : balanced arrays (row order not guaranteed)
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    rng = np.random.default_rng(random_state)

    classes, counts = np.unique(y, return_counts=True)
    min_count = int(counts.min())

    keep_idx = []
    for cls in classes:
        idx = np.where(y == cls)[0]
        chosen = rng.choice(idx, size=min_count, replace=False)
        keep_idx.append(chosen)

    keep = np.concatenate(keep_idx)
    keep.sort()          # consistent ordering
    return X[keep], y[keep]


def class_weights(y: np.ndarray) -> dict:
    """Compute inverse-frequency class weights, normalized so they sum to n_classes.

    Weight for class c:
        w_c = n_samples / (n_classes * count_c)

    This matches sklearn's "balanced" mode and ensures the weighted loss treats
    each class equally regardless of sample count.

    Parameters
    ----------
    y : array-like, shape (n,)

    Returns
    -------
    dict mapping each unique class label to its weight (float).
    """
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    n_samples = len(y)
    n_classes = len(classes)
    weights = {}
    for cls, cnt in zip(classes, counts):
        weights[cls] = float(n_samples / (n_classes * cnt))
    return weights
```

You will also need these imports at the top of `features.py` if they are not already
present:

```python
from typing import Optional, Tuple
import numpy as np
```

### 2. Place the Acceptance Gate

Create `exercises/module6/imbalanced-data/test_imbalance.py` with the exact content
below. Do not modify it.

```python
"""Acceptance gate: imbalanced data -- resampling strategies.

Tests
-----
1. NEGATIVE CASE: minority recall is low (< 0.5) on raw 95/5 data with overlapping classes.
2. POSITIVE FIX: after random_oversample, minority recall rises materially above raw recall.
3. random_oversample returns balanced class counts.
4. random_undersample returns balanced class counts.

Dataset design
--------------
To make the imbalance effect visible, we need two ingredients working together:
- Severe imbalance (5% minority) so the majority class dominates the gradient.
- Overlapping class distributions (means 0.5 apart, std 1.0) so logistic regression
  needs the minority signal but can't easily distinguish the boundary.
At 5% minority, logistic regression trained with gradient descent tends to collapse
to all-majority predictions (minority recall = 0.0) because moving the decision
boundary away from the majority costs more in cross-entropy than the small minority
gain. After oversampling, the classes are balanced and the minority signal guides the
gradient, lifting recall materially.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest

from ml.features import random_oversample, random_undersample
from ml.logreg import LogisticRegression
from ml.metrics import recall


# ---------------------------------------------------------------------------
# Dataset factory
# ---------------------------------------------------------------------------

def _make_imbalanced(n=1000, minority_frac=0.05, overlap=0.5, seed=42):
    """Binary dataset: ~95% majority (0), ~5% minority (1).

    Classes overlap (mean separation = overlap) so the decision boundary is
    not trivially learned from the few minority examples.
    """
    rng = np.random.default_rng(seed)
    n_majority = int(n * (1 - minority_frac))
    n_minority = n - n_majority

    X_maj = rng.normal(0.0, 1.0, size=(n_majority, 2))
    X_min = rng.normal(overlap, 1.0, size=(n_minority, 2))

    X = np.vstack([X_maj, X_min])
    y = np.concatenate([np.zeros(n_majority, dtype=int),
                        np.ones(n_minority, dtype=int)])
    return X, y


def _split(X, y, test_frac=0.2, seed=0):
    """Simple deterministic train/test split."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    n_test = int(len(y) * test_frac)
    test_idx = idx[:n_test]
    train_idx = idx[n_test:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


# ---------------------------------------------------------------------------
# Shared data (module-level so tests share the same split)
# ---------------------------------------------------------------------------

X_ALL, y_ALL = _make_imbalanced(n=1000, minority_frac=0.05, overlap=0.5, seed=42)
X_TRAIN, X_TEST, y_TRAIN, y_TEST = _split(X_ALL, y_ALL, test_frac=0.2, seed=0)


# ---------------------------------------------------------------------------
# 1. NEGATIVE CASE: raw data -> low minority recall
# ---------------------------------------------------------------------------

def test_raw_minority_recall_is_low():
    """Logistic regression on raw 95/5 imbalanced data has minority recall < 0.5.

    With 5% minority and overlapping distributions, GD collapses to mostly
    predicting the majority class, yielding recall < 0.5 on the minority.
    """
    clf = LogisticRegression(lr=0.1, n_iters=300)
    clf.fit(X_TRAIN, y_TRAIN)
    y_pred = clf.predict(X_TEST)
    raw_recall = recall(y_TEST, y_pred)
    assert raw_recall < 0.5, (
        f"Expected raw minority recall < 0.5 to demonstrate the imbalance problem; "
        f"got {raw_recall:.4f}"
    )


# ---------------------------------------------------------------------------
# 2. POSITIVE FIX: oversampling raises minority recall materially
# ---------------------------------------------------------------------------

def test_oversample_improves_minority_recall():
    """After oversampling the minority class, recall rises above the raw baseline."""
    # Raw baseline
    clf_raw = LogisticRegression(lr=0.1, n_iters=300)
    clf_raw.fit(X_TRAIN, y_TRAIN)
    raw_recall = recall(y_TEST, clf_raw.predict(X_TEST))

    # Oversampled
    X_res, y_res = random_oversample(X_TRAIN, y_TRAIN, random_state=0)
    clf_over = LogisticRegression(lr=0.1, n_iters=300)
    clf_over.fit(X_res, y_res)
    over_recall = recall(y_TEST, clf_over.predict(X_TEST))

    assert over_recall > raw_recall, (
        f"Oversampled recall ({over_recall:.4f}) should exceed raw recall ({raw_recall:.4f})"
    )
    # Require a clear margin so the test is meaningful
    assert over_recall - raw_recall >= 0.10, (
        f"Expected at least 0.10 recall improvement, got {over_recall - raw_recall:.4f}"
    )


# ---------------------------------------------------------------------------
# 3. random_oversample returns balanced counts
# ---------------------------------------------------------------------------

def test_oversample_balanced_counts():
    X_res, y_res = random_oversample(X_TRAIN, y_TRAIN, random_state=1)
    _, counts = np.unique(y_res, return_counts=True)
    assert counts[0] == counts[1], (
        f"After oversampling, class counts should be equal; got {counts}"
    )


# ---------------------------------------------------------------------------
# 4. random_undersample returns balanced counts
# ---------------------------------------------------------------------------

def test_undersample_balanced_counts():
    X_res, y_res = random_undersample(X_TRAIN, y_TRAIN, random_state=2)
    _, counts = np.unique(y_res, return_counts=True)
    assert counts[0] == counts[1], (
        f"After undersampling, class counts should be equal; got {counts}"
    )
```

## Done When

```
python -m pytest exercises/module6/imbalanced-data
```

All four assertions pass:

- `test_raw_minority_recall_is_low`: logistic regression on the raw 95/5 training split
  produces minority recall below 0.5; this is the imbalance problem.
- `test_oversample_improves_minority_recall`: after `random_oversample`, recall rises
  by at least 0.10 above the raw baseline; this is the fix.
- `test_oversample_balanced_counts`: `random_oversample` returns equal class counts.
- `test_undersample_balanced_counts`: `random_undersample` returns equal class counts.

Together these confirm the imbalance signature: a model trained on skewed data ignores
the minority class, and balancing the training set gives the loss function a reason to
find the decision boundary.

## Stretch

After the gate passes, try `class_weights`. Compute weights with `class_weights(y_TRAIN)`
and pass them to `LogisticRegression` if your implementation supports a `sample_weight`
argument, or apply them manually by scaling the per-sample loss. Does minority recall
improve compared to the raw baseline? Compare the weighted model's recall to the
oversampled model's recall. Report which strategy produced a higher recall on the test
set, and think about why.
