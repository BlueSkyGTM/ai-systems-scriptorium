# Exercise: Run, Test, and Ship

`pipeline.py` composes `wrangle.py` and `eval_engine.py` into a single runnable artifact that cleans data, evaluates predictions, and writes a report. That is enough to say the code works. It is not enough to say the code is trusted. The gate is trusted when two tests prove it: one that locks the honest result to the oracle, and one that shows the rubric rejects a deficient run. This exercise builds that gate and ships the skill write-up that closes the book's arc.

**Goal:** Write `exercises/module8/smoke.py` with `test_exam_passes` and `test_deficient_run_fails`; write `exercises/module8/tests/test_smoke.py` that imports both functions so pytest can collect them; and fill out `exercises/module8/outputs/skill-integrated-exam.md`. The final acceptance gate for the whole book is: `python pipeline.py` exits 0 and writes `report.md`; `python -m pytest tests/` passes both tests.

**Why:** A graded, gated pipeline is what separates a portfolio script from a portfolio artifact. The rubric passing the honest run and refusing the deficient one is the evidence a reviewer reads; the skill write-up is the translation layer that makes it legible to a hire.

## Before You Touch Code

Read the lesson at `src/module8/run-test-and-ship.md`. Then read `exercises/module8/pipeline.py` and `exercises/module8/rubric.py`. You are not touching either of those files. You are writing the gate that calls them.

The contracts you rely on, both established in lessons 2 and 3:

**`pipeline.run_pipeline(config) -> ExamRun`**

```python
ExamRun(
    report_path: str,
    n_clean: int,
    metrics: list[ClassMetrics],
    composed_modules: list[str],
    version: str,
)
```

`default_config` is exported from `pipeline.py`. `python pipeline.py` exits 0 and writes `report.md`.

**`rubric.grade(exam: ExamRun) -> RubricReport`**

```python
RubricReport(
    results: list[CriterionResult],  # six entries, R1..R6
    passed: bool,
)
# .failed() -> list[CriterionResult]   entries where passed is False
# .as_lines() -> list[str]             human-readable verdict per criterion
```

**`ClassMetrics(cls, precision, recall, f1, support)`** is the per-class record in `ExamRun.metrics`.

## The Locked Oracle

The bundled sample produces these exact per-class metrics. Your `test_exam_passes` asserts all nine numbers to a tolerance of `1e-3`:

| class | precision | recall | f1 | support |
|---|---|---|---|---|
| cat | 0.750 | 0.750 | 0.750 | 4 |
| dog | 0.667 | 0.500 | 0.571 | 4 |
| bird | 0.667 | 1.000 | 0.800 | 2 |

`n_clean` must equal 10. `report.passed` must be `True`. `report.failed()` must be `[]`. `len(report.results)` must be 6.

Use `abs(result - oracle) < 1e-3`, not equality. Floating-point division is not exact across environments.

## Steps

### 1. Write exercises/module8/smoke.py

Create `smoke.py` at the module root. It must be importable and also runnable as `python smoke.py`. Two test functions:

**`test_exam_passes`**

Wire the imports, call `run_pipeline(default_config)`, call `rubric.grade(exam)`, and assert every dimension listed in the oracle above. Assert per-class precision, recall, and f1 for all three classes. Assert `n_clean == 10`, `report.passed is True`, and `report.failed() == []`.

Signature stub:

```python
def test_exam_passes():
    exam = run_pipeline(default_config)
    report = grade(exam)
    # your assertions here
```

**`test_deficient_run_fails`**

Build a deficient `ExamRun` by copying the honest run and corrupting one field so that one criterion fires. The two sensible targets are:

- Corrupt `dog`'s recall to `0.0` (and f1 to `0.0`): this breaks the per-class recall criterion. Assert `"R3" in failed_ids`.
- Or set `n_clean` to `0` on an otherwise-honest `ExamRun`: this breaks the row-count criterion. Assert `"R2" in failed_ids`.

Pick one. Assert `report.passed is False`. Assert the offended criterion id is in `{r.rid for r in report.failed()}`.

