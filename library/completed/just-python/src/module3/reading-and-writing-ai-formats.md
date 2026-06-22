# Reading and Writing AI Formats

Every AI pipeline moves data through exactly three formats, and the one you reach for by default determines how much time you spend debugging dtype surprises at 2 AM. CSV loses type information the moment you write it. JSONL preserves structure but not column types. Parquet keeps both, compresses the data, and lets you load a single column out of a ten-million-row file without touching the rest.

## What You Build

You build `io_formats.py`, a script that writes a typed DataFrame to CSV, JSONL, and Parquet, reads each back, prints the dtypes before and after each round trip, and confirms what survived.

## The Three Formats

An AI pipeline uses these three formats for different reasons, at different stages.

**CSV** is the interchange default: the eval results table you hand to a reviewer, the split your training harness reads, the dataset someone ships you in a zip file. Every tool reads it. No tool preserves your dtypes.

**JSONL** (JSON Lines) is the corpus format: one JSON object per line, no enclosing array. Your annotation files are JSONL. Your fine-tuning dataset is JSONL. Your retrieval-augmentation source documents are JSONL. The record-per-line layout maps directly onto the made-with-ml `datasets/dataset.csv` pattern, which treats every row as an independent labeled record.

**Parquet** is the feature store and checkpoint format: columnar, typed, compressed. When your pipeline graduates from a few thousand rows to millions, Parquet is what you reach for because it lets you read one column without deserializing the rest.

Microsoft Learn's "Make Data Available in Azure Machine Learning" module shows these same tabular formats (CSV, JSON, Parquet) registered as versioned data assets in a production pipeline ([learn.microsoft.com/training/modules/make-data-available-azure-machine-learning](https://learn.microsoft.com/training/modules/make-data-available-azure-machine-learning/)).

## Reading and Writing CSV

Start with a typed DataFrame that mirrors an eval results table:

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "text":      ["classify this", "another sample", "third record"],
    "label":     pd.array([1, 0, 1], dtype="int32"),
    "score":     pd.array([0.91, 0.43, 0.78], dtype="float32"),
    "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
})

print(df.dtypes)
# text                object
# label                int32
# score               float32
# timestamp    datetime64[ns]
```

Write it and read it back:

```python
df.to_csv("eval.csv", index=False)
df_csv = pd.read_csv("eval.csv")

print(df_csv.dtypes)
# text         object
# label         int64   <-- int32 is gone
# score        float64  <-- float32 is gone
# timestamp     object  <-- datetime is gone
```

The round trip loses all three numeric dtypes and the datetime. CSV carries no schema: it is a text file with commas. When you read it back, pandas infers types from the character sequences it sees, and it guesses conservatively (`int64`, `float64`, `object`). To recover your types, pass `dtype` and `parse_dates` explicitly:

```python
df_csv = pd.read_csv(
    "eval.csv",
    dtype={"label": "int32", "score": "float32"},
    parse_dates=["timestamp"],
)

print(df_csv.dtypes)
# text                object
# label                int32
# score               float32
# timestamp    datetime64[ns]
```

The `dtype` dict maps column names to types. `parse_dates` accepts a list of column names to coerce from string to `datetime64`. You own the schema when you read CSV; the file does not carry it for you. Microsoft Learn's "Explore and Analyze Data with Python" module walks through loading and inspecting tabular data with Pandas this way ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/2-explore-data-numpy-pandas)).

## Reading and Writing JSONL

JSONL writes each row as a JSON object on its own line. Pandas calls this `orient="records"` combined with `lines=True`:

```python
df.to_json("corpus.jsonl", orient="records", lines=True)
```

The file looks like this:

```
{"text":"classify this","label":1,"score":0.9100000262260437,"timestamp":1704067200000}
{"text":"another sample","label":0,"score":0.4300000071525574,"timestamp":1704153600000}
{"text":"third record","label":1,"score":0.7799999713897705,"timestamp":1704240000000}
```

Two things to notice. First, `score` has expanded: the `float32` value `0.91` cannot be represented exactly in JSON's floating-point encoding, so pandas serializes it at full `float64` precision. Second, `timestamp` is a millisecond epoch integer, not an ISO string; pandas serializes datetimes as integers by default.

Read it back:

```python
df_jsonl = pd.read_json("corpus.jsonl", lines=True)

