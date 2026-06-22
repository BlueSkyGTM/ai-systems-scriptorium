"""Acceptance gate: regression metrics and slice_metric.

Tests
-----
1. mae/rmse/r2 match sklearn (mean_absolute_error / sqrt(mean_squared_error)
   / r2_score) to tolerance.
2. Outlier penalty: injecting one large error increases RMSE more than MAE
   relative to a clean baseline (RMSE punishes big misses).
3. slice_metric returns correct per-group values and surfaces a subgroup
   whose metric is far below the aggregate.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from ml.metrics import mae, r2, rmse, slice_metric

TOL = 1e-9

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def regression_data():
    """Seeded regression data: 50 samples, moderate residuals."""
    rng = np.random.default_rng(42)
    y_true = rng.uniform(0, 10, size=50)
    noise  = rng.normal(0, 0.5, size=50)
    y_pred = y_true + noise
    return y_true, y_pred


# ---------------------------------------------------------------------------
# 1. Agreement with sklearn
# ---------------------------------------------------------------------------

def test_mae_matches_sklearn(regression_data):
    y_true, y_pred = regression_data
    expected = mean_absolute_error(y_true, y_pred)
    assert abs(mae(y_true, y_pred) - expected) < TOL


def test_rmse_matches_sklearn(regression_data):
    y_true, y_pred = regression_data
    expected = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    assert abs(rmse(y_true, y_pred) - expected) < TOL


def test_r2_matches_sklearn(regression_data):
    y_true, y_pred = regression_data
    expected = r2_score(y_true, y_pred)
    assert abs(r2(y_true, y_pred) - expected) < TOL


# ---------------------------------------------------------------------------
# 2. Outlier penalty: RMSE grows more than MAE
# ---------------------------------------------------------------------------

def test_outlier_penalty_rmse_worse_than_mae():
    """Injecting one large residual raises RMSE more than MAE.

    Clean baseline: 20 samples with small residuals.
    Dirty version:  same, but the last sample has a huge error (+50).
    We measure the *ratio* of dirty/clean for each metric and assert
    RMSE ratio > MAE ratio (RMSE is more sensitive to outliers).
    """
    rng = np.random.default_rng(7)
    n = 20
    y_true = rng.uniform(0, 5, size=n)
    y_pred_clean = y_true + rng.normal(0, 0.3, size=n)

    # Inject one extreme outlier into the predictions
    y_pred_dirty = y_pred_clean.copy()
    y_pred_dirty[-1] += 50.0  # large miss on the last sample

    mae_clean  = mae(y_true, y_pred_clean)
    rmse_clean = rmse(y_true, y_pred_clean)
    mae_dirty  = mae(y_true, y_pred_dirty)
    rmse_dirty = rmse(y_true, y_pred_dirty)

    mae_ratio  = mae_dirty  / mae_clean
    rmse_ratio = rmse_dirty / rmse_clean

    assert rmse_ratio > mae_ratio, (
        f"Expected RMSE to grow more: rmse_ratio={rmse_ratio:.3f}, "
        f"mae_ratio={mae_ratio:.3f}"
    )


# ---------------------------------------------------------------------------
# 3. slice_metric: per-group correctness and worst-subgroup detection
# ---------------------------------------------------------------------------

def test_slice_metric_per_group_values():
    """slice_metric returns the exact metric for each group."""
    y_true  = np.array([1.0, 2.0, 3.0, 10.0, 20.0, 30.0])
    y_pred  = np.array([1.1, 2.1, 3.1, 10.5, 20.5, 30.5])
    groups  = np.array(["A", "A", "A", "B", "B", "B"])

    result = slice_metric(y_true, y_pred, groups, mae)

    # Manually compute expected values
    expected_A = mae(y_true[:3], y_pred[:3])
    expected_B = mae(y_true[3:], y_pred[3:])

    assert abs(result["A"] - expected_A) < TOL
    assert abs(result["B"] - expected_B) < TOL


def test_slice_metric_surfaces_worst_subgroup():
    """A bad subgroup must have a metric far below the aggregate.

    Groups: three 'good' groups (small residuals) + one 'bad' group (large
    residuals).  The worst-subgroup MAE should exceed the aggregate MAE by
    a clear margin (>= 2x).
    """
    rng = np.random.default_rng(99)
    n_per_group = 30

    # Three good groups: tiny noise
    y_true_good = rng.uniform(0, 5, size=3 * n_per_group)
    y_pred_good = y_true_good + rng.normal(0, 0.2, size=3 * n_per_group)
    groups_good = np.repeat(["G1", "G2", "G3"], n_per_group)

    # One bad group: large noise
    y_true_bad = rng.uniform(0, 5, size=n_per_group)
    y_pred_bad = y_true_bad + rng.normal(0, 5.0, size=n_per_group)
    groups_bad = np.repeat(["BAD"], n_per_group)

    y_true_all = np.concatenate([y_true_good, y_true_bad])
    y_pred_all = np.concatenate([y_pred_good, y_pred_bad])
    groups_all = np.concatenate([groups_good, groups_bad])

    slices = slice_metric(y_true_all, y_pred_all, groups_all, mae)
    aggregate = mae(y_true_all, y_pred_all)

    worst_group = max(slices, key=slices.get)
    worst_score = slices[worst_group]

    assert worst_group == "BAD", (
        f"Expected 'BAD' to be worst, got '{worst_group}'"
    )
    assert worst_score >= 2 * aggregate, (
        f"Worst subgroup MAE {worst_score:.4f} is not >= 2x aggregate {aggregate:.4f}"
    )
