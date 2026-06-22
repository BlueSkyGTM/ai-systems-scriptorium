# Exercise: Logistic Regression

**Goal:** Add `exercises/ml/logreg.py` to the throughline package, implementing a from-scratch
`LogisticRegression` that reuses `ml.gradient_descent` and `ml.distances.zscore`. Gate it on
breast-cancer: test accuracy must clear 0.95 and label agreement with scikit-learn must clear 0.95.

**Why:** The sigmoid is a one-line change on top of the gradient-descent machinery you already
built. If you can wire it in without duplicating the optimizer or the scaler, you understand
why the gradient shapes match and what the reuse is actually buying you.

## The Shared Artifact

`exercises/ml/` is the throughline package for this book. Module 1 contributed `ml/distances.py`
(metrics, `zscore`) and `ml/knn.py`. The start of Module 2 contributed `ml/gradient_descent.py`
and `ml/linreg.py`. This exercise adds `ml/logreg.py` beside them. Read the current state of
`ml/gradient_descent.py` before writing anything; you are calling its public interface, not
re-implementing it.

## Steps

### 1. Implement `exercises/ml/logreg.py`

The locked structure below is the contract the acceptance gate tests. Implement each method body;
do not alter signatures, docstrings, the `_sigmoid` helper, or the gradient/loss closures. The
only work is ensuring the pieces connect.

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

### 2. Run the Acceptance Gate

Place the locked test suite below at `exercises/module2/logistic-regression/test_logreg.py`.
scikit-learn is the oracle; the algorithm is yours.

```python
"""Acceptance gate for the logistic-regression exercise.

The from-scratch LogisticRegression must clear an accuracy floor on breast-cancer (a real
binary dataset) and agree with sklearn.linear_model.LogisticRegression's predictions at
a high rate. sklearn is the oracle; the algorithm is yours.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression as SklearnLR
from sklearn.model_selection import train_test_split

from ml.logreg import LogisticRegression
from ml.distances import zscore


def _split():
    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)


def _accuracy(pred, truth):
    return float(np.mean(np.asarray(pred) == np.asarray(truth)))


def test_accuracy_floor_on_breast_cancer():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s = zscore(X_tr)
    X_te_s = zscore(X_te)
    model = LogisticRegression(lr=0.1, n_iters=1000).fit(X_tr_s, y_tr)
    acc = _accuracy(model.predict(X_te_s), y_te)
    assert acc >= 0.95, f"Accuracy = {acc:.4f} below floor 0.95"


def test_agrees_with_sklearn():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s = zscore(X_tr)
    X_te_s = zscore(X_te)

    mine = LogisticRegression(lr=0.1, n_iters=1000).fit(X_tr_s, y_tr).predict(X_te_s)
    # sklearn with high max_iter to ensure convergence on the same scaled data
    ref = SklearnLR(max_iter=1000, random_state=0).fit(X_tr_s, y_tr).predict(X_te_s)

    agreement = float(np.mean(mine == ref))
    assert agreement >= 0.95, f"Label agreement with sklearn = {agreement:.4f} below 0.95"


def test_predict_proba_is_in_unit_interval():
    X_tr, X_te, y_tr, y_te = _split()
    X_tr_s = zscore(X_tr)
    X_te_s = zscore(X_te)
    model = LogisticRegression(lr=0.1, n_iters=1000).fit(X_tr_s, y_tr)
    proba = model.predict_proba(X_te_s)
    assert np.all(proba >= 0.0) and np.all(proba <= 1.0), "predict_proba returned values outside [0, 1]"


def test_loss_history_decreases():
    X_tr, _, y_tr, _ = _split()
    X_tr_s = zscore(X_tr)
    model = LogisticRegression(lr=0.1, n_iters=500).fit(X_tr_s, y_tr)
    history = model.loss_history_
    mid = len(history) // 2
    assert np.mean(history[:mid]) > np.mean(history[mid:]), "Cross-entropy did not decrease over training"
```

## Done When

```
python -m pytest exercises/module2/logistic-regression
```

All four tests pass: accuracy clears 0.95, label agreement with scikit-learn clears 0.95,
`predict_proba` returns values in [0, 1], and cross-entropy falls over training.

## Stretch

Check the loss at step 0: it should be very close to `log(2) ≈ 0.693`. Verify that `w = 0` at
initialization means `sigmoid(0) = 0.5` for every sample, which gives exactly that loss. Then
lower the threshold from 0.5 to 0.3 and rerun `predict` on the test set: report how accuracy
and the distribution of predicted labels change. Explain in one sentence why lowering the
threshold raises recall at the cost of precision.
