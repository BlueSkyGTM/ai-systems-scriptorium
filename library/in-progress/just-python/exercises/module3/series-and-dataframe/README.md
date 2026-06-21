# Exercise: Series and DataFrame

**Goal:** Extend your existing `measure.py` with `frame_bytes`, a function that reports the true memory cost of a DataFrame, compares a numeric column to its equivalent ndarray, and proves the object-dtype overhead against a string column.

**Why:** Every eval table you ship is a DataFrame. Knowing before you load which columns carry the object-dtype tax is what keeps that table from silently doubling your memory budget.

## Steps

1. Open `exercises/module1/the-cost-of-a-python-list/measure.py`. Read its current state. You are extending this file, not starting a new one. Do not re-implement `list_bytes`, `array_bytes`, `time_sum`, or `broadcast_allocates`.

2. Add the following imports at the top of `measure.py` if they are not already there:

   ```python
   import numpy as np
   import pandas as pd
   ```

3. Implement `frame_bytes` at module level, after the existing functions:

   ```python
   def frame_bytes(df: "pd.DataFrame") -> dict[str, int]:
       """
       Report the true memory cost of a DataFrame using deep inspection.

       Returns a dict with keys:
         'total_bytes'    -- df.memory_usage(deep=True).sum()
         'index_bytes'    -- df.memory_usage(deep=True)['Index']
         per-column keys  -- df.memory_usage(deep=True)[col] for each col in df.columns
       """
   ```

   The function must:
   - Call `df.memory_usage(deep=True)` once and store the result.
   - Return a dict where the key `'total_bytes'` is `.sum()` of that result, the key `'index_bytes'` is the `'Index'` entry, and every column name maps to its own byte count.
   - Not modify the DataFrame.

4. Add a `run_frame_bytes()` driver that builds a small, fixed DataFrame in-script (no file I/O, no random seed needed), calls `frame_bytes`, prints a comparison table, and asserts the expected relationships:

   ```python
   def run_frame_bytes() -> None:
       df = pd.DataFrame({
           "model":  ["gpt-4o", "claude-3", "llama-3", "mistral"],
           "f1":     [0.91, 0.87, 0.94, 0.73],
           "tokens": [4096, 8192, 8192, 32768],
           "open":   [False, False, True, True],
       })

       stats = frame_bytes(df)

       # Equivalent numeric ndarray for the f1 column
       numeric_col = np.array([0.91, 0.87, 0.94, 0.73], dtype=np.float64)

       print("--- frame_bytes ---")
       print(f"total (deep):          {stats['total_bytes']:>8,} bytes")
       print(f"index:                 {stats['index_bytes']:>8,} bytes")
       for col in df.columns:
           print(f"  {col:<10}            {stats[col]:>8,} bytes  ({df[col].dtype})")
       print(f"f1 column (Series):    {stats['f1']:>8,} bytes")
       print(f"f1 equivalent ndarray: {numeric_col.nbytes:>8,} bytes")

       # The object-dtype string column must cost more than the float64 column
       assert stats["model"] > stats["f1"], \
           "object-dtype string column must be heavier than float64 column"

       # The float64 column must match the equivalent ndarray's buffer exactly
       assert stats["f1"] == numeric_col.nbytes, \
           "float64 Series column bytes must equal equivalent ndarray.nbytes"

       # Total must equal the sum of index + all column entries
       expected_total = stats["index_bytes"] + sum(stats[col] for col in df.columns)
       assert stats["total_bytes"] == expected_total, \
           "total_bytes must equal index_bytes plus all column bytes"

       print("assertions passed: object dtype is heavier; numeric column matches ndarray")
   ```

5. Call `run_frame_bytes()` inside the existing `if __name__ == "__main__":` block, after the existing assertions.

6. Run `python measure.py` from `exercises/module1/the-cost-of-a-python-list/`. Confirm it still exits 0 and the new lines appear after the prior output.

## Done When

`python measure.py` exits 0, prints the `frame_bytes` comparison table, and all three assertions pass:

- The `model` (object) column costs more bytes than the `f1` (float64) column.
- The `f1` column's byte count equals `np.array([...], dtype=np.float64).nbytes` (32 bytes for 4 values).
- `total_bytes` equals `index_bytes` plus the sum of the per-column counts.

No external dependencies beyond NumPy, pandas, and the standard library. Deterministic: the DataFrame is built from fixed literals, no random state.

Expected output shape (numeric and bool columns are exact; the object column's byte count varies by pandas version):

```
--- frame_bytes ---
total (deep):               424 bytes
index:                      132 bytes
  model                     224 bytes  (object)
  f1                         32 bytes  (float64)
  tokens                     32 bytes  (int64)
  open                        4 bytes  (bool)
f1 column (Series):          32 bytes
f1 equivalent ndarray:       32 bytes
assertions passed: object dtype is heavier; numeric column matches ndarray
```

Note: `index_bytes` includes the `RangeIndex` metadata overhead, which is why it appears larger than the column buffers. The `model` column cost varies by string length; the float64 and int64 columns are exactly 8 bytes per row.

## Stretch

Add a second block to `run_frame_bytes` that converts the `model` column to `category` dtype and remeasures:

```python
df_cat = df.copy()
df_cat["model"] = df_cat["model"].astype("category")
stats_cat = frame_bytes(df_cat)
print(f"model as object:   {stats['model']:>8,} bytes")
print(f"model as category: {stats_cat['model']:>8,} bytes")
assert stats_cat["model"] < stats["model"], \
    "category dtype must be cheaper than object dtype for repeated strings"
print("stretch passed: category dtype reduces repeated-string overhead")
```

This proves that the object-dtype tax disappears when you encode a low-cardinality string column as a categorical, the standard move for model-name or label columns in a production eval table.
