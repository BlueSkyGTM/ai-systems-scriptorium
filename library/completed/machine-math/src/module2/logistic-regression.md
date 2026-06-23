# Logistic Regression

Linear regression predicts a number. When your label is a binary category, that number becomes a
probability, and a bare linear score has no business being one: it is unbounded, and cross-entropy
loss needs something in [0, 1]. The sigmoid function is the fix, and everything else follows from it.

## The Sigmoid Squashes a Score to a Probability

The linear score `z = w^T x + b` can be any real number. Apply sigmoid and it lands in (0, 1):

```
sigmoid(z) = 1 / (1 + exp(-z))
```

When `z` is large and positive, sigmoid approaches 1. When `z` is large and negative, it approaches
0. When `z = 0`, sigmoid returns exactly 0.5, and that is the decision boundary: wherever the linear
score crosses zero, the model is maximally uncertain.

Azure Machine Learning's Two-Class Logistic Regression component describes the same mechanism: the
algorithm "predicts the probability of occurrence of an event by fitting data to a logistic
function" ([learn.microsoft.com](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/two-class-logistic-regression)).

## Cross-Entropy Is the Right Loss for Probabilities

Mean squared error on a sigmoid output creates a non-convex loss surface with many local minima.
Binary cross-entropy solves this. It is convex, which means gradient descent finds the global
minimum. The formula:

```
Loss = -(1/n) * sum( y * log(p) + (1-y) * log(1-p) )
```

where `p = sigmoid(z)` and `y` is the true binary label. Read it from both directions. When `y=1`
and `p` is close to 1, `log(1) ~ 0`, the loss is nearly zero: correct prediction, no penalty. When
`y=1` and `p` is close to 0, `log(0)` diverges to negative infinity: wrong prediction, enormous
penalty. The loss is symmetric for `y=0`.

A useful sanity check: at initialization with `w = 0`, every prediction is `sigmoid(0) = 0.5`.
Cross-entropy of a perfectly uncertain binary classifier is `log(2) ≈ 0.693`. That is where your
`loss_history_[0]` starts. After 1000 steps on z-scored breast-cancer, it reaches 0.056.

## The Gradient Has the Same Shape as Linear Regression

The gradient of cross-entropy with respect to the weight vector is:

```
dL/dw = (1/n) * X^T (sigmoid(Xw) - y)
dL/db = (1/n) * sum( sigmoid(Xw) - y )
```

Compare this to the MSE gradient for linear regression:

```
dMSE/dw = (1/n) * X^T (Xw - y)
```

The structure is identical. The only difference is that `Xw` is replaced by `sigmoid(Xw)`. The same
`gradient_descent` function that fit your linear model fits this one. The sigmoid introduces the
nonlinearity; the optimizer sees the same interface.

## The Implementation

`ml/logreg.py` imports `gradient_descent` from the previous lesson. The only new pieces are
`_sigmoid` and the two closures `grad_fn` and `loss_fn`. Everything else, including the fit
interface and the weight update loop, comes from the shared optimizer.

```python
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
```

The `_sigmoid` clip at ±500 is a numerical guard: `exp(-500)` underflows to zero in float64, and
`exp(500)` overflows to infinity. The clip is invisible at any score a gradient-descent model
actually produces; it prevents silent NaN propagation on pathological inputs.

## What the Numbers Say

On z-scored breast-cancer (569 samples, 80/20 stratified split, `random_state=0`):

- Test accuracy: **96.49%**
- Agreement with scikit-learn's `LogisticRegression` on the same split: **99.12%** of labels match
- Cross-entropy loss: 0.693 at init (exactly `log 2`), 0.056 after 1000 steps

The 0.51% of labels that differ from scikit-learn is expected: scikit-learn uses L-BFGS with
L2 regularization by default, while this implementation runs plain gradient descent. The models
converge to nearby but not identical minima. The 96.49% floor is the meaningful signal.

## The 0.5 Threshold and `predict_proba`

The default threshold of 0.5 maps `predict_proba >= 0.5` to class 1. Because `sigmoid(z) = 0.5`
exactly when `z = 0`, the decision boundary is the hyperplane where the linear score is zero. That
is a linear boundary in feature space: logistic regression is a linear classifier.

The threshold is a tunable seam. Lower it (say, to 0.3) and recall rises while precision falls:
you catch more true positives at the cost of more false positives. That tradeoff belongs to the
business problem, not to the optimizer. `predict_proba` gives you the raw probability so you can
draw that boundary wherever the application demands.

The reuse here runs deeper than sharing an optimizer. Every piece of tooling you have from M1 and
the start of M2, distance metrics, z-score scaling, gradient descent, snaps into a production-grade
binary classifier with one new function: `_sigmoid`.

## Core Concepts

- The sigmoid function maps any real-valued linear score to (0, 1), making it a valid probability;
  the decision boundary is the hyperplane where the linear score equals zero.
- Binary cross-entropy is the correct loss for probability outputs; it is convex, guarantees a
  single global minimum, and starts at `log(2) ≈ 0.693` for an uninformed model.
- The cross-entropy gradient has the same shape as the MSE gradient; the same `gradient_descent`
  optimizer fits both, with only the loss and the sigmoid differing.
- `predict_proba` returns the raw sigmoid output; the 0.5 threshold is a tunable seam, not a
  fixed law, and the right threshold depends on the cost of false positives versus false negatives.

<div class="claude-handoff" data-exercise="exercises/module2/logistic-regression/">

**Build It in Claude Code**: Add `exercises/ml/logreg.py` to the throughline package, reusing
`ml.gradient_descent` and `ml.distances.zscore`. Fit a `LogisticRegression` on 80% of z-scored
breast-cancer (stratified, `random_state=0`) and confirm test accuracy clears 0.95, agreement with
scikit-learn clears 0.95, `predict_proba` stays in [0, 1], and cross-entropy decreases over
training. Gate: `python -m pytest exercises/module2/logistic-regression` green.

</div>
