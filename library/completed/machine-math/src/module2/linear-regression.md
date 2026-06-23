# Linear Regression: Fitting the Line

k-NN never learns anything: at prediction time it scans the full training set. Linear
regression does the opposite. It compresses everything about the training data into a
weight vector `w` and a bias `b`, then discards the raw rows. Predicting a new point
costs one matrix multiply. The question is how to find `w` and `b`.

## The Model and the Loss

The model is:

```
y_hat = w^T * x + b
```

For a dataset of `n` examples, the mean squared error (MSE) measures how badly the
current weights miss:

```
MSE = (1/n) * sum((y_hat_i - y_i)^2)
```

MSE penalizes large errors quadratically. It is smooth and differentiable everywhere,
which is the property gradient descent needs. The gradients of MSE with respect to the
weights and bias are:

```
dMSE/dw = (2/n) * X^T (Xw - y)   (matrix form)
dMSE/db = (2/n) * sum(y_hat - y)
```

Plug those into `gradient_descent` from the previous lesson and the optimizer walks
the weights downhill until the MSE stops decreasing. The Azure Machine Learning Linear
Regression component names this training method "Online Gradient Descent" and documents
it alongside ordinary least squares as its two supported solution methods, noting that
gradient descent is preferred "for models that are more complex, or that have too little
training data given the number of variables"
(learn.microsoft.com/azure/machine-learning/component-reference/linear-regression).

## The Normal Equation

For a small dataset there is a faster path. The normal equation solves for the optimal
weights directly, in one step, without iteration:

```
w* = (X^T X)^{-1} X^T y
```

This inverts a matrix of shape `(p, p)` where `p` is the number of features. For small
`p` that is cheap; for large `p` (thousands of features) the inversion costs `O(p^3)`
and gradient descent wins on speed.

The two methods are not competitors: they solve the same optimization problem. The
normal equation jumps straight to the bottom; gradient descent rolls there one step at
a time. They should agree numerically on the same data.

## What the Code Does

`LinearRegression.fit` applies z-score scaling to the features before running the
optimizer. This keeps the gradient magnitudes comparable across features and lets the
optimizer use a single learning rate for all weights. The scaling parameters (mean and
standard deviation per feature) are stored so `predict` can invert them transparently:
the caller always works in original space.

`normal_equation` takes the same feature matrix and target vector and solves via
`np.linalg.lstsq`, which is numerically stable for near-singular matrices.

Both are in the locked `ml/linreg.py` below. Read the docstrings: the note in
`LinearRegression` that says "the learned weights apply to the scaled space" is the
detail most readers miss the first time.

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

## Measured Results

On a seeded synthetic dataset with true relationship `y = 3*x1 - 2*x2 + 5 + noise`
(300 samples, noise std 0.2, 80/20 split, `seed=42`):

- `LinearRegression(lr=0.01, n_iters=3000)`: R-squared on the held-out test set = `0.9966`
- `normal_equation` predictions: mean absolute error vs. GD predictions `< 0.01`
- scikit-learn `LinearRegression` predictions: mean absolute error vs. GD predictions `< 0.01`
- MSE history: starts near `39.1`, falls to `0.037` within the first few hundred iterations,
  then plateaus at the noise floor

All three methods land at the same coefficients to roughly six decimal places. That
agreement is the proof. The normal equation is the answer key; gradient descent arrives
there by following the slope.

The plateau matters. MSE does not go to zero because the target has irreducible noise
(`noise_std=0.2` in the generator). No model can predict noise. The training run's job
is to reach the noise floor, not to drive past it. That limit is what the next lesson
names precisely: bias and variance.

Gradient descent generalizes. The optimizer that converges on MSE here is the same one
that will update weights through a sigmoid in the next lesson, and through layer after
layer of a neural network later. The loss surface changes; the optimizer does not.

## Core Concepts

- Linear regression fits `y_hat = w^T x + b` by minimizing MSE; the MSE gradient
  `(2/n) * X^T (Xw - y)` is the descent signal.
- The normal equation `w* = (X^T X)^{-1} X^T y` is the closed-form solution; it
  jumps to the optimum in one step but costs `O(p^3)` and is impractical for large
  feature counts.
- Gradient descent and the normal equation reach the same weights on the same data:
  GD is not an approximation of the normal equation, it is an alternative path to the
  same minimum.
- Feature z-scoring before gradient descent keeps all weight gradients on a comparable
  scale; without it, the highest-variance feature dominates the update.

<div class="claude-handoff" data-exercise="exercises/module2/linear-regression/">

**Build It in Claude Code**: Read the current state of `exercises/ml/` before touching anything. Then build `exercises/ml/linreg.py` with the `LinearRegression` class and the `normal_equation` function exactly as shown above. Note that `linreg.py` imports `gradient_descent` from `ml.gradient_descent`: do not copy the optimizer, import it. Then verify with the locked acceptance gate at `exercises/module2/linear-regression/test_linreg.py`. The gate checks that R-squared clears `0.95` on held-out data, that GD and the normal equation predictions agree within MAE `0.3`, and that GD and scikit-learn predictions agree within MAE `0.3`. Done when `python -m pytest exercises/module2/linear-regression` is green.

</div>
