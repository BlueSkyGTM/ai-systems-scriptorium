# Exercise: AUC-ROC: The Math of Ranking

**Goal:** Add `roc_curve` and `roc_auc` to `exercises/ml/metrics.py`. Verify that the
from-scratch AUC matches scikit-learn to 1e-6 tolerance, that a perfect ranker scores 1.0,
and that a random scorer stays near 0.5.

**Why:** AUC is the standard model-selection metric for binary classification in production
systems, including Azure AutoML's primary metric for classification experiments. Building
the Mann-Whitney U implementation yourself makes the probability interpretation concrete:
you are literally counting the fraction of (positive, negative) pairs where the model
ranks the positive higher.

## The Shared Artifact

Before touching any file, read `exercises/ml/metrics.py` in full. The previous lesson
added `confusion_matrix`, `accuracy`, `precision`, `recall`, and `f1`. You are extending
the same file by adding `roc_curve` and `roc_auc` after the `f1` function, before any
regression stubs.

Do not move any existing function. Do not rename any existing entry point. The file stays
in `exercises/ml/metrics.py`; the package layout does not change.

Current state of `exercises/ml/metrics.py` entering this exercise:

```
- module docstring (includes stubs for ROC/AUC and regression sections)
- import numpy as np
- _check_binary helper
- confusion_matrix
- accuracy
- precision
- recall
- f1
- (ROC and regression sections: stubs or empty)
```

You are adding:

```
- roc_curve
- roc_auc
```

## Steps

### 1. Read the Current File

Open `exercises/ml/metrics.py` and locate the end of the `f1` function. That is where
the two new functions go.

### 2. Add `roc_curve` and `roc_auc`

Add the functions exactly as shown in the lesson. The code for both:

```python
# ---------------------------------------------------------------------------
# ROC curve and AUC
# ---------------------------------------------------------------------------

def roc_curve(y_true, y_score):
    """Sweep score thresholds and return (fpr, tpr, thresholds).

    Thresholds are the unique score values in descending order, with an
    extra sentinel above the maximum (so the first operating point is (0,0)).
    Ties (multiple samples with the same score) are resolved by grouping
    them: all tied samples flip together when the threshold crosses their
    shared score value.  This ensures each unique score produces exactly
    one ROC point, matching sklearn's tie-handling convention.

    Arrays are aligned: fpr[i], tpr[i] is the rate state when predicting
    positive for every sample with score >= thresholds[i].
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    # Sort all samples by score descending (ties broken arbitrarily; they
    # will be grouped together below).
    desc_idx = np.argsort(y_score)[::-1]
    sorted_scores = y_score[desc_idx]
    sorted_labels = y_true[desc_idx]

    # Walk through sorted samples, accumulating TP and FP.
    # Each time we encounter a new (lower) score we emit an ROC point first,
    # then process all samples sharing the previous score level.
    fprs = [0.0]
    tprs = [0.0]
    # Collect threshold values corresponding to each emitted point.
    # The sentinel "above max" corresponds to the (0,0) starting point.
    thresh_vals = [sorted_scores[0] + 1.0]

    tp = 0
    fp = 0
    i = 0
    n = len(sorted_labels)
    while i < n:
        # Find the run of samples that share the current score value.
        current_score = sorted_scores[i]
        j = i
        while j < n and sorted_scores[j] == current_score:
            if sorted_labels[j] == 1:
                tp += 1
            else:
                fp += 1
            j += 1
        # Emit one ROC point for this score level.
        fprs.append(fp / n_neg if n_neg > 0 else 0.0)
        tprs.append(tp / n_pos if n_pos > 0 else 0.0)
        thresh_vals.append(current_score)
        i = j

    return np.array(fprs), np.array(tprs), np.array(thresh_vals)


def roc_auc(y_true, y_score):
    """Area under the ROC curve.

    Uses the rank-based Mann-Whitney U formula, which is equivalent to the
    trapezoidal area but handles ties exactly (no discretization gap).
    Agrees with sklearn.metrics.roc_auc_score to floating-point precision.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))
    if n_pos == 0 or n_neg == 0:
        raise ValueError("roc_auc requires at least one positive and one negative sample.")

    pos_scores = y_score[y_true == 1]
    neg_scores = y_score[y_true == 0]

    # U statistic: count (pos > neg) pairs + 0.5 * (pos == neg) pairs.
    # Broadcasting: shape (n_pos, n_neg)
    diff = pos_scores[:, None] - neg_scores[None, :]
    u = float(np.sum(diff > 0) + 0.5 * np.sum(diff == 0))
    return u / (n_pos * n_neg)
```

### 3. Run the Acceptance Gate

The locked test suite is at
`exercises/module5/auc-roc-the-math-of-ranking/test_auc.py`.
Do not modify it.

