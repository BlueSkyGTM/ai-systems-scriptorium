# Entropy and Information Gain

Every split in a decision tree is a bet: this question divides the labels better than
any other question you could ask right now. To evaluate that bet you need a ruler for
disorder. Entropy and Gini impurity are two such rulers; information gain is what you
read off the ruler after a split.

## What Entropy Measures

Shannon entropy answers: how many bits do you need to encode the labels in a node?

```
H(y) = -sum(p_i * log2(p_i))   for each class i with proportion p_i
```

The base-2 logarithm gives the answer in bits. Two properties follow directly from the
formula and are worth committing to memory.

A pure node, where every label is the same class, has entropy zero. One class, `p = 1`,
contributes `-(1 * log2(1)) = 0`. You need no bits to encode what you already know with
certainty.

A balanced two-class node has entropy exactly one bit. Both classes appear with `p = 0.5`
each, so `H = -(0.5 * log2(0.5) + 0.5 * log2(0.5)) = -(0.5 * -1 + 0.5 * -1) = 1.0`.
You need exactly one bit of information to resolve the label.

A balanced four-class node has entropy exactly two bits: `log2(4) = 2.0`. Each additional
doubling of equally probable classes costs one more bit.

## What Gini Impurity Measures

Gini impurity answers a different but related question: if you randomly drew a sample from
the node and labeled it according to the class distribution, what is the probability you
labeled it wrong?

```
Gini(y) = 1 - sum(p_k^2)   for each class k with proportion p_k
```

The same pure/mixed intuition holds. A pure node has `Gini = 0`: you can never mislabel
what you already know. A balanced two-class node has `Gini = 1 - (0.5^2 + 0.5^2) = 0.5`,
the maximum for binary classification. A 60/40 split scores
`1 - (0.36 + 0.16) = 0.48`, slightly below the maximum because one class is a little
more common.

The practical difference between entropy and Gini: Gini skips the logarithm and is
cheaper to compute. On real datasets they almost always agree on which split to make. The
Azure Machine Learning Two-Class Decision Forest component exposes both options via its
split-criterion parameter; its documentation notes that decision trees in general perform
"integrated feature selection and classification" precisely because they evaluate every
possible split against whichever impurity measure you choose
([Two-Class Decision Forest component](https://learn.microsoft.com/azure/machine-learning/component-reference/two-class-decision-forest?view=azureml-api-2)).

## Information Gain

Information gain is the impurity at the parent minus the size-weighted average impurity
at the two children:

```
IG = impurity(parent) - (n_left / n) * impurity(left) - (n_right / n) * impurity(right)
```

The weighting by child size matters: a perfect split on the left that leaves a chaotic
right child is not a good split. The gain must reflect the cost of both children.

A perfect split: parent has three cats and three dogs, left child gets all cats, right
child gets all dogs. Both children are pure, so both child impurities are zero; the full
parent impurity becomes the gain. For Gini that is `1 - (0.5^2 + 0.5^2) = 0.5`; for
entropy it is `1.0` bit.

A useless split: left and right children have the same class proportions as the parent.
Weighted child impurity equals parent impurity exactly. Gain is zero. The split bought
nothing.

## The Code

The locked `entropy`, `gini`, and `information_gain` functions below are the exact code
the acceptance gate imports. Read the docstrings, then read the body: every formula above
maps to a line.

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

The `entropy` function handles the pure-node edge case explicitly: when `len(probs) <= 1`
it returns `0.0` rather than evaluating `0 * log2(0)`, the indeterminate form that
information theory conventionally defines as 0 but that floating-point arithmetic
cannot resolve cleanly. The `gini` function has no such edge case because `1 - 1.0 = 0.0`
falls out of the arithmetic naturally.

## Measured Values

These are not estimates. Run the acceptance gate and you get these numbers exactly.

| Node | Entropy | Gini |
|---|---|---|
| Pure: `[1, 1, 1, 1]` | `0.0` | `0.0` |
| Balanced two-class: `[0, 0, 1, 1]` | `1.0` bit | `0.5` |
| Balanced four-class: `[0, 1, 2, 3]` | `2.0` bits | `0.75` |
| 60/40 split: `[0]*6 + [1]*4` | `0.971` bits | `0.48` |

Information gain on a perfect split (three of each class, all ones left, all zeros right):
Gini gain `= 0.5`; entropy gain `= 1.0` bit. Information gain on a useless split (same
50/50 proportions on both sides): Gini gain `= 0.0`; entropy gain `= 0.0`.

Entropy rewards purity in bits; Gini rewards purity in probability. They measure different
things, but they almost always agree on which split is best.

## Core Concepts

- Shannon entropy `H(y) = -sum(p_i * log2(p_i))` measures uncertainty in bits; a pure
  node scores `0`, a balanced two-class node scores `1.0`.
- Gini impurity `1 - sum(p_k^2)` measures the probability of mislabeling a random draw;
  pure is `0`, balanced two-class is `0.5`.
- Information gain is the parent impurity minus the size-weighted average child impurity;
  a perfect split returns the full parent impurity as gain, a useless split returns `0`.
- Gini skips the logarithm and is computationally cheaper; on real data both measures
  almost always select the same split.

<div class="claude-handoff" data-exercise="exercises/module3/entropy-and-information-gain/">

**Build It in Claude Code**: Read the current state of `exercises/ml/` before touching
anything. You are adding `exercises/ml/tree.py` to the package; earlier modules have
already contributed `ml/distances.py`, `ml/gradient_descent.py`, `ml/linreg.py`, and
others. Do not touch those files. Implement the three impurity functions (`entropy`,
`gini`, `information_gain`) in `exercises/ml/tree.py` exactly as shown above. Then
verify with the locked acceptance gate at
`exercises/module3/entropy-and-information-gain/test_impurity.py`. Done when
`python -m pytest exercises/module3/entropy-and-information-gain` is green.

</div>
