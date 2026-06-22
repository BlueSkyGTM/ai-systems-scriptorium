# Module 5 — What "Good" Means — Build Plan

Status: **PLAN SELF-LOCKED 2026-06-21** (M2–M7 straight-through). Inherits all locked decisions:
from-scratch NumPy, scikit-learn only as dataset source + oracle; growing `exercises/ml/` package gated by
`pytest`; Haiku fetch -> Sonnet builds + tests code -> Sonnet authors prose -> Opus conducts + gates.

## The stage in one line

M1–M4 built models. M5 asks the harder question: is a model any good, and good at what? A single accuracy
number hides the answer. The probability a model emits, the threshold that turns it into a decision, and the
metrics that read the result (precision, recall, F1, AUC-ROC for ranking, MAE/RMSE for regression, and
slice metrics for failure modes) are the math of "good." `ml/metrics.py` is the from-scratch evaluation
library; it is the artifact the M7 capstone composes to grade a real model.

## Ore

Distilled: `ingredients/source/machine-math/aefs-evaluation-metrics.md` (aefs Phase 02 model-evaluation +
Phase 01 probability-and-distributions, already fetched).

## Locked split (overview + 3 lessons, one idea each)

| # | Lesson (slug) | One idea | Builds |
|---|---------------|----------|--------|
| 0 | `00-overview` | Accuracy is one number that hides the truth; the confusion matrix and the metrics built on it tell you what the model is actually good at. | — |
| 1 | `confusion-matrix-and-thresholds` | A threshold on a probability makes the confusion matrix; precision and recall read its tradeoff; F1 balances them; accuracy lies on imbalanced data. | `ml/metrics.py` confusion + `precision`/`recall`/`f1` |
| 2 | `auc-roc-the-math-of-ranking` | AUC measures ranking quality independent of any threshold: the probability a random positive outranks a random negative. | `ml/metrics.py` `roc_curve` + `roc_auc` |
| 3 | `regression-error-and-slicing` | MAE and RMSE measure regression error differently (RMSE punishes big misses); slice metrics find the subgroup where the model fails. | `ml/metrics.py` `mae`/`rmse`/`r2` + `slice_metric` |

## Artifact contract (Opus locks; Sonnet builds + tests)

`ml/metrics.py`, pure NumPy, NO sklearn inside (sklearn is the oracle only):
- `confusion_matrix(y_true, y_pred)` -> 2x2 (binary) counts; `precision(y_true, y_pred)`, `recall(...)`,
  `f1(...)`, `accuracy(...)`.
- `roc_curve(y_true, y_score)` -> (fpr, tpr, thresholds); `roc_auc(y_true, y_score)` (rank-based or trapezoidal).
- `mae(y_true, y_pred)`, `rmse(...)`, `r2(...)`.
- `slice_metric(y_true, y_pred, groups, metric_fn)` -> per-group metric dict (the failure-mode finder).

## Acceptance gate (Sonnet writes, Opus runs)

- classification: from-scratch precision/recall/f1/accuracy match `sklearn.metrics` to tolerance on a fixed
  binary set; the imbalance demonstration shows accuracy high while recall on the minority class is low
  (accuracy-lies negative case).
- AUC: from-scratch `roc_auc` matches `sklearn.metrics.roc_auc_score` to tolerance across a few score
  vectors; AUC of a random scorer ~0.5, perfect ranking == 1.0.
- regression: mae/rmse/r2 match `sklearn.metrics` to tolerance; a single large outlier moves RMSE more than
  MAE (the penalty-shape point, shown by measurement).
- slicing: `slice_metric` returns the correct per-group values and surfaces a subgroup whose metric is far
  below the aggregate (the failure-mode the aggregate hid).

## Grounding + fleet

Three-source: distilled ingredient + Microsoft Learn (Azure ML Evaluate Model / AUC as the primary AutoML
classification metric / ROC module; verified live) + the seam framing (a Production AI Engineer is paid to
know where a model fails, not to report one accuracy number). One Sonnet builds + tests `ml/metrics.py` in
the m5 ref harness and captures real numbers (the confusion matrix, precision/recall/F1, AUC vs sklearn, the
RMSE-vs-MAE outlier effect, a slice table); two Sonnet authors write the overview + 3 lessons + 3 exercise
READMEs. Opus reviews, runs `pytest` + `mdbook build`, ships.
