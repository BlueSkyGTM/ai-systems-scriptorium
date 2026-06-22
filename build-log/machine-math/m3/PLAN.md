# Module 3 — Splitting and Branching — Build Plan

Status: **PLAN SELF-LOCKED 2026-06-21** (M2–M7 straight-through, self-locked plans, self-cleared
`GATE-APPROVE-SHIP`). Inherits all M1/M2 locked decisions: from-scratch NumPy, scikit-learn only as
dataset source + oracle; the growing `exercises/ml/` package gated by `pytest`; Haiku fetch -> Sonnet
builds + tests the code -> Sonnet authors write prose -> Opus conducts, reviews, runs the gate. Opus
does not hand-code.

## The stage in one line

M3 leaves geometry and distance behind for a different question: not "which points are near?" but "which
single yes/no split best separates the labels?" Information theory answers it (entropy and Gini measure
disorder; information gain measures how much a split reduces it), and a decision tree applies the answer
recursively. Cross-validation and overfitting enter here: a tree grown to full depth memorizes the
training set, and the depth that generalizes is chosen on held-out folds, not training error.

## Ore (distill into ingredients/source/machine-math/)

One Haiku fetcher distills (each has docs/en.md + code/):
- Phase 01: `09-information-theory`
- Phase 02: `04-decision-trees`
-> `ingredients/source/machine-math/aefs-information-theory-and-trees.md`
(Cross-validation is named but not deeply sourced here; it is taught as the method for choosing tree depth,
grounded on the bias-variance idea M2 established. Deep evaluation/metrics stay in M5's ore.)

## Locked split (overview + 3 lessons, one idea each)

| # | Lesson (slug) | One idea | Builds |
|---|---------------|----------|--------|
| 0 | `00-overview` | From distance to splits: measure disorder, pick the split that reduces it most, recurse; then stop before you memorize. | — |
| 1 | `entropy-and-information-gain` | Entropy and Gini impurity measure how mixed a node's labels are; information gain is the drop in impurity a split buys. | `ml/tree.py` impurity functions (`entropy`, `gini`, `information_gain`) |
| 2 | `decision-trees` | A decision tree greedily picks the highest-information-gain split and recurses until a stopping rule; prediction walks the tree to a leaf. | `ml/tree.py` `DecisionTreeClassifier(max_depth)` (fit = recursive best-split, predict = traverse) |
| 3 | `overfitting-and-cross-validation` | A deep tree memorizes; `max_depth` is the bias-variance knob; cross-validation picks it on held-out folds, not training accuracy. | concept; demonstrated with the M3 tree at rising `max_depth` (train vs CV accuracy) |

## Artifact contract (Opus locks; Sonnet builds + tests)

- `ml/tree.py`, pure NumPy: `entropy(y)`, `gini(y)`, `information_gain(parent_y, left_y, right_y, criterion)`;
  `class DecisionTreeClassifier(max_depth=None, criterion="gini", min_samples_split=2)` with `fit(X, y)`
  (recursive: at each node find the (feature, threshold) maximizing information gain, split, recurse to
  max_depth or purity) and `predict(X)` (traverse to a leaf, return majority label). Readable node struct.

## Acceptance gate (Sonnet writes, Opus runs)

- entropy/Gini: `entropy([all one class]) == 0`; entropy of a 50/50 binary split == 1.0 bit; Gini of pure == 0;
  `information_gain` is positive for a split that separates classes and ~0 for a useless split.
- tree: on Iris (stratified 80/20, random_state=0) the from-scratch tree's test accuracy clears a floor
  (e.g. >= 0.90) and agrees with `sklearn.tree.DecisionTreeClassifier` within tolerance.
- overfitting (NEGATIVE CASE): as `max_depth` rises, training accuracy climbs toward 1.0 while held-out (or
  cross-validated) accuracy peaks then degrades or stalls; a shallow tree generalizes at least as well as
  the fully grown one. Overfitting shown by measurement.

## Grounding + fleet

Three-source: distilled ingredient + Microsoft Learn (Azure ML Decision Forest / Two-Class Decision Tree
components; verified live, real URLs) + the seam framing (a Production AI Engineer reads a tree as the
interpretable baseline). One Haiku distills the ingredient; one Sonnet builds + tests `ml/tree.py` in the
m3 ref harness and captures real numbers (impurity values, tree accuracy + sklearn agreement, the
depth-vs-accuracy table); two Sonnet authors write the overview + 3 lessons + 3 exercise READMEs (embedding
the tested code). Opus reviews against STYLE/STANDARDS, runs `pytest` + `mdbook build`, ships.
