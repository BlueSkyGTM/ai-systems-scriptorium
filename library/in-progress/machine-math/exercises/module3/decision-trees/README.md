# Exercise: Decision Trees

**Goal:** Add `_Node` and `DecisionTreeClassifier` to `exercises/ml/tree.py` and verify
the classifier against scikit-learn on Iris.

**Why:** Building the classifier yourself locks in exactly what a "split" means in code:
iterating features, computing midpoint thresholds, calling `information_gain`, choosing
the best, and recursing. After this exercise you can open any decision tree implementation
and read it as a sequence of steps you have already written. The acceptance gate runs your
tree against scikit-learn's tree on the same data; if they agree on 90% or more of the
test labels, the algorithm is correct.

## The Shared Artifact

Before touching any file, open `exercises/ml/tree.py` and read what is already there.
The previous lesson added three functions to this file:

- `entropy(y)`: Shannon entropy in bits.
- `gini(y)`: Gini impurity.
- `information_gain(parent_y, left_y, right_y, criterion)`: impurity drop from a split.

You are adding the tree structure and classifier to the same file. Do not copy the
impurity functions; call them. The reuse is real: `DecisionTreeClassifier._grow` calls
`information_gain` on every candidate split. The throughline is intact because you import
nothing extra; it is all in `ml.tree`.

## Steps

### 1. Confirm What Is Already There

```
exercises/ml/tree.py    <- from Module 3, lesson 1: entropy, gini, information_gain
```

Read that file before writing anything. Understand the current module-level imports
(`from __future__ import annotations`, `dataclass`, `Optional`, `numpy`). They are
already in place; do not duplicate them.

### 2. Append to `exercises/ml/tree.py`

The locked structure below goes after the impurity functions in the same file. Do not
alter the impurity functions. Add exactly what is shown here.

```python
# ---------------------------------------------------------------------------
# Node structure
# ---------------------------------------------------------------------------

@dataclass
class _Node:
    """A node in the fitted tree. Either an internal split or a leaf."""
    # Internal split fields (None on a leaf)
    feature: Optional[int] = None
    threshold: Optional[float] = None
    left: Optional["_Node"] = None
    right: Optional["_Node"] = None
    # Leaf field
    prediction: Optional[int] = None

    @property
    def is_leaf(self) -> bool:
        return self.prediction is not None


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

class DecisionTreeClassifier:
    """Greedy, axis-aligned decision tree classifier.

    Parameters
    ----------
    max_depth : int or None
        Maximum depth of the tree. None means grow until pure or too few samples.
    criterion : "gini" or "entropy"
        Impurity measure used to choose splits.
    min_samples_split : int
        Do not split a node that has fewer than this many samples.
    """

    def __init__(
        self,
        max_depth: Optional[int] = None,
        criterion: str = "gini",
        min_samples_split: int = 2,
    ):
        self.max_depth = max_depth
        self.criterion = criterion
        self.min_samples_split = min_samples_split
        self.root_: Optional[_Node] = None
        self.n_classes_: int = 0

    # ------------------------------------------------------------------
    # fit
    # ------------------------------------------------------------------

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DecisionTreeClassifier":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        self.n_classes_ = int(y.max()) + 1
        self.root_ = self._grow(X, y, depth=0)
        return self

    def _grow(self, X: np.ndarray, y: np.ndarray, depth: int) -> _Node:
        n_samples, n_features = X.shape

        # Stopping conditions -> leaf
        pure = len(np.unique(y)) == 1
        too_small = n_samples < self.min_samples_split
        at_max = (self.max_depth is not None) and (depth >= self.max_depth)

        if pure or too_small or at_max:
            return _Node(prediction=self._majority(y))

        # Find the best split
        best_gain = -1.0
        best_feat: Optional[int] = None
        best_thresh: Optional[float] = None

        for feat in range(n_features):
            col = X[:, feat]
            unique_vals = np.unique(col)
            if len(unique_vals) < 2:
                continue
            # Candidate thresholds: midpoints between consecutive unique values
            thresholds = (unique_vals[:-1] + unique_vals[1:]) / 2.0

            for thresh in thresholds:
                mask = col <= thresh
                left_y, right_y = y[mask], y[~mask]
                if len(left_y) == 0 or len(right_y) == 0:
                    continue
                gain = information_gain(y, left_y, right_y, criterion=self.criterion)
                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = thresh

        # No beneficial split found -> leaf
        if best_feat is None or best_gain <= 0.0:
            return _Node(prediction=self._majority(y))

        mask = X[:, best_feat] <= best_thresh
        left_node = self._grow(X[mask], y[mask], depth + 1)
        right_node = self._grow(X[~mask], y[~mask], depth + 1)

        return _Node(
            feature=best_feat,
            threshold=best_thresh,
            left=left_node,
            right=right_node,
        )

    # ------------------------------------------------------------------
    # predict
    # ------------------------------------------------------------------

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        return np.array([self._traverse(self.root_, row) for row in X])

    def _traverse(self, node: _Node, row: np.ndarray) -> int:
        if node.is_leaf:
            return node.prediction
        if row[node.feature] <= node.threshold:
            return self._traverse(node.left, row)
        return self._traverse(node.right, row)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _majority(y: np.ndarray) -> int:
        counts = np.bincount(y)
        return int(np.argmax(counts))
```

### 3. Run the Acceptance Gate

The locked test suite is at `exercises/module3/decision-trees/test_tree.py`. It is
already in place; do not modify it.

```python
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
```

## Done When

```
python -m pytest exercises/module3/decision-trees
```

Both tests pass: from-scratch accuracy clears `0.90` on the Iris test set; label
agreement with scikit-learn clears `0.90` on the same 30 test samples.

## Stretch

After the tests pass, count the leaves in the fitted tree by writing a small recursive
function that traverses `clf.root_` and increments a counter at every node where
`is_leaf` is true. Then refit with `max_depth=None` and count again. How many leaves
does an unconstrained tree grow on Iris? Print the feature index and threshold at each
split in the depth-4 tree: do the splits match the feature importances you would expect
from Iris (petal length and petal width are the informative features)?
