# Exercise: Hyperparameters and the Tradeoff

**Goal:** Write a hyperparameter sweep that demonstrates overfitting by measurement. Fit
`ml.ensemble.GradientBoostingRegressor` at two configurations on the Friedman-1 regression
benchmark and prove, with numbers, that the high-variance configuration drives training error
lower while test error is worse. The gate asserts this relationship holds.

**Why:** Knowing that gradient boosting has three knobs is not the same as having watched the
tradeoff happen on real data. This exercise makes you produce the numbers: the overfit
configuration must reach a lower final training MSE than the tuned configuration, and a higher
test MSE. That gap is the overfitting signature you can quote in an interview.

## The Shared Artifact

This exercise does not add a new file to `exercises/ml/`. It uses `ml.ensemble.GradientBoostingRegressor`,
already in the package from the M4 build lessons. Before writing anything, list `exercises/ml/`
and read `ml/ensemble.py` to confirm the constructor parameters (`n_estimators`, `learning_rate`,
`max_depth`), the `fit` signature, the `predict` signature, and the `train_losses_` attribute
(a list of per-round training MSE). You are calling existing code, not writing new package code.

## Steps

### 1. Write the Experiment Script

Create `exercises/module4/hyperparameters-and-the-tradeoff/experiment.py`. The experiment must:

1. Generate the Friedman-1 dataset with `sklearn.datasets.make_friedman1(n_samples=300,
   n_features=10, noise=1.0, random_state=0)`.
2. Split 80/20 with `sklearn.model_selection.train_test_split(..., random_state=0)`.
3. Fit two configurations and record train MSE (final entry of `train_losses_`) and test MSE:

   - **Tuned:** `n_estimators=50, learning_rate=0.05, max_depth=3`
   - **Overfit:** `n_estimators=200, learning_rate=0.5, max_depth=8`

4. Print a comparison table.

The table should reproduce approximately:

| Config | Final Train MSE | Test MSE | Test R^2 |
|--------|-----------------|----------|----------|
| Tuned (n=50, lr=0.05, depth=3) | 3.06 | 7.29 | 0.665 |
| Overfit (n=200, lr=0.5, depth=8) | 0.00 | 11.52 | 0.471 |

Confirm that the overfit config's final train MSE is lower than the tuned config's, while its
test MSE is higher.

### 2. Run the Acceptance Gate

Place the locked test suite below verbatim at
`exercises/module4/hyperparameters-and-the-tradeoff/test_tradeoff.py`. Do not modify it.

```python
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
```

**Note:** The gate trains many trees from scratch and can take a couple of minutes. That is
expected: 200 deep trees on 240 training samples is a real compute load, not a toy.

## Done When

```
python -m pytest exercises/module4/hyperparameters-and-the-tradeoff
```

All three assertions pass:

- `test_overfit_config_has_lower_train_error`: the overfit configuration's final training MSE
  is strictly lower than the tuned configuration's. The overfit config fits training data harder.
- `test_overfit_config_has_worse_test_error`: the overfit configuration's test MSE is strictly
  higher than the tuned configuration's. More capacity did not help generalization.
- `test_overfit_train_loss_keeps_dropping`: the overfit configuration's training loss in its
  final 10 rounds is still lower than in its first 10 rounds, confirming it was still descending
  and had not converged.

Together these confirm the overfitting signature: a high-variance configuration drives training
error toward zero while test error climbs. The numbers are the demonstration, not the diagram.

## Stretch

After the gate passes, add a learning rate sweep. For three configurations that hold roughly
the same effective shrinkage but vary the rate and round count:

- `lr=0.5, n_estimators=20`
- `lr=0.1, n_estimators=100`
- `lr=0.05, n_estimators=200`

Fit each, record final train MSE and test MSE, and print the comparison. Do the test MSEs
converge toward similar values even though the configurations look different? Then try a fourth
config at `lr=0.01, n_estimators=500` and observe whether the pattern holds. Report what the
numbers say about the `learning_rate` / `n_estimators` coupling and when it breaks down.
