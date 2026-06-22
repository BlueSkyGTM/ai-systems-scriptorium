"""Acceptance gate for the linear-regression exercise.

The from-scratch LinearRegression must agree with the normal equation AND with
sklearn.linear_model.LinearRegression on the same synthetic data. scikit-learn and the
normal equation are the double oracle: GD is the algorithm you understand; the others
are the ground truth. R^2 on a held-out split must clear a sane floor for low-noise data.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.linear_model import LinearRegression as SklearnLR
from sklearn.model_selection import train_test_split

from ml.linreg import LinearRegression, normal_equation


def _make_dataset(seed=42):
    rng = np.random.default_rng(seed)
    n = 300
    X = rng.standard_normal((n, 3))
    # True relationship: y = 3*x1 - 2*x2 + 5 + small noise
    y = 3.0 * X[:, 0] - 2.0 * X[:, 1] + 5.0 + rng.standard_normal(n) * 0.2
    return X, y


def _r2(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return 1.0 - ss_res / ss_tot


def test_r2_clears_floor_on_synthetic():
    X, y = _make_dataset()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)
    model = LinearRegression(lr=0.01, n_iters=3000).fit(X_tr, y_tr)
    r2 = _r2(y_te, model.predict(X_te))
    assert r2 >= 0.95, f"R^2 = {r2:.4f} below floor 0.95"


def test_agrees_with_normal_equation():
    X, y = _make_dataset()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)

    gd_model = LinearRegression(lr=0.01, n_iters=3000).fit(X_tr, y_tr)
    gd_preds = gd_model.predict(X_te)

    # normal_equation works in the original space (no z-score); compare predictions
    ne_preds = np.hstack([X_te, np.ones((X_te.shape[0], 1))]) @ normal_equation(X_tr, y_tr)

    # Predictions must agree within 0.3 in mean absolute error
    mae = float(np.mean(np.abs(gd_preds - ne_preds)))
    assert mae < 0.3, f"GD vs normal equation MAE = {mae:.4f}"


def test_agrees_with_sklearn():
    X, y = _make_dataset()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)

    gd_model = LinearRegression(lr=0.01, n_iters=3000).fit(X_tr, y_tr)
    sk_model = SklearnLR().fit(X_tr, y_tr)

    gd_preds = gd_model.predict(X_te)
    sk_preds = sk_model.predict(X_te)

    mae = float(np.mean(np.abs(gd_preds - sk_preds)))
    assert mae < 0.3, f"GD vs sklearn MAE = {mae:.4f}"


def test_loss_history_decreases():
    X, y = _make_dataset()
    model = LinearRegression(lr=0.01, n_iters=500).fit(X, y)
    history = model.loss_history_
    # First half average should be higher than second half average
    mid = len(history) // 2
    assert np.mean(history[:mid]) > np.mean(history[mid:]), "Loss did not decrease over training"
