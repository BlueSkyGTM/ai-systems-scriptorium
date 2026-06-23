# Exercise: Honest Evaluation and Slicing

**Goal:** Add the eval and slice stage (steps 5 and 6) to `exercises/module7/pipeline.py`
so the pipeline reports AUC, F1, precision, and recall on the held-out test set, then
computes per-region recall via `slice_metric` and names the worst subgroup.

**Why:** Reporting an aggregate metric and calling it an evaluation is a liability in
production. A model that scores 0.8865 AUC overall can be missing four in ten positives in
one region. Finding that in testing, not in production, is the work. This exercise wires up
the instruments: the four overall metrics you built in earlier modules, plus `slice_metric`
over the regional subgroups. The model-card exercise in the next step reads these outputs;
build them correctly here or the card will be wrong.

## The Shared Artifact

`exercises/module7/pipeline.py` is the throughline artifact for Module 7. Prior modules
added the data-load stage (M7 exercise 1) and the feature-engineering and train stages
(M7 exercise 2). Before touching anything, read `exercises/module7/pipeline.py` to
understand what is already there. Confirm that `X_test`, `y_test`, `region_test`, and
`clf` are all defined before the point where you add your code.

The metric functions you call are already in `exercises/ml/metrics.py`. Do not reimplement
or inline them. The import at the top of `pipeline.py` already reads:

```python
from ml import metrics as ml_metrics
```

## Steps

### 1. Add Step 5: Overall Evaluation

After the train stage, append the following block verbatim. The classifier is already
fitted; you need the hard predictions and the probability scores:

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
```

`roc_auc` takes probability scores (`y_proba`), not hard predictions. The other three take
`y_pred`. The `overall_metrics` dict is the value stored on `PipelineResult.metrics`.

### 2. Add Step 6: Slice by Region

Immediately after step 5, append the following block verbatim:

```python
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

`region_test` is the region-label array for the held-out rows, extracted during the
train/test split stage. `skip_slicing` is a keyword argument on `pipeline.run()` used for
the rubric negative-case test. If `skip_slicing=False` (the default), `slices` contains
one recall value per region and `worst_subgroup` names the region with the lowest recall.

### 3. Update the Return Value

Confirm that `PipelineResult` is instantiated with `metrics=overall_metrics`,
`slices=slices`, and `worst_subgroup=worst_subgroup`. These fields are what the rubric and
the model-card writer read. If a prior stub set them to empty values, replace those stubs
with the computed values.

### 4. Verify the Output

Run the pipeline from the command line:

```
python exercises/module7/pipeline.py exercises/module7/data.csv
```

You should see output similar to:

```
Pipeline v1.0.0
Composed modules: ['ml.features', 'ml.metrics']

Overall metrics (test set):
  auc         : 0.8865
  f1          : 0.7455
  precision   : 0.8367
  recall      : 0.6721

Subgroup recall (region):
  east    : 0.6000 <-- WORST
  north   : 0.6667
  south   : 0.8125
  west    : 0.6000
```

The exact numbers depend on the seeded data; if your `data.csv` was generated with
`numpy.random.default_rng(seed=42)` and your split uses `random_state=42`, you will see
these numbers.

## Done When

- `exercises/module7/pipeline.py` computes and stores `overall_metrics`, `slices`, and
  `worst_subgroup` in the returned `PipelineResult`.
- The pipeline prints AUC, F1, precision, recall, and the per-region recall table with the
  worst subgroup identified.
- All acceptance tests in `exercises/module7/honest-evaluation-and-slicing/` pass:

```
python -m pytest exercises/module7/honest-evaluation-and-slicing
```

## Stretch

- Swap `ml_metrics.recall` for `ml_metrics.f1` in the `slice_metric` call. Compare the
  worst subgroup identified by recall versus F1. Do they agree? If not, what does the
  discrepancy tell you about the subgroup's precision?
- Add a second slice over a different column (for example, `plan_type`). Is the worst
  plan-type the same customer segment as the worst region?
