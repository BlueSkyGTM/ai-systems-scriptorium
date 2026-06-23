# Exercise: The Dataset and the Feature Pipeline

A churn dataset has no value until it has been read, encoded, and scaled. Raw string columns crash a model; unscaled numeric columns quietly distort one. This exercise builds the first two stages of the capstone pipeline: the generator that produces `data.csv` and the load-plus-feature stage of `pipeline.py` that turns that CSV into a model-ready feature matrix using your own `ml.features` functions.

**Goal:** Build `exercises/module7/generate_data.py` to produce `data.csv`, then add the load and feature-engineering stage to `exercises/module7/pipeline.py`. The gate is green when `python -m pytest exercises/module7/the-dataset-and-the-feature-pipeline` passes all composition checks.

**Why:** Feature engineering with your own code, not a library wrapper, is the line between knowing the math and knowing the craft. When `ml.features.zscore` or `ml.features.one_hot_encode` is wrong, the pipeline breaks at the call site with a clear error. That is the correct failure: the capstone composes prior artifacts off disk so that a broken Module 6 function cannot produce a silently wrong answer.

## Before You Touch Code

Read the lesson at `src/module7/the-dataset-and-the-feature-pipeline.md`. Then check whether `exercises/module7/generate_data.py` or `exercises/module7/pipeline.py` already exist; if they do, read them before adding anything.

You need two prior artifacts:

- `exercises/ml/features.py`: provides `one_hot_encode` and `zscore`
- `exercises/ml/metrics.py`: provides `roc_auc`, `f1`, `precision`, `recall`, `slice_metric`

Read both files before writing `pipeline.py`. You are calling their public contracts; understanding the signatures is the pre-condition. If either is absent, the Module 6 exercise built them; do that first.

## The Two Files You Build

### generate_data.py

Location: `exercises/module7/generate_data.py`

Copy this verbatim, then run it once to produce `data.csv`:

```python
"""generate_data.py -- produce data.csv for the M7 capstone.

Provenance: seeded synthetic benchmark designed to exercise the full methodology.
All randomness is fixed to numpy seed 42; the output is byte-reproducible.

Schema
------
tenure_months   int     [1, 60]
monthly_charge  float   [20.0, 120.0]
num_products    int     [1, 5]
plan_type       str     {basic, plus, premium}
region          str     {north, south, east, west}
churned         int     {0, 1}   ~30 pct positive, learnable signal

Run: python generate_data.py   (creates data.csv alongside this file)
"""
from __future__ import annotations

import os
import csv
import numpy as np

SEED = 42
N_ROWS = 1_000

PLAN_TYPES = ["basic", "plus", "premium"]
REGIONS = ["north", "south", "east", "west"]

HEADER = [
    "tenure_months",
    "monthly_charge",
    "num_products",
    "plan_type",
    "region",
    "churned",
]


def generate(n: int = N_ROWS, seed: int = SEED) -> list[dict]:
    rng = np.random.default_rng(seed)

    tenure = rng.integers(1, 61, size=n)                        # 1-60 months
    charge = rng.uniform(20.0, 120.0, size=n).round(2)         # $20-$120/mo
    num_products = rng.integers(1, 6, size=n)                   # 1-5 products
    plan_idx = rng.integers(0, 3, size=n)                       # 0=basic 1=plus 2=premium
    region_idx = rng.integers(0, 4, size=n)                     # 0-3

    # Learnable logistic signal:
    #   short tenure, high charge, basic plan, south region -> higher churn risk
    log_odds = (
        -0.5                                  # intercept (pulls baseline toward ~25-35%)
        - 0.08 * tenure                       # longer tenure => lower churn (stronger signal)
        + 0.035 * charge                      # higher charge => higher churn (stronger signal)
        - 0.5 * num_products                  # more products => lower churn (stronger stickiness)
        + np.where(plan_idx == 0, 1.2, 0.0)  # basic plan => higher churn (stronger)
        + np.where(region_idx == 3, 0.7, 0.0)  # south => higher churn
    )
    prob_churn = 1.0 / (1.0 + np.exp(-log_odds))
    churned = rng.binomial(1, prob_churn).astype(int)

    rows = []
    for i in range(n):
        rows.append({
            "tenure_months": int(tenure[i]),
            "monthly_charge": float(charge[i]),
            "num_products": int(num_products[i]),
            "plan_type": PLAN_TYPES[int(plan_idx[i])],
            "region": REGIONS[int(region_idx[i])],
            "churned": int(churned[i]),
        })
    return rows


def write_csv(rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "data.csv")
    rows = generate()
    write_csv(rows, out_path)
    churned = sum(r["churned"] for r in rows)
    print(f"Class balance: {churned}/{len(rows)} positive ({churned/len(rows):.1%})")
```

