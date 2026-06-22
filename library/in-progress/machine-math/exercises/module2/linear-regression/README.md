# Exercise: Linear Regression

**Goal:** Build `exercises/ml/linreg.py`, a from-scratch linear regression implementation
that reuses the `gradient_descent` optimizer from Module 2's first exercise, scales
features with `zscore` from Module 1, and passes a double oracle: the normal equation
and scikit-learn must agree with your gradient-descent predictions on the same data.

**Why:** The measure of understanding a model is not whether you can write it, but whether
your version produces the same numbers as a trusted reference. This exercise puts two
oracles side by side. If all three match, you own the algorithm.

## The Shared Artifact

Before touching any file, read the current state of `exercises/ml/`. You are building
on top of work that already exists:

- `exercises/ml/distances.py` contributes `euclidean`, `manhattan`, `cosine_distance`,
  `minmax_scale`, `zscore`, and `METRICS` (Module 1, lesson 1).
- `exercises/ml/gradient_descent.py` contributes `gradient_descent` (Module 2, lesson 1,
  the exercise you just completed).

The file you are adding is `exercises/ml/linreg.py`. It imports `gradient_descent`
from `ml.gradient_descent` directly. Do not copy the optimizer. The reuse is real.

## Steps

### 1. Confirm What Is Already There

```
exercises/ml/__init__.py          <- already exists
exercises/ml/distances.py         <- from Module 1 (do not touch)
exercises/ml/gradient_descent.py  <- from Module 2, lesson 1 (do not touch)
```

### 2. Implement `exercises/ml/linreg.py`

The locked structure below is the contract the acceptance gate imports. Implement it
exactly as shown; do not alter signatures, docstrings, import paths, or logic.

Note the import at the top: `from ml.gradient_descent import gradient_descent`. That
is the throughline. `linreg.py` does not re-implement descent; it drives the shared
optimizer with a MSE gradient function.

```python
"""Linear regression, from scratch in NumPy.

One idea: fit a line by minimizing mean squared error. The MSE gradient is the descent
signal; gradient descent walks downhill one step at a time. The normal equation is the
closed-form shortcut that jumps straight to the bottom -- useful as a cross-check and
fast for small datasets.

Reuses:
- ml.gradient_descent.gradient_descent  (the shared optimizer)
- ml.distances.zscore                    (feature scaling before GD)
"""
import numpy as np
from ml.gradient_descent import gradient_descent


def normal_equation(X, y):
    """Closed-form solution: w* = (X^T X)^-1 X^T y.

    Parameters
    ----------
    X : array-like, shape (n, p)
        Feature matrix (NOT augmented; intercept is added internally).
    y : array-like, shape (n,)
        Target vector.

    Returns
    -------
    w : np.ndarray, shape (p+1,)
        Weights with the intercept as the last element.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    ones = np.ones((X.shape[0], 1))
    Xb = np.hstack([X, ones])
    return np.linalg.lstsq(Xb, y, rcond=None)[0]


class LinearRegression:
    """Gradient-descent linear regression with an intercept term.

    Scales features with z-score before descent; the predict step inverts the
    scaling transparently so the caller works in original space.

    Parameters
    ----------
    lr : float
        Learning rate for gradient descent.
    n_iters : int
        Number of gradient steps.
    """

    def __init__(self, lr=0.01, n_iters=2000):
        self.lr = lr
        self.n_iters = n_iters
        self.w_ = None
        self.loss_history_ = None
        self._mu = None
        self._sd = None

    def fit(self, X, y):
        """Fit the model to training data.

        Internally z-scores X; the learned weights apply to the scaled space.
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n, p = X.shape

        # Scale features; store moments for predict
        self._mu = X.mean(axis=0)
        self._sd = X.std(axis=0)
        self._sd = np.where(self._sd == 0.0, 1.0, self._sd)
        Xs = (X - self._mu) / self._sd

        # Augment with a bias column (intercept)
        ones = np.ones((n, 1))
        Xb = np.hstack([Xs, ones])

        # MSE gradient: dL/dw = (2/n) * X^T (Xw - y)
        def grad_fn(w):
            residuals = Xb @ w - y
            return (2.0 / n) * Xb.T @ residuals

        def loss_fn(w):
            residuals = Xb @ w - y
            return float(np.mean(residuals ** 2))

        w0 = np.zeros(p + 1)
        self.w_, self.loss_history_ = gradient_descent(
            grad_fn, w0, lr=self.lr, n_iters=self.n_iters, loss_fn=loss_fn
        )
        return self

    def predict(self, X):
        """Predict targets for X (applies the stored z-score scaling)."""
        X = np.asarray(X, dtype=float)
        Xs = (X - self._mu) / self._sd
        ones = np.ones((X.shape[0], 1))
        Xb = np.hstack([Xs, ones])
        return Xb @ self.w_
```

### 3. Write the Acceptance Gate

Create `exercises/module2/linear-regression/test_linreg.py` with the locked test suite
below. scikit-learn and the normal equation are the double oracle: both must agree with
your gradient-descent predictions within the stated tolerance.

```python
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
```

## Done When

```
python -m pytest exercises/module2/linear-regression
```

All four tests pass: R-squared clears `0.95` on held-out data; gradient-descent and the
normal equation predictions agree within MAE `0.3`; gradient-descent and scikit-learn
predictions agree within MAE `0.3`; the loss history shows the first half higher than
the second half on average.

## Stretch

Print the learned weights from `LinearRegression` and compare them to the true
coefficients (`w1=3.0`, `w2=-2.0`, bias=`5.0`). Then fit the same model with
`n_iters=100`, `n_iters=500`, and `n_iters=3000` and plot (or print) the R-squared
at each count. At what iteration count does the model clear the noise floor? Compute
R-squared for the normal equation on the same split and confirm it matches your
converged gradient-descent result within two decimal places.
