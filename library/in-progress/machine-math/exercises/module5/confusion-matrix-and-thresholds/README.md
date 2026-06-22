# Exercise: The Confusion Matrix and Thresholds

**Goal:** Create `exercises/ml/metrics.py` and add `confusion_matrix`, `accuracy`,
`precision`, `recall`, and `f1` to it. Verify each function against scikit-learn on a
fixed binary vector and confirm the imbalance failure case.

**Why:** After this exercise you can read any confusion-matrix report and name what each
cell means in terms of real cost. You will also have built the gate that catches the
single most common evaluation mistake in production: reporting accuracy on an imbalanced
dataset and calling it a success.

## The Shared Artifact

Before touching any file, list the contents of `exercises/ml/` and read each file that
exists. Earlier modules placed distance metrics, a KNN classifier, a decision tree, and
ensemble methods in that package. You are creating a new file, `exercises/ml/metrics.py`,
and this file must not duplicate anything already there.

The throughline: `ml/metrics.py` houses all evaluation logic. Later lessons in this module
add `roc_curve`, `roc_auc`, regression metrics, and `slice_metric` to the same file. The
capstone imports `ml.metrics` directly; do not move the file or rename its entry points.

Current package state entering this exercise:

```
exercises/ml/
  __init__.py        (empty, marks the package)
  distances.py       (M1: Euclidean, Manhattan, Cosine; two scalers)
  knn.py             (M1: KNNClassifier importing from ml.distances)
  tree.py            (M3: entropy, gini, information_gain, _Node,
                          DecisionTreeClassifier, DecisionTreeRegressor)
  ensemble.py        (M4: RandomForestClassifier, GradientBoostingRegressor)
```

You are adding:

```
exercises/ml/
  metrics.py         (M5 lesson 1: confusion_matrix, accuracy, precision,
                                   recall, f1)
```

## Steps

### 1. Confirm the Current Package State

Open `exercises/ml/` and verify which files exist. Understand what each exports. You are
not modifying any existing file.

### 2. Create `exercises/ml/metrics.py`

The file begins with the module docstring and the `numpy` import, then defines the helper
`_check_binary`, then `confusion_matrix`, then `accuracy`, `precision`, `recall`, and
`f1`. Add them exactly as shown in the lesson. The complete starting state of the file for
this lesson:

```python
"""ml/metrics.py -- from-scratch evaluation metrics (pure NumPy).

Classification
--------------
confusion_matrix(y_true, y_pred)
    Binary {0,1} labels. Returns a 2x2 NumPy array:

        [[TN, FP],
         [FN, TP]]

    Row = actual class (0 top, 1 bottom).
    Col = predicted class (0 left, 1 right).

accuracy(y_true, y_pred)
precision(y_true, y_pred)   -- 0.0 when TP+FP == 0
recall(y_true, y_pred)      -- 0.0 when TP+FN == 0
f1(y_true, y_pred)          -- 0.0 when precision+recall == 0

ROC / AUC
---------
roc_curve(y_true, y_score)  -> (fpr, tpr, thresholds)
    Sweeps every unique score as a threshold (descending).  First point is
    (0, 0) at threshold above max score; last point is (1, 1) at threshold
    below min score.

roc_auc(y_true, y_score)    -> float in [0, 1]
    Trapezoidal area under the ROC curve (agrees with sklearn to float tol).

Regression
----------
mae(y_true, y_pred)
rmse(y_true, y_pred)
r2(y_true, y_pred)

Slicing
-------
slice_metric(y_true, y_pred, groups, metric_fn) -> dict {group_label: score}
    Evaluates metric_fn(y_true_slice, y_pred_slice) for each unique group.
"""
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_binary(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    return y_true, y_pred


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------

def confusion_matrix(y_true, y_pred):
    """Return 2x2 confusion matrix for binary labels {0, 1}.

    Layout:
        [[TN, FP],
         [FN, TP]]
    """
    y_true, y_pred = _check_binary(y_true, y_pred)
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return np.array([[tn, fp], [fn, tp]], dtype=int)


# ---------------------------------------------------------------------------
# Point metrics derived from the confusion matrix
# ---------------------------------------------------------------------------

def accuracy(y_true, y_pred):
    """Fraction of correct predictions."""
    y_true, y_pred = _check_binary(y_true, y_pred)
    return float(np.mean(y_true == y_pred))


def precision(y_true, y_pred):
    """TP / (TP + FP).  Returns 0.0 when denominator is 0."""
    cm = confusion_matrix(y_true, y_pred)
    tp = cm[1, 1]
    fp = cm[0, 1]
    denom = tp + fp
    return float(tp / denom) if denom > 0 else 0.0


def recall(y_true, y_pred):
    """TP / (TP + FN).  Returns 0.0 when denominator is 0."""
    cm = confusion_matrix(y_true, y_pred)
    tp = cm[1, 1]
    fn = cm[1, 0]
    denom = tp + fn
    return float(tp / denom) if denom > 0 else 0.0


def f1(y_true, y_pred):
    """Harmonic mean of precision and recall.  Returns 0.0 when both are 0."""
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    denom = p + r
    return float(2 * p * r / denom) if denom > 0 else 0.0
```

Leave the ROC / AUC and regression sections as stubs or comments for now. The next lesson
fills them in.

### 3. Run the Acceptance Gate

The locked test suite is at
`exercises/module5/confusion-matrix-and-thresholds/test_classification_metrics.py`.
Do not modify it.

```python
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
```

## Done When

```
python -m pytest exercises/module5/confusion-matrix-and-thresholds
```

All eight tests pass: every metric matches scikit-learn on the fixed binary fixture;
the imbalance case shows accuracy >= 0.90 and minority recall == 0.0; all three
zero-division paths return 0.0 without NaN or crash.

## Stretch

After the tests pass, add a `threshold_sweep` function to `ml/metrics.py` (do not modify
the acceptance gate). It should accept `y_true` and `y_score`, sweep tau from 0.01 to 0.99
in steps of 0.01, compute precision and recall at each step by thresholding `y_score`,
and return a list of `(tau, precision, recall)` tuples. Plot the result. Where does the
F1-maximizing threshold land on this curve, and is it 0.5?
