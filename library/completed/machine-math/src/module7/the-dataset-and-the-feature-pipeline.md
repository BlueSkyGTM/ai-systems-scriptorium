# The Dataset and the Feature Pipeline

Raw columns do not feed a model. A column of "basic," "plus," and "premium" means nothing to gradient boosting until you encode it; a column of monthly charges from $20 to $120 sitting next to a column of product counts from 1 to 5 gives income the same distance-distortion problem KNN had in Module 1. The first stage of every ML pipeline is the same work: read the data, encode the categoricals, scale the numerics, and hold out a test set before you touch the model.

## The Dataset

`generate_data.py` produces `data.csv`: a 1,000-row synthetic churn table with a fixed seed so the output is byte-reproducible.

```
Schema
------
tenure_months   int     [1, 60]
monthly_charge  float   [20.0, 120.0]
num_products    int     [1, 5]
plan_type       str     {basic, plus, premium}
region          str     {north, south, east, west}
churned         int     {0, 1}   ~30% positive
```

The signal is real: short tenure, high monthly charge, the basic plan, and the south region all push churn probability up. The logistic function mixes those signals with a fixed seed, so the dataset is learnable and reproducible. `region` is the subgroup column; the evaluation stage slices by it to surface where the model underperforms.

Run `generate_data.py` once to produce `data.csv`:

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

## The Load and Feature Stage

The first two stages of `pipeline.py` are the load stage and the feature-engineering stage. Read them together: the load stage reads the CSV into numpy arrays; the feature stage calls your `ml.features` functions off disk.

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

## Why Each Step Matters

The numeric z-score call is `ml_features.zscore(numeric_raw[:, col_i])` for each column in turn. That is the function you wrote in Module 6: subtract the column mean, divide by the standard deviation, return a zero-mean unit-variance array. Without it, `monthly_charge` (range 20 to 120) dominates gradient boosting's split decisions over `num_products` (range 1 to 5). Gradient boosting is less sensitive to scale than KNN or linear models, but the consistency matters for reproducibility and for the rubric.

The categorical call is `ml_features.one_hot_encode(plan_col)`, also from your Module 6 code. It returns a binary indicator matrix and the discovered category list. `plan_type` has three values; the encoder produces three binary columns. `region` has four values; four columns. The feature matrix that enters the model has shape `(1000, 10)`: three scaled numerics plus three plan indicators plus four region indicators.

The stratified split holds out 20% of rows with the same churn ratio as the full dataset. `stratify=y` is the argument that enforces it. The test set never touches training; the model never sees it until evaluation.

Azure ML AutoML applies the same two transforms automatically, one-hot encoding for low-cardinality categoricals and standard scaling for numerics, as part of its featurization step ([learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-auto-features](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-configure-auto-features)). You are doing the same work explicitly, with functions you wrote yourself.

## Core Concepts

- Z-score normalization puts numeric columns on a common scale by subtracting the mean and dividing by the standard deviation; without it, high-range columns dominate distance and split calculations.
- One-hot encoding converts a nominal categorical column into one binary indicator column per category; no ordering is implied, so no spurious magnitude signal enters the model.
- Stratified splitting preserves the positive class ratio in both train and test sets; a random split on a 30% positive dataset can produce a test set with a very different ratio by chance.
- Calling `ml_features.zscore` and `ml_features.one_hot_encode` from the installed package, not reimplementing them inside `pipeline.py`, is the composition the capstone requires: if your Module 6 code is broken, the pipeline fails immediately at the call site.

<div class="claude-handoff" data-exercise="exercises/module7/the-dataset-and-the-feature-pipeline/">

**Build It in Claude Code:** Build `exercises/module7/generate_data.py` and the load-plus-feature stage of `exercises/module7/pipeline.py`. The gate is green when `python -m pytest exercises/module7/the-dataset-and-the-feature-pipeline` passes all composition checks.

</div>
