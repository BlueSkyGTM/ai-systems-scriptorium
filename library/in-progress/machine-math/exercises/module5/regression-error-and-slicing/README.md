# Exercise: Regression Error and Slicing

**Goal:** Add `mae`, `rmse`, `r2`, and `slice_metric` to `exercises/ml/metrics.py`, then
run the locked acceptance gate that proves RMSE punishes outliers harder than MAE and that
`slice_metric` can surface a broken subgroup hidden inside a passable aggregate.

**Why:** Reporting a single aggregate metric on a regression model is not an evaluation; it
is a guess. In production, the metric that matters is the one on the slice where the model
fails. This exercise gives you the two instruments you need: `mae`/`rmse` to measure
magnitude and outlier sensitivity, and `slice_metric` to decompose any metric by group. The
M7 portfolio capstone calls both. Build them once; use them everywhere.

## The Shared Artifact

`exercises/ml/metrics.py` is the package file this module extends. Before touching
anything, list `exercises/ml/` and read `metrics.py` to understand what is already there.
Do not re-implement any function that exists. Do not move or rename anything an earlier
module installed.

The four functions you are adding are pure NumPy; they do not import sklearn. They must
match sklearn's `mean_absolute_error`, `mean_squared_error`, and `r2_score` to
floating-point tolerance, which the gate verifies.

## Steps

### 1. Add the Regression Functions

Open `exercises/ml/metrics.py` and append the following four functions verbatim. Place them
after any classification functions already in the file; do not interleave them.

```python
# ---------------------------------------------------------------------------
# Regression metrics
# ---------------------------------------------------------------------------

def mae(y_true, y_pred):
    """Mean Absolute Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    """Root Mean Squared Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def r2(y_true, y_pred):
    """Coefficient of determination R^2 = 1 - SS_res / SS_tot."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return float(1.0 - ss_res / ss_tot)


# ---------------------------------------------------------------------------
# Slice metric
# ---------------------------------------------------------------------------

def slice_metric(y_true, y_pred, groups, metric_fn):
    """Evaluate metric_fn per unique group.

    Parameters
    ----------
    y_true : array-like
    y_pred : array-like
    groups : array-like, same length as y_true
        Group label for each sample (any hashable dtype).
    metric_fn : callable(y_true_slice, y_pred_slice) -> float

    Returns
    -------
    dict mapping each unique group label to its metric score.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    groups = np.asarray(groups)
    result = {}
    for label in np.unique(groups):
        mask = groups == label
        result[label] = metric_fn(y_true[mask], y_pred[mask])
    return result
```

### 2. Place the Acceptance Gate

Create `exercises/module5/regression-error-and-slicing/test_regression_and_slicing.py`
with the following content verbatim. Do not modify it.

```python
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
```

### 3. Run the Gate

```
python -m pytest exercises/module5/regression-error-and-slicing
```

All five tests must pass before you move on.

## Done When

```
python -m pytest exercises/module5/regression-error-and-slicing
```

All five assertions pass:

- `test_mae_matches_sklearn`: `mae` agrees with sklearn's `mean_absolute_error` to 1e-9.
- `test_rmse_matches_sklearn`: `rmse` agrees with sklearn's `sqrt(mean_squared_error)` to
  1e-9.
- `test_r2_matches_sklearn`: `r2` agrees with sklearn's `r2_score` to 1e-9.
- `test_outlier_penalty_rmse_worse_than_mae`: injecting a +50 error raises the RMSE ratio
  higher than the MAE ratio, confirming RMSE's greater sensitivity to large misses.
- `test_slice_metric_surfaces_worst_subgroup`: the "BAD" group is detected as the worst
  cohort, with an MAE at least 2x the aggregate, confirming that `slice_metric` can expose
  failures the overall number hides.

## Stretch

After the gate passes, add a second experiment script at
`exercises/module5/regression-error-and-slicing/experiment.py`. Use your `mae` and
`slice_metric` to reproduce the numbers from the lesson: generate a four-group dataset with
`rng = np.random.default_rng(99)`, three good groups (noise scale 0.2) and one "BAD" group
(noise scale 5.0), 30 samples each. Print the per-group MAE table and the aggregate MAE.
Verify the "BAD" group lands around 3.83 and the aggregate around 1.08. Then vary the bad
group's noise scale from 1.0 to 10.0 and observe at what scale the aggregate first crosses
2.0. That is the threshold where the aggregate becomes a misleading number without slicing
to diagnose it.
