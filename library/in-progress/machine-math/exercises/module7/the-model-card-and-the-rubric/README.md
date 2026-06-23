# Exercise: The Model Card and the Rubric

**Goal:** Add the model-card writer to `exercises/module7/pipeline.py` (step 7), then
build `exercises/module7/rubric.py` with the six-criterion grader. The capstone gate is
`python -m pytest exercises/module7/the-model-card-and-the-rubric`: green when the good
run grades 6/6 and each deficient run fails exactly the criterion it offends.

**Why:** A model you cannot explain and grade is not a portfolio artifact; it is a script.
The model card is the artifact a hiring manager reads. The rubric is the machine that
certifies it, in code, not opinion. This is the final gate of the Machine Math throughline:
every number on the card traces to a function in `ml/`; the rubric checks that trace at
test time.

## The Shared Artifact

`exercises/module7/pipeline.py` accumulates the full capstone pipeline across all Module 7
exercises. Before touching anything, read the file top to bottom. Confirm that steps 1
through 6 (load, features, split, train, evaluate, slice) are complete and that
`PipelineResult` carries `metrics`, `slices`, `worst_subgroup`, `composed_modules`, and
`version`. Step 7 (the model-card writer) extends the same file.

`exercises/module7/rubric.py` is a new file you will create in this exercise.

## Steps

### 1. Add Step 7: The Model Card Writer

In `pipeline.py`, add the model-card call inside `run()`, after the slice stage and before
the `return` statement. The card is written to the same directory as `data.csv`:

```python
    # ------------------------------------------------------------------
    # 7. Model card
    # ------------------------------------------------------------------
    card_path = os.path.join(os.path.dirname(data_path), card_name)

    if stub_model_card:
        with open(card_path, "w", encoding="utf-8") as fh:
            fh.write("This is a stub model card with no required sections.\n")
    else:
        _write_model_card(
            card_path,
            data_path=data_path,
            n_rows=n,
            numeric_cols=NUMERIC_COLS,
            categorical_cols=CATEGORICAL_COLS,
            subgroup_col=SUBGROUP_COL,
            metrics=overall_metrics,
            slices=slices,
            worst_subgroup=worst_subgroup,
            skip_scaling=skip_scaling,
            skip_encoding=skip_encoding,
        )

    composed_modules = ["ml.features", "ml.metrics"]
```

The `stub_model_card` and `card_name` parameters are already declared on `run()` if you
are working from the locked `pipeline.py`. If they are not yet present in your file, add
them now:

```python
def run(
    data_path: str,
    skip_scaling: bool = False,
    skip_encoding: bool = False,
    skip_slicing: bool = False,
    stub_model_card: bool = False,
    card_name: str = "MODEL_CARD.md",
) -> PipelineResult:
```

Also add `model_card_path=card_path` to the `PipelineResult(...)` constructor call.

### 2. Add the Card Template and Writer

After `run()` and before the `if __name__ == "__main__":` block, add the
`_CARD_TEMPLATE` string and `_write_model_card()` function from `pipeline.py` in the
locked reference. The template uses Python `str.format()` with named placeholders
(`{data_path}`, `{n_rows}`, `{auc}`, `{slice_rows}`, etc.). The writer formats and writes
it to `card_path`.

The six required section headers the rubric checks are:

```
## Dataset
## Features
## Model
## Overall Metrics
## Slice Table
## Limitations
```

Your template must contain all six, using those exact strings as H2 headings.

### 3. Build rubric.py

Create `exercises/module7/rubric.py`. The file must contain the `CRITERIA` tuple and
`grade(result)` exactly as shown in the lesson. The `CRITERIA` tuple is:

```python
CRITERIA = (
    ("R1", "RUNS: predictions array is non-empty"),
    ("R2", "FEATURES-ENGINEERED: categoricals one-hot encoded, numerics z-score scaled"),
    ("R3", "EVALUATED: AUC >= 0.75 and F1 >= 0.50 and precision/recall both present"),
    ("R4", "SLICED: per-subgroup metrics computed, worst subgroup identified"),
    ("R5", "COMPOSED: ml.features and ml.metrics imported from ml/ package on disk"),
    ("R6", "MODEL-CARD: MODEL_CARD.md exists with required section headers"),
)
```

Do not alter the text of any criterion. The acceptance gate compares criterion IDs by
string; any deviation fails the test.

`grade(result)` reads `result.predictions`, `result._encoding_done`,
`result._scaling_done`, `result.metrics`, `result.slices`, `result.worst_subgroup`,
`result.composed_modules`, and `result.model_card_path`. It returns a `dict[str, bool]`
mapping each criterion ID to its pass/fail verdict.

Also add `main(result=None) -> int` so `python rubric.py` grades the default run and
returns 0 on all-pass, nonzero otherwise.

### 4. Place the Acceptance Gate

The locked test file goes at
`exercises/module7/the-model-card-and-the-rubric/test_rubric.py`. Place it verbatim:

