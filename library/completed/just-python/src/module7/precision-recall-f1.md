# Precision, Recall, and F1

An eval job that crashes on a class with no predictions is worse than one that returns 0.0. Three small formulas stand between a blank report and a running pipeline.

## What You Build

You build `ClassMetrics`, a frozen dataclass that holds per-class precision, recall, F1, and support, then `per_class_metrics`, which iterates every class in the dataset and calls `confusion_counts` to fill one record per class, and `to_markdown_table`, which renders those records as a Markdown report with a macro-average row.

## The Three Formulas

`confusion_counts` (built in L2) returns `(tp, fp, fn)` for one class. The three derived metrics are:

```python
precision = tp / (tp + fp)   # of every time you predicted this class, how often were you right?
recall    = tp / (tp + fn)   # of every actual instance, how many did you catch?
f1        = 2 * precision * recall / (precision + recall)   # harmonic mean of the two
```

Support is the number of actual instances of the class: `support = tp + fn`. A class with support 0 never appears in the ground truth; a class with `tp + fp == 0` was never predicted.

Azure Machine Learning's Evaluate Model component uses exactly these definitions: Precision = TP/(TP+FP), Recall = TP/(TP+FN), F1 as the weighted average of the two ([learn.microsoft.com/azure/machine-learning/component-reference/evaluate-model](https://learn.microsoft.com/azure/machine-learning/component-reference/evaluate-model)).

## The ClassMetrics Dataclass

`ClassMetrics` is a frozen dataclass (M5 pattern) with one record per class:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ClassMetrics:
    cls:       str
    precision: float
    recall:    float
    f1:        float
    support:   int
```

`frozen=True` keeps the record immutable after construction. Each call to `per_class_metrics` produces a list of these; nothing downstream can silently mutate a score.

## The Zero-Division Rule

A class that was never predicted gives `tp + fp == 0`; dividing for precision raises `ZeroDivisionError`. A class with no actual instances gives `tp + fn == 0`; dividing for recall does the same. Production eval code never raises on these cases: it returns 0.0 instead.

The rule, in full:

```python
precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
```

This is not a workaround; it is the convention the industry adopted because a metric function that divides by zero takes down the eval job at the exact moment you most need the report. A class that appears nowhere in predictions scores 0.0, the report renders, and the pipeline moves on.

## Building per_class_metrics

Collect the full set of classes from both `label` and `prediction` columns, then iterate in sorted order:

```python
import pandas as pd

def per_class_metrics(df: pd.DataFrame, config) -> list[ClassMetrics]:
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

The union of both columns catches any class that appears in predictions but not ground truth (and vice versa). Sorting makes the output deterministic.

## Building to_markdown_table

The table gets one row per class, then a macro-average row across all classes. Macro-average is the unweighted mean of each metric across classes: it treats a rare class and a common one equally.

```python
def to_markdown_table(metrics: list[ClassMetrics]) -> str:
    header = "| class | precision | recall | f1 | support |"
    sep    = "|-------|-----------|--------|----|---------|"
    rows   = [header, sep]
    for m in metrics:
        rows.append(
            f"| {m.cls} | {m.precision:.3f} | {m.recall:.3f} | {m.f1:.3f} | {m.support} |"
        )
    n    = len(metrics)
    rows.append(
        f"| **macro avg** | {sum(m.precision for m in metrics)/n:.3f} "
        f"| {sum(m.recall for m in metrics)/n:.3f} "
        f"| {sum(m.f1 for m in metrics)/n:.3f} "
        f"| {sum(m.support for m in metrics)} |"
    )
    return "\n".join(rows)
```

## Concrete Example

On the ten-row sample (`exercises/module7/predictions.csv`), `per_class_metrics` returns:

| class | precision | recall | f1    | support |
|-------|-----------|--------|-------|---------|
| bird  | 0.667     | 1.000  | 0.800 | 2       |
| cat   | 0.750     | 0.750  | 0.750 | 4       |
| dog   | 0.667     | 0.500  | 0.571 | 4       |
| **macro avg** | 0.694 | 0.750 | 0.707 | 10 |

Bird has perfect recall (both actual birds were predicted bird) but imperfect precision (one non-bird was also called bird). Dog has the lowest F1 because two of its four actual instances were missed. The macro average weights all three classes equally regardless of support.

The formulas are small. What makes them production-ready is what happens when a denominator goes to zero.

## Core Concepts

- Precision = TP/(TP+FP): of every prediction of a class, how many were correct. Recall = TP/(TP+FN): of every actual instance, how many were found. F1 is the harmonic mean of the two.
- Support is the count of actual instances of a class (`tp + fn`); a class with support 0 was absent from the ground truth, not from the predictions.
- When `tp + fp == 0` set precision to 0.0; when `tp + fn == 0` set recall to 0.0; when `precision + recall == 0` set F1 to 0.0. Never raise `ZeroDivisionError` in a metric function.
- Macro-average is the unweighted mean of per-class precision, recall, and F1; it treats every class equally regardless of how often it appears.

<div class="claude-handoff" data-exercise="exercises/module7/precision-recall-f1/">

**Build It in Claude Code:** Add `ClassMetrics`, `per_class_metrics`, and `to_markdown_table` to the shared `eval_engine.py`, assert the expected per-class and macro-average metrics against the ten-row sample, and confirm the zero-division path returns 0.0 without crashing.

</div>
