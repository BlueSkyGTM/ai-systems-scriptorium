# Exercise: Entropy and Information Gain

**Goal:** Build the three impurity functions (`entropy`, `gini`, `information_gain`) in
`exercises/ml/tree.py` and verify them against closed-form values that come directly
from information theory.

**Why:** Entropy and Gini are the foundation every decision tree stands on. If your ruler
is wrong, every split in the tree is wrong. This exercise proves the ruler is right by
checking it against values you can derive on paper: pure sets score zero, balanced
two-class nodes score exactly one bit, balanced four-class nodes score exactly two bits.
The acceptance gate runs those checks. If all of them pass, you own the impurity math.

## The Shared Artifact

Before touching any file, list the files in `exercises/ml/` and read what is already
there. You are adding to an existing package:

- `exercises/ml/distances.py`: distance metrics and scalers from Module 1.
- `exercises/ml/gradient_descent.py`: the shared optimizer from Module 2.
- `exercises/ml/linreg.py`: linear regression from Module 2.
- `exercises/ml/logreg.py`: logistic regression from Module 2 (if present).

The file you are creating is `exercises/ml/tree.py`. It starts a new throughline for
Module 3; Module 3's second lesson will add the classifier to the same file. Do not
touch the earlier module files.

## Steps

### 1. Confirm What Is Already There

```
exercises/ml/__init__.py           <- already exists
exercises/ml/distances.py          <- from Module 1 (do not touch)
exercises/ml/gradient_descent.py   <- from Module 2, lesson 1 (do not touch)
exercises/ml/linreg.py             <- from Module 2, lesson 2 (do not touch)
```

### 2. Implement `exercises/ml/tree.py`

The locked structure below is the contract the acceptance gate imports. Implement it
exactly as shown; do not alter signatures, docstrings, import paths, or logic. The file
header and impurity functions are the full contract for this exercise; the classifier
that follows in the next lesson will be appended to the same file.

```python
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
```

### 3. Run the Acceptance Gate

The locked test suite is at `exercises/module3/entropy-and-information-gain/test_impurity.py`.
It is already in place; do not modify it. The tests check:

```python
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
```

## Done When

```
python -m pytest exercises/module3/entropy-and-information-gain
```

All seven tests pass: pure arrays score zero for both entropy and Gini; balanced
two-class and four-class nodes hit the exact theoretical values; the 60/40 split scores
`0.48` Gini; a perfect split yields positive gain under both criteria; a useless split
yields zero gain under both criteria.

## Stretch

Pick a node with 4 cats, 3 dogs, and 3 birds (10 samples, three classes). Compute its
entropy and Gini by hand, then verify with your functions. Try every possible binary
split on the label vector and find the one with the highest information gain. Compare
your answer to the worked example in the lesson source: does the algorithm always pick
the same winner?
