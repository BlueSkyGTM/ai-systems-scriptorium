# Honest Evaluation and Slicing

An overall AUC of 0.8865 sounds solid. One subgroup's recall of 0.600 tells you the model
is missing four out of ten positive cases there. The aggregate metric kept that fact hidden
until you sliced.

## Why the Aggregate Lies

A single number computed over the full test set is a weighted average of per-sample errors.
When subgroups are unequal in size or difficulty, the majority swamps the minority. The
model can be excellent on three regions and broken on a fourth; the average absorbs the
failure and reports something that looks acceptable. M5 showed this with regression: an
aggregate MAE of 1.08 masked a "BAD" cohort at MAE 3.83, more than three times the
aggregate. The same effect applies here, with recall as the metric and region as the slice.

The fix is `slice_metric`. It takes any metric function and any group-label array and
returns per-group scores. You already built it in `ml/metrics.py` during M5. The M7
pipeline calls it off that same file. Reuse, not rebuild.

## The Eval and Slice Stage

Steps 5 and 6 of `pipeline.py` implement the full evaluation. Read them verbatim; you will
embed this code in the exercise:

```python
    # ------------------------------------------------------------------
    # 5. Evaluate (ml.metrics)
    # ------------------------------------------------------------------
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    auc_val = ml_metrics.roc_auc(y_test, y_proba)
    f1_val = ml_metrics.f1(y_test, y_pred)
    prec_val = ml_metrics.precision(y_test, y_pred)
    rec_val = ml_metrics.recall(y_test, y_pred)

    overall_metrics = {
        "auc": auc_val,
        "f1": f1_val,
        "precision": prec_val,
        "recall": rec_val,
    }

    # ------------------------------------------------------------------
    # 6. Slice (ml.metrics.slice_metric)
    # ------------------------------------------------------------------
    if skip_slicing:
        slices = {}
        worst_subgroup = ""
    else:
        slices_raw = ml_metrics.slice_metric(
            y_test, y_pred, region_test, ml_metrics.recall
        )
        # Convert numpy str keys to plain str
        slices = {str(k): float(v) for k, v in slices_raw.items()}
        worst_subgroup = min(slices, key=slices.__getitem__)
```

Every metric call targets a function in `ml.metrics`. `roc_auc` takes the probability
scores and computes the area under the ROC curve; it uses the trapezoid rule over the
sorted threshold sweep you built in M3. `f1`, `precision`, and `recall` operate on the
hard predictions. `slice_metric` partitions `y_test` and `y_pred` by `region_test`
(the region column for the held-out rows) and applies `ml_metrics.recall` to each
partition. The worst subgroup is one `min()` call away.

The import line at the top of `pipeline.py` names where these functions live:

```python
from ml import metrics as ml_metrics
```

That `ml` is the package on disk in `exercises/ml/`. Nothing here is reimplemented inline.
The math lives in your from-scratch package; the pipeline composes it.

## The Measured Numbers

Running the full pipeline on the 200-row held-out test set (20% stratified split of the
1,000-row seeded dataset) produces these numbers:

**Overall metrics:**

| Metric | Value |
|--------|-------|
| AUC (ROC) | 0.8865 |
| F1 | 0.7455 |
| Precision | 0.8367 |
| Recall | 0.6721 |

**Per-region recall (slice_metric over `region`):**

| Subgroup | Recall |
|----------|--------|
| east | 0.6000 |
| north | 0.6667 |
| south | 0.8125 |
| west | 0.6000 |

Worst subgroup: `east` (tied with `west` at 0.600; `min()` over alphabetical sort resolves
to `east`).

The aggregate recall of 0.6721 sits between south (0.8125) and the eastern and western
subgroups (both 0.600). A reviewer reading only the aggregate would see a model that
correctly identifies about two-thirds of churners. The slice reveals that in the east and
west, the model misses four in ten. If east or west maps to a real service region with
distinct pricing or plan-mix, that gap is a business problem, not a rounding error.

## AUC as the Primary Ranking Metric

AUC measures the model's ability to rank a randomly drawn positive above a randomly drawn
negative. It is threshold-free, which makes it robust to class imbalance: it does not
penalize the model for the default 0.5 cutoff on an imbalanced dataset. Azure Machine
Learning's AutoML documentation notes that `AUC_weighted` is the recommended primary metric
for churn prediction and fraud detection precisely because threshold-dependent metrics like
accuracy degrade under class skew. See
[Evaluate AutoML Experiment Results](https://learn.microsoft.com/azure/machine-learning/how-to-understand-automated-ml?view=azureml-api-2#classification-metrics)
for the full classification metric table and the guidance on when to prefer AUC over
accuracy.

F1 complements AUC by operating at the actual decision boundary. With precision at 0.8367
and recall at 0.6721, the F1 of 0.7455 reflects a model that is conservative: when it
predicts churn, it is usually right, but it is missing about a third of actual churners
overall. The slice tells you where that missing third concentrates.

## Why a Production AI Engineer Always Slices

Azure Machine Learning's error analysis component automates this at production scale. Its
documentation states: "Model accuracy might not be uniform across subgroups of data, and
there might be input cohorts for which the model fails more often." It builds a decision
tree over input features to surface erroneous cohorts and exposes them through a heatmap.
See
[Assess Errors in Machine Learning Models](https://learn.microsoft.com/azure/machine-learning/concept-error-analysis?view=azureml-api-2)
for the full component description. The `slice_metric` call in `pipeline.py` is the
from-scratch equivalent of that cohort-filtering step.

Aggregate metrics satisfy a dashboard. Slice metrics answer a question: which population
segment is the model breaking on, and by how much? Shipping without that answer is not a
model evaluation; it is a guess presented as one.

## Core Concepts

- AUC is threshold-free and ranks positives above negatives; at 0.8865 on the 200-row
  held-out set it is the stable headline metric, but it tells you nothing about which
  subgroup the model is failing.
- Aggregate recall of 0.6721 hides a 21-point gap between the best region (south, 0.8125)
  and the worst (east and west, 0.6000); only `slice_metric` surfaces the gap.
- `slice_metric` partitions `y_test` and `y_pred` by any group-label array and applies any
  metric function; it is the same function you built in M5, imported from `ml.metrics`
  on disk.
- A model that looks fine on aggregate can be systematically broken on a subgroup; finding
  that in testing, not in production, is the job.

<div class="claude-handoff" data-exercise="exercises/module7/honest-evaluation-and-slicing/">

**Build It in Claude Code:** Read `exercises/CLAUDE.md` first, then the current state of
`exercises/module7/pipeline.py` (the prior modules added the load, feature-engineering, and
train stages). Your task is to add the eval and slice stage verbatim as shown above: steps
5 and 6. The functions you call (`roc_auc`, `f1`, `precision`, `recall`, `slice_metric`)
are already in `exercises/ml/metrics.py` from M3 and M5; do not reimport or reimplement
them. Done when the pipeline prints overall AUC/F1/precision/recall and a per-region recall
slice with the worst subgroup identified. Gate: the relevant acceptance tests in
`exercises/module7/honest-evaluation-and-slicing/` must pass.

</div>
