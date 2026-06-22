# Decision Trees: Recursive Partitioning

The impurity functions from the previous lesson answer one question at a time: how much
does this split help? A decision tree is just that question asked greedily, over and
over, until there is nothing left to split.

## The Algorithm

At every node the tree does the same thing: try every (feature, threshold) pair, compute
the information gain for each, pick the best one, split the data along it, and recurse.
Stop when the node is pure, too small to split, or at the depth limit.

Prediction reverses the process. You walk the tree from root to leaf. At each internal
node you check the stored feature against the stored threshold and go left or right. At
the leaf you return the majority class among the training samples that ended up there.

This is a greedy algorithm. It picks the locally best split at each node without any
knowledge of what splits further down would look like. Finding the globally optimal tree
is NP-hard; greedy is the practical path, and it works well enough that the Azure Machine
Learning designer wraps exactly this strategy in its classification components. The
Two-Class Decision Forest and Multiclass Decision Forest both document that "decision
trees perform integrated feature selection and classification" through this greedy
split search, and that trees can "represent non-linear decision boundaries" precisely
because each split can operate on any feature, not just a linear combination
([Two-Class Decision Forest component](https://learn.microsoft.com/azure/machine-learning/component-reference/two-class-decision-forest?view=azureml-api-2),
[Multiclass Decision Forest component](https://learn.microsoft.com/azure/machine-learning/component-reference/multiclass-decision-forest?view=azureml-api-2)).

## The Code

The locked `_Node` dataclass and `DecisionTreeClassifier` below are the exact code the
acceptance gate imports. The impurity functions (`entropy`, `gini`, `information_gain`)
come from the same `ml/tree.py` file you built in the previous lesson: they are called,
not copied.

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

The split loop in `_grow` iterates over every feature, computes candidate thresholds as
midpoints between consecutive unique values, and calls `information_gain` from the
previous lesson for each one. That is the throughline: the tree reuses the impurity
functions; it does not re-implement them.

The `_Node` dataclass stores either a split (feature index, threshold, left child, right
child) or a leaf (majority class prediction). The `is_leaf` property checks which by
asking whether `prediction` is set. A walk from root to leaf is two or three dozen lines
of code total. That is the interpretability advantage: you can read every decision the
model makes.

## Measured Results

On Iris (150 samples, 3 classes, 4 features), with a stratified 80/20 split and
`random_state=0`:

- `DecisionTreeClassifier(max_depth=4, criterion="gini")`: test accuracy `0.9667`.
- scikit-learn's `DecisionTreeClassifier(max_depth=4, criterion="gini", random_state=0)`:
  test accuracy `0.9667`.
- Label-by-label agreement between the two on the 30 test samples: 100%. Both predict
  the same class for every point.

The agreement is not a coincidence. Both implementations search midpoints between
consecutive unique values and pick the split with the highest Gini gain. The same data
plus the same algorithm equals the same tree, which equals the same predictions. The
scikit-learn tree is the oracle; the agreement is the proof.

There is a catch worth naming. Greedy does not mean wrong; it means locally optimal.
The tree that maximizes information gain at each node is not guaranteed to be the
globally smallest or most accurate tree. On datasets where the best first split obscures
a better second split, greedy will miss. For the problems where this matters, Module 4
covers ensembles: train many trees on overlapping subsets of the data and take a vote.
The vote is more accurate than any single greedy tree.

## Core Concepts

- A decision tree fits by greedily selecting the (feature, threshold) pair with the
  highest information gain at each node, then recursing; it is not globally optimal but
  works well in practice.
- Prediction is a walk from root to leaf: at each node you branch on the stored feature
  and threshold; at the leaf you return the majority class of the training samples that
  landed there.
- `max_depth`, `min_samples_split`, and related stopping conditions control the
  bias-variance tradeoff; a tree with no limit memorizes the training set.
- A from-scratch tree and scikit-learn's tree agree on all 30 Iris test labels at
  `max_depth=4`, confirming that the greedy algorithm is deterministic given identical
  data and split logic.

<div class="claude-handoff" data-exercise="exercises/module3/decision-trees/">

**Build It in Claude Code**: Read the current state of `exercises/ml/tree.py` before
touching anything. The previous lesson already added `entropy`, `gini`, and
`information_gain` to that file. You are adding `_Node` and `DecisionTreeClassifier`
to the same file. Do not re-implement the impurity functions; call them.
Implement the classifier exactly as shown above. Then verify with the locked acceptance
gate at `exercises/module3/decision-trees/test_tree.py`. Done when
`python -m pytest exercises/module3/decision-trees` is green.

</div>
