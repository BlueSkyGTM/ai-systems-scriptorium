# AUC-ROC: The Math of Ranking

Precision and recall answer "how is the model doing at threshold tau?" AUC answers a
different question: "how well does the model rank positives above negatives, regardless of
where tau sits?" That shift in question is the shift in thinking.

## The ROC Curve

The Receiver Operating Characteristic curve plots two rates against each other as the
threshold sweeps from high to low.

True Positive Rate (TPR), also called recall or sensitivity, is TP / (TP + FN): the
fraction of actual positives the model catches. False Positive Rate (FPR) is
FP / (FP + TN): the fraction of actual negatives the model falsely calls positive. Both
rates move as the threshold moves.

Start with tau above the highest score: the model predicts positive for nothing. TPR = 0,
FPR = 0. Lower the threshold. The first sample to cross it gets a positive prediction; if
it is actually positive, TPR ticks up; if it is actually negative, FPR ticks up. Lower tau
all the way to zero: the model predicts positive for every sample. TPR = 1, FPR = 1.

Plot (FPR, TPR) at every threshold and you get the ROC curve. It starts at (0, 0) and ends
at (1, 1). A perfect ranker reaches the top-left corner, (0, 1), before touching the FPR
axis: it catches all positives without any false alarms. A random scorer hugs the diagonal.
Azure Machine Learning AutoML generates the ROC curve for every classification experiment;
see the [AutoML evaluation guide](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-understand-automated-ml)
for the visual and the interpretation of models above and below the diagonal.

## AUC as a Probability

The area under the ROC curve has a clean probabilistic meaning: AUC is the probability
that a randomly chosen positive example receives a higher predicted score than a randomly
chosen negative example. A perfect ranker scores 1.0; a random scorer scores 0.5 on
average.

That interpretation comes directly from the Mann-Whitney U statistic. Count every
(positive, negative) pair where the positive outranks the negative; add half a point for
each tie. Divide by the total number of pairs. The result is identical to the trapezoidal
area under the ROC curve, without any discretization error.

## The Code

The locked `roc_curve` and `roc_auc` functions below belong in `exercises/ml/metrics.py`
alongside the classification metrics from the previous lesson.

```python
# ---------------------------------------------------------------------------
# ROC curve and AUC
# ---------------------------------------------------------------------------

def roc_curve(y_true, y_score):
    """Sweep score thresholds and return (fpr, tpr, thresholds).

    Thresholds are the unique score values in descending order, with an
    extra sentinel above the maximum (so the first operating point is (0,0)).
    Ties (multiple samples with the same score) are resolved by grouping
    them: all tied samples flip together when the threshold crosses their
    shared score value.  This ensures each unique score produces exactly
    one ROC point, matching sklearn's tie-handling convention.

    Arrays are aligned: fpr[i], tpr[i] is the rate state when predicting
    positive for every sample with score >= thresholds[i].
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))

    # Sort all samples by score descending (ties broken arbitrarily; they
    # will be grouped together below).
    desc_idx = np.argsort(y_score)[::-1]
    sorted_scores = y_score[desc_idx]
    sorted_labels = y_true[desc_idx]

    # Walk through sorted samples, accumulating TP and FP.
    # Each time we encounter a new (lower) score we emit an ROC point first,
    # then process all samples sharing the previous score level.
    fprs = [0.0]
    tprs = [0.0]
    # Collect threshold values corresponding to each emitted point.
    # The sentinel "above max" corresponds to the (0,0) starting point.
    thresh_vals = [sorted_scores[0] + 1.0]

    tp = 0
    fp = 0
    i = 0
    n = len(sorted_labels)
    while i < n:
        # Find the run of samples that share the current score value.
        current_score = sorted_scores[i]
        j = i
        while j < n and sorted_scores[j] == current_score:
            if sorted_labels[j] == 1:
                tp += 1
            else:
                fp += 1
            j += 1
        # Emit one ROC point for this score level.
        fprs.append(fp / n_neg if n_neg > 0 else 0.0)
        tprs.append(tp / n_pos if n_pos > 0 else 0.0)
        thresh_vals.append(current_score)
        i = j

    return np.array(fprs), np.array(tprs), np.array(thresh_vals)


def roc_auc(y_true, y_score):
    """Area under the ROC curve.

    Uses the rank-based Mann-Whitney U formula, which is equivalent to the
    trapezoidal area but handles ties exactly (no discretization gap).
    Agrees with sklearn.metrics.roc_auc_score to floating-point precision.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)

    n_pos = int(np.sum(y_true == 1))
    n_neg = int(np.sum(y_true == 0))
    if n_pos == 0 or n_neg == 0:
        raise ValueError("roc_auc requires at least one positive and one negative sample.")

    pos_scores = y_score[y_true == 1]
    neg_scores = y_score[y_true == 0]

    # U statistic: count (pos > neg) pairs + 0.5 * (pos == neg) pairs.
    # Broadcasting: shape (n_pos, n_neg)
    diff = pos_scores[:, None] - neg_scores[None, :]
    u = float(np.sum(diff > 0) + 0.5 * np.sum(diff == 0))
    return u / (n_pos * n_neg)
```

