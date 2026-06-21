# Exercise: Ingest the Corpus

**Goal:** Build the `ingest` function and the `WrangleConfig` dataclass in `exercises/module6/wrangle.py`, create the sample corpus fixture the whole module uses, assert the loaded DataFrame has the expected shape and dtypes, and exit 0.

**Why:** Every production wrangling pipeline starts at a typed boundary. An `ingest` stage that declares its dtypes on load and holds its contract in a frozen dataclass is the seam where the pipeline can be tested in isolation, swapped for a different corpus, and handed to a hiring manager as evidence that you build pipelines, not scripts.

## The Shared Artifact

`wrangle.py` is the M6 throughline artifact. This lesson builds the first two pieces; later lessons add the remaining stages. Before you add anything, check whether `exercises/module6/wrangle.py` already exists. If it does, read it before touching it. If not, create it here.

The locked structure for the whole module is:

```python
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class WrangleConfig:
    input_path: str
    output_path: str
    required_cols: tuple[str, ...] = ("id", "text", "label")
    dedup_key: str = "id"

def ingest(path: str) -> pd.DataFrame:          # your work (L1)
def clean(df: pd.DataFrame) -> pd.DataFrame:    # L2 (given later)
def reshape_and_validate(df, config) -> pd.DataFrame:  # L3 (given later)
def emit(df, path) -> None:                     # L4 (given later, owns run + main)
```

Build only `WrangleConfig` and `ingest` now. Leave stubs or omit the other stages; do not write them.

## Steps

### 1. Create the Sample Corpus Fixture

Create `exercises/module6/sample_corpus.jsonl` with exactly these 8 records, in this order:

```
{"id": 1, "text": "  Great Product  ", "label": "pos", "score": 0.9}
{"id": 2, "text": "Terrible", "label": "neg", "score": 0.2}
{"id": 2, "text": "Terrible", "label": "neg", "score": 0.2}
{"id": 3, "text": "Works FINE", "label": "pos", "score": null}
{"id": 4, "text": null, "label": "neu", "score": 0.5}
{"id": 5, "text": "Another  BAD  one", "label": "neg", "score": 0.15}
{"id": 6, "text": "Solid", "label": "pos", "score": 0.7}
{"id": 7, "text": "ok", "label": "neu", "score": 0.4}
```

This fixture is deterministic: one duplicate id (2), one null `text` (id 4), one null `score` (id 3), and mixed-case text. Every later lesson in M6 uses this same file; do not alter it once it exists.

### 2. Add `WrangleConfig` to `wrangle.py`

```python
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class WrangleConfig:
    input_path: str
    output_path: str
    required_cols: tuple[str, ...] = ("id", "text", "label")
    dedup_key: str = "id"
```

Confirm that constructing a `WrangleConfig` with only `input_path` and `output_path` works, and that trying to reassign a field after construction raises a `FrozenInstanceError`.

### 3. Add `ingest` to `wrangle.py`

```python
DTYPE_MAP = {
    "id":    "int64",
    "text":  "object",
    "label": "object",
    "score": "float64",
}

def ingest(path: str) -> pd.DataFrame:
    df = pd.read_json(path, lines=True, dtype=DTYPE_MAP)
    return df
```

The dtype map declares the schema at the entry point. `ingest` does not clean, filter, or drop anything; it delivers the raw corpus as-is with the declared types.

### 4. Write the Smoke Check

Create `exercises/module6/ingest-the-corpus/smoke.py`. It must run with one command and exit 0 if everything passes.

```python
import sys
import pathlib
import numpy as np
import pandas as pd

# Add the module root so wrangle.py is importable
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))
from wrangle import ingest, WrangleConfig  # noqa: E402

CORPUS = pathlib.Path(__file__).parents[1] / "sample_corpus.jsonl"

config = WrangleConfig(
    input_path=str(CORPUS),
    output_path=str(pathlib.Path(__file__).parents[1] / "output.jsonl"),
)

df = ingest(config.input_path)

# Print the loaded frame so you can see it
print(df.to_string())
print()
print("dtypes:")
print(df.dtypes)
print()

# Shape gate
assert df.shape == (8, 4), f"Expected (8, 4), got {df.shape}"

# Dtype gate
assert df["id"].dtype == np.dtype("int64"),   f"id: expected int64, got {df['id'].dtype}"
assert df["text"].dtype == np.dtype("object"), f"text: expected object, got {df['text'].dtype}"
assert df["label"].dtype == np.dtype("object"), f"label: expected object, got {df['label'].dtype}"
assert df["score"].dtype == np.dtype("float64"), f"score: expected float64, got {df['score'].dtype}"

# Null values must be present (ingest does not clean)
assert df["text"].isna().sum() == 1, "Expected exactly 1 null text"
assert df["score"].isna().sum() == 1, "Expected exactly 1 null score"

# Frozen config: reassignment must raise
import dataclasses
try:
    config.input_path = "other.jsonl"  # type: ignore
    raise AssertionError("WrangleConfig must be frozen but accepted a write")
except dataclasses.FrozenInstanceError:
    pass

print("[PASS] shape (8, 4) confirmed")
print("[PASS] dtypes confirmed: id=int64, text=object, label=object, score=float64")
print("[PASS] nulls present: 1 null text, 1 null score")
print("[PASS] WrangleConfig is frozen")
```

Run it:

```sh
python exercises/module6/ingest-the-corpus/smoke.py
```

No external dependencies beyond `pandas` and `numpy`.

## Done When

`python exercises/module6/ingest-the-corpus/smoke.py` prints the loaded DataFrame, confirms shape `(8, 4)`, confirms all four dtypes, confirms the null counts, confirms the frozen config, and exits 0.

## Stretch

Add a column-presence guard to `ingest`: after the read, assert that every column in a given `required_cols` tuple is present in the DataFrame, and raise a `ValueError` naming the missing column if not. Then write a second smoke check that passes a JSONL file missing the `label` column and asserts the `ValueError` is raised. This is the first line of defense a production ingest stage adds beyond dtype declaration.

```python
def ingest(path: str, required_cols: tuple[str, ...] = ()) -> pd.DataFrame:
    df = pd.read_json(path, lines=True, dtype=DTYPE_MAP)
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Required column missing from corpus: {col!r}")
    return df
```

The negative case is tested. Strength is what a pipeline refuses, not only what it ships.
