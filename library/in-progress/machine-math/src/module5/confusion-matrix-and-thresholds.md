# The Confusion Matrix and Thresholds

Every classifier ends in the same place: a number between 0 and 1. That number is a
probability, and it means nothing by itself. A threshold turns it into a decision.

## The Threshold and the Matrix

The decision rule is simple. Pick a threshold tau. If the model's predicted probability
exceeds tau, predict 1 (positive). If not, predict 0 (negative). The standard choice is
tau = 0.5, but nothing forces that. Move the threshold and the decisions change.

Four outcomes are possible for each example. The example is actually positive (label 1) or
actually negative (label 0). The model predicts positive or negative. That produces a
2x2 matrix:

```
          Predicted 0    Predicted 1
Actual 0     TN             FP
Actual 1     FN             TP
```

True Positives (TP): model predicted 1, truth is 1. True Negatives (TN): model predicted
0, truth is 0. False Positives (FP): model predicted 1, truth is 0 (a false alarm). False
Negatives (FN): model predicted 0, truth is 1 (a missed positive).

The Azure Machine Learning Evaluate Model component visualizes this matrix for every
classification model. In the studio, a darker cell means more samples; a normalized view
shows the fraction of each actual class predicted as each label. See the [Evaluate Model
component reference](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/evaluate-model)
for the designer-level details and the screenshot of a good vs. bad confusion matrix from
the [AutoML evaluation guide](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-understand-automated-ml).

## The Code

The locked functions below are the exact code the acceptance gate imports. Add them to
`exercises/ml/metrics.py`.

```python
"""ml/metrics.py -- from-scratch evaluation metrics (pure NumPy).

Classification
--------------
confusion_matrix(y_true, y_pred)
    Binary {0,1} labels. Returns a 2x2 NumPy array:

        [[TN, FP],
         [FN, TP]]

    Row = actual class (0 top, 1 bottom).
    Col = predicted class (0 left, 1 right).

accuracy(y_true, y_pred)
precision(y_true, y_pred)   -- 0.0 when TP+FP == 0
recall(y_true, y_pred)      -- 0.0 when TP+FN == 0
f1(y_true, y_pred)          -- 0.0 when precision+recall == 0

ROC / AUC
---------
roc_curve(y_true, y_score)  -> (fpr, tpr, thresholds)
    Sweeps every unique score as a threshold (descending).  First point is
    (0, 0) at threshold above max score; last point is (1, 1) at threshold
    below min score.

roc_auc(y_true, y_score)    -> float in [0, 1]
    Trapezoidal area under the ROC curve (agrees with sklearn to float tol).

Regression
----------
mae(y_true, y_pred)
rmse(y_true, y_pred)
r2(y_true, y_pred)

Slicing
-------
slice_metric(y_true, y_pred, groups, metric_fn) -> dict {group_label: score}
    Evaluates metric_fn(y_true_slice, y_pred_slice) for each unique group.
"""
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_binary(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    return y_true, y_pred


# ---------------------------------------------------------------------------
# Confusion matrix
# ---------------------------------------------------------------------------

def confusion_matrix(y_true, y_pred):
    """Return 2x2 confusion matrix for binary labels {0, 1}.

    Layout:
        [[TN, FP],
         [FN, TP]]
    """
    y_true, y_pred = _check_binary(y_true, y_pred)
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    return np.array([[tn, fp], [fn, tp]], dtype=int)


# ---------------------------------------------------------------------------
# Point metrics derived from the confusion matrix
# ---------------------------------------------------------------------------

def accuracy(y_true, y_pred):
    """Fraction of correct predictions."""
    y_true, y_pred = _check_binary(y_true, y_pred)
    return float(np.mean(y_true == y_pred))


def precision(y_true, y_pred):
    """TP / (TP + FP).  Returns 0.0 when denominator is 0."""
    cm = confusion_matrix(y_true, y_pred)
    tp = cm[1, 1]
    fp = cm[0, 1]
    denom = tp + fp
    return float(tp / denom) if denom > 0 else 0.0


def recall(y_true, y_pred):
    """TP / (TP + FN).  Returns 0.0 when denominator is 0."""
    cm = confusion_matrix(y_true, y_pred)
    tp = cm[1, 1]
    fn = cm[1, 0]
    denom = tp + fn
    return float(tp / denom) if denom > 0 else 0.0


def f1(y_true, y_pred):
    """Harmonic mean of precision and recall.  Returns 0.0 when both are 0."""
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    denom = p + r
    return float(2 * p * r / denom) if denom > 0 else 0.0
```

