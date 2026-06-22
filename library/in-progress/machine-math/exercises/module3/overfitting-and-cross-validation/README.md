# Exercise: Overfitting and Cross-Validation

**Goal:** Write the depth-sweep experiment: fit `ml.tree.DecisionTreeClassifier` on breast
cancer data at rising `max_depth`, measure train accuracy and test accuracy, and demonstrate
overfitting by measurement. The gate asserts that train accuracy climbs toward 1.000 while the
deep tree's test accuracy is no better than the best shallow tree's.

**Why:** Overfitting is not a diagram in a textbook. It is a number: the gap between train
accuracy and test accuracy, measured on held-out data. This exercise makes you produce that
number, prove the gap exists, and confirm that the fully grown tree memorizes the training set
while a shallower tree generalizes better.

## The Shared Artifact

This exercise does not add a new file to `exercises/ml/`. It uses `ml.tree.DecisionTreeClassifier`,
already in the package from the decision tree lesson. Before writing anything, list
`exercises/ml/` and read `ml/tree.py` to confirm the `fit` and `predict` signatures and the
`max_depth` and `criterion` parameters. You are calling existing code, not writing new package
code.

## Steps

### 1. Write the Experiment Script

Create `exercises/module3/overfitting-and-cross-validation/experiment.py`. The experiment must:

1. Load `sklearn.datasets.load_breast_cancer`.
2. Split with `sklearn.model_selection.train_test_split`, `test_size=0.25`, `random_state=42`.
3. For each depth in `[1, 2, 3, 4, 7, None]`:
   a. Fit `DecisionTreeClassifier(max_depth=d, criterion="gini")` on the training split.
   b. Predict on the training split and the test split.
   c. Record train accuracy and test accuracy.
4. Print the table.

The table should reproduce:

| max_depth | Train accuracy | Test accuracy |
|-----------|----------------|---------------|
| 1         | 0.923          | 0.895         |
| 2         | 0.946          | 0.916         |
| 3         | 0.972          | 0.951         |
| 4         | 0.995          | 0.944         |
| 7         | 1.000          | 0.944         |
| None      | 1.000          | 0.944         |

Confirm that train accuracy reaches 1.000 by depth 7 and that test accuracy peaks at depth 3
then stays flat or falls.

### 2. Run the Acceptance Gate

Place the locked test suite below at
`exercises/module3/overfitting-and-cross-validation/test_overfitting.py`. This is the
overfitting gate: the deep tree memorizing the training set is the pass condition.

```python
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
```

## Done When

```
python -m pytest exercises/module3/overfitting-and-cross-validation
```

All three assertions pass:

- `test_train_accuracy_climbs_with_depth`: train accuracy is monotonically non-decreasing and
  the deepest tree reaches at least 0.99.
- `test_deep_tree_overfits`: the depth-20 tree's test accuracy is no better than the best
  depth-1-through-5 tree's test accuracy.
- `test_unlimited_depth_memorizes_train`: a tree with `max_depth=None` achieves exactly 1.000
  train accuracy.

Together these confirm the overfitting signature: the tree memorizes the training set, and more
depth past the sweet spot does not improve generalization.

## Stretch

After the gate passes, add a cross-validation sweep. For each candidate depth in
`[1, 2, 3, 4, 5, 7]`, use `sklearn.model_selection.cross_val_score` with 5 folds on the
training split (not the test split). Print the mean and standard deviation of the cross-validated
accuracy for each depth. Which depth does the cross-validation sweep select? Does it match the
depth that produced the best test accuracy in the table? Report what you observe. Then seal
the test set: confirm that the depth chosen by cross-validation also performs well on the test
split, without tuning on the test split to find it.
