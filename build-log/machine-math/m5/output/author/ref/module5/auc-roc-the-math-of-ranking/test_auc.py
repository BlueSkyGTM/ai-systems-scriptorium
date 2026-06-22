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
