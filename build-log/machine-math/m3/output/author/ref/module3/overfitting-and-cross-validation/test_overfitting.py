"""Acceptance gate: overfitting demonstration.

As max_depth rises from 1 to a large value on breast cancer data:
- TRAIN accuracy climbs toward 1.0 (a deep tree memorizes the training set).
- TEST accuracy peaks at a moderate depth and does not keep improving.
- Specifically: the fully-grown tree's test accuracy must be <= the best shallow tree's test accuracy,
  proving that depth beyond a point hurts generalization.

Uses sklearn.datasets.load_breast_cancer (seeded split) so the effect is reliable and measurable.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

from ml.tree import DecisionTreeClassifier


DEPTHS = [1, 2, 3, 4, 5, 7, 10, 15, 20]


def _load_split():
    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.25, random_state=42)


def test_train_accuracy_climbs_with_depth():
    """Training accuracy must increase monotonically as max_depth grows."""
    X_tr, X_te, y_tr, y_te = _load_split()
    train_accs = []
    for d in DEPTHS:
        clf = DecisionTreeClassifier(max_depth=d, criterion="gini").fit(X_tr, y_tr)
        train_accs.append(float(np.mean(clf.predict(X_tr) == y_tr)))

    # Each step should be >= the previous (allow tiny float ties)
    for i in range(1, len(train_accs)):
        assert train_accs[i] >= train_accs[i - 1] - 1e-9, (
            f"Train accuracy dropped from depth {DEPTHS[i-1]} ({train_accs[i-1]:.4f}) "
            f"to depth {DEPTHS[i]} ({train_accs[i]:.4f})"
        )

    # The deep tree should nearly memorize the training set
    assert train_accs[-1] >= 0.99, (
        f"Deep tree train accuracy {train_accs[-1]:.4f} expected to near 1.0"
    )


def test_deep_tree_overfits():
    """The fully-grown tree's test accuracy must be no better than the best shallow tree's.

    This is the overfitting signal: train goes up, test plateaus and falls back.
    """
    X_tr, X_te, y_tr, y_te = _load_split()

    shallow_depths = [d for d in DEPTHS if d <= 5]
    deep_depth = DEPTHS[-1]  # 20

    shallow_test_accs = []
    for d in shallow_depths:
        clf = DecisionTreeClassifier(max_depth=d, criterion="gini").fit(X_tr, y_tr)
        shallow_test_accs.append(float(np.mean(clf.predict(X_te) == y_te)))

    best_shallow = max(shallow_test_accs)

    deep_clf = DecisionTreeClassifier(max_depth=deep_depth, criterion="gini").fit(X_tr, y_tr)
    deep_test = float(np.mean(deep_clf.predict(X_te) == y_te))

    assert deep_test <= best_shallow, (
        f"Expected deep tree (depth={deep_depth}) test acc {deep_test:.4f} "
        f"to be <= best shallow (depth<=5) test acc {best_shallow:.4f}. "
        f"Overfitting not demonstrated."
    )


def test_unlimited_depth_memorizes_train():
    """A tree with no depth limit should perfectly memorize the training set."""
    X_tr, X_te, y_tr, y_te = _load_split()
    clf = DecisionTreeClassifier(max_depth=None, criterion="gini").fit(X_tr, y_tr)
    train_acc = float(np.mean(clf.predict(X_tr) == y_tr))
    assert train_acc == 1.0, (
        f"Unlimited-depth tree should memorize training set; got {train_acc:.4f}"
    )
