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
