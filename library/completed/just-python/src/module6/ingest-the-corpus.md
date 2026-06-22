# Ingest the Corpus

A bare `pd.read_json` call buried in a script is a liability: no declared dtypes, no named contract, no seam where the pipeline can be tested in isolation. The first stage of a production wrangler reads the raw corpus into a typed DataFrame and publishes its input/output contract in a frozen dataclass so the whole pipeline knows what it agreed to.

## What You Build

You build the `ingest` function and the `WrangleConfig` dataclass: the entry point and the contract for `wrangle.py`, the shared artifact this module assembles across four lessons.

## The Pipeline's Shape

`wrangle.py` has four stages that compose in sequence. Your work in this lesson is the first stage; the others are given.

```python
def ingest(path: str) -> pd.DataFrame:          # this lesson
def clean(df: pd.DataFrame) -> pd.DataFrame:    # L2
def reshape_and_validate(df, config) -> pd.DataFrame:  # L3
def emit(df, path) -> None:                     # L4 (owns run + main)
```

Each stage takes what the prior stage returns. `ingest` is the only one that touches the file system; every later stage works on a DataFrame in memory.

## The Contract: `WrangleConfig`

Before writing `ingest`, declare what the pipeline expects and produces. A frozen dataclass (M5) is the right tool: it is immutable, it has a repr, and it fails loudly if you pass it something wrong.

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

`frozen=True` makes the config immutable after construction. Pass a `WrangleConfig` to `run` and every stage downstream shares the same source of truth, with no way to accidentally mutate it mid-pipeline. The `required_cols` tuple names the columns every downstream stage can count on; `dedup_key` tells the dedup stage which column to use.

## Reading JSONL with Declared Dtypes

The raw corpus is JSONL: one JSON object per line, the format you met in M3. `pd.read_json` with `lines=True` reads it into a DataFrame. The key move here is not the read itself but what you hand `dtype` on the way in.

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

Declaring dtypes on load does two things. First, it removes inference: pandas does not guess `id` is an int or `score` is a float; you said so, and any row that cannot coerce will surface immediately. Second, it documents the schema at the point of entry. The rest of the pipeline inherits this contract without re-reading the file.

Microsoft Fabric's production guidance for reading data into pandas DataFrames follows the same principle: declare the format and the path explicitly, then let the DataFrame carry the typed result forward ([learn.microsoft.com/fabric/data-science/read-write-pandas](https://learn.microsoft.com/fabric/data-science/read-write-pandas)).

## A Concrete Run Against the Sample Corpus

The sample corpus (`exercises/module6/sample_corpus.jsonl`) has 8 records: one duplicate id, one null `text`, one null `score`, and mixed-case text. `ingest` reads all 8 without dropping anything; cleaning is L2's job.

```python
config = WrangleConfig(
    input_path="exercises/module6/sample_corpus.jsonl",
    output_path="exercises/module6/output.jsonl",
)

df = ingest(config.input_path)
print(df)
#    id                text label  score
# 0   1     Great Product   pos    0.90
# 1   2        Terrible    neg    0.20
# 2   2        Terrible    neg    0.20
# 3   3       Works FINE   pos     NaN
# 4   4            None    neu    0.50
# 5   5  Another  BAD  one  neg    0.15
# 6   6           Solid    pos    0.70
# 7   7              ok    neu    0.40

print(df.dtypes)
# id       int64
# text    object
# label   object
# score  float64
# dtype: object

print(df.shape)
# (8, 4)
```

Eight rows, four columns, dtypes as declared. The duplicate (id 2) is present; the null `text` on row 4 and the null `score` on row 3 are present. Nothing is hidden or dropped. That is the contract of `ingest`: deliver the raw corpus faithfully so the cleaning stage can make explicit decisions about each defect.

## Why a Typed Ingest Stage Beats an Ad-Hoc Read

A bare `pd.read_json("corpus.jsonl", lines=True)` works until it does not: an `id` that pandas infers as `float64` because one row has a null, a `score` that silently widens, a dtype mismatch that surfaces three stages later. Declaring dtypes at the boundary converts a runtime surprise into an entry-time failure, the cheapest possible failure. The frozen dataclass makes the input/output paths explicit rather than scattered across a script. Together they turn a fragile read into a stage a hiring manager can point to and say: this is where data enters the system, and this is what it guarantees.

## Core Concepts

- `pd.read_json(path, lines=True, dtype=...)` reads a JSONL corpus into a typed DataFrame in one call; declaring `dtype` on load converts inference errors into entry-time failures instead of silent downstream surprises.
- A `@dataclass(frozen=True)` config holds the pipeline's input/output contract in an immutable, repr-able object; every stage downstream reads from it without being able to mutate it.
- The `ingest` stage's contract is to deliver the raw corpus faithfully with declared dtypes, not to clean it; cleaning belongs to the next stage so each decision is explicit and testable.
- A typed ingest stage is the seam where a pipeline can be tested in isolation: swap the path in `WrangleConfig`, call `ingest`, assert shape and dtypes.

<div class="claude-handoff" data-exercise="exercises/module6/ingest-the-corpus/">

**Build It in Claude Code:** Add the `ingest` function and `WrangleConfig` dataclass to `exercises/module6/wrangle.py`, create the sample corpus fixture, assert the loaded DataFrame has 8 rows and the correct dtypes, and exit 0.

</div>
