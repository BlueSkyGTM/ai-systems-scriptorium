# Gradient Descent: Rolling Downhill

The derivative of a function at a point tells you the slope. A positive slope means the
function is rising to the right; a negative slope means it is falling. The optimizer's
only job is to read that slope and step the opposite way. That is gradient descent.

## The Update Rule

For a scalar parameter `theta` and a loss `L(theta)`, the gradient descent update is:

```
theta_new = theta_old - lr * dL/dtheta
```

The learning rate `lr` controls how far you step. The gradient `dL/dtheta` tells you
which direction is uphill; subtracting it points you downhill. Repeat until the gradient
is near zero.

For a vector of parameters the rule is identical, component by component:

```
theta_new = theta_old - lr * grad L(theta)
```

The gradient is a vector: each component is the partial derivative of the loss with
respect to one parameter. The negative gradient points toward the steepest descent across
all parameters simultaneously.

## Why Convexity Guarantees the Bottom

A convex function has only one valley. The second-derivative test makes this precise:
if `f''(theta) >= 0` everywhere, the function curves upward everywhere, and every local
minimum is the global minimum. For multivariate functions, the Hessian matrix (the matrix
of second partial derivatives) must be positive semidefinite everywhere.

Mean squared error for a linear model is convex in the weights. That means gradient
descent on MSE cannot get stuck in a bad local minimum. Follow the slope long enough
with a sensible learning rate and you reach the global optimum.

Non-convex losses, like those in neural networks, have many local minima and saddle
points. The same optimizer still runs; convexity just removes the guarantee. The engine
here is the same one that trains transformers; this lesson is where you understand it.

## The Learning Rate Tradeoff

Pick `lr` too small and convergence is slow: you take thousands of tiny steps toward a
bottom you could reach in dozens. Pick `lr` too large and the step overshoots the valley:
instead of landing near the minimum, you bounce off the far wall and the loss grows. The
Azure Machine Learning Linear Regression component, which offers online gradient descent
as a training method alongside ordinary least squares, exposes this knob directly: "For
**Learning rate**, specify the initial learning rate for the stochastic gradient descent
optimizer" and notes that larger datasets with fewer variables converge better with a
small fixed rate, while complex problems benefit from the option to decrease the learning
rate as training progresses
(learn.microsoft.com/azure/machine-learning/component-reference/linear-regression).

The ingredient data confirms the pattern numerically: on the Rosenbrock function, `lr=0.0001`
barely moves the parameters, `lr=0.0005` converges to the true minimum, and `lr=0.001`
overshoots and diverges. For the convex case you build here, `lr=0.1` is safe and fast.

## The Locked Optimizer

The function below is the optimizer you build in the exercise and that every later model
in this package imports. Read the docstring before the code: the design decision is that
`grad_fn` and `loss_fn` are kept separate so the function works for any differentiable
objective without modification.

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

## A Measured Run

On `f(theta) = (theta - 3)^2`, the gradient is `2 * (theta - 3)`. From `theta = 0` with
`lr = 0.1`, the measured result is:

- Starting loss: `(0 - 3)^2 = 9.0`
- After 50 iterations: loss near `0.0`, `theta` within `0.01` of `3.0`
- After 200 iterations: `theta = 2.999...`, loss indistinguishable from `0`

The loss history is strictly non-increasing, which the acceptance gate verifies directly.
That monotone property is the signature of a well-chosen learning rate on a convex loss.

## Core Concepts

- The gradient points toward steepest ascent; the negative gradient points toward
  steepest descent; subtracting `lr * gradient` from the current parameters is the
  entire update.
- A convex loss has exactly one minimum; gradient descent on a convex loss reaches
  the global optimum regardless of starting point, given a learning rate small enough
  to avoid overshooting.
- The learning rate trades convergence speed against stability: too small is slow, too
  large diverges; for convex problems a fixed moderate rate (here `0.1`) works reliably.
- The optimizer accepts any `grad_fn`; the loss surface determines the difficulty, not
  the optimizer code.

<div class="claude-handoff" data-exercise="exercises/module2/gradient-descent/">

**Build It in Claude Code**: Build `exercises/ml/gradient_descent.py` with the `gradient_descent` function exactly as shown above. Then verify it with the locked acceptance gate at `exercises/module2/gradient-descent/test_gradient_descent.py`. The gate tests convergence on a known convex function (`f(theta) = (theta-3)^2`), confirms the loss history is non-increasing, checks that gradient-norm history works when no `loss_fn` is given, and verifies multi-dimensional convergence. Done when `python -m pytest exercises/module2/gradient-descent` is green.

</div>
