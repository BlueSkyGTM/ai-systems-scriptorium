# Regression Error and Slicing

A model that looks fine on the overall test set can be broken on a specific group of
users, a product category, or a time window. The aggregate metric hides it. Your job is
to find it before it ships.

## Two Ways to Measure a Miss

When your model predicts a continuous value, the error on sample `i` is `y_true - y_pred`.
Every regression metric starts from that residual; the difference is how it treats large misses.

**MAE** (Mean Absolute Error) treats every unit of error the same:

```
MAE = mean(|y_true - y_pred|)
```

An error of 2.0 contributes exactly 2.0 to the average. Ten small errors of 0.2 and one
large error of 2.0 are weighted equally by magnitude. That linearity makes MAE robust: a
single outlier prediction barely moves the needle.

**RMSE** (Root Mean Squared Error) squares the residuals before averaging, then takes the
square root to return to the same units:

```
RMSE = sqrt( mean((y_true - y_pred)^2) )
```

The squaring step punishes large misses geometrically. A single error of 2.0 contributes
4.0 to the sum inside the square root; two errors of 1.0 contribute only 2.0. RMSE
amplifies the big miss far beyond what MAE would show for the same residual set.

**R^2** (Coefficient of Determination) shifts the question from absolute error to explained
variance:

```
R^2 = 1 - SS_res / SS_tot
```

where `SS_res` is the sum of squared residuals and `SS_tot` is the total variance of the
targets. R^2 = 1.0 means the model explains all variance; R^2 = 0.0 means predicting the
training mean would do just as well; R^2 < 0.0 means the model is worse than that baseline.

Azure Machine Learning's Evaluate Model component reports all three. The official component
reference notes that RMSE "creates a single value that summarizes the error in the model"
and that "by squaring the difference, the metric disregards the difference between
over-prediction and under-prediction," while MAE "measures how close the predictions are to
the actual outcomes." The AutoML evaluation page adds that R^2 "measures the proportional
reduction in mean squared error (MSE) relative to the total variance of the observed data."
See the
[Evaluate Model component reference](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/evaluate-model?view=azureml-api-2)
and
[Evaluate AutoML experiment results](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-understand-automated-ml?view=azureml-api-2)
for the full metric tables and normalization rules.

## The Code

These four functions go in `exercises/ml/metrics.py`. They are the M5 additions to that
package: pure NumPy, no sklearn dependency at runtime.

```python
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
```

## Outlier Penalty: The Numbers

The difference between MAE and RMSE is not theoretical. Here is the measured gap on a
controlled experiment (20 samples, small Gaussian noise, seed 7), using the functions
above.

**Clean baseline** (no injected error):

| Metric | Value |
|--------|-------|
| MAE    | 0.217 |
| RMSE   | 0.292 |

**After injecting one large error (+50.0 on the last sample)**:

| Metric | Value | Ratio vs. clean |
|--------|-------|-----------------|
| MAE    | 2.717 | 12.5x           |
| RMSE   | 11.194 | 38.3x          |

MAE rose 12.5 times. RMSE rose 38.3 times. The single large miss moved both metrics, but
RMSE reacted more than three times as hard as MAE. That is the squaring step working as
designed: it scales the penalty with the square of the error, so a miss of magnitude 50
receives 2,500 times the weight a miss of magnitude 1 would carry.

The practical consequence: if your production dataset has occasional gross errors (a sensor
spike, a mis-labeled batch, an imputed value 10 standard deviations out), MAE will report
those without alarming you, while RMSE will flag them loudly. Which you want depends on
whether those large misses matter. In a safety-critical system they probably do; in a demand
forecast with occasional data glitches, they might not.

## Slicing: Where the Aggregate Lies

A single aggregate metric is a claim that a model works on the full population. It often
does not tell you anything about subpopulations.

Here is the measured breakdown on a four-group synthetic dataset (120 total samples: three
"good" groups with small residuals, one "BAD" group with noise scaled 25 times larger):

| Group | MAE    |
|-------|--------|
| G1    | ~0.15  |
| G2    | ~0.15  |
| G3    | ~0.15  |
| BAD   | 3.83   |
| **Aggregate** | **1.08** |

The aggregate MAE of 1.08 looks mediocre; not alarming. The slice tells a different story:
three groups sit near 0.15, and one group has an MAE of 3.83, which is 3.55 times worse
than the aggregate and roughly 25 times worse than the well-behaved groups. The aggregate
hid the failure entirely. If "BAD" maps to a real user cohort, a product line, or a
geographic region, the model is not just mediocre there: it is broken.

The `slice_metric` function makes this transparent. It takes any metric function and any
group label array and returns per-group scores. The worst subgroup is one `max()` call away.

This is exactly what Azure Machine Learning's error analysis component automates at
production scale. The Responsible AI dashboard documentation describes the goal directly:
"Model accuracy might not be uniform across subgroups of data, and there might be input
cohorts for which the model fails more often." It exposes error rates by cohort through a
decision tree and heatmap so practitioners can "break down the aggregate performance metrics
to automatically discover erroneous cohorts." See
[Assess errors in machine learning models](https://learn.microsoft.com/en-us/azure/machine-learning/concept-error-analysis?view=azureml-api-2)
for the full component description. The `slice_metric` function you are building is the
from-scratch equivalent of that cohort-filtering step.

## Why This Matters for a Production AI Engineer

The M7 portfolio capstone evaluates a real model with slice metrics: you will compute
per-group performance, identify the worst-performing cohort, and report the gap between the
worst slice and the aggregate. That is a standard deliverable in a model evaluation memo.
Getting comfortable with `slice_metric` here means you arrive at the capstone with one more
production tool already built.

Shipping aggregate metrics alone is an audit risk. The aggregate looked fine; one slice was
broken. The engineer who finds that in testing, not in production, is the one who keeps the
job.

## Core Concepts

- MAE penalizes errors linearly, so each unit of miss contributes equally regardless of
  size; injecting one large outlier raised MAE 12.5x on the test set.
- RMSE penalizes errors quadratically before taking the root, making it far more sensitive
  to large misses; the same outlier raised RMSE 38.3x, more than three times the MAE ratio.
- R^2 measures the fraction of target variance the model explains; a score of 0.0 means the
  model is no better than predicting the training mean, and a negative score means it is
  worse.
- Aggregate metrics hide subgroup failures: an aggregate MAE of 1.08 masked a "BAD" cohort
  with MAE 3.83, a 3.55x gap that only `slice_metric` surfaced.

<div class="claude-handoff" data-exercise="exercises/module5/regression-error-and-slicing/">

**Build It in Claude Code**: Read `exercises/CLAUDE.md` first, then the current state of
`exercises/ml/metrics.py`. Module 4 did not add to that file, but earlier modules may have;
confirm what is already there before writing anything. Your task for this module is to add
`mae`, `rmse`, `r2`, and `slice_metric` to `exercises/ml/metrics.py` exactly as shown
above. Do not copy any function that already exists. Then place the locked acceptance gate
verbatim at `exercises/module5/regression-error-and-slicing/test_regression_and_slicing.py`
(the full test file is in the exercise README). Done when
`python -m pytest exercises/module5/regression-error-and-slicing` is green.

</div>
