# Exercise: Emit, Test, and Ship

Data wrangling is the most common source of silent model failures. A corpus that enters training with duplicate records inflates accuracy metrics. One with null labels trains on noise. This artifact builds a production wrangling pipeline that rejects both problems at the gate and ships the validated corpus as typed Parquet that downstream steps can load without re-inferring types.

**Goal:** Finish `exercises/module6/wrangle.py` by adding `WrangleStats`, `emit`, `run`, and `main`; write `smoke.py` with a happy-path test and a negative-case test; and fill `outputs/skill-data-wrangling.md`. The gate is green when `python wrangle.py` exits 0 and `pytest smoke.py` passes both tests.

**Why:** A data pipeline that only runs on good input is a script. One that proves it rejects bad input is a pipeline. This exercise closes the gap.

## Before You Touch Code

Read the lesson at `src/module6/emit-test-and-ship.md`. Then open `exercises/module6/wrangle.py` and read its current state. It already contains:

- `WrangleConfig` (frozen dataclass: `input_path`, `output_path`, `required_cols`, `dedup_key`)
- `ingest(path) -> pd.DataFrame` (L1: loads JSONL)
- `clean(df) -> pd.DataFrame` (L2: deduplicates on `dedup_key`, then drops null-text rows, fills null scores, normalizes text)
- `reshape_and_validate(df, config) -> pd.DataFrame` (L3: enforces required cols; raises if any are missing)
- The sample corpus (8 rows: 1 duplicate id, 1 null text, 1 null score) at `exercises/module6/sample_corpus.jsonl` (built in the L1 exercise)

You are adding to `wrangle.py`. Read it before adding anything.

## Steps

### 1. Add the WrangleStats Dataclass

At the top of `wrangle.py`, after the imports and after `WrangleConfig`, add:

```python
from dataclasses import dataclass

@dataclass
class WrangleStats:
    rows_in: int
    rows_out: int
    dropped_dupes: int
    dropped_nulls: int
```

Do not use `frozen=True`; stats are a report, not a config.

### 2. Add emit

Add `emit` as a module-level function after the given stages:

```python
def emit(df: pd.DataFrame, path: str) -> None:
    """Write a validated DataFrame to Parquet.

    Requires pyarrow. The caller is responsible for passing a validated frame.
    """
    try:
        df.to_parquet(path, engine="pyarrow", index=False)
    except ImportError:
        raise RuntimeError("emit requires pyarrow: pip install pyarrow") from None
```

The `try/except ImportError` guard wraps the error pandas raises if pyarrow is absent. The pipeline fails loudly with a clear install hint, not with a cryptic internal traceback.

### 3. Add run

`run` composes the four stages and returns a `WrangleStats` record. The counting of `dropped_nulls` and `dropped_dupes` requires care: `clean` drops nulls first, then deduplicates. You must derive each delta without modifying `clean`.

One approach: before calling `clean`, count the rows that have a null in any required column, and the rows that are duplicates on `dedup_key` after null removal.

```python
def run(config: WrangleConfig) -> WrangleStats:
    df_raw   = ingest(config.input_path)
    rows_in  = len(df_raw)

    # Validate first, so a malformed corpus fails at the gate (a clear ValueError
    # from reshape_and_validate) before any stats derivation touches a missing column.
    df_clean = clean(df_raw)
    df_valid = reshape_and_validate(df_clean, config)
    emit(df_valid, config.output_path)

    # Derive the dropped counts from the raw frame. This runs only after the gate
    # passed, so the required columns are guaranteed present.
    # Hint: df_raw[list(config.required_cols)].isnull().any(axis=1).sum()
    #       then, after dropping those rows, .duplicated(subset=[config.dedup_key]).sum()
    dropped_nulls = ...  # your derivation
    dropped_dupes = ...  # your derivation

    return WrangleStats(
        rows_in=rows_in,
        rows_out=len(df_valid),
        dropped_dupes=dropped_dupes,
        dropped_nulls=dropped_nulls,
    )
```

Do not change `clean` or `reshape_and_validate`. Work out the counts from the raw frame.

### 4. Add main

Add an `if __name__ == "__main__":` block that runs the pipeline with a default config and prints the stats:

```python
if __name__ == "__main__":
    import pathlib

    _here = pathlib.Path(__file__).parent
    default_config = WrangleConfig(
        input_path=str(_here / "sample_corpus.jsonl"),
        output_path=str(_here / "outputs" / "wrangled.parquet"),
    )
    pathlib.Path(default_config.output_path).parent.mkdir(parents=True, exist_ok=True)
    stats = run(default_config)
    print(stats)
```

Running `python wrangle.py` from the `exercises/module6/` directory should exit 0 and print the `WrangleStats` record.

### 5. Write smoke.py

Create `exercises/module6/smoke.py`. It must be runnable as:

```
python -m pytest exercises/module6/smoke.py -v
```

from the repo root, or as `python smoke.py` from `exercises/module6/`.

The file needs two test functions.

**Test 1: happy path**

