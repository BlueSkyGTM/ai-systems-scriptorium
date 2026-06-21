# Exercise: Reshape and Validate

**Goal:** Add `reshape_and_validate` to `exercises/module6/wrangle.py` and prove it works as a gate: the passing case returns a validated frame; the failing cases raise `ValueError` with a precise message.

**Why:** The pipeline's `ingest` and `clean` stages (L1 and L2) are already in `wrangle.py`. This stage is the acceptance gate before `emit` writes Parquet. A pipeline without this gate tells you "it ran" and nothing else. Adding it is what converts a hopeful script into a defensible artifact.

## Before You Start

Open `exercises/module6/wrangle.py` and read the current state. `ingest` and `clean` are already built. You are adding the third stage. Do not rewrite the stages that exist.

## Steps

1. Read the `WrangleConfig` dataclass at the top of `wrangle.py`. Note `required_cols` and `dedup_key`.

2. Implement `reshape_and_validate(df, config)` directly below `clean` in `wrangle.py`. The function must:
   - Check that every column in `config.required_cols` exists; raise `ValueError` listing the missing ones if not.
   - Select columns in the order: `list(config.required_cols) + ["score"]`.
   - Check that no required column contains a null; raise `ValueError` naming the offending column(s) and counts if any do.
   - Check that dtypes match the expected schema below; raise `ValueError` naming the column and actual dtype if any mismatch.
   - Return the validated frame.

   Expected dtypes, checked with `pandas.api.types` predicates so the gate survives pandas version differences (a Parquet round-trip can return text as the newer `str` dtype, not `object`):

   ```python
   import pandas.api.types as pat
   checks = {
       "id":    pat.is_integer_dtype,
       "text":  pat.is_string_dtype,
       "label": pat.is_string_dtype,
       "score": pat.is_float_dtype,
   }
   ```

3. Write `smoke.py` (in `exercises/module6/reshape-and-validate/`) that:

   a. Builds a deterministic six-row sample:

   ```python
   import pandas as pd
   import numpy as np
   import sys
   sys.path.insert(0, "exercises/module6")

   from wrangle import ingest, clean, reshape_and_validate, WrangleConfig

   sample_records = [
       {"id": 1, "text": "clear explanation", "label": "pos", "score": 0.92},
       {"id": 2, "text": "wrong answer",      "label": "neg", "score": 0.15},
       {"id": 3, "text": "mostly correct",    "label": "pos", "score": 0.71},
       {"id": 4, "text": "great detail",      "label": "pos", "score": 0.88},
       {"id": 5, "text": "too vague",         "label": "neg", "score": 0.34},
       {"id": 6, "text": "on target",         "label": "pos", "score": 0.79},
   ]

   raw = pd.DataFrame(sample_records)
   config = WrangleConfig(input_path="", output_path="")
   ```

   b. Runs the full pipeline through `reshape_and_validate`:

   ```python
   df_clean = clean(raw)
   validated = reshape_and_validate(df_clean, config)
   ```

   c. Asserts the passing case:

   ```python
   assert validated.shape == (6, 4), f"expected (6, 4), got {validated.shape}"
   assert list(validated.columns) == ["id", "text", "label", "score"]
   assert validated[["id", "text", "label"]].isna().sum().sum() == 0
   import pandas.api.types as pat
   assert pat.is_integer_dtype(validated["id"])
   assert pat.is_string_dtype(validated["text"])
   assert pat.is_string_dtype(validated["label"])
   assert pat.is_float_dtype(validated["score"])
   print("[PASS] validated frame: 6 rows, correct columns and dtypes, no nulls in required columns")
   ```

   d. **Negative case (required):** builds a frame missing the `text` column and asserts `reshape_and_validate` raises:

   ```python
   import traceback

   bad_frame = raw.drop(columns=["text"])
   try:
       reshape_and_validate(bad_frame, config)
       print("[FAIL] expected ValueError for missing column; none raised")
       sys.exit(1)
   except ValueError as e:
       print(f"[PASS] missing column raises ValueError: {e}")
   ```

   e. **Second negative case:** injects a null into a required column and asserts the gate catches it:

   ```python
   null_frame = df_clean.copy()
   null_frame.loc[2, "label"] = None
   try:
       reshape_and_validate(null_frame, config)
       print("[FAIL] expected ValueError for null in required column; none raised")
       sys.exit(1)
   except ValueError as e:
       print(f"[PASS] null in required column raises ValueError: {e}")
   ```

   f. Exit 0 on success.

4. Run the script:

   ```sh
   python exercises/module6/reshape-and-validate/smoke.py
   ```

   Expected output:

   ```
   [PASS] validated frame: 6 rows, correct columns and dtypes, no nulls in required columns
   [PASS] missing column raises ValueError: Missing required columns: ['text']
   [PASS] null in required column raises ValueError: Null values in required columns: {'label': 1}
   ```

## Done When

All three `[PASS]` lines print and the script exits with code 0. No external dependencies beyond pandas and numpy.

## Stretch

The dtype check in `reshape_and_validate` catches a mismatch after the frame is selected. But what if `id` arrives as `object` dtype from a poorly-typed JSON source? Add a fourth negative case: build a frame where `id` is `object` dtype (e.g., `pd.Series(["1", "2", "3", "4", "5", "6"])`), pass it through `reshape_and_validate`, and assert the dtype error fires. Then add a one-line coercion to `reshape_and_validate` that converts `id` to `int64` before the dtype check so the cast-and-validate path also exits 0:

```python
# Before dtype check, coerce id if possible
if "id" in df.columns and str(df["id"].dtype) != "int64":
    try:
        df = df.copy()
        df["id"] = df["id"].astype("int64")
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Cannot coerce 'id' to int64: {exc}") from exc
```

Assert the coerced frame passes validation. Then build a frame with a non-numeric `id` (e.g., `"abc"`) and assert the coercion itself raises `ValueError`.
