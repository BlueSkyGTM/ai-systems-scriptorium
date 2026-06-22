# Reshape and Validate

"The pipeline ran" is not a guarantee. It is just evidence that no Python exception fired. A training set with the wrong columns, the wrong dtypes, or a null hiding in the `text` field can pass silently through `ingest` and `clean` and arrive at the model intact. The model does not complain; it just learns the wrong thing.

## The Artifact

You build `reshape_and_validate`, the third stage in `wrangle.py`. It selects and orders columns to match the target schema, then asserts three things before returning: every required column is present, no required column contains a null, and the dtypes are right. If any assertion fails, it raises a `ValueError` with a message precise enough to act on. That is the gate.

## Why a Gate, Not a Hope

The `clean` stage (L2) handles duplication, null text, and score filling. After `clean`, the data is better, but not contractually correct. There is no guarantee that all required columns exist, that column order matches what the downstream writer expects, or that dtypes have not drifted from an upstream schema change.

The difference between a gate and a hope is who bears the cost of failure. A hope means the model run costs you three hours before a `KeyError` or a silent NaN propagates into the loss. A gate means `reshape_and_validate` raises in the first second.

Azure Databricks documents this as schema enforcement: "schema enforcement ensures that data written to a table adheres to a predefined schema," and NOT NULL constraints prevent null values from propagating downstream at all ([learn.microsoft.com/azure/databricks/transform/validate](https://learn.microsoft.com/azure/databricks/transform/validate)). The same logic applies in a Python pipeline: the stage that writes Parquet is not the place to discover the schema is wrong.

## Select and Order First

Reshaping is simpler than it looks. From the cleaned frame, select `config.required_cols` in the declared order, then append `score`. Column order is a contract: the Parquet writer in L4 depends on it.

```python
from dataclasses import dataclass
from typing import Tuple
import pandas as pd

@dataclass(frozen=True)
class WrangleConfig:
    input_path: str
    output_path: str
    required_cols: Tuple[str, ...] = ("id", "text", "label")
    dedup_key: str = "id"
```

The `required_cols` tuple is fixed in `WrangleConfig`. Select by it:

```python
def reshape_and_validate(df: pd.DataFrame, config: WrangleConfig) -> pd.DataFrame:
    cols = list(config.required_cols) + ["score"]
    df = df[cols]
    ...
```

If any column in `cols` is absent, pandas raises a `KeyError`. That is not a clear message. The next step is your explicit check.

## Assert the Schema

Three checks, in order. The first catches missing columns before the later checks can reference them. The second catches null leakage in required columns. The third catches silent dtype drift.

```python
def reshape_and_validate(df: pd.DataFrame, config: WrangleConfig) -> pd.DataFrame:
    cols = list(config.required_cols) + ["score"]

    # 1. Required columns present
    missing = [c for c in config.required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[cols]

    # 2. No nulls in required columns
    null_counts = df[list(config.required_cols)].isna().sum()
    bad = null_counts[null_counts > 0]
    if not bad.empty:
        raise ValueError(f"Null values in required columns: {bad.to_dict()}")

    # 3. Dtypes correct. Use pandas.api.types predicates, not strict string
    #    equality: a Parquet round-trip can return text as the newer `str`
    #    dtype instead of `object`, and is_string_dtype accepts both.
    import pandas.api.types as pat
    checks = {"id": pat.is_integer_dtype, "text": pat.is_string_dtype,
              "label": pat.is_string_dtype, "score": pat.is_float_dtype}
    for col, ok in checks.items():
        if col in df.columns and not ok(df[col]):
            raise ValueError(f"Column '{col}' has dtype {df[col].dtype}, failed {ok.__name__}")

    return df
```

Each `ValueError` names the exact column and the exact problem. A reviewer reading the traceback knows what to fix without opening the data.

## The Passing Case

Start with the same six-row sample the earlier stages use:

```python
import pandas as pd
import numpy as np

sample = pd.DataFrame({
    "id":    [1, 2, 3, 4, 5, 6],
    "text":  ["good", "bad", "ok", "great", "poor", "fine"],
    "label": ["pos", "neg", "pos", "pos", "neg", "pos"],
    "score": [0.9, 0.2, 0.6, 0.85, 0.3, 0.75],
})

config = WrangleConfig(input_path="in.jsonl", output_path="out.parquet")
validated = reshape_and_validate(sample, config)
print(validated.dtypes)
print(validated.shape)   # (6, 4)
```

The frame passes: required columns present, no nulls, dtypes match. `reshape_and_validate` returns it in the declared column order, ready for `emit`.

## The Raising Case

Remove a column before calling the gate and it raises immediately:

```python
bad_frame = sample.drop(columns=["text"])

try:
    reshape_and_validate(bad_frame, config)
except ValueError as e:
    print(f"[CAUGHT] {e}")
# [CAUGHT] Missing required columns: ['text']
```

Or inject a null into a required column after cleaning:

```python
null_frame = sample.copy()
null_frame.loc[2, "label"] = None

try:
    reshape_and_validate(null_frame, config)
except ValueError as e:
    print(f"[CAUGHT] {e}")
# [CAUGHT] Null values in required columns: {'label': 1}
```

The gate catches both. The model never sees either frame.

## Placing This in the Pipeline

`reshape_and_validate` sits between `clean` and `emit`. In `run`:

```python
def run(config: WrangleConfig) -> None:
    df = ingest(config.input_path)    # L1 (given)
    df = clean(df)                    # L2 (given)
    df = reshape_and_validate(df, config)  # L3 (this stage)
    emit(df, config.output_path)      # L4 (given)
```

The Parquet file `emit` writes is trustworthy because this gate ran. Without it, you are shipping an assertion-free artifact: "the pipeline ran" again, and nothing more.

The gate is what makes the Parquet file a promise instead of a guess. Skip it and you are trusting every upstream change to be benign; add it and a broken input breaks loudly, exactly here, before it costs anything.

## Core Concepts

- Reshaping to a target schema means selecting and ordering columns by a declared list; the list lives in the config, not hardcoded in the stage.
- A validation gate asserts the schema as a contract: required columns present, no nulls in required columns, dtypes correct. A violated assertion raises with a precise message.
- The gate belongs in the pipeline, not in a reviewer's head. "The pipeline ran" proves nothing without it.
- Raising `ValueError` with a column name and count is the minimum useful error: it names what is wrong so the next person can fix it without opening the data.

<div class="claude-handoff" data-exercise="exercises/module6/reshape-and-validate/">

**Build It in Claude Code:** Add `reshape_and_validate` to `exercises/module6/wrangle.py`, run it on `clean(ingest(sample))`, and assert both the passing case and the raising case behave correctly. One `python` command, exit 0.

</div>
