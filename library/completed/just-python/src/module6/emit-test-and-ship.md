# Emit, Test, and Ship

The artifact is done when the gate is green. You have three stages: `ingest` loads the corpus, `clean` strips nulls and normalizes text, `reshape_and_validate` enforces the schema contract. This lesson adds the final two pieces: `emit` writes the validated frame to typed Parquet, and `run` composes the four stages into a single callable that returns a `WrangleStats` record. Then you prove the whole thing works with a `pytest` smoke test that catches both the happy path and the deliberate failure, and you write the skill file that turns the artifact into a portfolio piece.

## What You Build

You build the `emit` function and the `run` composer for `wrangle.py`, a `smoke.py` pytest gate that asserts row counts, dtypes, and the negative case, and `outputs/skill-data-wrangling.md`, the write-up that explains what you shipped and why it matters.

## The emit Stage

`emit` writes the validated DataFrame to Parquet. The pattern is one line: `df.to_parquet(path, engine="pyarrow", index=False)`. The reason to call it out as a named stage is the same reason the earlier stages are named: each stage does one thing, takes a clear input, and is independently testable.

```python
def emit(df: pd.DataFrame, path: str) -> None:
    """Write a validated DataFrame to Parquet.

    Requires pyarrow. The caller is responsible for calling
    reshape_and_validate before emit; emit writes what it receives.
    """
    try:
        df.to_parquet(path, engine="pyarrow", index=False)
    except ImportError:
        # pyarrow is optional at import time; fail loudly here, not silently
        raise RuntimeError(
            "emit requires pyarrow: pip install pyarrow"
        ) from None
```

The guard matters. M3 taught that Parquet depends on `pyarrow`, which is not in the standard library. The import error from `to_parquet` is clear enough on its own, but wrapping it in a `RuntimeError` with the install hint means the pipeline fails at the emit stage, not at a cryptic internal pandas call. That is the difference between a crash and a message.

Microsoft Fabric's pandas integration page shows this exact pattern: `df.to_parquet("/LAKEHOUSE_PATH/Files/FILENAME.parquet")` followed by `pd.read_parquet(...)` for round-trip validation, used in production Lakehouse pipelines ([learn.microsoft.com/fabric/data-science/read-write-pandas](https://learn.microsoft.com/fabric/data-science/read-write-pandas#reading-and-writing-various-file-formats)). The local artifact uses the same API surface.

## The WrangleStats Dataclass

`run` needs to return something a caller can inspect and assert against. A dict would work, but M5 established the pattern: when the fields are named and fixed, use a dataclass.

```python
from dataclasses import dataclass

@dataclass
class WrangleStats:
    rows_in: int
    rows_out: int
    dropped_dupes: int
    dropped_nulls: int
```

No `frozen=True` here: stats are a report, not a config. The four fields map one-to-one to what the pipeline can measure:

- `rows_in`: the count after `ingest`, before anything else.
- `dropped_dupes`: rows removed by `clean`'s dedup pass (8 rows in, 7 after dedup for the sample).
- `dropped_nulls`: rows removed by `clean`'s null drop (7 to 6 on the sample).
- `rows_out`: the count that reaches `emit`.

The smoke test asserts these four numbers exactly. When a field is wrong, the failure message names the field, not a key string.

## The run Composer

`run` wires the four stages in order and collects the stats as it goes.

```python
def run(config: WrangleConfig) -> WrangleStats:
    df_raw = ingest(config.input_path)
    rows_in = len(df_raw)

    df_clean = clean(df_raw)
    # derive dropped counts by diffing row counts
    dropped_nulls = rows_in - len(df_clean) - ...  # TODO: compute dropped_dupes separately
```

The counting requires care. `clean` deduplicates first, then drops nulls. To get `dropped_dupes` and `dropped_nulls` separately, track the intermediate length:

```python
def run(config: WrangleConfig) -> WrangleStats:
    df_raw = ingest(config.input_path)
    rows_in = len(df_raw)

    df_clean = clean(df_raw)
    # clean drops nulls first, then deduplicates; compute each delta
    after_null_drop = rows_in - df_clean.pipe(
        lambda df: df  # placeholder; see exercise
    )
    # ...
```

The exercise asks you to work out the counting logic. The key constraint: `clean` is a given and you cannot change its implementation. You must derive the two deltas from the row counts available before and after `clean`, and from the dedup key. One approach is to track null rows before calling `clean`; another is to compute deduplication from the raw frame directly. Either is correct as long as `smoke.py` asserts the numbers.

A complete reference signature:

```python
def run(config: WrangleConfig) -> WrangleStats:
    df_raw   = ingest(config.input_path)
    rows_in  = len(df_raw)
    df_clean = clean(df_raw)
    df_valid = reshape_and_validate(df_clean, config)
    emit(df_valid, config.output_path)
    # stats derivation: your job in the exercise
    return WrangleStats(
        rows_in=rows_in,
        rows_out=len(df_valid),
        dropped_dupes=...,
        dropped_nulls=...,
    )
```

