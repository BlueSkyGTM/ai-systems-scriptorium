"""Acceptance gate for DecisionTreeRegressor and RandomForestClassifier.

DecisionTreeRegressor on a seeded 1-D signal:
- reduces test MSE vs the constant-mean baseline.
- agrees with sklearn.tree.DecisionTreeRegressor within tolerance.

RandomForestClassifier on breast_cancer (stratified 80/20, random_state=0):
- clears >= 0.93 test accuracy.
- beats a single DecisionTreeClassifier of the same max_depth on the same split.
- agrees with sklearn.ensemble.RandomForestClassifier on >= 90% of test labels.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier as SklearnRF
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as SklearnDTC
from sklearn.tree import DecisionTreeRegressor as SklearnDTR

from ml.ensemble import RandomForestClassifier
from ml.tree import DecisionTreeClassifier, DecisionTreeRegressor


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TREE_MAX_DEPTH = 4
FOREST_N_ESTIMATORS = 100
FOREST_MAX_DEPTH = 6
RANDOM_STATE = 0


def _regression_split():
    """Seeded 1-D regression signal: noisy sine wave."""
    rng = np.random.default_rng(42)
    n = 200
    X = rng.uniform(0, 2 * np.pi, size=(n, 1))
    y = np.sin(X[:, 0]) + rng.normal(0, 0.1, size=n)
    return train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)


def _cancer_split():
    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)


# ---------------------------------------------------------------------------
# DecisionTreeRegressor tests
# ---------------------------------------------------------------------------

def test_regressor_beats_mean_baseline():
    """From-scratch regressor must reduce MSE below the constant-mean baseline."""
    X_tr, X_te, y_tr, y_te = _regression_split()

    reg = DecisionTreeRegressor(max_depth=TREE_MAX_DEPTH).fit(X_tr, y_tr)
    preds = reg.predict(X_te)

    baseline_mse = float(np.mean((y_te - np.mean(y_tr)) ** 2))
    tree_mse = float(np.mean((y_te - preds) ** 2))

    assert tree_mse < baseline_mse, (
        f"Tree MSE {tree_mse:.4f} is not better than mean baseline {baseline_mse:.4f}"
    )


def test_regressor_agrees_with_sklearn():
    """From-scratch regressor must agree with sklearn's on held-out predictions.

    Agreement is measured as Pearson correlation >= 0.98 (exact values diverge
    only due to tie-breaking; structure should be nearly identical).
    """
    X_tr, X_te, y_tr, y_te = _regression_split()

    scratch = DecisionTreeRegressor(max_depth=TREE_MAX_DEPTH).fit(X_tr, y_tr)
    sk = SklearnDTR(max_depth=TREE_MAX_DEPTH, random_state=RANDOM_STATE).fit(X_tr, y_tr)

    p_scratch = scratch.predict(X_te)
    p_sk = sk.predict(X_te)

    corr = float(np.corrcoef(p_scratch, p_sk)[0, 1])
    assert corr >= 0.98, (
        f"Prediction correlation with sklearn = {corr:.4f} (below 0.98)"
    )


# ---------------------------------------------------------------------------
# RandomForestClassifier tests
# ---------------------------------------------------------------------------

def test_forest_clears_accuracy_floor():
    """From-scratch RandomForest must reach >= 0.93 test accuracy on breast_cancer."""
    X_tr, X_te, y_tr, y_te = _cancer_split()
    rf = RandomForestClassifier(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)
    acc = float(np.mean(rf.predict(X_te) == y_te))
    assert acc >= 0.93, f"Forest test accuracy {acc:.4f} is below 0.93 floor"


def test_forest_beats_single_tree():
    """RandomForest must be >= the single tree accuracy on the same split."""
    X_tr, X_te, y_tr, y_te = _cancer_split()

    single = DecisionTreeClassifier(max_depth=FOREST_MAX_DEPTH).fit(X_tr, y_tr)
    forest = RandomForestClassifier(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)

    acc_single = float(np.mean(single.predict(X_te) == y_te))
    acc_forest = float(np.mean(forest.predict(X_te) == y_te))

    assert acc_forest >= acc_single, (
        f"Forest acc {acc_forest:.4f} < single tree acc {acc_single:.4f}"
    )


def test_forest_agrees_with_sklearn():
    """From-scratch and sklearn forests must agree on >= 90% of test labels."""
    X_tr, X_te, y_tr, y_te = _cancer_split()

    scratch_rf = RandomForestClassifier(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)
    sk_rf = SklearnRF(
        n_estimators=FOREST_N_ESTIMATORS,
        max_depth=FOREST_MAX_DEPTH,
        random_state=RANDOM_STATE,
    ).fit(X_tr, y_tr)

    p_scratch = scratch_rf.predict(X_te)
    p_sk = sk_rf.predict(X_te)

    agreement = float(np.mean(p_scratch == p_sk))
    assert agreement >= 0.90, (
        f"Label agreement with sklearn = {agreement:.4f} (below 0.90)"
    )
