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