```python
"""Acceptance gate: rubric grader correctness.

Tests
-----
1. Good run -> rubric.grade(result) is all True (6/6).
2. rubric.main() with a good run exits 0.
3. DEFICIENT RUN (no_encoding): R2 fails, rubric.main() exits nonzero.
4. DEFICIENT RUN (no_slicing): R4 fails, rubric.main() exits nonzero.
5. DEFICIENT RUN (stub_card): R6 fails, rubric.main() exits nonzero.
6. Each deficient run fails exactly the expected criterion and no others
   (all other criteria remain True, confirming the rubric is criterion-specific).
"""
import os
import sys

# Path setup: ref/ for ml package, ref/module7/ for pipeline/rubric
_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE7 = os.path.dirname(_HERE)
_REF = os.path.dirname(_MODULE7)

for _p in [_REF, _MODULE7]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
import pipeline
import rubric

DATA_PATH = os.path.join(_MODULE7, "data.csv")


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def good_result():
    return pipeline.run(DATA_PATH)


@pytest.fixture(scope="module")
def deficient_no_encoding():
    """Omits encoding + scaling -- R2 should fail."""
    return pipeline.run_deficient(DATA_PATH, failure_mode="no_encoding")


@pytest.fixture(scope="module")
def deficient_no_slicing():
    """Omits subgroup slicing -- R4 should fail."""
    return pipeline.run_deficient(DATA_PATH, failure_mode="no_slicing")


@pytest.fixture(scope="module")
def deficient_stub_card():
    """Writes a stub model card -- R6 should fail."""
    return pipeline.run_deficient(DATA_PATH, failure_mode="stub_card")


# ---------------------------------------------------------------------------
# 1. Good run: all 6 criteria pass
# ---------------------------------------------------------------------------

def test_good_run_all_pass(good_result):
    scores = rubric.grade(good_result)
    failing = [cid for cid, passed in scores.items() if not passed]
    assert len(failing) == 0, f"Expected 0 failures on good run; got failures: {failing}"


def test_good_run_six_criteria(good_result):
    scores = rubric.grade(good_result)
    assert len(scores) == 6, f"Expected 6 criteria, got {len(scores)}"


# ---------------------------------------------------------------------------
# 2. rubric.main() exits 0 on a good run
# ---------------------------------------------------------------------------

def test_main_exits_zero_on_good_run(good_result):
    exit_code = rubric.main(result=good_result)
    assert exit_code == 0, f"Expected exit 0 on good run, got {exit_code}"


# ---------------------------------------------------------------------------
# 3. Deficient run: no_encoding fails R2 only
# ---------------------------------------------------------------------------

def test_no_encoding_fails_r2(deficient_no_encoding):
    scores = rubric.grade(deficient_no_encoding)
    assert scores["R2"] is False, "Expected R2 to fail when encoding is skipped"


def test_no_encoding_only_fails_r2(deficient_no_encoding):
    """R1, R3, R4, R5, R6 should still pass when only encoding is skipped."""
    scores = rubric.grade(deficient_no_encoding)
    for cid in ["R1", "R3", "R4", "R5", "R6"]:
        assert scores[cid] is True, (
            f"Criterion {cid} unexpectedly failed in no_encoding run: {scores}"
        )


def test_no_encoding_main_exits_nonzero(deficient_no_encoding):
    exit_code = rubric.main(result=deficient_no_encoding)
    assert exit_code != 0, "Expected nonzero exit when R2 fails"


# ---------------------------------------------------------------------------
# 4. Deficient run: no_slicing fails R4 only
# ---------------------------------------------------------------------------

def test_no_slicing_fails_r4(deficient_no_slicing):
    scores = rubric.grade(deficient_no_slicing)
    assert scores["R4"] is False, "Expected R4 to fail when slicing is skipped"


def test_no_slicing_only_fails_r4(deficient_no_slicing):
    """R1, R2, R3, R5, R6 should still pass when only slicing is skipped."""
    scores = rubric.grade(deficient_no_slicing)
    for cid in ["R1", "R2", "R3", "R5", "R6"]:
        assert scores[cid] is True, (
            f"Criterion {cid} unexpectedly failed in no_slicing run: {scores}"
        )


def test_no_slicing_main_exits_nonzero(deficient_no_slicing):
    exit_code = rubric.main(result=deficient_no_slicing)
    assert exit_code != 0, "Expected nonzero exit when R4 fails"


# ---------------------------------------------------------------------------
# 5. Deficient run: stub_card fails R6 only
# ---------------------------------------------------------------------------

def test_stub_card_fails_r6(deficient_stub_card):
    scores = rubric.grade(deficient_stub_card)
    assert scores["R6"] is False, "Expected R6 to fail when stub card is written"


def test_stub_card_only_fails_r6(deficient_stub_card):
    """R1, R2, R3, R4, R5 should still pass when only the card is stubbed."""
    scores = rubric.grade(deficient_stub_card)
    for cid in ["R1", "R2", "R3", "R4", "R5"]:
        assert scores[cid] is True, (
            f"Criterion {cid} unexpectedly failed in stub_card run: {scores}"
        )


def test_stub_card_main_exits_nonzero(deficient_stub_card):
    exit_code = rubric.main(result=deficient_stub_card)
    assert exit_code != 0, "Expected nonzero exit when R6 fails"
```

Do not alter this file. The gate is locked.

## Done When

```
python -m pytest exercises/module7/the-model-card-and-the-rubric
```

is green: all 12 tests pass. That means:

- The good run grades 6/6 and `rubric.main()` exits 0.
- `no_encoding` fails R2 and only R2; `rubric.main()` exits nonzero.
- `no_slicing` fails R4 and only R4; `rubric.main()` exits nonzero.
- `stub_card` fails R6 and only R6; `rubric.main()` exits nonzero.

## Stretch

- Add a seventh criterion, R7, to both the `CRITERIA` tuple and the prose table in the
  lesson: for example, `VERSION: result.version is a non-empty string`. Update
  `test_rubric.py` to check that the good run passes R7 and that a `run()` call with
  `version=""` fails it. This is a schema-extension exercise; the rubric shape stays the
  same.
- Run `python rubric.py` from the command line and read the scorecard output. Post it as
  the `outputs/skill-the-model-card-and-the-rubric.md` skill artifact: a screenshot of the
  terminal output plus a one-paragraph description of what each criterion proved.
