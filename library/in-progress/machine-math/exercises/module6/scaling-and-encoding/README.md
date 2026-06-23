# Exercise: Scaling and Encoding

**Goal:** Create `exercises/ml/features.py` and add `one_hot_encode` and `ordinal_encode` to it. The scaling functions (`zscore`, `minmax_scale`) already live in `ml.distances` from Module 1; import them, do not reimplement them. Verify both encoding functions against scikit-learn on fixed inputs.

**Why:** After this exercise you can look at any raw column in a real dataset and choose the right encoding. You will also have built the first piece of the feature-engineering library the capstone imports. Every model you train in the rest of this book depends on getting encoding right before the data reaches the algorithm.

## The Shared Artifact

Before touching any file, list the contents of `exercises/ml/` and read each file that exists. Earlier modules placed the following in that package:

```
exercises/ml/
  __init__.py        (empty, marks the package)
  distances.py       (M1: Euclidean, Manhattan, Cosine; zscore; minmax_scale)
  knn.py             (M1: KNNClassifier importing from ml.distances)
  tree.py            (M3: entropy, gini, information_gain, DecisionTreeClassifier,
                          DecisionTreeRegressor)
  ensemble.py        (M4: RandomForestClassifier, GradientBoostingRegressor)
  metrics.py         (M5: confusion_matrix, accuracy, precision, recall, f1,
                          roc_curve, roc_auc, mae, rmse, r2, slice_metric)
```

You are adding:

```
exercises/ml/
  features.py        (M6 lesson 1: one_hot_encode, ordinal_encode;
                                   imports zscore, minmax_scale from ml.distances)
```

The throughline: `ml/features.py` houses all feature-engineering logic. Later lessons in this module add `random_oversample`, `random_undersample`, `class_weights`, `select_by_variance`, and `select_by_importance` to the same file. The capstone imports `ml.features` directly; do not move the file or rename its entry points.

## Steps

### 1. Confirm the Current Package State

Open `exercises/ml/` and verify which files exist. Understand what each exports. You are not modifying any existing file.

### 2. Create `exercises/ml/features.py`

The file begins with the module docstring, then the imports (including `from ml.distances import zscore, minmax_scale`), then `one_hot_encode`, then `ordinal_encode`. Add them exactly as shown in the lesson. The complete starting state of the file for this lesson:

```python
"""ml/features.py -- feature engineering utilities, from scratch in NumPy.

Six tools housed here:

1. one_hot_encode      -- nominal -> binary indicator columns
2. ordinal_encode      -- ordered categorical -> integer codes
3. random_oversample   -- balance classes by upsampling the minority
4. random_undersample  -- balance classes by downsampling the majority
5. class_weights       -- inverse-frequency weights for cost-sensitive learning
6. select_by_variance  -- drop near-constant columns
7. select_by_importance -- keep top-k features ranked by forest split frequency

Scaling (zscore / minmax_scale) is imported from ml.distances; no reimplementation.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from ml.distances import zscore, minmax_scale  # re-export so callers can import from here too


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def one_hot_encode(
    col: np.ndarray,
) -> Tuple[np.ndarray, list]:
    """One-hot encode a 1-D categorical column.

    Each unique category gets its own binary column. Category order is
    sorted-unique (lexicographic for strings, numeric for numbers), so the
    mapping is deterministic regardless of data order.

    Parameters
    ----------
    col : array-like, shape (n,)
        Raw categorical values (strings or integers).

    Returns
    -------
    encoded : np.ndarray, shape (n, n_categories)
        Binary matrix; encoded[i, j] == 1 iff col[i] == categories[j].
    categories : list
        The sorted unique categories, one per column of encoded.
    """
    col = np.asarray(col)
    categories = sorted(set(col.tolist()))   # stable sorted order
    n = len(col)
    k = len(categories)
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    encoded = np.zeros((n, k), dtype=int)
    for i, val in enumerate(col):
        encoded[i, cat_to_idx[val]] = 1
    return encoded, categories


def ordinal_encode(
    col: np.ndarray,
    order: Optional[list] = None,
) -> Tuple[np.ndarray, list]:
    """Encode an ordinal categorical column as integer codes.

    Parameters
    ----------
    col : array-like, shape (n,)
        Raw categorical values.
    order : list or None
        Explicit ordered category list, e.g. ["low", "med", "high"].
        If None, uses sorted-unique order (ties go to lexicographic rank).

    Returns
    -------
    codes : np.ndarray, shape (n,), dtype int
        Integer codes aligned with order_used.
    order_used : list
        The category ordering that was applied.
    """
    col = np.asarray(col)
    if order is None:
        order_used = sorted(set(col.tolist()))
    else:
        order_used = list(order)
    cat_to_code = {c: i for i, c in enumerate(order_used)}
    codes = np.array([cat_to_code[v] for v in col], dtype=int)
    return codes, order_used
```

Leave placeholder comments for the resampling and feature-selection sections; the next lessons fill them in.

### 3. Run the Acceptance Gate

The locked test suite is at `exercises/module6/scaling-and-encoding/test_encoding.py`. Do not modify it.

