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
