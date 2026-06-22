"""Acceptance gate: confusion matrix and derived classification metrics.

Tests
-----
1. accuracy/precision/recall/f1/confusion_matrix match sklearn on a fixed
   binary (y_true, y_pred) pair.
2. Imbalance negative case: accuracy is high (>= 0.9) while minority-class
   recall is 0.0 when a model predicts all-majority.
3. Zero-division safety: precision/recall/f1 return 0.0 (not NaN/crash) when
   the denominator is 0.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix as sk_confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.metrics import (
    accuracy,
    confusion_matrix,
    f1,
    precision,
    recall,
)

TOL = 1e-9

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fixed_binary():
    """Small balanced binary fixture with a mix of TP/TN/FP/FN."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    y_pred = np.array([0, 0, 1, 1, 0, 0, 1, 1, 1, 1])
    return y_true, y_pred


# ---------------------------------------------------------------------------
# 1. Agreement with sklearn
# ---------------------------------------------------------------------------

def test_accuracy_matches_sklearn(fixed_binary):
    y_true, y_pred = fixed_binary
    assert abs(accuracy(y_true, y_pred) - accuracy_score(y_true, y_pred)) < TOL


def test_precision_matches_sklearn(fixed_binary):
    y_true, y_pred = fixed_binary
    expected = precision_score(y_true, y_pred, zero_division=0)
    assert abs(precision(y_true, y_pred) - expected) < TOL


def test_recall_matches_sklearn(fixed_binary):
    y_true, y_pred = fixed_binary
    expected = recall_score(y_true, y_pred, zero_division=0)
    assert abs(recall(y_true, y_pred) - expected) < TOL


def test_f1_matches_sklearn(fixed_binary):
    y_true, y_pred = fixed_binary
    expected = f1_score(y_true, y_pred, zero_division=0)
    assert abs(f1(y_true, y_pred) - expected) < TOL


def test_confusion_matrix_matches_sklearn(fixed_binary):
    """From-scratch [[TN,FP],[FN,TP]] must agree with sklearn's layout."""
    y_true, y_pred = fixed_binary
    sk_cm = sk_confusion_matrix(y_true, y_pred)  # sklearn: [[TN,FP],[FN,TP]]
    scratch_cm = confusion_matrix(y_true, y_pred)
    assert scratch_cm.shape == (2, 2)
    np.testing.assert_array_equal(scratch_cm, sk_cm)


# ---------------------------------------------------------------------------
# 2. Imbalance negative case
# ---------------------------------------------------------------------------

def test_imbalance_accuracy_high_recall_zero():
    """All-majority predictor: accuracy >= 0.9 but minority recall == 0.0.

    Dataset: 95 negatives, 5 positives. Model always predicts 0 (majority).
    Accuracy = 95/100 = 0.95 (looks great); minority recall = 0 (terrible).
    """
    rng = np.random.default_rng(0)
    n = 100
    # 95 negatives, 5 positives
    y_true = np.array([0] * 95 + [1] * 5)
    y_pred = np.zeros(n, dtype=int)  # always predicts majority

    acc = accuracy(y_true, y_pred)
    rec = recall(y_true, y_pred)  # recall on positive (minority) class

    assert acc >= 0.90, f"Expected accuracy >= 0.90, got {acc:.4f}"
    assert rec == 0.0, f"Expected minority recall == 0.0, got {rec:.4f}"


# ---------------------------------------------------------------------------
# 3. Zero-division safety
# ---------------------------------------------------------------------------

def test_precision_zero_division_safe():
    """precision returns 0.0 when model predicts all negatives (TP+FP == 0)."""
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 0, 0, 0])  # all negative -> no positives predicted
    result = precision(y_true, y_pred)
    assert result == 0.0
    assert not np.isnan(result)


def test_recall_zero_division_safe():
    """recall returns 0.0 when there are no positive ground-truth samples."""
    y_true = np.array([0, 0, 0, 0])  # no positives
    y_pred = np.array([1, 1, 0, 0])
    result = recall(y_true, y_pred)
    assert result == 0.0
    assert not np.isnan(result)


def test_f1_zero_division_safe():
    """f1 returns 0.0 when both precision and recall are 0."""
    y_true = np.array([1, 1, 1, 1])
    y_pred = np.array([0, 0, 0, 0])  # all misses -> precision=0, recall=0
    result = f1(y_true, y_pred)
    assert result == 0.0
    assert not np.isnan(result)
