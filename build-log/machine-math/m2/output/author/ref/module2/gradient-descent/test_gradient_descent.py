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