`roc_curve` sorts samples by score descending, then walks the sorted list and groups ties.
Each unique score level produces exactly one (FPR, TPR) point; the (0, 0) sentinel is
prepended with a threshold one unit above the maximum. `roc_auc` skips the curve entirely
and computes the U statistic by broadcasting: `pos_scores[:, None] - neg_scores[None, :]`
produces an (n_pos, n_neg) matrix of differences; count the positives, add half for ties,
divide by the total pair count.

## Measured: What the Numbers Show

On a seeded random sample (`n=200, seed=42`), the from-scratch `roc_auc` matches
scikit-learn's `roc_auc_score` to 1e-6 tolerance. For example, both return `0.49925`
(to five decimal places) on the same random labels and scores: the result is near 0.5
because random labels and random scores produce a random ranker, which is exactly what the
theory predicts.

A perfect ranker, where every positive receives a higher score than every negative:

```python
y_true  = np.array([0, 0, 0, 1, 1, 1])
y_score = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
```

scores AUC = **1.0**. A constant scorer (all scores identical) scores AUC = **0.5**:
with no ranking information, the result is chance.

## Why AUC, and When the PR Curve Is Better

AUC is threshold-independent. You do not need to decide on a tau before evaluating the
model. That makes it the right metric for model selection and for the primary metric in
Azure AutoML classification experiments, where the best model needs to be chosen before
the deployment threshold is tuned. The AutoML evaluation table lists `AUC_weighted` as the
primary optimized metric for binary classification.

One limitation matters on imbalanced data. FPR involves TN: when the negative class is
large, even a high absolute number of false positives produces a small FPR, making the
ROC curve look better than it is. The Precision-Recall curve replaces FPR with precision,
which involves only positives and false positives: it is blind to TN and therefore more
honest when negatives dominate. If your positive class is rare, use the PR curve. If
classes are roughly balanced or you need a ranking summary for model selection, AUC is the
right tool. Azure AutoML generates both; the [AutoML evaluation guide](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-understand-automated-ml)
presents the ROC and PR curves side by side for exactly this reason.

## Core Concepts

- The ROC curve plots TPR against FPR as the classification threshold sweeps from high to
  low; AUC is the area under that curve, ranging from 0.5 (random) to 1.0 (perfect).
- AUC equals the probability that the model assigns a higher score to a randomly chosen
  positive than to a randomly chosen negative: it is a ranking metric, not a threshold
  metric.
- The from-scratch `roc_auc` uses the Mann-Whitney U formula, which handles ties exactly
  and matches scikit-learn's `roc_auc_score` to floating-point tolerance.
- On imbalanced data the PR curve is more informative than ROC because it replaces FPR
  (which involves the dominant negative class) with precision (which focuses only on
  predicted positives).

<div class="claude-handoff" data-exercise="exercises/module5/auc-roc-the-math-of-ranking/">

**Build It in Claude Code**: Read the current state of `exercises/ml/metrics.py` before
touching anything. The previous lesson added `confusion_matrix`, `accuracy`, `precision`,
`recall`, and `f1`. You are now adding `roc_curve` and `roc_auc` to the same file. Add
the two functions exactly as shown above, after the `f1` function and before any regression
metrics. Then verify with the locked acceptance gate at
`exercises/module5/auc-roc-the-math-of-ranking/test_auc.py`. Done when
`python -m pytest exercises/module5/auc-roc-the-math-of-ranking` is green.

</div>
