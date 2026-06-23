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
