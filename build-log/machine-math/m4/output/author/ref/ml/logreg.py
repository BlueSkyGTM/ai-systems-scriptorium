"""Logistic regression, from scratch in NumPy.

One idea: the sigmoid squashes a linear score to a probability; cross-entropy is the right
loss for probabilities; the gradient has the same elegant shape as linear regression's.
Binary only; reuses gradient_descent from M2 and zscore from M1.

Reuses:
- ml.gradient_descent.gradient_descent  (the shared optimizer)
- ml.distances.zscore                    (feature scaling before GD)
"""
import numpy as np
from ml.gradient_descent import gradient_descent


def _sigmoid(z):
    """Numerically stable sigmoid: clips z to avoid exp overflow."""
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


class LogisticRegression:
    """Gradient-descent logistic regression (binary, with intercept).

    Scales features with z-score before descent; predict / predict_proba work in
    the original feature space (scaling is applied internally).

    Parameters
    ----------
    lr : float
        Learning rate for gradient descent.
    n_iters : int
        Number of gradient steps.
    threshold : float
        Decision threshold for predict(). Default 0.5.
    """

    def __init__(self, lr=0.1, n_iters=1000, threshold=0.5):
        self.lr = lr
        self.n_iters = n_iters
        self.threshold = threshold
        self.w_ = None
        self.loss_history_ = None
        self._mu = None
        self._sd = None

    def fit(self, X, y):
        """Fit using gradient descent on binary cross-entropy loss."""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n, p = X.shape

        # Scale features; store moments for inference
        self._mu = X.mean(axis=0)
        self._sd = X.std(axis=0)
        self._sd = np.where(self._sd == 0.0, 1.0, self._sd)
        Xs = (X - self._mu) / self._sd

        ones = np.ones((n, 1))
        Xb = np.hstack([Xs, ones])

        # Cross-entropy gradient: dL/dw = (1/n) * X^T (sigmoid(Xw) - y)
        def grad_fn(w):
            probs = _sigmoid(Xb @ w)
            return (1.0 / n) * Xb.T @ (probs - y)

        def loss_fn(w):
            probs = _sigmoid(Xb @ w)
            # Clip to avoid log(0)
            probs = np.clip(probs, 1e-12, 1.0 - 1e-12)
            return float(-np.mean(y * np.log(probs) + (1 - y) * np.log(1 - probs)))

        w0 = np.zeros(p + 1)
        self.w_, self.loss_history_ = gradient_descent(
            grad_fn, w0, lr=self.lr, n_iters=self.n_iters, loss_fn=loss_fn
        )
        return self

    def _scaled_Xb(self, X):
        X = np.asarray(X, dtype=float)
        Xs = (X - self._mu) / self._sd
        ones = np.ones((X.shape[0], 1))
        return np.hstack([Xs, ones])

    def predict_proba(self, X):
        """Return probability of class 1 for each sample."""
        return _sigmoid(self._scaled_Xb(X) @ self.w_)

    def predict(self, X):
        """Return binary class labels using self.threshold."""
        return (self.predict_proba(X) >= self.threshold).astype(int)
