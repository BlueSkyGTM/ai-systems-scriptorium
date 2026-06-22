# Module 4 — Ensembles and the Gradient — Build Plan

Status: **PLAN SELF-LOCKED 2026-06-21** (M2–M7 straight-through). Inherits all locked decisions:
from-scratch NumPy, scikit-learn only as dataset source + oracle; growing `exercises/ml/` package gated by
`pytest`; Haiku fetch -> Sonnet builds + tests code -> Sonnet authors prose -> Opus conducts + gates.

## The stage in one line

One tree is a weak, high-variance learner. M4 is about combining many of them. Two opposite strategies:
bagging builds many independent trees on bootstrap samples and averages them down to low variance (random
forests); boosting builds trees in sequence, each one fitting the errors the last one left behind, and for
squared loss "the error left behind" is exactly the negative gradient, so gradient boosting is gradient
descent in function space. The M3 tree is the building block both reuse.

## Ore (distill into ingredients/source/machine-math/)

One Haiku fetcher distills `aefs` Phase 02 `11-ensemble-methods` (docs/en.md + code/) ->
`ingredients/source/machine-math/aefs-ensembles.md`. The chain-rule / gradient-on-residuals math is already
distilled in `aefs-calculus-and-optimization.md` (M2); authors reuse it for the boosting lesson.

## Locked split (overview + 3 lessons, one idea each)

| # | Lesson (slug) | One idea | Builds |
|---|---------------|----------|--------|
| 0 | `00-overview` | One tree overfits; many trees, combined two different ways (bag them or boost them), do not. | — |
| 1 | `bagging-and-random-forests` | Train many trees on bootstrap samples with random feature subsets; averaging independent high-variance learners cuts variance. | `ml/ensemble.py` `RandomForestClassifier` (bags M3 `DecisionTreeClassifier`) |
| 2 | `boosting-and-the-gradient` | Boosting fits trees in sequence to the residuals; for squared loss the residual is the negative gradient, so this is gradient descent in function space. | `ml/tree.py` `DecisionTreeRegressor` + `ml/ensemble.py` `GradientBoostingRegressor` |
| 3 | `hyperparameters-and-the-tradeoff` | n_estimators, learning_rate, and tree depth trade bias against variance; this is what XGBoost / LightGBM tune at scale. | concept; demonstrated by sweeping n_estimators / learning_rate on the built ensembles |

## Artifact contract (Opus locks; Sonnet builds + tests)

- `ml/tree.py` gains `class DecisionTreeRegressor(max_depth, min_samples_split)`: same greedy recursion as
  the classifier but splits on variance reduction (MSE) and a leaf predicts the mean. Keep the classifier
  unchanged.
- `ml/ensemble.py`, pure NumPy, reusing `ml/tree.py`:
  - `class RandomForestClassifier(n_estimators=100, max_depth=None, max_features="sqrt", random_state=None)`:
    bootstrap-sample the rows, random feature subset per tree, fit a `DecisionTreeClassifier` each, predict
    by majority vote across trees.
  - `class GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3)`: start from the
    mean; at each round fit a `DecisionTreeRegressor` to the current residuals and add `learning_rate * tree`
    to the running prediction. `predict` sums the base value + the scaled tree contributions.

## Acceptance gate (Sonnet writes, Opus runs)

- regression tree: on a seeded 1-D signal, `DecisionTreeRegressor` reduces MSE vs the constant-mean baseline
  and agrees with `sklearn.tree.DecisionTreeRegressor` within tolerance.
- random forest: on Iris / breast cancer (stratified split, seeded), the forest's test accuracy >= a single
  M3 tree's and clears a floor; agrees with `sklearn.ensemble.RandomForestClassifier` within tolerance.
- gradient boosting: on a seeded regression set, test R^2 clears a floor and the training loss DECREASES as
  n_estimators grows; agrees with `sklearn.ensemble.GradientBoostingRegressor` within tolerance.
- hyperparameter / tradeoff (NEGATIVE CASE): a too-large learning_rate or too-many deep estimators overfits
  (train error keeps dropping, test error rises) while a tuned setting generalizes. Shown by measurement.

## Grounding + fleet

Three-source: distilled ingredient + Microsoft Learn (Azure ML Boosted Decision Tree = LightGBM-backed, the
MART gradient-boosting algorithm; Decision Forest; verified live) + the seam framing (a Production AI
Engineer reaches for gradient boosting as the strong tabular baseline). One Haiku distills the ingredient;
one Sonnet builds + tests `DecisionTreeRegressor` + `ml/ensemble.py` in the m4 ref harness and captures real
numbers (forest vs single-tree accuracy, GB R^2 + loss-vs-n_estimators, the overfitting sweep); two Sonnet
authors write the overview + 3 lessons + 3 exercise READMEs. Opus reviews, runs `pytest` + `mdbook build`,
ships.