Running `python generate_data.py` from `exercises/module7/` writes `data.csv` alongside the script. The class balance line confirms about 30% positive churn.

### pipeline.py: Load and Feature Stage

Location: `exercises/module7/pipeline.py`

Build `pipeline.py` in stages across the four module exercises. This exercise adds the imports, the column schema constants, the `_load_csv` helper, and the load-plus-feature stage. Add the model stage in the next exercise.

The load and feature stage to implement:

```python
    # ------------------------------------------------------------------
    # 1. Load
    # ------------------------------------------------------------------
    rows = _load_csv(data_path)
    n = len(rows)

    # Extract raw columns
    tenure = np.array([float(r["tenure_months"]) for r in rows])
    charge = np.array([float(r["monthly_charge"]) for r in rows])
    n_products = np.array([float(r["num_products"]) for r in rows])
    plan_col = np.array([r["plan_type"] for r in rows])
    region_col = np.array([r["region"] for r in rows])
    y = np.array([int(r[TARGET_COL]) for r in rows])

    # ------------------------------------------------------------------
    # 2. Feature engineering (ml.features)
    # ------------------------------------------------------------------
    encoding_done = False
    scaling_done = False

    # Numeric block
    numeric_raw = np.column_stack([tenure, charge, n_products])  # (n, 3)

    if skip_scaling:
        numeric_block = numeric_raw
    else:
        # zscore each column independently using ml.features.zscore
        scaled_cols = []
        for col_i in range(numeric_raw.shape[1]):
            scaled_cols.append(ml_features.zscore(numeric_raw[:, col_i]))
        numeric_block = np.column_stack(scaled_cols)
        scaling_done = True

    # Categorical block
    if skip_encoding:
        # Deficient: drop categoricals entirely
        feature_matrix = numeric_block
    else:
        ohe_plan, plan_categories = ml_features.one_hot_encode(plan_col)
        # Subgroup col (region) also one-hot encoded for model input
        ohe_region, region_categories = ml_features.one_hot_encode(region_col)
        feature_matrix = np.hstack([numeric_block, ohe_plan, ohe_region]).astype(float)
        encoding_done = True

    feature_engineering_done = encoding_done or scaling_done or (not skip_scaling)

    # ------------------------------------------------------------------
    # 3. Train/test split (stratified, seeded)
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        feature_matrix,
        y,
        np.arange(n),
        test_size=0.20,
        stratify=y,
        random_state=42,
    )
    region_test = region_col[idx_test]
```

The imports at the top of `pipeline.py` must include:

```python
from ml import features as ml_features
from ml import metrics as ml_metrics
```

These lines are the composition. They import your Module 6 code off disk. If `ml.features` does not exist or is missing `one_hot_encode`, the import fails here with a clear error.

## The Acceptance Gate

The test file for this stage is `exercises/module7/the-dataset-and-the-feature-pipeline/test_pipeline.py`. Run it with:

```
python -m pytest exercises/module7/the-dataset-and-the-feature-pipeline
```

The test file:

