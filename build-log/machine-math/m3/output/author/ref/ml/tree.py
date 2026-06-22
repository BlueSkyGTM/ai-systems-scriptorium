"""Decision tree classifier, from scratch in NumPy.

One idea: partition the feature space greedily -- at each node pick the (feature, threshold) split
that reduces impurity the most, then recurse. The math is just weighted averages of entropy or Gini;
the structure is just a binary tree of those choices frozen at fit time.

No sklearn inside the algorithm. Pure NumPy + Python dataclasses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Impurity functions
# ---------------------------------------------------------------------------

def entropy(y: np.ndarray) -> float:
    """Shannon entropy in bits: -sum p_i * log2(p_i). Returns 0.0 for a pure set."""
    y = np.asarray(y)
    n = len(y)
    if n == 0:
        return 0.0
    counts = np.bincount(y.astype(int))
    probs = counts[counts > 0] / n
    if len(probs) <= 1:          # pure node: -p*log2(p) = -1*0 = 0 exactly
        return 0.0
    return float(-np.sum(probs * np.log2(probs)))


def gini(y: np.ndarray) -> float:
    """Gini impurity: 1 - sum p_i^2. Returns 0.0 for a pure set."""
    y = np.asarray(y)
    n = len(y)
    if n == 0:
        return 0.0
    counts = np.bincount(y.astype(int))
    probs = counts / n
    return float(1.0 - np.sum(probs ** 2))


def information_gain(
    parent_y: np.ndarray,
    left_y: np.ndarray,
    right_y: np.ndarray,
    criterion: str = "gini",
) -> float:
    """Impurity of the parent minus the size-weighted average impurity of the two children.

    Parameters
    ----------
    parent_y : labels at the current node before the split.
    left_y   : labels routed to the left child.
    right_y  : labels routed to the right child.
    criterion: "gini" or "entropy".
    """
    impurity_fn = {"gini": gini, "entropy": entropy}
    if criterion not in impurity_fn:
        raise ValueError(f"criterion must be 'gini' or 'entropy', got {criterion!r}")
    fn = impurity_fn[criterion]

    n = len(parent_y)
    n_l, n_r = len(left_y), len(right_y)
    if n == 0:
        return 0.0
    weighted_child = (n_l / n) * fn(left_y) + (n_r / n) * fn(right_y)
    return float(fn(parent_y) - weighted_child)


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