print(df_jsonl.dtypes)
# text         object
# label         int64   <-- int32 gone
# score        float64  <-- float32 gone
# timestamp    datetime64[ns]  <-- this one survives, pandas infers it
```

JSONL preserves the datetime (because pandas interprets epoch milliseconds as `datetime64`) but loses numeric subtypes just like CSV does. For a corpus, this is acceptable: the structure survives, and the text is what matters. For a typed feature store, it is not.

## Reading and Writing Parquet

Parquet encodes the schema alongside the data. Your dtypes do not need to survive inference; they are written into the file's metadata and restored exactly on read. The engine that makes this work with pandas is `pyarrow` (`pip install pyarrow`):

```python
df.to_parquet("features.parquet", engine="pyarrow", index=False)
df_parquet = pd.read_parquet("features.parquet", engine="pyarrow")

print(df_parquet.dtypes)
# text                object
# label                int32   <-- exact
# score               float32  <-- exact
# timestamp    datetime64[ns]  <-- exact
```

All four dtypes survive intact. The file is also smaller: the pandas docs note that Parquet uses columnar compression, which means a column of repeated `int32` values compresses far more aggressively than the same values encoded as ASCII digits in a CSV row. For a 3-row frame the size difference is negligible; at a million rows it is the difference between a 40 MB file and a 4 MB file.

Parquet also supports column-subset reads. If your feature store has 200 columns and a downstream model needs only 3, you pull those 3 without deserializing the rest:

```python
subset = pd.read_parquet("features.parquet", columns=["text", "score"])
print(subset.shape)    # (3, 2)
print(subset.dtypes)
# text      object
# score    float32
```

CSV has no equivalent. Reading 3 columns from a CSV still parses every byte of every row.

## The Round-Trip Discipline

Before you commit a format choice, trace what survives the round trip for your specific dtypes:

| Format | `int32` | `float32` | `datetime64` | Column subset read |
|--------|---------|-----------|--------------|-------------------|
| CSV    | No (needs `dtype=`) | No (needs `dtype=`) | No (needs `parse_dates=`) | No |
| JSONL  | No | No | Yes (epoch ms) | No |
| Parquet | Yes | Yes | Yes | Yes |

The rule is: use the format that matches what you need to preserve, not the one that is most convenient to produce. Your eval table ships as CSV because every reviewer can open it. Your annotated corpus ships as JSONL because every annotation tool reads it. Your feature store ships as Parquet because memory and speed matter at scale, and nothing downstream should be re-inferring types from bytes.

Format selection is a memory-and-speed contract with your pipeline, not a file extension you pick at random.

## Core Concepts

- CSV serializes data as text and carries no schema; every numeric and datetime dtype must be explicitly declared on `read_csv` via `dtype=` and `parse_dates=`, or pandas infers conservatively and widens types.
- JSONL writes one JSON object per line using `orient="records", lines=True` and is the standard corpus format; it preserves structure but not numeric subtypes, so `int32` and `float32` return as `int64` and `float64`.
- Parquet encodes the DataFrame schema in the file's metadata and restores all dtypes exactly on read, including `int32`, `float32`, and `datetime64`; it is the format you choose once data is big and column-subset reads matter.
- Each format has a natural pipeline role: CSV for eval interchange, JSONL for corpora and annotation, Parquet for feature stores and anything that needs typed round trips at scale.

<div class="claude-handoff" data-exercise="exercises/module3/reading-and-writing-ai-formats/">

**Build It in Claude Code:** Build `io_formats.py`, a self-contained script that round-trips a typed DataFrame through CSV, JSONL, and Parquet, asserts dtype behavior at each step, and confirms Parquet is smaller than CSV for the same data.

</div>
