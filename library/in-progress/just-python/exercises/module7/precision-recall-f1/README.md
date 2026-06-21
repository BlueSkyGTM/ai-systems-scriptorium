# Exercise: Precision, Recall, and F1

**Goal:** Add `ClassMetrics`, `per_class_metrics`, and `to_markdown_table` to the shared `exercises/module7/eval_engine.py`. Load the ten-row sample, assert the expected per-class metrics and zero-division behaviour, print the Markdown table, and exit 0.

**Why:** `confusion_counts` returns raw counts. This stage turns them into the three production metrics every eval report needs: precision, recall, and F1, one record per class, with zero-division handled correctly so the eval job never crashes on an absent class.

## Before You Touch Code

Read `src/module7/precision-recall-f1.md`. Then open `exercises/module7/eval_engine.py` and read its current state. L1 built `load_predictions` and `EvalConfig`; L2 built `confusion_counts`. You are adding the L3 stage. Do not rebuild or rename anything that already exists.

## What Is Already in eval_engine.py

```python
# Given: do not modify
@dataclass(frozen=True)
class EvalConfig:
    input_path:  str
    output_path: str
    pred_col:    str = "prediction"
    label_col:   str = "label"

def load_predictions(path: str, config: EvalConfig) -> pd.DataFrame: ...  # L1
def confusion_counts(df, cls: str, config: EvalConfig) -> tuple[int,int,int]: ...  # L2: returns (tp, fp, fn)
def run(config: EvalConfig) -> list: ...  # L4: given stub
```

## Steps

### 1. Define ClassMetrics

Add to `eval_engine.py` after the `EvalConfig` block:

```python
@dataclass(frozen=True)
class ClassMetrics:
    cls:       str
    precision: float
    recall:    float
    f1:        float
    support:   int
```

`frozen=True` makes each record immutable after construction.

### 2. Implement per_class_metrics

```python
def per_class_metrics(df: pd.DataFrame, config: EvalConfig) -> list[ClassMetrics]:
    classes = sorted(
        set(df[config.label_col].unique()) | set(df[config.pred_col].unique())
    )
    results = []
    for cls in classes:
        tp, fp, fn = confusion_counts(df, cls, config)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        support   = tp + fn
        results.append(ClassMetrics(cls=cls, precision=precision, recall=recall, f1=f1, support=support))
    return results
```

The union of both columns catches classes that appear only in predictions.

### 3. Implement to_markdown_table

```python
def to_markdown_table(metrics: list[ClassMetrics]) -> str:
    header = "| class | precision | recall | f1 | support |"
    sep    = "|-------|-----------|--------|----|---------|"
    rows   = [header, sep]
    for m in metrics:
        rows.append(
            f"| {m.cls} | {m.precision:.3f} | {m.recall:.3f} | {m.f1:.3f} | {m.support} |"
        )
    n = len(metrics)
    rows.append(
        f"| **macro avg** | {sum(m.precision for m in metrics)/n:.3f} "
        f"| {sum(m.recall for m in metrics)/n:.3f} "
        f"| {sum(m.f1 for m in metrics)/n:.3f} "
        f"| {sum(m.support for m in metrics)} |"
    )
    return "\n".join(rows)
```

### 4. Write the Smoke Script

Create `exercises/module7/precision-recall-f1/smoke.py`:

