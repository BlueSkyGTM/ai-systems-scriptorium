# Module 6 — Feature Reality — Build Plan

Status: **PLAN SELF-LOCKED 2026-06-21** (M2–M7 straight-through). Inherits all locked decisions:
from-scratch NumPy, scikit-learn only as dataset source + oracle; growing `exercises/ml/` package gated by
`pytest`; Haiku fetch -> Sonnet builds + tests code -> Sonnet authors prose -> Opus conducts + gates.

## The stage in one line

Every earlier module assumed the features were already clean and numeric. They never are. M6 is the
unglamorous work that decides whether any of the math works: scaling and encoding raw columns into a matrix,
the naive Bayes model that lives or dies on feature quality, the imbalanced-data problem that makes accuracy
lie (callback to M5), and feature selection that fights the curse of dimensionality (callback to M1).
`ml/features.py` is the feature-engineering library the M7 capstone uses to build its pipeline.

## Ore (distill into ingredients/source/machine-math/)

- Haiku A: aefs Phase 02 `08-feature-engineering` + `17-imbalanced-data` + `18-feature-selection`
  -> `ingredients/source/machine-math/aefs-feature-engineering.md`
- Haiku B: aefs Phase 02 `14-naive-bayes` -> `ingredients/source/machine-math/aefs-naive-bayes.md`

## Locked split (overview + 4 lessons, one idea each)

| # | Lesson (slug) | One idea | Builds |
|---|---------------|----------|--------|
| 0 | `00-overview` | The math only works on features you engineered: scale, encode, balance, select. | — |
| 1 | `scaling-and-encoding` | Models read numbers; turn raw categories into numbers with one-hot / ordinal encoding and put every column on a common scale. | `ml/features.py` `one_hot_encode`, `ordinal_encode` (reuse M1 `zscore`/`minmax_scale`) |
| 2 | `naive-bayes` | Naive Bayes multiplies per-feature likelihoods under a strong independence assumption; it is fast and breaks loudly when features are bad. | `ml/naive_bayes.py` `GaussianNB` (fit class priors + per-feature mean/var, predict via log-posterior) |
| 3 | `imbalanced-data` | On a 95/5 split a model can score 0.95 accuracy and catch zero positives; resampling and class weights fix the training signal. | `ml/features.py` `random_oversample` / `random_undersample` + class-weight helper |
| 4 | `feature-selection` | More features is not better; drop near-constant and redundant columns, keep the ones that carry signal (tree importances). | `ml/features.py` `select_by_variance` / `select_by_importance` (uses M4 forest) |

## Artifact contract (Opus locks; Sonnet builds + tests)

- `ml/features.py`, pure NumPy: `one_hot_encode(col)`, `ordinal_encode(col, order=None)`,
  `random_oversample(X, y, random_state)`, `random_undersample(X, y, random_state)`,
  `class_weights(y)`, `select_by_variance(X, threshold)`, `select_by_importance(X, y, k, random_state)`
  (the last uses M4 `RandomForestClassifier` feature frequencies / a simple importance proxy). Reuse M1
  `zscore`/`minmax_scale` (do not reimplement).
- `ml/naive_bayes.py`, pure NumPy: `class GaussianNB` with `fit` (class priors + per-class per-feature
  mean/var) and `predict` / `predict_proba` (Gaussian log-likelihood summed across features + log prior).

## Acceptance gate (Sonnet writes, Opus runs)

- encoding: one_hot_encode matches `sklearn.preprocessing.OneHotEncoder` shape/contents; ordinal_encode maps
  a known order correctly.
- naive bayes: GaussianNB on Iris (or a Gaussian-ish set) clears an accuracy floor and agrees with
  `sklearn.naive_bayes.GaussianNB` within tolerance.
- imbalance (NEGATIVE CASE -> FIX): on a 90/10 imbalanced set, a model trained on the raw data has near-zero
  minority recall; after `random_oversample`, minority recall rises materially. Shown by measurement (uses
  M5 `recall`).
- feature selection: `select_by_variance` drops an injected constant column; `select_by_importance` keeps the
  informative features of a set with added noise columns and a model on the selected subset does at least as
  well as on the full set.

## Grounding + fleet

Three-source: distilled ingredients + Microsoft Learn (Azure ML feature engineering / featurization, the
SMOTE component for imbalance, Two-Class / Multiclass... and the Filter Based Feature Selection component;
verified live) + the seam framing (a Production AI Engineer spends most of the time here). Two Haiku
distillers; one Sonnet builds + tests `ml/features.py` + `ml/naive_bayes.py` in the m6 ref harness and
captures real numbers (encoder shapes, NB accuracy vs sklearn, the imbalance recall before/after, the
selection result); two Sonnet authors write the overview + 4 lessons + 4 exercise READMEs. Opus reviews,
runs `pytest` + `mdbook build`, ships.
