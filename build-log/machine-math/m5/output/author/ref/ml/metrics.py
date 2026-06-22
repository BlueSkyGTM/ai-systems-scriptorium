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


# ---------------------------------------------------------------------------
# Regression metrics
# ---------------------------------------------------------------------------

def mae(y_true, y_pred):
    """Mean Absolute Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    """Root Mean Squared Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def r2(y_true, y_pred):
    """Coefficient of determination R^2 = 1 - SS_res / SS_tot."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return float(1.0 - ss_res / ss_tot)


# ---------------------------------------------------------------------------
# Slice metric
# ---------------------------------------------------------------------------

def slice_metric(y_true, y_pred, groups, metric_fn):
    """Evaluate metric_fn per unique group.

    Parameters
    ----------
    y_true : array-like
    y_pred : array-like
    groups : array-like, same length as y_true
        Group label for each sample (any hashable dtype).
    metric_fn : callable(y_true_slice, y_pred_slice) -> float

    Returns
    -------
    dict mapping each unique group label to its metric score.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    groups = np.asarray(groups)
    result = {}
    for label in np.unique(groups):
        mask = groups == label
        result[label] = metric_fn(y_true[mask], y_pred[mask])
    return result