```python
"""Acceptance gate: one-hot encoding and ordinal encoding.

Tests
-----
1. one_hot_encode produces the correct shape and one-hot rows on a known column.
2. one_hot_encode contents match sklearn.preprocessing.OneHotEncoder (up to column ordering).
3. ordinal_encode maps a given explicit order correctly (low/med/high -> 0/1/2).
4. ordinal_encode without an explicit order falls back to sorted-unique order.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest
from sklearn.preprocessing import OneHotEncoder

from ml.features import one_hot_encode, ordinal_encode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def color_col():
    return np.array(["red", "blue", "green", "blue", "red"])


@pytest.fixture
def grade_col():
    return np.array(["high", "low", "med", "low", "high", "med"])


# ---------------------------------------------------------------------------
# 1. one_hot_encode: shape and one-hot validity
# ---------------------------------------------------------------------------

def test_one_hot_shape(color_col):
    encoded, cats = one_hot_encode(color_col)
    assert encoded.shape == (len(color_col), len(cats)), (
        f"Expected shape ({len(color_col)}, {len(cats)}), got {encoded.shape}"
    )


def test_one_hot_rows_are_one_hot(color_col):
    """Each row must sum to 1 and contain only 0s and 1s."""
    encoded, _ = one_hot_encode(color_col)
    assert np.all(encoded.sum(axis=1) == 1), "Each row must have exactly one 1"
    assert set(np.unique(encoded)).issubset({0, 1}), "Values must be 0 or 1"


def test_one_hot_categories_sorted(color_col):
    """Categories must be in sorted order: blue, green, red."""
    _, cats = one_hot_encode(color_col)
    assert cats == sorted(cats), f"Categories not sorted: {cats}"


def test_one_hot_correct_indicator(color_col):
    """Verify specific indicator positions by name."""
    encoded, cats = one_hot_encode(color_col)
    cat_idx = {c: i for i, c in enumerate(cats)}
    # First sample is "red"
    assert encoded[0, cat_idx["red"]] == 1
    assert encoded[0, cat_idx["blue"]] == 0
    assert encoded[0, cat_idx["green"]] == 0
    # Second sample is "blue"
    assert encoded[1, cat_idx["blue"]] == 1


# ---------------------------------------------------------------------------
# 2. one_hot_encode matches sklearn (dense, sorted categories)
# ---------------------------------------------------------------------------

def test_one_hot_matches_sklearn(color_col):
    """Compare our encoding against sklearn.OneHotEncoder for the same column.

    sklearn OneHotEncoder with sparse_output=False and default alphabetic sort
    produces the same category order as our sorted-unique approach.
    """
    encoded, cats = one_hot_encode(color_col)

    sk_enc = OneHotEncoder(sparse_output=False)
    sk_encoded = sk_enc.fit_transform(color_col.reshape(-1, 1))
    sk_cats = list(sk_enc.categories_[0])

    # Map sklearn column order to our column order
    # (both should be alphabetically sorted, but we verify explicitly)
    assert cats == sk_cats, f"Category order mismatch: ours={cats}, sklearn={sk_cats}"
    np.testing.assert_array_equal(encoded, sk_encoded.astype(int))


# ---------------------------------------------------------------------------
# 3. ordinal_encode with explicit order
# ---------------------------------------------------------------------------

def test_ordinal_encode_explicit_order(grade_col):
    """low->0, med->1, high->2 when order=["low","med","high"]."""
    order = ["low", "med", "high"]
    codes, order_used = ordinal_encode(grade_col, order=order)
    assert order_used == order
    expected = np.array([2, 0, 1, 0, 2, 1])   # high,low,med,low,high,med
    np.testing.assert_array_equal(codes, expected)


# ---------------------------------------------------------------------------
# 4. ordinal_encode default (sorted-unique)
# ---------------------------------------------------------------------------

def test_ordinal_encode_default_order(grade_col):
    """Without explicit order, sorted unique gives high->0, low->1, med->2."""
    codes, order_used = ordinal_encode(grade_col)
    assert order_used == ["high", "low", "med"]   # sorted
    expected_map = {"high": 0, "low": 1, "med": 2}
    expected = np.array([expected_map[v] for v in grade_col])
    np.testing.assert_array_equal(codes, expected)
```

## Done When

```
python -m pytest exercises/module6/scaling-and-encoding
```

All seven tests pass: shape is correct; each row is one-hot; categories are sorted; specific indicator positions are correct; encoding matches scikit-learn; ordinal with explicit order maps correctly; ordinal without explicit order falls back to sorted-unique.

## Stretch

After the tests pass, encode the Iris dataset's target column (class names "setosa," "versicolor," "virginica") with both functions. With `one_hot_encode`, what shape does the result have? With `ordinal_encode` and no explicit order, what integer does "versicolor" receive? Now try fitting a KNN classifier from `ml.knn` on the one-hot-encoded version of a nominal feature. Does accuracy improve, degrade, or stay the same compared to ordinal encoding? Form a hypothesis before running the experiment.
