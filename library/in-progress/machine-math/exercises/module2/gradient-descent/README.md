# Exercise: Gradient Descent

**Goal:** Build `exercises/ml/gradient_descent.py`, a generic gradient descent optimizer
that accepts any differentiable objective and any starting point, and that every
subsequent model in the `ml/` package reuses as the shared training engine.

**Why:** Every parameterized model in this book trains by minimizing a loss. Understanding
the optimizer once, deeply, means you never have to re-derive it: the same function that
minimizes `(theta - 3)^2` here will minimize MSE in the next lesson and cross-entropy
in the one after that. The optimizer does not change; only the gradient function does.

## The Shared Artifact

`exercises/ml/` is the throughline package for this book. Before you add anything:

1. Check whether `exercises/ml/__init__.py` exists. If it does, read the package first.
   If it does not, create it as an empty file.
2. Check whether `exercises/ml/distances.py` already exists (from Module 1). Do not
   touch it; you are adding to the package, not replacing it.

The file you are adding is `exercises/ml/gradient_descent.py`.

## Steps

### 1. Confirm the Package Root

```
exercises/ml/__init__.py    <- empty file; must exist
exercises/ml/distances.py   <- already there from Module 1 (do not touch)
```

### 2. Implement `exercises/ml/gradient_descent.py`

The locked structure below is the contract every later module imports. Implement it
exactly as shown; do not alter signatures, docstrings, or logic.

```python
"""Gradient descent optimizer, from scratch in NumPy.

One idea: the derivative points uphill; step the opposite way, scaled by a learning rate.
For a convex loss there is exactly one bottom -- gradient descent finds it by following
the slope. For a non-convex loss it finds a local minimum; the learning rate and the number
of iterations are the two knobs you tune.
"""
import numpy as np


def gradient_descent(grad_fn, theta0, lr=0.1, n_iters=1000, loss_fn=None):
    """Minimize an objective by iterative gradient steps.

    Parameters
    ----------
    grad_fn : callable
        grad_fn(theta) -> gradient array with the same shape as theta.
    theta0 : array-like
        Starting parameters.
    lr : float
        Learning rate (step size). Default 0.1.
    n_iters : int
        Number of gradient steps to take. Default 1000.
    loss_fn : callable or None
        loss_fn(theta) -> scalar. When provided, history records loss values per
        iteration. When None, history records the L2 gradient norm -- a proxy that
        decreases as the optimizer converges.

    Returns
    -------
    theta : np.ndarray
        Parameter values after n_iters steps.
    history : list of float
        One value per iteration: the loss (if loss_fn given) or gradient norm.
    """
    theta = np.asarray(theta0, dtype=float).copy()
    history = []
    for _ in range(n_iters):
        grad = grad_fn(theta)
        if loss_fn is not None:
            history.append(float(loss_fn(theta)))
        else:
            history.append(float(np.linalg.norm(grad)))
        theta = theta - lr * grad
    return theta, history
```

### 3. Write the Acceptance Gate

Create `exercises/module2/gradient-descent/test_gradient_descent.py` with the
locked test suite below. No external oracle is needed: the ground truth is the
analytical solution `theta* = 3`.

```python
"""Acceptance gate for the gradient-descent exercise.

The generic optimizer must find the minimum of a known convex function (f(theta) = (theta-3)^2)
from a cold start, and the loss history must be non-increasing -- the proof that the learning
rate is not so large it bounces past the minimum. scikit-learn has no direct analogue here;
the oracle is the analytical solution (theta* = 3).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from ml.gradient_descent import gradient_descent


def test_converges_to_known_minimum():
    # f(theta) = (theta - 3)^2  =>  grad = 2*(theta - 3)  =>  minimum at theta = 3
    grad_fn = lambda theta: 2.0 * (theta - 3.0)
    loss_fn = lambda theta: float((theta[0] - 3.0) ** 2)
    theta, history = gradient_descent(
        grad_fn, theta0=np.array([0.0]), lr=0.1, n_iters=200, loss_fn=loss_fn
    )
    assert abs(float(theta[0]) - 3.0) < 1e-2, f"Expected ~3.0, got {float(theta[0]):.6f}"


def test_loss_history_is_non_increasing():
    grad_fn = lambda theta: 2.0 * (theta - 3.0)
    loss_fn = lambda theta: float((theta[0] - 3.0) ** 2)
    _, history = gradient_descent(
        grad_fn, theta0=np.array([0.0]), lr=0.1, n_iters=200, loss_fn=loss_fn
    )
    for i in range(1, len(history)):
        # Allow a tiny numerical slack (1e-10) for floating-point rounding
        assert history[i] <= history[i - 1] + 1e-10, (
            f"Loss increased at step {i}: {history[i - 1]:.6e} -> {history[i]:.6e}"
        )


def test_gradient_norm_history_without_loss_fn():
    # When no loss_fn is given, history should record gradient norms and still be positive
    grad_fn = lambda theta: 2.0 * (theta - 3.0)
    theta, history = gradient_descent(
        grad_fn, theta0=np.array([0.0]), lr=0.1, n_iters=100
    )
    assert len(history) == 100
    assert all(h >= 0.0 for h in history)
    # Gradient norm should decrease toward 0 as we approach the minimum
    assert history[-1] < history[0]


def test_multidimensional_convergence():
    # f(theta) = sum((theta_i - target_i)^2); minimum is target itself
    target = np.array([1.0, -2.0, 5.0])
    grad_fn = lambda theta: 2.0 * (theta - target)
    loss_fn = lambda theta: float(np.sum((theta - target) ** 2))
    theta, _ = gradient_descent(
        grad_fn, theta0=np.zeros(3), lr=0.1, n_iters=300, loss_fn=loss_fn
    )
    assert np.allclose(theta, target, atol=1e-2), f"Expected {target}, got {theta}"
```

## Done When

```
python -m pytest exercises/module2/gradient-descent
```

All four tests pass: the optimizer converges to `theta = 3.0` within tolerance, the
loss history is non-increasing, gradient-norm tracking works when no `loss_fn` is given,
and the optimizer converges in three dimensions simultaneously.

## Stretch

Add a `momentum_gradient_descent` function to `ml/gradient_descent.py` that implements
the momentum update rule:

```
v = beta * v + grad
theta = theta - lr * v
```

Use `beta=0.9` as the default. Add one test: confirm that momentum converges to the same
minimum as vanilla gradient descent on `f(theta) = (theta - 3)^2` but in fewer iterations.
Then try both on `f(x, y) = 50*x^2 + y^2` from `(10, 10)` and compare the step counts
to convergence. The elongated bowl (high condition number) is where momentum shows its
advantage by dampening the oscillation along the steep axis.
