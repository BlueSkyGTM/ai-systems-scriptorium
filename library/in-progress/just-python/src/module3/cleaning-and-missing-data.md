# Cleaning and Missing Data

The gap between a raw scrape and a training set is not a formatting problem. It is a modeling decision: every row you leave in reaches the model, and every NaN that survives to a metric silently corrupts your numbers.

## The Artifact

You build `clean_corpus.py`: a script that takes a messy DataFrame of raw text examples, deduplicates it, handles missing values, reshapes an eval summary table, and normalizes the text column, then asserts the output is clean.

## Drop Duplicates First

Duplicate rows in a training set inflate apparent class frequency. Duplicates in an eval set let the same example vote twice. Catch them before anything else.

```python
import pandas as pd
import numpy as np

raw = pd.DataFrame({
    "id":    [1, 2, 2, 3, 4, 4],
    "label": ["positive", "negative", "negative", "positive", "neutral", "neutral"],
    "text":  ["Great product", "Terrible", "Terrible", "Works fine", None, "Ok product"],
})

print("Before dedup:", raw.shape)          # (6, 3)
print(raw.duplicated().sum(), "duplicates")  # 2
```

`duplicated()` returns a boolean Series: `True` for every row that is a repeat of an earlier one. The default keeps the first occurrence.

```python
clean = raw.drop_duplicates()
print("After dedup:", clean.shape)         # (4, 3)
```

If you need to drop on a subset of columns (same `id` counts as duplicate regardless of text), pass `subset`:

```python
clean = raw.drop_duplicates(subset=["id"])
```

The choice of `keep` (`"first"`, `"last"`, or `False` to drop all copies) is a data decision, not a default. State it in a comment so the next person reading the pipeline knows why.

## Handle Missing Values

After dedup, audit the nulls:

```python
print(clean.isna().sum())
# id       0
# label    0
# text     1
```

Now comes the decision. `dropna` removes rows with any null; `fillna` replaces them. They are not equivalent, and the right answer depends on the data:

- Drop when the null column is the target or when imputing would fabricate signal. A text column with `None` cannot be imputed without inventing content; drop the row.
- Fill when a numeric feature is missing at random and a sensible default (zero, column mean) exists without introducing bias.

For a text corpus, drop:

```python
clean = clean.dropna(subset=["text"])
print("After dropna:", clean.shape)        # (3, 3)
assert clean["text"].isna().sum() == 0
```

For a numeric score column with a known sentinel, fill:

```python
scores = pd.Series([0.9, np.nan, 0.7, np.nan, 0.85])
filled = scores.fillna(scores.mean())
print(filled)
```

`fillna` accepts a scalar, a dict keyed by column name, or a forward/backward fill strategy (`ffill`, `bfill`). The strategy matters: forward-filling a time-ordered label column is reasonable; forward-filling a shuffled corpus is not. Microsoft Learn's "Explore and Analyze Data with Python" module covers detecting and handling missing values in real-world tabular data ([learn.microsoft.com/training/modules/explore-analyze-data-with-python](https://learn.microsoft.com/training/modules/explore-analyze-data-with-python/6-examine-real-world-data)).

## Reshape an Eval Table

Eval results often arrive wide: one column per metric, one row per model. To compare models across metrics with groupby or plotting, you need long format. `melt` converts wide to long.

Start with a wide eval summary:

```python
eval_wide = pd.DataFrame({
    "model":     ["bert-base", "distilbert"],
    "precision": [0.82, 0.79],
    "recall":    [0.78, 0.81],
    "f1":        [0.80, 0.80],
})
print(eval_wide)
#        model  precision  recall    f1
# 0  bert-base       0.82    0.78  0.80
# 1  distilbert      0.79    0.81  0.80
```

Melt it so every row is one (model, metric, value) triple:

```python
eval_long = eval_wide.melt(
    id_vars=["model"],
    var_name="metric",
    value_name="score",
)
print(eval_long)
#         model     metric  score
# 0   bert-base  precision   0.82
# 1  distilbert  precision   0.79
# 2   bert-base     recall   0.78
# 3  distilbert     recall   0.81
# 4   bert-base         f1   0.80
# 5  distilbert         f1   0.80
```

To go the other direction, from long to wide, use `pivot`:

```python
back_wide = eval_long.pivot(index="model", columns="metric", values="score")
back_wide.columns.name = None      # drop the "metric" label on the column axis
back_wide = back_wide.reset_index()
print(back_wide)
```

`pivot` requires unique (index, column) pairs; if your data has duplicates per cell, use `pivot_table` and supply an `aggfunc` (e.g., `"mean"`) to resolve them.

The long format is what groupby, seaborn, and most metric reporters expect. Knowing when to melt and when to pivot is the difference between clean downstream code and a wall of `.iloc` calls.

## Normalize Text Columns

The `.str` accessor gives you vectorized string methods on a Series, the same way M2's broadcasting gave you vectorized arithmetic on an array. No Python loop. No `apply(lambda x: x.lower())`.

```python
df = pd.DataFrame({
    "text": ["  Great Product! ", "TERRIBLE service.", "works FINE ", None]
})

df["text_clean"] = (
    df["text"]
    .str.strip()           # remove leading/trailing whitespace
    .str.lower()           # lowercase everything
    .str.replace(r"[!?.,]", "", regex=True)   # strip punctuation
    .str.replace(r"\s+", " ", regex=True)     # collapse multiple spaces
    .str.strip()           # strip again after regex replacements
)

print(df[["text", "text_clean"]])
#                 text          text_clean
# 0   Great Product!    great product
# 1  TERRIBLE service.  terrible service
# 2        works FINE   works fine
# 3               None          None
```

The `.str` accessor skips `NaN` automatically and returns `NaN` in those positions. That means text cleaning does not require a prior `dropna`; the null propagates cleanly and you handle it separately. This is the `clean_text` step in the made-with-ml `data.py` pipeline: strip, lowercase, replace punctuation, collapse whitespace, one vectorized chain.

For regex-heavy normalization, chain `.str.replace()` calls with explicit `regex=True`. The default in pandas 2.0 requires you to state your intent; pass `regex=False` for literal string replacement to avoid ambiguity.

```python
# Confirm text is normalized: no uppercase letters remain
assert df["text_clean"].dropna().str.match(r"^[^A-Z]*$").all()
```

The output of these four steps is what the tokenizer receives. A capital letter that survives lowercase normalization, a duplicate that survives dedup, or a NaN that survives dropna is not a minor impurity. It is training signal the model will learn.

## Core Concepts

- `duplicated()` flags repeat rows; `drop_duplicates()` removes them. The `keep` argument is a data decision: state it explicitly.
- Dropping vs. filling missing values is a modeling decision, not a default: drop when imputing would fabricate signal (a null text column); fill when a sensible sentinel exists (a missing numeric score).
- `melt` converts wide to long (one metric per row); `pivot` converts long to wide (one metric per column). Long format is what groupby and plotting APIs expect.
- The `.str` accessor applies vectorized string methods to a Series without a Python loop, skips `NaN` automatically, and chains: `str.strip().str.lower().str.replace(...)`.

<div class="claude-handoff" data-exercise="exercises/module3/cleaning-and-missing-data/">

**Build It in Claude Code:** Build `clean_corpus.py`, a script that deduplicates, handles missing values, and normalizes a messy text DataFrame, then asserts the output is clean in one `python` command.

</div>
