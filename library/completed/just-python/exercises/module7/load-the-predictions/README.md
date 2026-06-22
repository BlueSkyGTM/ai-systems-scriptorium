# Exercise: Load the Predictions

**Goal:** Build `EvalConfig` and `load_predictions` in `exercises/module7/eval_engine.py`, create the `predictions.csv` fixture the whole module uses, assert the loaded DataFrame has the expected shape and columns, and exit 0.

**Why:** Every production eval engine starts at a typed boundary. A `load_predictions` stage that names its columns in a frozen config and checks their presence at load time is the seam where the engine can be tested in isolation, pointed at a different dataset, and handed to a hiring manager as evidence that you build engines, not scripts.

## The Shared Artifact

`eval_engine.py` is the M7 throughline artifact. This lesson builds the first two pieces; later lessons add the remaining stages. Before you add anything, check whether `exercises/module7/eval_engine.py` already exists. If it does, read it before touching it. If not, create it here.

The locked structure for the whole module is:

```python
import pandas as pd
from dataclasses import dataclass

@dataclass(frozen=True)
class EvalConfig:
    input_path: str
    output_path: str            # a .md path
    pred_col: str = "prediction"
    label_col: str = "label"

def load_predictions(path: str, config: EvalConfig) -> pd.DataFrame:   # your work (L1)
def confusion_counts(df, cls, config) -> tuple[int,int,int]:           # L2 (given later)
def per_class_metrics(df, config) -> list:                             # L3 (given later)
def to_markdown_table(metrics) -> str:                                 # L3 (given later)
def run(config) -> list:                                               # L4 (given later, owns main)
```

Build only `EvalConfig` and `load_predictions` now. Leave stubs or omit the other stages; do not write them.

## Steps

### 1. Create the Prediction Fixture

Create `exercises/module7/predictions.csv` with exactly these 10 rows, in this order:

```
id,prediction,label
1,cat,cat
2,cat,dog
3,dog,dog
4,bird,bird
5,cat,cat
6,dog,cat
7,bird,bird
8,dog,dog
9,cat,cat
10,bird,dog
```

This fixture is deterministic: three classes (`cat`, `dog`, `bird`), two mismatches on `cat` (rows 2 and 6), one mismatch on `bird` (row 10). Every later lesson in M7 uses this same file; do not alter it once it exists.

### 2. Add `EvalConfig` to `eval_engine.py`

```python
import pandas as pd
from dataclasses import dataclass

@dataclass(frozen=True)
class EvalConfig:
    input_path: str
    output_path: str
    pred_col: str = "prediction"
    label_col: str = "label"
```

Confirm that constructing an `EvalConfig` with only `input_path` and `output_path` works and that the defaults for `pred_col` and `label_col` are applied. Confirm that trying to reassign a field after construction raises a `FrozenInstanceError`.

### 3. Add `load_predictions` to `eval_engine.py`

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

`load_predictions` does not filter, rename, or compute anything. It delivers the raw prediction file as a DataFrame with the named columns confirmed present. The checks convert a silent `KeyError` three stages later into a loud failure at the entry point.

### 4. Write the Smoke Check

Create `exercises/module7/load-the-predictions/smoke.py`. It must run with one command and exit 0 if everything passes.

```python
import sys
import pathlib
import dataclasses
import pandas as pd

# Add the module7 root so eval_engine.py is importable
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))
from eval_engine import load_predictions, EvalConfig  # noqa: E402

PREDICTIONS = pathlib.Path(__file__).parents[2] / "predictions.csv"

config = EvalConfig(
    input_path=str(PREDICTIONS),
    output_path=str(pathlib.Path(__file__).parents[2] / "report.md"),
)

df = load_predictions(config.input_path, config)

# Print the loaded frame so you can see it
print(df.to_string())
print()

# Shape gate
assert df.shape == (10, 3), f"Expected (10, 3), got {df.shape}"

# Column gate
assert list(df.columns) == ["id", "prediction", "label"], (
    f"Expected ['id', 'prediction', 'label'], got {list(df.columns)}"
)

# Values spot-check: first and last row
assert df.iloc[0]["prediction"] == "cat" and df.iloc[0]["label"] == "cat"
assert df.iloc[9]["prediction"] == "bird" and df.iloc[9]["label"] == "dog"

# Frozen config: reassignment must raise
try:
    config.pred_col = "other"  # type: ignore
    raise AssertionError("EvalConfig must be frozen but accepted a write")
except dataclasses.FrozenInstanceError:
    pass

print("[PASS] shape (10, 3) confirmed")
print("[PASS] columns ['id', 'prediction', 'label'] confirmed")
print("[PASS] spot-check values confirmed")
print("[PASS] EvalConfig is frozen")
```

Run it:

```sh
python exercises/module7/load-the-predictions/smoke.py
```

No external dependencies beyond `pandas`.

## Done When

`python exercises/module7/load-the-predictions/smoke.py` prints the loaded DataFrame, confirms shape `(10, 3)`, confirms columns `['id', 'prediction', 'label']`, confirms spot-check values, confirms the frozen config, and exits 0.

## Stretch

Add a column-presence check that goes through the config rather than hardcoding column names. Then write a second smoke check that passes a CSV missing the `label` column and confirms the `AssertionError` is raised with a message naming the missing column.

```python
# In a bad_predictions.csv with only id,prediction columns:
try:
    bad_config = EvalConfig(
        input_path="bad_predictions.csv",
        output_path="report.md",
    )
    load_predictions(bad_config.input_path, bad_config)
    raise AssertionError("Should have failed on missing label column")
except AssertionError as e:
    assert "label" in str(e), f"Error message should name the missing column: {e}"
    print("[PASS] missing column detected at load time")
```

The negative case is tested. Strength is what a pipeline refuses, not only what it ships.
