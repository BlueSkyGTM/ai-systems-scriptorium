# Exercise: Feature Selection

**Goal:** Add `select_by_variance` and `select_by_importance` to
`exercises/ml/features.py`. The gate asserts that `select_by_variance` drops an injected
constant column, and that `select_by_importance` identifies the single informative
feature in an 8-column dataset where 7 columns are pure noise.

**Why:** More features is not better. A near-constant column carries no information; a
noise column wastes a dimension the model must search. This exercise makes you build and
run both selection functions, confirm they find the signal, and prove that a model on
the selected subset performs at least as well as a model on the full set.

## The Shared Artifact

This exercise adds two functions to `exercises/ml/features.py`. Before writing anything:

1. List `exercises/ml/` and read the current `features.py` to see what exists from
   earlier modules.
2. Read `exercises/ml/ensemble.py` to confirm `RandomForestClassifier` exists and check
   its `fit` and `predict` signatures. The `select_by_importance` function imports it
   directly; the import must resolve before the gate will run.

Do not duplicate any function that already exists in the package.

## Steps

### 1. Add the Selection Functions

Open `exercises/ml/features.py` and append the following two functions after the
resampling functions added in the previous exercise.

```python
def select_by_variance(
    X: np.ndarray,
    threshold: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Drop columns whose variance is <= threshold.

    A column with zero (or near-zero) variance carries no information;
    dropping it reduces noise for distance- and coefficient-based learners.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    threshold : float
        Columns with var <= threshold are removed.

    Returns
    -------
    X_selected : np.ndarray, shape (n, k)  where k <= p
    kept_indices : np.ndarray of int, shape (k,)
    """
    X = np.asarray(X, dtype=float)
    variances = X.var(axis=0)
    kept = np.where(variances > threshold)[0]
    return X[:, kept], kept


def select_by_importance(
    X: np.ndarray,
    y: np.ndarray,
    k: int,
    random_state: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Keep the top-k features by permutation importance.

    Importance proxy: permutation importance
    ----------------------------------------
    A random forest is fit on an 80% training split. Each feature's importance
    is measured as the accuracy drop on the held-out 20% when that feature's
    values are randomly shuffled. Shuffling breaks the association between that
    feature and the label; a large accuracy drop means the model relied on that
    feature heavily. Features with near-zero (or negative) drop are noise.

    This proxy is straightforward and signal-based: noise features that happen
    to appear in many trees (due to random subsampling) don't get inflated
    counts -- they simply don't hurt accuracy when shuffled.

    The RandomForestClassifier from ml.ensemble is used.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    k : int
        Number of features to keep.
    random_state : int or None

    Returns
    -------
    X_selected : np.ndarray, shape (n, k)
    kept_indices : np.ndarray of int, shape (k,)
        Original column indices, sorted ascending.
    """
    from ml.ensemble import RandomForestClassifier

    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    n_samples, n_features = X.shape

    # Split 80/20 to get an honest evaluation set for permutation
    rng = np.random.default_rng(random_state)
    idx = rng.permutation(n_samples)
    n_train = int(n_samples * 0.8)
    train_idx, test_idx = idx[:n_train], idx[n_train:]

    forest = RandomForestClassifier(
        n_estimators=50,
        max_depth=None,
        max_features="sqrt",
        random_state=random_state,
    )
    forest.fit(X[train_idx], y[train_idx])

    X_test = X[test_idx]
    y_test = y[test_idx]
    baseline = float(np.mean(forest.predict(X_test) == y_test))

    # Permutation importance: accuracy drop when feature f is shuffled
    rng_perm = np.random.default_rng((random_state or 0) + 1)
    importance = np.zeros(n_features, dtype=float)
    for f in range(n_features):
        X_perm = X_test.copy()
        X_perm[:, f] = rng_perm.permutation(X_test[:, f])
        perm_acc = float(np.mean(forest.predict(X_perm) == y_test))
        importance[f] = baseline - perm_acc  # positive = feature mattered

    # Rank descending by importance; keep top-k
    ranked = np.argsort(importance)[::-1]
    kept = np.sort(ranked[:k])
    return X[:, kept], kept
```

### 2. Place the Acceptance Gate

Create `exercises/module6/feature-selection/test_selection.py` with the exact content
below. Do not modify it.