```python
import sys
import os
import pandas as pd

# Add the module7 exercises root so eval_engine imports cleanly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from eval_engine import EvalConfig, load_predictions, per_class_metrics, to_markdown_table

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "predictions.csv")

config = EvalConfig(input_path=SAMPLE_CSV, output_path="/tmp/eval_out")
df     = load_predictions(SAMPLE_CSV, config)
metrics = per_class_metrics(df, config)

# Index by class name for assertions
by_cls = {m.cls: m for m in metrics}

TOL = 1e-3

# --- per-class assertions ---
assert abs(by_cls["cat"].precision - 0.750) < TOL,  f"cat precision: {by_cls['cat'].precision}"
assert abs(by_cls["cat"].recall    - 0.750) < TOL,  f"cat recall: {by_cls['cat'].recall}"
assert abs(by_cls["cat"].f1        - 0.750) < TOL,  f"cat f1: {by_cls['cat'].f1}"
assert by_cls["cat"].support == 4,                   f"cat support: {by_cls['cat'].support}"

assert abs(by_cls["dog"].precision - 0.667) < TOL,  f"dog precision: {by_cls['dog'].precision}"
assert abs(by_cls["dog"].recall    - 0.500) < TOL,  f"dog recall: {by_cls['dog'].recall}"
assert abs(by_cls["dog"].f1        - 0.571) < TOL,  f"dog f1: {by_cls['dog'].f1}"
assert by_cls["dog"].support == 4,                   f"dog support: {by_cls['dog'].support}"

assert abs(by_cls["bird"].precision - 0.667) < TOL, f"bird precision: {by_cls['bird'].precision}"
assert abs(by_cls["bird"].recall    - 1.000) < TOL, f"bird recall: {by_cls['bird'].recall}"
assert abs(by_cls["bird"].f1        - 0.800) < TOL, f"bird f1: {by_cls['bird'].f1}"
assert by_cls["bird"].support == 2,                  f"bird support: {by_cls['bird'].support}"

print("per-class assertions passed")

# --- macro-average assertions ---
n = len(metrics)
macro_p = sum(m.precision for m in metrics) / n
macro_r = sum(m.recall    for m in metrics) / n
macro_f = sum(m.f1        for m in metrics) / n

assert abs(macro_p - 0.694) < TOL, f"macro precision: {macro_p}"
assert abs(macro_r - 0.750) < TOL, f"macro recall: {macro_r}"
assert abs(macro_f - 0.707) < TOL, f"macro f1: {macro_f}"

print("macro-average assertions passed")

# --- zero-division assertion ---
# Construct a tiny frame where one class has no predictions (precision denom = 0)
# and one class has no actual instances (recall denom = 0).
zero_rows = pd.DataFrame({
    "label":      ["cat", "cat"],
    "prediction": ["dog", "dog"],
})
zero_config = EvalConfig(input_path="", output_path="", pred_col="prediction", label_col="label")
zero_metrics = per_class_metrics(zero_rows, zero_config)
zero_by_cls  = {m.cls: m for m in zero_metrics}

# cat: tp=0, fp=0 (never predicted), fn=2; precision denom is 0
assert zero_by_cls["cat"].precision == 0.0, "expected 0.0 precision for never-predicted class"
# dog: tp=0, fp=2, fn=0 (never labeled); recall denom is 0
assert zero_by_cls["dog"].recall    == 0.0, "expected 0.0 recall for never-labeled class"
# both p and r are 0; f1 denom is 0
assert zero_by_cls["cat"].f1        == 0.0, "expected 0.0 f1 when p+r=0"

print("zero-division assertions passed (no ZeroDivisionError)")

# --- print the Markdown table ---
print()
print(to_markdown_table(metrics))
print()
print("all assertions passed")
```

### 5. Run It

```
python exercises/module7/precision-recall-f1/smoke.py
```

Confirm exit 0 and all assertion lines printed.

## Done When

`python smoke.py` exits 0 and prints:

```
per-class assertions passed
macro-average assertions passed
zero-division assertions passed (no ZeroDivisionError)

| class | precision | recall | f1 | support |
|-------|-----------|--------|----|---------|
| bird  | 0.667 | 1.000 | 0.800 | 2 |
| cat   | 0.750 | 0.750 | 0.750 | 4 |
| dog   | 0.667 | 0.500 | 0.571 | 4 |
| **macro avg** | 0.694 | 0.750 | 0.707 | 10 |

all assertions passed
```

All per-class values are within `1e-3` of the expected values. The zero-division test constructs its own tiny frame; it does not rely on the sample CSV.

Dependencies: `pandas`, `numpy` (via eval_engine). One command, no external services, exit 0.

## Stretch

Add a `weighted_avg` row to `to_markdown_table`. Weighted average weights each class's metric by its support before averaging:

```python
total_support   = sum(m.support for m in metrics)
weighted_p      = sum(m.precision * m.support for m in metrics) / total_support
weighted_r      = sum(m.recall    * m.support for m in metrics) / total_support
weighted_f      = sum(m.f1        * m.support for m in metrics) / total_support
```

Assert the weighted-average row for the sample: precision 0.708, recall 0.700, F1 0.697 (within `1e-3`).

Macro-average treats every class equally. Weighted-average rewards accuracy on common classes. Both appear in production eval reports; the choice reflects whether rare classes matter as much as common ones for the use case.
