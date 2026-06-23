"""pipeline.py -- M7 capstone: tabular ML pipeline composing ml.features + ml.metrics.

Entry point
-----------
    result = pipeline.run("path/to/data.csv")
    result = pipeline.run("path/to/data.csv", skip_scaling=True)   # deficient mode

The pipeline composes ml.features and ml.metrics from the from-scratch package,
then uses sklearn.ensemble.GradientBoostingClassifier as the learner.
"""
from __future__ import annotations

import os
import sys
import csv
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List

# ---------------------------------------------------------------------------
# Path setup: add ref/ (for ml package) and ref/module7/ (for pipeline/rubric)
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REF = os.path.dirname(_HERE)   # ref/

for _p in [_REF, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

from ml import features as ml_features
from ml import metrics as ml_metrics

# ---------------------------------------------------------------------------
# Column schema for data.csv
# ---------------------------------------------------------------------------
NUMERIC_COLS = ["tenure_months", "monthly_charge", "num_products"]
CATEGORICAL_COLS = ["plan_type"]           # one-hot encoded
SUBGROUP_COL = "region"                    # used for slicing
TARGET_COL = "churned"

VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    predictions: np.ndarray
    probabilities: np.ndarray
    metrics: Dict[str, float]             # auc, f1, precision, recall
    slices: Dict[str, float]              # subgroup_value -> recall
    worst_subgroup: str
    model_card_path: str
    composed_modules: List[str]
    version: str
    # Internal flags for the rubric
    _feature_engineering_done: bool = field(default=False, repr=False)
    _encoding_done: bool = field(default=False, repr=False)
    _scaling_done: bool = field(default=False, repr=False)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _load_csv(path: str):
    """Return (header, rows-as-dicts)."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return rows


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(
    data_path: str,
    skip_scaling: bool = False,
    skip_encoding: bool = False,
    skip_slicing: bool = False,
    stub_model_card: bool = False,
    card_name: str = "MODEL_CARD.md",
) -> PipelineResult:
    """Run the full tabular ML pipeline.

    Parameters
    ----------
    data_path : str
        Path to data.csv produced by generate_data.py.
    skip_scaling : bool
        Deficient mode: omit z-score scaling of numeric columns.
    skip_encoding : bool
        Deficient mode: omit one-hot encoding of categorical columns.
    skip_slicing : bool
        Deficient mode: omit subgroup slicing evaluation.
    stub_model_card : bool
        Deficient mode: write a stub card with no section headers.

    Returns
    -------
    PipelineResult
    """
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

    # ------------------------------------------------------------------
    # 4. Train
    # ------------------------------------------------------------------
    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42,
    )
    clf.fit(X_train, y_train)

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

    # ------------------------------------------------------------------
    # 7. Model card
    # ------------------------------------------------------------------
    card_path = os.path.join(os.path.dirname(data_path), card_name)

    if stub_model_card:
        with open(card_path, "w", encoding="utf-8") as fh:
            fh.write("This is a stub model card with no required sections.\n")
    else:
        _write_model_card(
            card_path,
            data_path=data_path,
            n_rows=n,
            numeric_cols=NUMERIC_COLS,
            categorical_cols=CATEGORICAL_COLS,
            subgroup_col=SUBGROUP_COL,
            metrics=overall_metrics,
            slices=slices,
            worst_subgroup=worst_subgroup,
            skip_scaling=skip_scaling,
            skip_encoding=skip_encoding,
        )

    composed_modules = ["ml.features", "ml.metrics"]

    return PipelineResult(
        predictions=y_pred,
        probabilities=y_proba,
        metrics=overall_metrics,
        slices=slices,
        worst_subgroup=worst_subgroup,
        model_card_path=card_path,
        composed_modules=composed_modules,
        version=VERSION,
        _feature_engineering_done=feature_engineering_done,
        _encoding_done=encoding_done,
        _scaling_done=scaling_done,
    )


# ---------------------------------------------------------------------------
# Deficient pipeline convenience wrapper
# ---------------------------------------------------------------------------

def run_deficient(data_path: str, failure_mode: str = "no_encoding") -> PipelineResult:
    """Run a deliberately broken pipeline for rubric negative-case testing.

    Parameters
    ----------
    failure_mode : str
        "no_encoding"   -- omit one-hot encoding (R2 fails)
        "no_slicing"    -- omit subgroup slicing (R4 fails)
        "stub_card"     -- write a stub model card (R6 fails)
    """
    # Deficient runs write to a separate card path so they never clobber the real MODEL_CARD.md.
    deficient_card = "MODEL_CARD.deficient.md"
    if failure_mode == "no_encoding":
        return run(data_path, skip_encoding=True, skip_scaling=True, card_name=deficient_card)
    elif failure_mode == "no_slicing":
        return run(data_path, skip_slicing=True, card_name=deficient_card)
    elif failure_mode == "stub_card":
        return run(data_path, stub_model_card=True, card_name=deficient_card)
    else:
        raise ValueError(f"Unknown failure_mode: {failure_mode!r}")


# ---------------------------------------------------------------------------
# Model card writer
# ---------------------------------------------------------------------------

_CARD_TEMPLATE = """\
# MODEL_CARD.md

## Dataset

- **Path**: {data_path}
- **Rows**: {n_rows:,}
- **Provenance**: seeded synthetic benchmark designed to exercise the full methodology.
  Generated by `generate_data.py` with `numpy.random.default_rng(seed=42)`; byte-reproducible.
- **Task**: binary classification (churn prediction).
- **Class balance**: roughly 30% positive (churned=1).

## Features

**Numeric columns** (z-score scaled): {numeric_cols}
{scaling_note}

**Categorical columns** (one-hot encoded): {categorical_cols}
{encoding_note}

**Subgroup column** (for slicing): `{subgroup_col}` -- values: north, south, east, west.

All feature engineering uses `ml.features` from the from-scratch package:
- `ml.features.zscore` for numeric scaling
- `ml.features.one_hot_encode` for categorical encoding

## Model + Hyperparameters

| Parameter | Value |
|-----------|-------|
| Algorithm | `sklearn.ensemble.GradientBoostingClassifier` |
| n_estimators | 200 |
| max_depth | 4 |
| learning_rate | 0.05 |
| subsample | 0.8 |
| random_state | 42 |

Train/test split: 80/20, stratified on `churned`, `random_state=42`.

## Overall Metrics

Evaluated on the held-out 20% test set using `ml.metrics` from-scratch implementations.

| Metric | Value |
|--------|-------|
| AUC (ROC) | {auc:.4f} |
| F1 | {f1:.4f} |
| Precision | {precision:.4f} |
| Recall | {recall:.4f} |

All metrics computed with `ml.metrics.roc_auc`, `ml.metrics.f1`,
`ml.metrics.precision`, `ml.metrics.recall`.

## Slice Table

Per-subgroup recall (via `ml.metrics.slice_metric` over `{subgroup_col}`):

| Subgroup | Recall |
|----------|--------|
{slice_rows}

**Worst subgroup**: `{worst_subgroup}` (recall = {worst_recall:.4f}).
Identifies the population segment where the model performs least well on positive detection.

## Limitations

1. **Synthetic data**: the signal is deterministic and clean; real churn data has more noise,
   missing values, and temporal drift. AUC on real data would likely be lower.
2. **Subgroup gaps**: recall varies across regions (see slice table); the model should be
   monitored and possibly calibrated for the worst-performing subgroup in production.
3. **No temporal validation**: the split is random, not time-based; a model deployed to predict
   future churn should be evaluated on future holdout data.
4. **Feature coverage**: `num_products` and `plan_type` encode product stickiness; other
   signals common in production (contract type, support tickets, usage frequency) are absent.
5. **Threshold choice**: the default 0.5 threshold is used for F1/precision/recall; an
   optimal threshold tuned on a validation set would change these numbers.
"""


def _write_model_card(
    card_path: str,
    data_path: str,
    n_rows: int,
    numeric_cols: list,
    categorical_cols: list,
    subgroup_col: str,
    metrics: dict,
    slices: dict,
    worst_subgroup: str,
    skip_scaling: bool,
    skip_encoding: bool,
) -> None:
    slice_rows = "\n".join(
        f"| {k} | {v:.4f} |" for k, v in sorted(slices.items())
    )
    worst_recall = slices.get(worst_subgroup, float("nan"))

    scaling_note = (
        "Applied: each numeric column is z-score normalized (mean 0, std 1)."
        if not skip_scaling
        else "WARNING: scaling was skipped (deficient run)."
    )
    encoding_note = (
        "Applied: `plan_type` and `region` one-hot encoded into binary indicator columns."
        if not skip_encoding
        else "WARNING: encoding was skipped (deficient run)."
    )

    content = _CARD_TEMPLATE.format(
        data_path=os.path.basename(data_path),
        n_rows=n_rows,
        numeric_cols=", ".join(f"`{c}`" for c in numeric_cols),
        categorical_cols=", ".join(f"`{c}`" for c in categorical_cols),
        subgroup_col=subgroup_col,
        auc=metrics["auc"],
        f1=metrics["f1"],
        precision=metrics["precision"],
        recall=metrics["recall"],
        slice_rows=slice_rows,
        worst_subgroup=worst_subgroup,
        worst_recall=worst_recall,
        scaling_note=scaling_note,
        encoding_note=encoding_note,
    )

    with open(card_path, "w", encoding="utf-8") as fh:
        fh.write(content)


# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run M7 tabular ML pipeline")
    parser.add_argument(
        "data_path",
        nargs="?",
        default=os.path.join(os.path.dirname(__file__), "data.csv"),
        help="Path to data.csv (default: module7/data.csv)",
    )
    parser.add_argument("--skip-scaling", action="store_true")
    parser.add_argument("--skip-encoding", action="store_true")
    parser.add_argument("--deficient", choices=["no_encoding", "no_slicing", "stub_card"],
                        help="Run a deficient pipeline for rubric testing")
    args = parser.parse_args()

    if args.deficient:
        result = run_deficient(args.data_path, failure_mode=args.deficient)
    else:
        result = run(
            args.data_path,
            skip_scaling=args.skip_scaling,
            skip_encoding=args.skip_encoding,
        )

    print(f"\nPipeline v{result.version}")
    print(f"Composed modules: {result.composed_modules}")
    print(f"\nOverall metrics (test set):")
    for k, v in result.metrics.items():
        print(f"  {k:12s}: {v:.4f}")
    print(f"\nSubgroup recall (region):")
    for sub, score in sorted(result.slices.items()):
        marker = " <-- WORST" if sub == result.worst_subgroup else ""
        print(f"  {sub:8s}: {score:.4f}{marker}")
    print(f"\nModel card: {result.model_card_path}")
