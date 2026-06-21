# Load the Predictions

Batch inference produces a file. What you do next determines whether your evaluation engine is a one-off script or a reusable tool.

## What You Build

You build the `load_predictions` function and the `EvalConfig` dataclass: the entry point and the column contract for `eval_engine.py`, the shared artifact this module assembles across four lessons.

## The Engine's Shape

`eval_engine.py` has four stages. Your work in this lesson is the first; the others are given so you can see how the whole machine fits together.

```python
import pandas as pd
from dataclasses import dataclass

@dataclass(frozen=True)
class EvalConfig:
    input_path: str
    output_path: str
    pred_col: str = "prediction"
    label_col: str = "label"

def load_predictions(path: str, config: EvalConfig) -> pd.DataFrame:   # your stage (L1)
def confusion_counts(df, cls, config) -> tuple[int,int,int]:           # L2 (given)
def per_class_metrics(df, config) -> list:                             # L3 (given)
def to_markdown_table(metrics) -> str:                                 # L3 (given)
def run(config) -> list:                                               # L4 (given, owns main)
```

Each later stage receives the DataFrame that `load_predictions` returns. Nothing past L1 touches the file system.

## The Contract: `EvalConfig`

Before writing `load_predictions`, declare what the engine expects. A frozen dataclass (M5) is the right tool: immutable, repr-able, and loud when you try to mutate it.

```python
@dataclass(frozen=True)
class EvalConfig:
    input_path: str
    output_path: str            # a .md path; the report lives here
    pred_col: str = "prediction"
    label_col: str = "label"
```

`pred_col` and `label_col` are the load-bearing fields. Every downstream stage reads the prediction and label columns by name through the config object, not by position. Change the column names in `EvalConfig` and the whole engine adapts without a grep-and-replace.

## Reading the Prediction File

The input is a CSV with three columns: `id`, `prediction`, and `label`. One row per prediction. This is the format Azure Machine Learning batch endpoints write when you set `output_action: append_row` and add a ground-truth column, the pattern documented in the Azure ML batch scoring guide ([learn.microsoft.com/azure/machine-learning/how-to-mlflow-batch](https://learn.microsoft.com/azure/machine-learning/how-to-mlflow-batch?view=azureml-api-2#analyze-outputs)).

```python
def load_predictions(path: str, config: EvalConfig) -> pd.DataFrame:
    df = pd.read_csv(path)
    assert config.pred_col in df.columns, (
        f"Prediction column {config.pred_col!r} not found in {list(df.columns)}"
    )
    assert config.label_col in df.columns, (
        f"Label column {config.label_col!r} not found in {list(df.columns)}"
    )
    return df
```

`pd.read_csv` is the M3 tool you already know. The two assertions are the integrity gate: if the file came back without the columns the engine needs, you want a failure here, at the boundary, not a `KeyError` three stages later when `confusion_counts` tries to slice the frame.

## A Concrete Run Against the Sample

The sample file (`exercises/module7/predictions.csv`) has 10 rows: three classes, a few mismatches, one row per prediction.

```python
config = EvalConfig(
    input_path="exercises/module7/predictions.csv",
    output_path="exercises/module7/report.md",
)

df = load_predictions(config.input_path, config)
print(df)
#     id prediction label
# 0    1        cat   cat
# 1    2        cat   dog
# 2    3        dog   dog
# 3    4       bird  bird
# 4    5        cat   cat
# 5    6        dog   cat
# 6    7       bird  bird
# 7    8        dog   dog
# 8    9        cat   cat
# 9   10       bird   dog

print(df.shape)
# (10, 3)

print(df.columns.tolist())
# ['id', 'prediction', 'label']
```

Ten rows. Three columns. The prediction and label columns are present, named exactly what `EvalConfig` expects. `confusion_counts` in L2 will slice these two columns by class; it never touches the raw file.

## Why the Config Object Earns Its Place

Without `EvalConfig`, the column names live in the function signature, or worse, hardcoded inside the function body. A dataset where the prediction column is named `pred` or `model_output` means a code edit. With `EvalConfig`, you change one field and the entire engine follows. The frozen dataclass also means the config cannot drift between stages: whatever `load_predictions` sees, `confusion_counts` and `per_class_metrics` see too. An evaluation engine you cannot point at a named config is a script; naming the columns in a config is what makes it an engine.

## Core Concepts

- `pd.read_csv` reads the prediction file into a DataFrame in one call; the two integrity assertions convert a silent column-mismatch into a load-time failure, the cheapest possible failure.
- A `@dataclass(frozen=True)` `EvalConfig` holds `pred_col` and `label_col` so every stage reads the same column names from one immutable source; changing the config changes the engine.
- The `load_predictions` stage's only job is to deliver the prediction DataFrame with the named columns present; computing metrics belongs to the later stages.
- Column-name indirection through a config object is what separates a reusable eval engine from a script written for one dataset.

<div class="claude-handoff" data-exercise="exercises/module7/load-the-predictions/">

**Build It in Claude Code:** Add `EvalConfig` and `load_predictions` to `exercises/module7/eval_engine.py`, create the `predictions.csv` fixture, assert the loaded DataFrame has 10 rows and columns `id`, `prediction`, and `label`, and exit 0.

</div>
