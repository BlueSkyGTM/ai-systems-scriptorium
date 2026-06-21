# Clean and Deduplicate

A duplicate that reaches an embedding model and a null that reaches a metric share the same
property: neither announces itself. The `clean` stage is the one place in `wrangle.py` where you
decide what the model is allowed to see.

## What You Build

You build the `clean` function that slots into the shared `wrangle.py` pipeline. It takes the
DataFrame that `ingest` loaded, removes noise in a fixed order, and returns a frame the rest of the
pipeline can trust.

## The Pipeline's Shape

`wrangle.py` composes four stages in sequence. `ingest` (L1) loads raw JSONL into a typed
DataFrame. `clean` (this lesson) scrubs it. `reshape_and_validate` (L3) enforces schema rules.
`emit` (L4) writes the result. You build `clean`; the other three are given.

The corpus the pipeline receives looks like this before cleaning:

```
   id  text                  label   score
0   1  "Great Product "      pos     0.90
1   2  "terrible service"    neg     0.20
2   2  "terrible service"    neg     0.20   ← duplicate id
3   3  "Works Fine"          pos     NaN    ← missing score
4   4  None                  neu     0.50   ← missing text
5   5  " Another product "   neg     0.15
6   6  "FAST delivery"       pos     0.80
7   7  "slow response  "     neg     0.60
```

Eight rows in, six rows out. The two that fall: the duplicate on `id=2`, and the null-text on `id=4`.

## The Four Steps, in Order

The function signature is fixed for the smoke gate downstream:

```python
def clean(df: pd.DataFrame) -> pd.DataFrame:
```

**Step 1: Drop duplicates on the key.**

```python
df = df.drop_duplicates(subset=["id"])
```

Before dedup the corpus has eight rows. After, it has seven. The duplicate on `id=2` is gone; the
first occurrence stays.

Why first? When both copies carry identical data, it does not matter. In real pipelines duplicates
differ by timestamp or score, so you pass `keep="first"` or `keep="last"` explicitly and comment
why. Here the two copies are identical, so first is fine.

**Step 2: Drop rows where the required text is null.**

```python
df = df.dropna(subset=["text"])
```

Seven rows become six. The row for `id=4` is gone. You cannot impute a null text column without
inventing signal the model will learn; dropping is the only honest choice. M3 covered this decision
in detail. The point here is ordering: if you filled score nulls before dropping text nulls, you
would compute a mean over a row you are about to delete. Dedup before dropna, dropna before fillna.

**Step 3: Fill missing numeric scores with the column mean.**

```python
df["score"] = df["score"].fillna(df["score"].mean())
```

Before this line, `id=3` carries a null score. After it, that cell holds the mean of the five
non-null scores in the surviving frame. The mean is computed from the already-cleaned rows, so the
deleted duplicate and the null-text row do not influence it.

`fillna` accepts a scalar, a per-column dict, or a fill strategy. Column mean is the standard
sentinel for a continuous quality score with no structural reason to be missing.

**Step 4: Normalize the text column with the `.str` accessor.**

```python
df["text"] = df["text"].str.strip().str.lower()
```

You covered the `.str` accessor in M5: vectorized string operations over a Series, no Python loop,
no `apply`. Here `strip` removes leading and trailing whitespace, `lower` lowercases every
character. Both run across all six surviving rows in one pass.

"Great Product " becomes "great product". "FAST delivery" becomes "fast delivery". The tokenizer
that receives this corpus sees one representation per concept, not two.

Microsoft's data-preparation guidance calls this the clean-and-normalize step and flags it as the
required first stage before chunking or embedding: even basic normalization significantly improves
embedding quality because models are sensitive to noise ([Prepare Data for AI App and Agent
Development for Azure HorizonDB](https://learn.microsoft.com/azure/horizondb/ai/ai-data-preparation)).
The same principle applies at every scale.

**The complete function:**

```python
def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["id"])          # dedup on key
    df = df.dropna(subset=["text"])                 # drop unrecoverable nulls
    df["score"] = df["score"].fillna(df["score"].mean())  # fill numeric sentinel
    df["text"] = df["text"].str.strip().str.lower() # normalize text
    return df
```

## Why the Order Is Load-Bearing

Reverse steps 1 and 3 and the mean shifts: you compute it over eight rows instead of seven, and the
duplicate contributes twice. Reverse steps 2 and 3 and the mean includes the about-to-be-deleted
null-text row's score. The gate downstream is deterministic because this order is locked. Change it
and the assertions break.

## Seam Line

Every metric your pipeline computes is only as clean as the rows that reached it; the `clean` stage
is not a preprocessing chore but a commitment about what counts as data.

## Core Concepts

- Dedup before dropna before fillna: the order is not arbitrary. Each step removes or imputes from
  the frame the next step sees, so reversing the order shifts the results.
- Drop null text, do not fill it. Imputing a text column fabricates training signal; the model
  learns from the fiction you inserted.
- Fill null numeric scores with the column mean computed over surviving rows only, so deleted
  duplicates and null-text rows do not skew the sentinel.
- `.str.strip().str.lower()` is the vectorized normalization idiom from M5. It runs once over the
  whole column; `apply(lambda x: x.lower())` runs once per row and is the slower pattern.

<div class="claude-handoff" data-exercise="exercises/module6/clean-and-deduplicate/">

**Build It in Claude Code:** Add the `clean` stage to the shared `wrangle.py` and run it against
the sample corpus, asserting the before/after counts and null state. Open the repo and run the
exercise for this lesson.

</div>
