"""Acceptance gate for DecisionTreeClassifier.

On Iris (stratified 80/20, random_state=0):
- from-scratch tree clears >= 0.90 test accuracy.
- from-scratch tree agrees with sklearn's tree on >= 90% of test labels
  (exact tie-breaking differs; the floor + agreement check is sufficient).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as SklearnDT

from ml.tree import DecisionTreeClassifier


MAX_DEPTH = 4


def _load_split():
    X, y = load_iris(return_X_y=True)
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=0)


def test_iris_test_accuracy_clears_floor():
    """From-scratch tree must reach at least 90% test accuracy on Iris."""
    X_tr, X_te, y_tr, y_te = _load_split()
    clf = DecisionTreeClassifier(max_depth=MAX_DEPTH, criterion="gini").fit(X_tr, y_tr)
    preds = clf.predict(X_te)
    acc = float(np.mean(preds == y_te))
    assert acc >= 0.90, f"Test accuracy {acc:.4f} is below the 0.90 floor"


def test_iris_agrees_with_sklearn():
    """From-scratch and sklearn trees must agree on >= 90% of test labels."""
    X_tr, X_te, y_tr, y_te = _load_split()

    scratch = DecisionTreeClassifier(max_depth=MAX_DEPTH, criterion="gini").fit(X_tr, y_tr)
    sk = SklearnDT(max_depth=MAX_DEPTH, criterion="gini", random_state=0).fit(X_tr, y_tr)

    preds_scratch = scratch.predict(X_te)
    preds_sk = sk.predict(X_te)

    agreement = float(np.mean(preds_scratch == preds_sk))
    assert agreement >= 0.90, (
        f"Label agreement with sklearn = {agreement:.4f} (below 0.90). "
        f"scratch: {preds_scratch}, sklearn: {preds_sk}"
    )
