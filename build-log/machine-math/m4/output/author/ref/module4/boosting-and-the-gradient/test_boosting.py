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