## The Smoke Test

A "smoke test" answers one question: does the pipeline produce the right output without catching fire? It is not an exhaustive test suite. It is the minimum gate that makes "done" mean something.

`smoke.py` has two test functions. `test_pipeline_happy_path` runs the full pipeline on the sample corpus and asserts:

- `stats.rows_in == 8`
- `stats.rows_out == 6`
- `stats.dropped_dupes == 1`
- `stats.dropped_nulls == 1`
- No nulls in the required columns of the output Parquet
- The Parquet file exists and round-trips, checked with `pandas.api.types` predicates (`id` an integer, `text` and `label` strings, `score` a float) so a round-trip's `str` dtype does not fail the gate

`test_pipeline_negative_case` provides a corpus that is missing the `label` column and asserts that `run` raises. The pipeline's whole job is to reject data that violates the contract; a test that only checks the happy path does not prove the pipeline does its job.

```python
import pytest
import pandas as pd
import pathlib

def test_pipeline_negative_case(tmp_path):
    """A corpus missing a required column must make reshape_and_validate raise."""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from wrangle import WrangleConfig, run

    # write a JSONL corpus with no 'label' column
    bad_corpus = tmp_path / "bad.jsonl"
    bad_corpus.write_text(
        '{"id": 1, "text": "hello"}\n'
        '{"id": 2, "text": "world"}\n',
        encoding="utf-8",
    )
    bad_config = WrangleConfig(
        input_path=str(bad_corpus),
        output_path=str(tmp_path / "out.parquet"),
    )
    with pytest.raises(Exception):
        run(bad_config)
```

The assertion is `pytest.raises(Exception)`, not a specific exception type, because `reshape_and_validate` is a given: its exact exception class is an implementation detail of a stage you did not write. The test proves the gate fires, not which Python class it uses.

## The README and the Skill Write-Up

Every strong project frames the business problem before the code. The exercise README you write starts with this:

> Data wrangling is the most common source of silent model failures. A corpus that enters training with duplicate records inflates accuracy metrics. One with null labels trains on noise. This artifact builds a production wrangling pipeline that rejects both problems at the gate, and ships the validated corpus as typed Parquet that downstream steps can load without re-inferring types.

That is the STANDARDS Part 2 "README frames the business problem" criterion. It answers "why does this exist" before it answers "what does it do."

`outputs/skill-data-wrangling.md` is the portfolio surface. It documents what the artifact does, the business problem it solves, the skills it demonstrates, and how to run it. A hiring manager reading a GitHub repo will read the README first and the skill write-up second; the code is third. The write-up is not optional and it is not filler: it is the translation layer between a script and a hire.

## The Standards Check

Every build lesson in this book is held to the Part 2 rubric. Here is where each criterion lands in this artifact:

| Criterion | Where it lives |
|---|---|
| Real entry point | `python wrangle.py` runs the pipeline and exits 0 |
| README frames the business problem | `exercises/module6/emit-test-and-ship/README.md` leads with the duplicate/null failure mode |
| Machine-checkable acceptance gate | `pytest smoke.py` passes; two assertions cover happy path and negative case |
| The negative case is tested | `test_pipeline_negative_case` asserts a malformed corpus raises |
| Versioned, clean layout; no secrets | Parquet goes to `outputs/`; no keys; `.gitignore` optional |
| Ships a skill artifact | `outputs/skill-data-wrangling.md` is a required output |

The gate is green when `python wrangle.py` exits 0 and `pytest smoke.py` reports two tests passed.

Shipping a smoke-tested artifact with a typed output and a negative case is not about following a checklist. It is what separates a data script from a data pipeline: the script does something useful; the pipeline proves it did.

## Core Concepts

- `emit` writes a validated DataFrame to Parquet using `df.to_parquet(path, engine="pyarrow", index=False)`; it is the final stage in a chain where each earlier stage earns the trust this one cashes.
- `WrangleStats` is a `@dataclass` (not a dict) because the four row-count fields are named, fixed, and asserted by name in the smoke test; a dict key typo fails at runtime, an attribute typo fails before you run.
- A smoke test earns its name by covering both paths: the happy path proves the output is correct; the negative case proves the gate rejects what it should, and that is what a hiring manager evaluates.
- The skill write-up in `outputs/skill-data-wrangling.md` is the translation between a script and a portfolio piece; the README's first sentence is the business problem, not the file name.

<div class="claude-handoff" data-exercise="exercises/module6/emit-test-and-ship/">

**Build It in Claude Code:** Finish `wrangle.py` by adding `WrangleStats`, `emit`, `run`, and the `if __name__ == "__main__":` block; write `smoke.py` with the happy-path and negative-case tests; and fill out `outputs/skill-data-wrangling.md`. The gate is green when `python wrangle.py` exits 0 and `pytest smoke.py` passes both tests.

</div>