```python
import pytest
import pathlib
import sys

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))

from wrangle import WrangleConfig, WrangleStats, run

def test_pipeline_happy_path(tmp_path):
    config = WrangleConfig(
        input_path=str(_HERE / "sample_corpus.jsonl"),
        output_path=str(tmp_path / "out.parquet"),
    )
    stats = run(config)

    # Row-count assertions
    assert stats.rows_in == 8,         f"expected rows_in=8, got {stats.rows_in}"
    assert stats.rows_out == 6,        f"expected rows_out=6, got {stats.rows_out}"
    assert stats.dropped_dupes == 1,   f"expected dropped_dupes=1, got {stats.dropped_dupes}"
    assert stats.dropped_nulls == 1,   f"expected dropped_nulls=1, got {stats.dropped_nulls}"

    # Output file exists
    import pandas as pd
    out_path = pathlib.Path(config.output_path)
    assert out_path.exists(), "Parquet output file was not created"

    # Round-trip: dtypes survive
    df_out = pd.read_parquet(out_path)
    assert "id"    in df_out.columns
    assert "text"  in df_out.columns
    assert "label" in df_out.columns

    # No nulls in required columns
    for col in ("id", "text", "label"):
        assert df_out[col].isnull().sum() == 0, f"null values found in column '{col}'"

    # dtype check: id integer, text and label strings, score float. Predicates,
    # not strict object/int, so a Parquet round-trip's str dtype passes.
    import pandas.api.types as pat
    assert pat.is_integer_dtype(df_out["id"]),   f"id dtype is {df_out['id'].dtype}, expected integer"
    assert pat.is_string_dtype(df_out["text"]),  f"text dtype is {df_out['text'].dtype}, expected string"
    assert pat.is_string_dtype(df_out["label"]), f"label dtype is {df_out['label'].dtype}, expected string"
```

**Test 2: negative case**

```python
def test_pipeline_negative_case(tmp_path):
    """A corpus missing a required column must make reshape_and_validate raise."""
    # Write a JSONL corpus with no 'label' column
    bad_corpus = tmp_path / "bad.jsonl"
    bad_corpus.write_text(
        # has score, missing label: clean runs, then reshape_and_validate raises at the gate
        '{"id": 1, "text": "hello", "score": 0.5}\n'
        '{"id": 2, "text": "world", "score": 0.6}\n',
        encoding="utf-8",
    )
    bad_config = WrangleConfig(
        input_path=str(bad_corpus),
        output_path=str(tmp_path / "out.parquet"),
    )
    with pytest.raises(Exception):
        run(bad_config)
```

The negative case uses `pytest.raises(Exception)` rather than a specific subclass because the exception type is an implementation detail of `reshape_and_validate`, which is a given stage you did not write.

### 6. Write outputs/skill-data-wrangling.md

Create `exercises/module6/outputs/skill-data-wrangling.md` using this template. Fill in the bracketed sections with your own answers after you run the pipeline.

```markdown
# Skill: Data Wrangling Artifact

## What I Built

`wrangle.py` is a four-stage data wrangling pipeline: `ingest` loads a JSONL
corpus, `clean` removes null records and deduplicates, `reshape_and_validate`
enforces the required column schema, and `emit` writes the validated frame to
typed Parquet. `run` composes all four stages and returns a `WrangleStats`
dataclass with row-count accounting.

## The Business Problem

[Describe in 2–3 sentences: what goes wrong when a model trains on a corpus
that has duplicates or null labels, and how this pipeline prevents that.]

## What I Learned

[2–3 bullet points: one thing about Parquet/emit, one about testing with
pytest (especially the negative case), one about composing stages with a
dataclass return.]

## How to Run It

```
cd exercises/module6
python wrangle.py          # runs the pipeline; exits 0; prints WrangleStats
python -m pytest smoke.py -v   # runs both tests; must pass
```

## Skills Demonstrated

- Pandas data cleaning: null removal, deduplication
- Typed Parquet output with pyarrow
- Pytest smoke testing: happy path + negative case
- Dataclasses as typed return values (M5 pattern applied)
- Pipeline composition: four stages, one entry point, one acceptance gate
```

## Done When

`python wrangle.py` exits 0, prints a `WrangleStats` record, and writes `outputs/wrangled.parquet`.

`python -m pytest exercises/module6/smoke.py -v` (from the repo root) reports:

```
PASSED  smoke.py::test_pipeline_happy_path
PASSED  smoke.py::test_pipeline_negative_case
2 passed
```

Both assertions in `test_pipeline_happy_path` confirm the expected row counts (`rows_in==8`, `rows_out==6`, `dropped_dupes==1`, `dropped_nulls==1`), the Parquet file exists and round-trips cleanly, and the required columns contain no nulls.

`test_pipeline_negative_case` confirms that a corpus missing the `label` column makes the pipeline raise.

No external dependencies beyond `pandas`, `numpy`, and `pyarrow` (for Parquet). If `pyarrow` is absent, `emit` raises `RuntimeError` with an install hint rather than failing silently; guard the install before running the smoke test.

## Expected Output (python wrangle.py)

```
WrangleStats(rows_in=8, rows_out=6, dropped_dupes=1, dropped_nulls=1)
```

The Parquet file lands at `exercises/module6/outputs/wrangled.parquet`.

## Stretch

Add a fourth assertion to `test_pipeline_happy_path`: confirm that the output Parquet is smaller in bytes than the input JSONL. Use `pathlib.Path.stat().st_size` on both files. On a 6-row frame this margin will be small, but the assertion documents the production expectation (Parquet compresses; JSONL does not).

Then add a second negative case: a corpus where `id` is not unique (all rows have `id=1`). Assert that after `clean`'s dedup pass, `rows_out` is 1. This tests that the dedup key works as intended across a pathological input, not just the sample corpus.
