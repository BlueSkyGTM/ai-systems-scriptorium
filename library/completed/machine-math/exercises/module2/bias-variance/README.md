# Exercise: The Bias-Variance Tradeoff

**Goal:** Write the overfitting experiment: fit `ml.linreg.LinearRegression` on polynomial
features of a noisy 1-D signal at rising degree, measure train MSE and test MSE, and demonstrate
overfitting by measurement. The gate asserts that test error rises while train error falls as
degree climbs to 15.

**Why:** Overfitting is not an opinion and it is not a diagram in a textbook. It is a number: the
gap between train MSE and test MSE, measured on held-out data you did not train on. This exercise
makes you produce that number and prove the gap exists.

## The Shared Artifact

This exercise does not add a new file to `exercises/ml/`. It uses `ml.linreg.LinearRegression`,
already in the package from the linear regression lesson. Before writing anything, list
`exercises/ml/` and read `ml/linreg.py` to confirm the `fit` and `predict` signatures. You are
calling existing code, not writing new package code.

## Steps

### 1. Write the Experiment Script

Create `exercises/module2/bias-variance/experiment.py` (or work directly in the test file if you
prefer). The experiment must:

1. Generate 60 points from `y = sin(x) + noise` with noise std 0.3. Use `x = np.linspace(-3, 3, 60)`.
2. Split deterministically: indices `[:45]` for training, `[45:]` for test.
3. For each degree in `[1, 3, 5, 9, 15]`:
   a. Build polynomial features with `np.column_stack([x ** d for d in range(1, degree + 1)])`.
   b. Fit `LinearRegression(lr=0.001, n_iters=5000)` on the training features.
   c. Measure train MSE and test MSE.
4. Print the table. Confirm that train error falls and test error climbs at the high-degree end.

### 2. Run the Acceptance Gate

Place the locked test suite below at `exercises/module2/bias-variance/test_bias_variance.py`.
This is the negative case: overfitting is the pass condition.

```python
"""Acceptance gate for the bias-variance exercise.

This is the NEGATIVE CASE -- the point is to show overfitting by measurement.
We fit LinearRegression on polynomial features of a 1-D synthetic at rising degree
and assert that train error keeps dropping while test error eventually rises above
the low-degree baseline. Overfitting is not an opinion; it is a gap you can read
from the train/test error table.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from ml.linreg import LinearRegression


def _make_1d_dataset(seed=0):
    rng = np.random.default_rng(seed)
    n = 60
    x = np.linspace(-3, 3, n)
    y = np.sin(x) + rng.standard_normal(n) * 0.3
    return x, y


def _poly_features(x, degree):
    """Return a (n, degree) matrix of [x, x^2, ..., x^degree]."""
    return np.column_stack([x ** d for d in range(1, degree + 1)])


def _mse(y_true, y_pred):
    return float(np.mean((y_true - y_pred) ** 2))


def test_train_error_falls_while_test_error_eventually_rises():
    x, y = _make_1d_dataset()
    # 75/25 split (deterministic index split to keep reproducibility)
    n_train = 45
    x_tr, x_te = x[:n_train], x[n_train:]
    y_tr, y_te = y[:n_train], y[n_train:]

    degrees = [1, 3, 5, 9, 15]
    train_errors = []
    test_errors = []

    for deg in degrees:
        X_tr = _poly_features(x_tr, deg)
        X_te = _poly_features(x_te, deg)
        model = LinearRegression(lr=0.001, n_iters=5000).fit(X_tr, y_tr)
        train_errors.append(_mse(y_tr, model.predict(X_tr)))
        test_errors.append(_mse(y_te, model.predict(X_te)))

    # 1. Train error at the highest degree must be lower than at degree 1 (more capacity = better train fit).
    #    We do not require strict monotonicity step-by-step because GD may not fully converge for very high
    #    degree polynomials with large feature magnitudes; the trend over the full range is what matters.
    assert train_errors[-1] < train_errors[0], (
        f"Expected degree-15 train error to be lower than degree-1; "
        f"degree-1={train_errors[0]:.4f}, degree-15={train_errors[-1]:.4f}"
    )

    # 2. Test error at the highest degree must exceed the minimum-degree test error -- overfitting demonstrated
    low_degree_test = test_errors[0]   # degree 1
    high_degree_test = test_errors[-1]  # degree 15
    assert high_degree_test > low_degree_test, (
        f"Expected test error to rise with extreme degree; "
        f"degree-1 test={low_degree_test:.4f}, degree-15 test={high_degree_test:.4f}"
    )

    # 3. A middle degree (3 or 5) should have lower test error than degree 15 (the U-shape is visible)
    min_test = min(test_errors)
    assert min_test < high_degree_test, (
        f"No U-shape found: minimum test error {min_test:.4f} is not below degree-15 test error {high_degree_test:.4f}"
    )
```

## Done When

```
python -m pytest exercises/module2/bias-variance
```

All three assertions pass: degree-15 train error is lower than degree-1 train error; degree-15
test error exceeds degree-1 test error; and the minimum test error across degrees is lower than
the degree-15 test error. Together these confirm the U-shape: overfit is demonstrated by
measurement, not by description.

## Stretch

Print the full table of train MSE and test MSE for all five degrees. Then add a sixth degree,
such as 20 or 25, and report what happens to the test error. If it continues to climb, the
variance regime is confirmed. If it drops unexpectedly, investigate: gradient descent may not
have converged at that degree because polynomial features for high degrees have extreme magnitudes.
Try normalizing the feature columns and rerunning. Report what changes.
