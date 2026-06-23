"""rubric.py -- M7 capstone: 6-criterion code grader.

The code IS the lesson prose table.

Criteria
--------
R1  RUNS            -- predictions exist (non-empty array)
R2  FEATURES-ENGINEERED -- categorical columns were encoded + numerics scaled
R3  EVALUATED       -- auc/f1/precision/recall present and clear metric floors
R4  SLICED          -- slices dict non-empty, worst subgroup identified
R5  COMPOSED        -- ml.features and ml.metrics are from the ml/ package on disk
R6  MODEL-CARD      -- MODEL_CARD.md exists with all required section headers

Usage
-----
    python rubric.py            # grades the default pipeline run
    import rubric; rubric.grade(result)
"""
from __future__ import annotations

import os
import sys
import re

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REF = os.path.dirname(_HERE)
for _p in [_REF, _HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Criteria registry (id, human-readable description)
# ---------------------------------------------------------------------------

CRITERIA = (
    ("R1", "RUNS: predictions array is non-empty"),
    ("R2", "FEATURES-ENGINEERED: categoricals one-hot encoded, numerics z-score scaled"),
    ("R3", "EVALUATED: AUC >= 0.75 and F1 >= 0.50 and precision/recall both present"),
    ("R4", "SLICED: per-subgroup metrics computed, worst subgroup identified"),
    ("R5", "COMPOSED: ml.features and ml.metrics imported from ml/ package on disk"),
    ("R6", "MODEL-CARD: MODEL_CARD.md exists with required section headers"),
)

# Floors for R3
_AUC_FLOOR = 0.75
_F1_FLOOR = 0.50

# Required section headers in the model card (checked as substrings)
_REQUIRED_HEADERS = [
    "## Dataset",
    "## Features",
    "## Model",
    "## Overall Metrics",
    "## Slice Table",
    "## Limitations",
]


# ---------------------------------------------------------------------------
# Grading logic
# ---------------------------------------------------------------------------

def grade(result) -> dict[str, bool]:
    """Grade a PipelineResult against the six criteria.

    Parameters
    ----------
    result : PipelineResult
        Returned by pipeline.run().

    Returns
    -------
    dict mapping each criterion id ("R1" .. "R6") to True (pass) or False (fail).
    """
    scores = {}

    # R1 -- RUNS
    try:
        preds = result.predictions
        scores["R1"] = preds is not None and len(preds) > 0
    except Exception:
        scores["R1"] = False

    # R2 -- FEATURES-ENGINEERED
    try:
        scores["R2"] = bool(result._encoding_done) and bool(result._scaling_done)
    except Exception:
        scores["R2"] = False

    # R3 -- EVALUATED
    try:
        m = result.metrics
        auc_ok = isinstance(m.get("auc"), (int, float)) and m["auc"] >= _AUC_FLOOR
        f1_ok = isinstance(m.get("f1"), (int, float)) and m["f1"] >= _F1_FLOOR
        prec_ok = "precision" in m and isinstance(m["precision"], (int, float))
        rec_ok = "recall" in m and isinstance(m["recall"], (int, float))
        scores["R3"] = auc_ok and f1_ok and prec_ok and rec_ok
    except Exception:
        scores["R3"] = False

    # R4 -- SLICED
    try:
        slices_ok = isinstance(result.slices, dict) and len(result.slices) > 0
        worst_ok = isinstance(result.worst_subgroup, str) and result.worst_subgroup != ""
        scores["R4"] = slices_ok and worst_ok
    except Exception:
        scores["R4"] = False

    # R5 -- COMPOSED (ml.features and ml.metrics imported from ml/ package on disk)
    try:
        modules_listed = (
            "ml.features" in result.composed_modules
            and "ml.metrics" in result.composed_modules
        )
        # Verify they are genuinely imported from the ml/ package on disk
        import importlib
        feat_mod = sys.modules.get("ml.features")
        metr_mod = sys.modules.get("ml.metrics")
        feat_on_disk = (
            feat_mod is not None
            and hasattr(feat_mod, "__file__")
            and feat_mod.__file__ is not None
            and os.path.basename(feat_mod.__file__) == "features.py"
            and "ml" in feat_mod.__file__
        )
        metr_on_disk = (
            metr_mod is not None
            and hasattr(metr_mod, "__file__")
            and metr_mod.__file__ is not None
            and os.path.basename(metr_mod.__file__) == "metrics.py"
            and "ml" in metr_mod.__file__
        )
        scores["R5"] = modules_listed and feat_on_disk and metr_on_disk
    except Exception:
        scores["R5"] = False

    # R6 -- MODEL-CARD
    try:
        card_path = result.model_card_path
        card_exists = os.path.isfile(card_path)
        if card_exists:
            with open(card_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            headers_ok = all(h in content for h in _REQUIRED_HEADERS)
        else:
            headers_ok = False
        scores["R6"] = card_exists and headers_ok
    except Exception:
        scores["R6"] = False

    return scores


# ---------------------------------------------------------------------------
# Scorecard printer / CLI entry point
# ---------------------------------------------------------------------------

def main(result=None) -> int:
    """Print scorecard and return 0 iff all six criteria pass.

    If result is not supplied, runs the default pipeline.
    """
    if result is None:
        import pipeline as _pipeline
        data_path = os.path.join(os.path.dirname(__file__), "data.csv")
        result = _pipeline.run(data_path)

    scores = grade(result)

    print("\n===  M7 CAPSTONE RUBRIC  ===")
    print(f"{'ID':<4}  {'PASS/FAIL':<10}  Description")
    print("-" * 72)
    all_pass = True
    for cid, desc in CRITERIA:
        passed = scores.get(cid, False)
        status = "PASS" if passed else "FAIL"
        print(f"{cid:<4}  {status:<10}  {desc}")
        if not passed:
            all_pass = False

    n_pass = sum(scores.values())
    n_total = len(CRITERIA)
    print("-" * 72)
    print(f"Score: {n_pass}/{n_total}")
    print("Result: ALL PASS" if all_pass else "Result: INCOMPLETE -- see FAILed criteria above")
    print()

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