To construct the deficient run: call `run_pipeline(default_config)` to get a clean base, then build a new `ExamRun` with the corrupted field. Import `ExamRun` from `pipeline`. To corrupt a metric, use `dataclasses.replace(m, recall=0.0, f1=0.0)` on the honest `ClassMetrics`: `replace` copies a dataclass without importing its class (`ClassMetrics` lives in `eval_engine.py`, loaded off disk, not in `pipeline`).

Signature stub:

```python
def test_deficient_run_fails():
    honest = run_pipeline(default_config)
    # build deficient ExamRun here
    report = grade(deficient)
    assert report.passed is False
    # assert the offended criterion
```

### 2. Write exercises/module8/tests/test_smoke.py

Create the `tests/` directory if it does not exist. `test_smoke.py` imports the two test functions from `smoke.py` and re-exposes them so pytest collects them from the standard `tests/` path. Do not duplicate any logic.

```python
import pathlib
import sys

_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from smoke import test_deficient_run_fails, test_exam_passes

__all__ = ["test_exam_passes", "test_deficient_run_fails"]
```

### 3. Write exercises/module8/outputs/skill-integrated-exam.md

Create the `outputs/` directory if it does not exist. The write-up is your portfolio surface. Fill in every section yourself after you run the pipeline.

Required sections:

**What I Built:** describe `pipeline.py`'s role as the composer: it calls `wrangle.py`'s `run()` and `eval_engine.py`'s `run()` in sequence, captures the result in `ExamRun`, and writes `report.md`. Then describe the gate: `smoke.py` proves the honest run passes and the deficient run fails.

**The Business Problem:** one repo, three scripts, a graded report. A reviewer clones the repo, runs `python pipeline.py`, reads the report, runs `pytest tests/`, and sees two tests pass. That is the artifact. Frame the problem in 2–3 sentences for someone who has not read the book.

**Lineage (the arc):** `measure.py` (M1–M3) → `vectorization_report.py` (M4) → `wrangle.py` (M6) → `eval_engine.py` (M7) → `pipeline.py` (M8). Each step imports the prior artifact; nothing is rebuilt. This paragraph is the evidence that the compounding is real.

**The Rubric It Passes:** list all six criteria (R1–R6) and what each checks. One line per criterion.

**How to Run It:** two commands, in a fenced block:

```
python pipeline.py            # exits 0; writes outputs/report.md
python -m pytest tests/ -v    # two tests passed
```

**Skills Demonstrated:** 4–6 bullets. Concrete: not "testing skills" but "smoke testing a typed pipeline result with toleranced float assertions and a deliberate negative case."

Use the template in the lesson as a guide, not a form. Write it after you run the code so the words come from the real output, not a guess.

## Acceptance Check (the Book's Final Gate)

The exam is done when all four are true:

1. `python pipeline.py` exits 0 and writes `outputs/report.md`.
2. `python -m pytest tests/ -v` from `exercises/module8/` reports:

```
PASSED  tests/test_smoke.py::test_exam_passes
PASSED  tests/test_smoke.py::test_deficient_run_fails
2 passed
```

3. `test_exam_passes` asserts all nine per-class oracle numbers to `1e-3`, `n_clean == 10`, `report.passed is True`, and `len(report.results) == 6`.
4. `test_deficient_run_fails` asserts `report.passed is False` and names the offended criterion by id.

No network, no live model, no API key. The gate is deterministic and offline: stdlib plus pandas plus pytest.

Data validation for production ML pipelines follows exactly this pattern: acceptance criteria are expressed in code, checked against a locked sample, and the deficient case is tested explicitly ([learn.microsoft.com/fabric/data-science/semantic-link-validate-data](https://learn.microsoft.com/fabric/data-science/semantic-link-validate-data)). The gate you build here is that pattern, applied to the arc you built across the whole book.

## Stretch

Add a third test: `test_rubric_has_six_criteria`. Import `CRITERIA` from `rubric` and assert `len(CRITERIA) == 6` and that the ids are exactly `["R1", "R2", "R3", "R4", "R5", "R6"]` in order. This is the coherence invariant: it catches the case where the guide and the code drift to different rubric counts. In production, a test like this is cheaper than discovering the drift in a review.

Then add a second deficient variant targeting the other criterion you did not test in step 1. Two deficient cases, one per criterion family (row-count and per-class metric), proves the rubric is checking what it claims to check.
