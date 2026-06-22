"""Negative-case acceptance gate: measuring overfit by configuration.

Shows that a high-variance configuration (high learning_rate, many deep trees)
overfits measurably: its TRAIN error keeps dropping while its TEST error is
worse than a moderate, tuned configuration.

The test fails if overfit cannot be demonstrated -- which would mean either the
implementations are wrong or the test data is degenerate.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import make_friedman1
from sklearn.model_selection import train_test_split

from ml.ensemble import GradientBoostingRegressor


# ---------------------------------------------------------------------------
# Shared data
# ---------------------------------------------------------------------------

RANDOM_STATE = 0


def _data():
    X, y = make_friedman1(n_samples=300, n_features=10, noise=1.0, random_state=RANDOM_STATE)
    return train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)


def _mse(y_true, y_pred):
    return float(np.mean((y_true - y_pred) ** 2))


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

# Moderate config: smaller lr, shallow trees, fewer estimators
TUNED = dict(n_estimators=50, learning_rate=0.05, max_depth=3)

# Overfit config: large lr + deep trees -> low bias, high variance
OVERFIT = dict(n_estimators=200, learning_rate=0.5, max_depth=8)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_overfit_config_has_lower_train_error():
    """Overfit config must achieve lower TRAIN error than tuned config."""
    X_tr, X_te, y_tr, y_te = _data()

    tuned = GradientBoostingRegressor(**TUNED).fit(X_tr, y_tr)
    overfit = GradientBoostingRegressor(**OVERFIT).fit(X_tr, y_tr)

    train_mse_tuned = tuned.train_losses_[-1]
    train_mse_overfit = overfit.train_losses_[-1]

    assert train_mse_overfit < train_mse_tuned, (
        f"Expected overfit config train MSE ({train_mse_overfit:.4f}) < "
        f"tuned train MSE ({train_mse_tuned:.4f})"
    )


def test_overfit_config_has_worse_test_error():
    """Overfit config must have higher TEST error than tuned config."""
    X_tr, X_te, y_tr, y_te = _data()

    tuned = GradientBoostingRegressor(**TUNED).fit(X_tr, y_tr)
    overfit = GradientBoostingRegressor(**OVERFIT).fit(X_tr, y_tr)

    test_mse_tuned = _mse(y_te, tuned.predict(X_te))
    test_mse_overfit = _mse(y_te, overfit.predict(X_te))

    assert test_mse_overfit > test_mse_tuned, (
        f"Expected overfit config test MSE ({test_mse_overfit:.4f}) > "
        f"tuned test MSE ({test_mse_tuned:.4f})"
    )


def test_overfit_train_loss_keeps_dropping():
    """Overfit config's training loss must still be falling in its final rounds.

    Checks that the last-10-round average loss is strictly lower than the
    first-10-round average loss -- a proxy for 'still descending at the end'.
    """
    X_tr, X_te, y_tr, y_te = _data()
    overfit = GradientBoostingRegressor(**OVERFIT).fit(X_tr, y_tr)

    losses = overfit.train_losses_
    early_avg = float(np.mean(losses[:10]))
    late_avg = float(np.mean(losses[-10:]))

    assert late_avg < early_avg, (
        f"Expected late train loss ({late_avg:.4f}) < early train loss ({early_avg:.4f})"
    )
