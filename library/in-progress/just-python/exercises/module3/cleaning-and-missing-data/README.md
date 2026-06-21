# Exercise: Cleaning and Missing Data

**Goal:** Build `clean_corpus.py`, a self-contained script that takes a messy DataFrame, deduplicates it, handles missing values, normalizes the text column, and asserts the output is clean, then exits with code 0.

**Why:** A NaN that reaches a metric, or a duplicate that reaches an eval, silently corrupts your numbers. This exercise is the mechanical core of every data pipeline you will build before a model trains.

## Setup

No external downloads. Build the messy DataFrame in-script:

```python
import pandas as pd
import numpy as np

raw = pd.DataFrame({
    "id":    [1, 2, 2, 3, 4, 5],
    "label": ["pos", "neg", "neg", "pos", "neu", "neg"],
    "text":  [
        "  Great Product!  ",
        "TERRIBLE service.",
        "TERRIBLE service.",
        "Works FINE.",
        None,
        "  Another  bad  experience!  ",
    ],
    "score": [0.9, 0.2, 0.2, np.nan, 0.5, 0.15],
})
```

The frame has three problems: one duplicate row (id=2 appears twice), one null text entry (id=4), and one null score (id=3). They are in different rows on purpose: working through them in order is the exercise.

## Steps

1. **Audit the raw frame.** Print shape, duplicate count, and null counts per column before touching anything.

2. **Drop duplicate rows.** Use `drop_duplicates()` and keep the first occurrence. Assert the row count dropped by exactly 1 (the id=2 duplicate).

   ```python
   deduped = raw.drop_duplicates()
   assert len(deduped) == len(raw) - 1, f"expected 1 duplicate removed, got {len(raw) - len(deduped)}"
   ```

3. **Handle the missing text.** Drop rows where `text` is null. State in a comment why you drop rather than fill. Assert no nulls remain in the `text` column.

   ```python
   deduped = deduped.dropna(subset=["text"])
   assert deduped["text"].isna().sum() == 0, "null text survived"
   ```

4. **Fill the missing score.** Fill the null in the `score` column with the column mean. Assert no nulls remain in `score`.

   ```python
   deduped["score"] = deduped["score"].fillna(deduped["score"].mean())
   assert deduped["score"].isna().sum() == 0, "null score survived"
   ```

5. **Normalize the text column.** Apply the vectorized chain: strip whitespace, lowercase, strip punctuation (`!?.,.`), collapse multiple spaces, strip again. Use the `.str` accessor, not `apply` or a Python loop.

   ```python
   deduped["text_clean"] = (
       deduped["text"]
       .str.strip()
       .str.lower()
       .str.replace(r"[!?.,]", "", regex=True)
       .str.replace(r"\s+", " ", regex=True)
       .str.strip()
   )
   ```

6. **Assert the normalized text.** Check that no uppercase letters remain in any non-null text entry:

   ```python
   assert deduped["text_clean"].dropna().str.match(r"^[^A-Z]*$").all(), \
       "uppercase letters survived normalization"
   ```

7. **Assert final shape and print a structured report.** The clean frame must have shape `(4, 5)` (4 rows after removing 1 duplicate and 1 null-text row from the original 6, original 4 columns plus `text_clean`):

   ```python
   assert deduped.shape == (4, 5), f"expected (4, 5), got {deduped.shape}"

   print("[PASS] dedup: 1 duplicate removed (id=2)")
   print("[PASS] dropna: null text removed (id=4)")
   print("[PASS] fillna: score null filled with column mean (id=3)")
   print("[PASS] text normalized: no uppercase, no extra whitespace")
   print(f"[PASS] final shape: {deduped.shape}")
   ```

## Done When

All assertions pass, the `[PASS]` report prints, and the script exits with code 0. Run it with:

```sh
python clean_corpus.py
```

No dependencies beyond pandas and numpy. The in-script DataFrame makes every run deterministic.

## Stretch

Reshape the clean frame into a long eval summary and back. Add a `split` column (`"train"` for the first row, `"eval"` for the rest), then:

1. Build a wide summary table: one row per `split`, columns `mean_score` and `row_count`.
2. Melt it to long format with `melt(id_vars=["split"], var_name="metric", value_name="value")`.
3. Assert the melted frame has shape `(4, 3)` (2 splits x 2 metrics).
4. Pivot it back to wide with `pivot(index="split", columns="metric", values="value")` and assert you recover the original shape `(2, 2)`.

```python
summary = deduped.groupby("split").agg(
    mean_score=("score", "mean"),
    row_count=("id", "count"),
).reset_index()

long = summary.melt(id_vars=["split"], var_name="metric", value_name="value")
assert long.shape == (4, 3), f"expected (4, 3), got {long.shape}"

wide = long.pivot(index="split", columns="metric", values="value")
wide.columns.name = None
assert wide.shape == (2, 2), f"expected (2, 2), got {wide.shape}"
print("[PASS] melt/pivot round-trip: shapes match")
```
