# Exercise: Reading and Writing AI Formats

**Goal:** Build `io_formats.py`, a self-contained script that constructs a typed DataFrame, round-trips it through CSV, JSONL, and Parquet in a temporary directory, asserts what survives each round trip, and confirms Parquet produces a smaller file than CSV.

**Why:** An AI pipeline engineer who cannot control dtype fidelity across format boundaries spends debugging time that belongs to building. This exercise makes the dtype contract concrete and machine-verifiable before your data gets large enough to hide the cost.

## Steps

### 1. Build the Typed DataFrame

Create a DataFrame with four columns that cover the dtypes most likely to surprise you across formats: a 32-bit integer label, a 32-bit float score, a datetime timestamp, and a text column.

```python
import pandas as pd
import numpy as np
import tempfile
import os

df = pd.DataFrame({
    "text":      ["classify this", "another sample", "third record",
                  "fourth record", "fifth record"],
    "label":     pd.array([1, 0, 1, 0, 1], dtype="int32"),
    "score":     pd.array([0.91, 0.43, 0.78, 0.55, 0.88], dtype="float32"),
    "timestamp": pd.to_datetime([
        "2024-01-01", "2024-01-02", "2024-01-03",
        "2024-01-04", "2024-01-05",
    ]),
})
```

Print the original dtypes so you have a baseline to compare against.

### 2. Write and Read CSV

Write to a temp directory and read back without any dtype hints first. Print the dtypes you get back; they will differ from the originals. Then read again with `dtype=` and `parse_dates=` to restore them.

```python
tmpdir = tempfile.mkdtemp()
csv_path = os.path.join(tmpdir, "eval.csv")

df.to_csv(csv_path, index=False)
df_csv_raw = pd.read_csv(csv_path)

# Row count must be preserved even without dtype recovery
assert len(df_csv_raw) == len(df), "CSV row count mismatch"

# Show the type degradation
print("CSV dtypes (raw read, no hints):")
print(df_csv_raw.dtypes)

# Now recover the types
df_csv = pd.read_csv(
    csv_path,
    dtype={"label": "int32", "score": "float32"},
    parse_dates=["timestamp"],
)

assert df_csv["label"].dtype == np.dtype("int32"), "label must be int32 after coercion"
assert df_csv["score"].dtype == np.dtype("float32"), "score must be float32 after coercion"
assert pd.api.types.is_datetime64_any_dtype(df_csv["timestamp"]), \
    "timestamp must be datetime64 after parse_dates"
assert len(df_csv) == len(df), "CSV row count must be preserved"

print("[PASS] CSV: row count preserved, dtypes recovered with explicit hints")
```

### 3. Write and Read JSONL

Write using `orient="records"` and `lines=True`. Read back with `lines=True`. Assert that the row count survives and that `int32` and `float32` are widened (not preserved), but `timestamp` survives as `datetime64`.

```python
jsonl_path = os.path.join(tmpdir, "corpus.jsonl")

df.to_json(jsonl_path, orient="records", lines=True)
df_jsonl = pd.read_json(jsonl_path, lines=True)

assert len(df_jsonl) == len(df), "JSONL row count mismatch"

# int32 and float32 do NOT survive JSONL without explicit coercion
assert df_jsonl["label"].dtype != np.dtype("int32"), \
    "label must NOT be int32 after JSONL round trip (expected widening)"
assert df_jsonl["score"].dtype != np.dtype("float32"), \
    "score must NOT be float32 after JSONL round trip (expected widening)"

# datetime survives because pandas reads epoch milliseconds as datetime64
assert pd.api.types.is_datetime64_any_dtype(df_jsonl["timestamp"]), \
    "timestamp must survive JSONL as datetime64"

print("[PASS] JSONL: row count preserved, int32/float32 widened as expected, datetime64 survived")
```

### 4. Write and Read Parquet (pyarrow required)

Guard the Parquet block: if `pyarrow` is not installed, print a clear message and skip this section. The CSV and JSONL asserts above must pass unconditionally.

```python
try:
    import pyarrow  # noqa: F401

    parquet_path = os.path.join(tmpdir, "features.parquet")
    df.to_parquet(parquet_path, engine="pyarrow", index=False)
    df_parquet = pd.read_parquet(parquet_path, engine="pyarrow")

    assert len(df_parquet) == len(df), "Parquet row count mismatch"
    assert df_parquet["label"].dtype == np.dtype("int32"), \
        "label must be int32 after Parquet round trip"
    assert df_parquet["score"].dtype == np.dtype("float32"), \
        "score must be float32 after Parquet round trip"
    assert pd.api.types.is_datetime64_any_dtype(df_parquet["timestamp"]), \
        "timestamp must be datetime64 after Parquet round trip"

    # Parquet must be smaller than CSV for the same frame
    csv_size     = os.path.getsize(csv_path)
    parquet_size = os.path.getsize(parquet_path)
    assert parquet_size < csv_size, (
        f"Parquet ({parquet_size} bytes) must be smaller than CSV ({csv_size} bytes)"
    )

    print(f"[PASS] Parquet: row count preserved, all dtypes exact, "
          f"file size {parquet_size} bytes vs CSV {csv_size} bytes")

except ImportError:
    print("[SKIP] Parquet block skipped: pyarrow not installed "
          "(pip install pyarrow to enable)")
```

Install pyarrow if needed:

```sh
pip install pyarrow
```

### 5. Print a Summary and Exit 0

```python
print()
print("=== Round-trip summary ===")
print(f"Original dtypes:\n{df.dtypes.to_string()}")
print()
print("CSV raw dtypes (no hints):")
print(df_csv_raw.dtypes.to_string())
print()
print("JSONL dtypes:")
print(df_jsonl.dtypes.to_string())
```

## Done When

All CSV and JSONL assertions pass, the summary prints, and the script exits with code 0. If `pyarrow` is installed, the Parquet assertions pass too and the file-size comparison is included in the output. Run with:

```sh
python io_formats.py
```

No external dependencies beyond `pandas`, `numpy`, and (optionally) `pyarrow`. The DataFrame is constructed in-script; no external files are needed.

## Stretch

Add a column-subset read for Parquet. After the Parquet round trip, read back only the `text` and `score` columns using the `columns=` parameter. Assert the resulting DataFrame has exactly 2 columns and that `score` is still `float32`. Then measure how long a full read takes versus a column-subset read for a larger frame (use `pd.concat([df] * 1000)` to grow the data) and print the ratio:

```python
import time

big_df = pd.concat([df] * 1000, ignore_index=True)
big_path = os.path.join(tmpdir, "big_features.parquet")
big_df.to_parquet(big_path, engine="pyarrow", index=False)

t0 = time.perf_counter()
_ = pd.read_parquet(big_path)
full_time = time.perf_counter() - t0

t0 = time.perf_counter()
_ = pd.read_parquet(big_path, columns=["text", "score"])
subset_time = time.perf_counter() - t0

print(f"[STRETCH] full read: {full_time*1000:.1f}ms, "
      f"subset read: {subset_time*1000:.1f}ms, "
      f"ratio: {full_time/subset_time:.1f}x")
```

The ratio tells you why column-subset reads matter at scale; CSV has no equivalent path.
