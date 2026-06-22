# Exercise: Clean and Deduplicate

**Goal:** Add the `clean` stage to the shared `wrangle.py` pipeline. Run `clean(ingest(sample))`
against the sample corpus, assert the before/after row counts and null state, print a structured
report, and exit with code 0.

**Why:** Every metric your pipeline computes is only as clean as the rows that reached it. Shipping
a broken `clean` function is a silent data contract violation: the smoke gate will not catch it, but
a model trained on the output will reflect it.

## Setup

L1 created `exercises/module6/wrangle.py` with `WrangleConfig`, the sample corpus, and `ingest`.
Open it and read its current state before adding anything. You are continuing a build, not starting
one.

The sample corpus in `wrangle.py` looks like this (eight rows, three problems):

```python
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class WrangleConfig:
    input_path: str
    output_path: str
    required_cols: tuple = ("id", "text", "label")
    dedup_key: str = "id"

SAMPLE = pd.DataFrame({
    "id":    [1, 2, 2, 3, 4, 5, 6, 7],
    "text":  [
        "Great Product ",
        "terrible service",
        "terrible service",   # duplicate id=2
        "Works Fine",
        None,                 # null text id=4
        " Another product ",
        "FAST delivery",
        "slow response  ",
    ],
    "label": ["pos", "neg", "neg", "pos", "neu", "neg", "pos", "neg"],
    "score": [0.90, 0.20, 0.20, np.nan, 0.50, 0.15, 0.80, 0.60],
})

def ingest(path) -> pd.DataFrame:
    """L1 stage: typed JSONL load. Returns SAMPLE for the smoke gate."""
    return SAMPLE.copy()
```

## Steps

1. **Print the raw frame.** Before writing any code, print the shape, the duplicate count on `id`,
   and the null counts per column. Write what you expect before you run it.

2. **Add `clean(df)` to `wrangle.py`.** The function must, in this order:

   - Drop duplicates on `"id"`.
   - Drop rows where `"text"` is null.
   - Fill null `"score"` values with the column mean.
   - Normalize `"text"` with `.str.strip().str.lower()`.
   - Return the cleaned frame.

   ```python
   def clean(df: pd.DataFrame) -> pd.DataFrame:
       # your implementation here
       ...
   ```

   Use the `.str` accessor for step 4. No `apply`, no loop.

3. **Run the pipeline and assert correctness.**

   ```python
   raw = ingest("smoke")
   print("=== BEFORE ===")
   print(f"rows: {raw.shape[0]}")
   print(f"dup id count: {raw.duplicated(subset=['id']).sum()}")
   print(f"null text: {raw['text'].isna().sum()}")
   print(f"null score: {raw['score'].isna().sum()}")

   result = clean(raw)
   print("\n=== AFTER ===")
   print(result[["id", "text", "score"]].to_string())

   # Row count: 8 in, 6 out (1 dup dropped, 1 null-text dropped)
   assert result.shape[0] == 6, f"expected 6 rows, got {result.shape[0]}"

   # No nulls in text
   assert result["text"].isna().sum() == 0, "null text survived"

   # No nulls in score
   assert result["score"].isna().sum() == 0, "null score survived"

   # Text is normalized: all lowercase, no leading/trailing whitespace
   assert result["text"].str.strip().eq(result["text"]).all(), "whitespace survived"
   assert not result["text"].str.contains(r"[A-Z]", regex=True).any(), "uppercase survived"

   print("\n[PASS] row count: 8 → 6")
   print("[PASS] zero null text")
   print("[PASS] zero null score (filled with mean)")
   print("[PASS] text normalized: lowercase + stripped")
   ```

## Done When

All assertions pass, the `[PASS]` lines print, and the script exits with code 0. Run it with:

```sh
python wrangle.py
```

No dependencies beyond pandas and numpy.

## Stretch

The smoke gate confirms `clean` is correct for the locked sample. Now stress-test the order
dependency the lesson describes.

Add a second function, `clean_wrong_order(df)`, that reverses steps 2 and 3: fill `score` first,
then drop null text. Assert that the mean score it computes differs from the one `clean` produces,
and print both means so the difference is visible.

```python
def clean_wrong_order(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["id"])
    df["score"] = df["score"].fillna(df["score"].mean())  # fill BEFORE dropna
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].str.strip().str.lower()
    return df

result_wrong = clean_wrong_order(ingest("smoke"))
result_right = clean(ingest("smoke"))

mean_wrong = result_wrong["score"].mean()
mean_right = result_right["score"].mean()

print(f"\nmean score (correct order): {mean_right:.4f}")
print(f"mean score (wrong order):   {mean_wrong:.4f}")
assert mean_wrong != mean_right, "means should differ when null-text row participates in fill"
print("[PASS] order matters: means diverge when null-text row participates in fillna")
```

This is the concrete proof of why order is load-bearing, not just convention.