```python
"""Acceptance gate: ROC curve and AUC.

Tests
-----
1. roc_auc matches sklearn.metrics.roc_auc_score to tolerance on several
   (y_true, y_score) vectors.
2. AUC of a perfect ranker == 1.0.
3. AUC of a random/constant scorer ~= 0.5 (within a band on a seeded sample).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from ml.metrics import roc_auc, roc_curve

TOL = 1e-6

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seeded_binary(n=200, seed=42):
    rng = np.random.default_rng(seed)
    y_true = rng.integers(0, 2, size=n)
    y_score = rng.random(size=n)
    return y_true, y_score


# ---------------------------------------------------------------------------
# 1. Agreement with sklearn on several vectors
# ---------------------------------------------------------------------------

def test_roc_auc_matches_sklearn_random():
    """Random scores: from-scratch AUC matches sklearn to 1e-6."""
    y_true, y_score = _seeded_binary(n=200, seed=42)
    scratch = roc_auc(y_true, y_score)
    expected = roc_auc_score(y_true, y_score)
    assert abs(scratch - expected) < TOL, (
        f"scratch={scratch:.8f}, sklearn={expected:.8f}"
    )


def test_roc_auc_matches_sklearn_structured():
    """Structured scores (noisy rank): from-scratch AUC matches sklearn."""
    rng = np.random.default_rng(7)
    n = 300
    y_true = rng.integers(0, 2, size=n)
    # scores correlated with labels to get a non-trivial AUC
    y_score = y_true * 0.6 + rng.random(n) * 0.4
    scratch = roc_auc(y_true, y_score)
    expected = roc_auc_score(y_true, y_score)
    assert abs(scratch - expected) < TOL, (
        f"scratch={scratch:.8f}, sklearn={expected:.8f}"
    )


def test_roc_auc_matches_sklearn_small():
    """Small deterministic vector: from-scratch AUC matches sklearn."""
    y_true  = np.array([0, 0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.4, 0.35, 0.8, 0.2, 0.9])
    scratch = roc_auc(y_true, y_score)
    expected = roc_auc_score(y_true, y_score)
    assert abs(scratch - expected) < TOL


# ---------------------------------------------------------------------------
# 2. Perfect ranker -> AUC == 1.0
# ---------------------------------------------------------------------------

def test_roc_auc_perfect_ranker():
    """A score that perfectly separates classes must give AUC == 1.0."""
    y_true  = np.array([0, 0, 0, 1, 1, 1])
    y_score = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    assert abs(roc_auc(y_true, y_score) - 1.0) < TOL


# ---------------------------------------------------------------------------
# 3. Random/constant scorer ~= 0.5
# ---------------------------------------------------------------------------

def test_roc_auc_random_scorer_near_half():
    """Random scores (seed=0, n=1000) must give AUC within [0.45, 0.55]."""
    rng = np.random.default_rng(0)
    n = 1000
    y_true = rng.integers(0, 2, size=n)
    y_score = rng.random(size=n)
    auc = roc_auc(y_true, y_score)
    assert 0.45 <= auc <= 0.55, (
        f"Random-score AUC={auc:.4f} outside expected [0.45, 0.55] band"
    )


def test_roc_auc_constant_scorer_near_half():
    """Constant score (all 0.5): AUC == 0.5 (degenerate; single point on ROC)."""
    y_true  = np.array([0, 0, 1, 1])
    y_score = np.array([0.5, 0.5, 0.5, 0.5])
    auc = roc_auc(y_true, y_score)
    # Constant score maps to a single ROC point; area under the step is 0.5
    assert abs(auc - 0.5) < TOL, f"Constant-score AUC={auc:.4f}, expected 0.5"


# ---------------------------------------------------------------------------
# ROC curve shape sanity
# ---------------------------------------------------------------------------

def test_roc_curve_endpoints():
    """ROC curve must start at (0,0) and end at (1,1)."""
    y_true, y_score = _seeded_binary(n=100, seed=1)
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    assert fpr[0] == pytest.approx(0.0, abs=TOL)
    assert tpr[0] == pytest.approx(0.0, abs=TOL)
    assert fpr[-1] == pytest.approx(1.0, abs=TOL)
    assert tpr[-1] == pytest.approx(1.0, abs=TOL)
```

## Done When

```
python -m pytest exercises/module5/auc-roc-the-math-of-ranking
```

All seven tests pass: three sklearn-agreement checks on different vectors; the perfect
ranker at AUC = 1.0; the random scorer in [0.45, 0.55]; the constant scorer at 0.5; the
curve endpoints at (0, 0) and (1, 1).

## Stretch

After the tests pass, write a small script that generates a dataset with a tunable signal
strength: `y_score = y_true * signal + rng.random(n) * (1 - signal)` for `signal` in
`[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]`. Compute the from-scratch AUC at each level. Plot AUC
as a function of signal strength. At what signal level does the model first meaningfully
outperform a random ranker, and how quickly does AUC approach 1.0?
