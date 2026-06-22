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
