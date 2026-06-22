"""Acceptance gate for impurity functions.

Tests: entropy, gini, information_gain from ml.tree.
All assertions check known closed-form values from information theory.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import numpy as np
import pytest

from ml.tree import entropy, gini, information_gain


# ---------------------------------------------------------------------------
# entropy
# ---------------------------------------------------------------------------

def test_entropy_pure_array():
    """A node where all labels are the same has zero entropy."""
    assert entropy(np.array([1, 1, 1, 1])) == 0.0
    assert entropy(np.array([0, 0, 0])) == 0.0


def test_entropy_balanced_two_class():
    """Equal split of two classes: entropy = log2(2) = 1.0 bit."""
    y = np.array([0, 0, 1, 1])
    assert abs(entropy(y) - 1.0) < 1e-9


def test_entropy_balanced_four_class():
    """Equal split of four classes: entropy = log2(4) = 2.0 bits."""
    y = np.array([0, 1, 2, 3])
    assert abs(entropy(y) - 2.0) < 1e-9


# ---------------------------------------------------------------------------
# gini
# ---------------------------------------------------------------------------

def test_gini_pure_array():
    """A node where all labels are the same has zero Gini impurity."""
    assert gini(np.array([2, 2, 2])) == 0.0
    assert gini(np.array([0, 0, 0, 0, 0])) == 0.0


def test_gini_balanced_two_class():
    """Equal split of two classes: Gini = 1 - (0.5^2 + 0.5^2) = 0.5."""
    y = np.array([0, 0, 1, 1])
    assert abs(gini(y) - 0.5) < 1e-9


def test_gini_six_four_split():
    """60/40 class split: Gini = 1 - (0.6^2 + 0.4^2) = 1 - (0.36 + 0.16) = 0.48."""
    y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])  # 6 zeros, 4 ones
    assert abs(gini(y) - 0.48) < 1e-9


# ---------------------------------------------------------------------------
# information_gain
# ---------------------------------------------------------------------------

def test_information_gain_perfect_split():
    """A split that perfectly separates two classes should yield positive gain."""
    parent = np.array([0, 0, 0, 1, 1, 1])
    left   = np.array([0, 0, 0])
    right  = np.array([1, 1, 1])
    # Both criteria should give the full parent impurity as gain
    gain_gini = information_gain(parent, left, right, criterion="gini")
    gain_entr = information_gain(parent, left, right, criterion="entropy")
    assert gain_gini > 0.0, f"Expected positive gain, got {gain_gini}"
    assert gain_entr > 0.0, f"Expected positive gain, got {gain_entr}"


def test_information_gain_useless_split():
    """A split that preserves class proportions should yield ~0 gain."""
    # Same 50/50 split on both sides
    parent = np.array([0, 0, 1, 1, 0, 0, 1, 1])
    left   = np.array([0, 0, 1, 1])
    right  = np.array([0, 0, 1, 1])
    gain_gini = information_gain(parent, left, right, criterion="gini")
    gain_entr = information_gain(parent, left, right, criterion="entropy")
    assert abs(gain_gini) < 1e-9, f"Expected ~0 gain, got {gain_gini}"
    assert abs(gain_entr) < 1e-9, f"Expected ~0 gain, got {gain_entr}"