```python
"""Acceptance gate: feature selection.

Tests
-----
1. select_by_variance drops an injected near-constant column and keeps informative ones.
2. select_by_importance keeps the known informative feature in its top-k (permutation proxy).
3. A classifier on the selected subset scores >= 0.80 accuracy.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.datasets import make_classification

from ml.features import select_by_variance, select_by_importance
from ml.tree import DecisionTreeClassifier


# ---------------------------------------------------------------------------
# 1. select_by_variance
# ---------------------------------------------------------------------------

def test_variance_drops_constant_column():
    """An injected constant column (variance=0) must be removed."""
    rng = np.random.default_rng(7)
    n, p = 100, 5
    X = rng.normal(0, 1, size=(n, p))
    # Inject a constant column at index 2
    X[:, 2] = 5.0
    X_sel, kept = select_by_variance(X, threshold=0.0)
    assert 2 not in kept, f"Constant column 2 should have been dropped; kept={kept}"


def test_variance_keeps_informative_columns():
    """Columns with variance > threshold must be retained."""
    rng = np.random.default_rng(8)
    n, p = 100, 5
    X = rng.normal(0, 1, size=(n, p))
    # All columns have variance ~1; threshold=0.5 should keep all
    X_sel, kept = select_by_variance(X, threshold=0.5)
    assert len(kept) == p, f"All {p} columns should be kept; kept={kept}"


def test_variance_selection_shape():
    rng = np.random.default_rng(9)
    X = rng.normal(0, 1, size=(50, 6))
    X[:, 0] = 3.14   # constant
    X_sel, kept = select_by_variance(X, threshold=0.0)
    assert X_sel.shape[1] == len(kept)
    assert X_sel.shape[0] == 50


# ---------------------------------------------------------------------------
# 2. select_by_importance: known informative feature is in top-k
#
# make_classification with shuffle=False and n_informative=1 guarantees that
# column 0 is the sole informative feature; all other columns are pure noise.
# class_sep=3.0 and n_clusters_per_class=1 give a clean, strong signal so
# the permutation-importance proxy can find it reliably across seeds.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def informative_dataset():
    """One strongly informative feature (col 0) + 7 pure noise columns.

    sklearn.datasets.make_classification with shuffle=False places the
    informative columns first. With n_informative=1 and class_sep=3.0 the
    signal is unambiguous and appears in col 0.
    """
    X, y = make_classification(
        n_samples=600,
        n_features=8,
        n_informative=1,
        n_redundant=0,
        n_repeated=0,
        n_clusters_per_class=1,
        n_classes=2,
        class_sep=3.0,
        random_state=0,
        shuffle=False,
    )
    informative_index = 0   # guaranteed by shuffle=False, n_informative=1
    return X, y, informative_index


def test_importance_keeps_informative_feature(informative_dataset):
    """Top-1 selected feature must be the known informative column (col 0)."""
    X, y, info_idx = informative_dataset
    X_sel, kept = select_by_importance(X, y, k=1, random_state=42)
    assert info_idx in kept, (
        f"Informative feature {info_idx} not found in top-1 kept={kept}"
    )


def test_importance_selection_shape(informative_dataset):
    X, y, _ = informative_dataset
    k = 3
    X_sel, kept = select_by_importance(X, y, k=k, random_state=0)
    assert X_sel.shape[1] == k
    assert len(kept) == k


def test_importance_selected_subset_accuracy(informative_dataset):
    """A decision tree on the top-1 selected feature must hit >= 0.80 accuracy."""
    X, y, _ = informative_dataset
    rng = np.random.default_rng(5)
    idx = rng.permutation(len(y))
    n_train = int(0.8 * len(y))
    train_idx, test_idx = idx[:n_train], idx[n_train:]

    X_sel, _ = select_by_importance(X, y, k=1, random_state=42)

    clf = DecisionTreeClassifier(max_depth=4)
    clf.fit(X_sel[train_idx], y[train_idx])
    y_pred = clf.predict(X_sel[test_idx])
    acc = float(np.mean(y_pred == y[test_idx]))
    assert acc >= 0.80, f"Expected accuracy >= 0.80 on selected feature, got {acc:.4f}"
```

## Done When

```
python -m pytest exercises/module6/feature-selection
```

All assertions pass:

- `test_variance_drops_constant_column`: an injected constant column at index 2 is
  absent from `kept`.
- `test_variance_keeps_informative_columns`: all 5 normal-variance columns survive a
  threshold of 0.5.
- `test_variance_selection_shape`: output shape matches the number of kept indices.
- `test_importance_keeps_informative_feature`: column 0 (the sole informative feature in
  an 8-column dataset) appears in the top-1 selection.
- `test_importance_selection_shape`: the returned arrays have the correct dimensions.
- `test_importance_selected_subset_accuracy`: a decision tree on the single selected
  feature scores at least 0.80 on a held-out set.

Together these confirm both selection functions work: variance filter catches obvious
useless columns, and permutation importance finds the real signal even when 7 of 8
columns are noise.

## Stretch

After the gate passes, run both functions on the same 8-column dataset and compare their
outputs. Does `select_by_variance` with threshold 0.0 drop any columns? (It should not:
all 8 have nonzero variance.) Does that mean it is useless here? What would have to be
true about a dataset for variance filtering to be the right first pass? Write one
paragraph explaining when you would reach for each method and why.