Read the `confusion_matrix` function carefully. The layout is `[[TN, FP], [FN, TP]]`:
row 0 is actual-negative, row 1 is actual-positive; column 0 is predicted-negative, column
1 is predicted-positive. `precision` reads `cm[1, 1]` (TP) and `cm[0, 1]` (FP). `recall`
reads `cm[1, 1]` (TP) and `cm[1, 0]` (FN). Both return 0.0 rather than dividing by zero
when no positive predictions exist.

## Measured: A Worked Example

Take ten examples: four actually positive, six actually negative. The confusion matrix is
`[[TN=2, FP=2], [FN=2, TP=4]]`.

From that matrix:

- accuracy = (TP + TN) / total = (4 + 2) / 10 = **0.60**
- precision = TP / (TP + FP) = 4 / (4 + 2) = **0.667**
- recall = TP / (TP + FN) = 4 / (4 + 2) = **0.667**
- F1 = 2 * 0.667 * 0.667 / (0.667 + 0.667) = **0.667**

Now consider the imbalance case. A dataset has 95 negatives and 5 positives. A model that
always predicts the majority class (always predicts 0) produces:

- accuracy = 95 / 100 = **0.95** (looks fine)
- recall on the positive class = 0 / 5 = **0.0** (finds no positives at all)

Accuracy scores 0.95. The model has learned nothing useful. This is the failure mode
accuracy conceals on imbalanced data, and it is exactly the case the Azure AutoML
evaluation guide [flags](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-understand-automated-ml)
when it notes that the confusion matrix Raw view reveals minority-class misclassification
that the normalized view can hide.

## The Precision-Recall Tradeoff

As the threshold moves, precision and recall trade off against each other. Lowering tau
catches more positives: recall rises because fewer positives are missed. But the model also
fires on more negatives: precision falls because more false alarms enter the positive
predictions. Raising tau has the opposite effect: fewer false alarms, higher precision, but
more missed positives, lower recall.

Neither extreme is right. The right threshold depends on cost. A cancer screening tool
tolerates false alarms (low precision) to avoid missing a tumor (high recall). A spam
filter tolerates missing some spam (lower recall) to avoid blocking real email (high
precision). F1 is the harmonic mean of the two and balances them when neither cost
dominates, but the first decision is always: which error is more expensive?

## Core Concepts

- A threshold on the model's probability output produces a 2x2 confusion matrix; the four
  cells are TP, TN, FP, FN, and every classification metric derives from them.
- Precision is TP / (TP + FP): how many of the model's positive predictions are correct.
  Recall is TP / (TP + FN): how many of the actual positives the model catches.
- F1 is the harmonic mean of precision and recall; it penalizes extreme imbalance between
  the two more than a simple average would.
- On a 95/5 imbalanced dataset, a model that always predicts the majority class scores 0.95
  accuracy and 0.0 minority recall: accuracy lies, and recall exposes it.

<div class="claude-handoff" data-exercise="exercises/module5/confusion-matrix-and-thresholds/">

**Build It in Claude Code**: Read the current state of `exercises/ml/` before touching
anything. You are creating `exercises/ml/metrics.py` and adding `confusion_matrix`,
`accuracy`, `precision`, `recall`, and `f1` to it. The complete file for this lesson
starts with the module docstring shown above and ends after the `f1` function; the
ROC/AUC and regression sections are placeholders that arrive in later lessons. Implement
the functions exactly as shown. Then verify with the locked acceptance gate at
`exercises/module5/confusion-matrix-and-thresholds/test_classification_metrics.py`.
Done when `python -m pytest exercises/module5/confusion-matrix-and-thresholds` is green.

</div>
