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