```python
"""Acceptance gate: tabular ML pipeline composition.

Tests
-----
1. run() returns a PipelineResult with metrics clearing AUC >= 0.75 and F1 >= 0.50.
2. predictions length equals the test set size (20% of 1000 rows).
3. composed_modules contains "ml.features" and "ml.metrics".
4. slices dict has one entry per region subgroup value; worst subgroup identifiable.
5. COMPOSITION: ml.features and ml.metrics are imported from the ml/ package on disk.
"""
import os
import sys

# Path setup: ref/ for ml package, ref/module7/ for pipeline/rubric
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE7 = os.path.dirname(_HERE)
_REF = os.path.dirname(_MODULE7)

for _p in [_REF, _MODULE7]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import pytest

import pipeline
from pipeline import PipelineResult

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

DATA_PATH = os.path.join(_MODULE7, "data.csv")

EXPECTED_REGIONS = {"north", "south", "east", "west"}
TEST_SET_SIZE = 200   # 20% of 1000 rows


@pytest.fixture(scope="module")
def good_result() -> PipelineResult:
    """Run the full pipeline once; reuse result across tests."""
    return pipeline.run(DATA_PATH)


# ---------------------------------------------------------------------------
# 1. Metrics clear floors
# ---------------------------------------------------------------------------

def test_auc_floor(good_result):
    auc = good_result.metrics["auc"]
    assert auc >= 0.75, f"Expected AUC >= 0.75, got {auc:.4f}"


def test_f1_floor(good_result):
    f1 = good_result.metrics["f1"]
    assert f1 >= 0.50, f"Expected F1 >= 0.50, got {f1:.4f}"


def test_precision_and_recall_present(good_result):
    m = good_result.metrics
    assert "precision" in m and isinstance(m["precision"], float)
    assert "recall" in m and isinstance(m["recall"], float)


# ---------------------------------------------------------------------------
# 2. Predictions length
# ---------------------------------------------------------------------------

def test_predictions_length(good_result):
    assert len(good_result.predictions) == TEST_SET_SIZE, (
        f"Expected {TEST_SET_SIZE} predictions, got {len(good_result.predictions)}"
    )


def test_probabilities_length(good_result):
    assert len(good_result.probabilities) == TEST_SET_SIZE


def test_probabilities_in_unit_interval(good_result):
    proba = good_result.probabilities
    assert float(proba.min()) >= 0.0
    assert float(proba.max()) <= 1.0


# ---------------------------------------------------------------------------
# 3. Composed modules listed
# ---------------------------------------------------------------------------

def test_composed_modules_contains_features(good_result):
    assert "ml.features" in good_result.composed_modules


def test_composed_modules_contains_metrics(good_result):
    assert "ml.metrics" in good_result.composed_modules


# ---------------------------------------------------------------------------
# 4. Slices coverage and worst subgroup
# ---------------------------------------------------------------------------

def test_slices_has_all_regions(good_result):
    """One entry per region value present in the test set."""
    found = set(good_result.slices.keys())
    assert found == EXPECTED_REGIONS, (
        f"Expected slices for {EXPECTED_REGIONS}, got {found}"
    )


def test_worst_subgroup_identifiable(good_result):
    """worst_subgroup is the key with the lowest recall value."""
    slices = good_result.slices
    worst = min(slices, key=slices.__getitem__)
    assert good_result.worst_subgroup == worst, (
        f"worst_subgroup={good_result.worst_subgroup!r} but min-recall subgroup={worst!r}"
    )


def test_worst_subgroup_nonempty(good_result):
    assert good_result.worst_subgroup != ""


# ---------------------------------------------------------------------------
# 5. COMPOSITION: ml.features and ml.metrics are from ml/ package on disk
# ---------------------------------------------------------------------------

def test_ml_features_imported_from_disk(good_result):
    import ml.features as mf
    assert hasattr(mf, "__file__") and mf.__file__ is not None
    assert os.path.basename(mf.__file__) == "features.py", (
        f"Expected features.py, got {mf.__file__}"
    )
    # Must live inside the ml/ directory
    assert os.path.sep + "ml" + os.path.sep in mf.__file__ or "/ml/" in mf.__file__, (
        f"ml.features not inside ml/ directory: {mf.__file__}"
    )


def test_ml_metrics_imported_from_disk(good_result):
    import ml.metrics as mm
    assert hasattr(mm, "__file__") and mm.__file__ is not None
    assert os.path.basename(mm.__file__) == "metrics.py", (
        f"Expected metrics.py, got {mm.__file__}"
    )
    assert os.path.sep + "ml" + os.path.sep in mm.__file__ or "/ml/" in mm.__file__, (
        f"ml.metrics not inside ml/ directory: {mm.__file__}"
    )


def test_ml_features_has_one_hot_encode():
    import ml.features as mf
    assert callable(getattr(mf, "one_hot_encode", None))


def test_ml_metrics_has_roc_auc():
    import ml.metrics as mm
    assert callable(getattr(mm, "roc_auc", None))
```

The test fixture runs the complete pipeline once and reuses the result across all tests. Tests 1 through 4 check the pipeline's outputs; test 5 verifies that `ml.features` and `ml.metrics` were imported from the `ml/` package on disk, not reimplemented inside `pipeline.py`.

At this stage `pipeline.run()` must produce a `PipelineResult`. The model and evaluation stages can be stubs that return placeholder values; the gate checks shape and composition, not final metric values. Fill those stages in the next two exercises.

## Done When

- `python generate_data.py` (from `exercises/module7/`) exits 0 and writes `data.csv` with 1,000 rows and the class balance line printed.
- `python -m pytest exercises/module7/the-dataset-and-the-feature-pipeline` exits 0.
- `pipeline.py` imports `ml.features` and `ml.metrics` at the top; no local reimplementation of `one_hot_encode`, `zscore`, `roc_auc`, or `f1`.

## Stretch

Add an assertion after `ml_features.one_hot_encode(plan_col)` that the number of columns in `ohe_plan` equals the number of unique values in `plan_col`. If a new dataset had a previously unseen plan type, the feature matrix shape would change silently and the model would fail at fit time; the assertion turns that into a loud error at the right place.
