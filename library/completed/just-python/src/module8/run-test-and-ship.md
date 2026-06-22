# Run, Test, and Ship

The exam is done when the gate is green and the run is graded. You have the pipeline, the rubric, and the oracle numbers: `smoke.py` and `tests/test_smoke.py` close the loop, then a skill write-up ships the whole arc as a portfolio piece.

## What You Build

You build `smoke.py`, the deterministic offline gate that calls `pipeline.run_pipeline` on the bundled sample, grades the result with `rubric.grade`, and asserts the exam passes; `tests/test_smoke.py`, the pytest entry point that the CI gate runs with one command; and `outputs/skill-integrated-exam.md`, the portfolio surface that documents what you built and what it proved.

## The Contracts You Rely On

The earlier lessons in this module built two contracts. You do not redefine them here; you use them.

`pipeline.run_pipeline(config) -> ExamRun` composes `wrangle.py` and `eval_engine.py` off disk, cleans the sample, runs the evaluation, and returns a typed result:

```python
ExamRun(
    report_path: str,
    n_clean: int,
    metrics: list[ClassMetrics],
    composed_modules: list[str],
    version: str,
)
```

`python pipeline.py` exits 0 and writes `report.md`.

`rubric.grade(exam: ExamRun) -> RubricReport` checks six criteria, R1 through R6, and returns a record with `.passed`, `.failed()`, and `.as_lines()`:

```python
RubricReport(
    results: list[CriterionResult],
    passed: bool,
)
```

`ClassMetrics(cls, precision, recall, f1, support)` is the per-class record `eval_engine` returns, imported here through `ExamRun.metrics`.

## The Smoke Test

`smoke.py` answers two questions with two test functions: does the pipeline pass the rubric on the locked sample, and does a deficient run fail the criterion it offends?

### test_exam_passes

This function runs the full chain and asserts every dimension of the honest result.

```python
import pathlib
import sys

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE))

from pipeline import default_config, run_pipeline
from rubric import grade

def test_exam_passes():
    exam = run_pipeline(default_config)
    report = grade(exam)

    # The rubric must pass and all six criteria must hold.
    assert report.passed is True
    assert report.failed() == []
    assert len(report.results) == 6

    # The pipeline cleaned exactly ten rows.
    assert exam.n_clean == 10

    # Lock the per-class metrics to the oracle within 1e-3 tolerance.
    by_class = {m.cls: m for m in exam.metrics}

    assert abs(by_class["cat"].precision - 0.750) < 1e-3
    assert abs(by_class["cat"].recall    - 0.750) < 1e-3
    assert abs(by_class["cat"].f1        - 0.750) < 1e-3

    assert abs(by_class["dog"].precision - 0.667) < 1e-3
    assert abs(by_class["dog"].recall    - 0.500) < 1e-3
    assert abs(by_class["dog"].f1        - 0.571) < 1e-3

    assert abs(by_class["bird"].precision - 0.667) < 1e-3
    assert abs(by_class["bird"].recall    - 1.000) < 1e-3
    assert abs(by_class["bird"].f1        - 0.800) < 1e-3
```

The oracle numbers are the same locked values `eval_engine.py` produced in M7: cat 0.750/0.750/0.750, dog 0.667/0.500/0.571, bird 0.667/1.000/0.800. The tolerance is `1e-3`, not equality; floating-point division is not exact across environments.

### test_deficient_run_fails

This function builds a corrupted `ExamRun` and asserts the rubric rejects it. Strength is proven by what the gate refuses.

```python
from dataclasses import replace

from pipeline import ExamRun, default_config, run_pipeline
from rubric import grade

def test_deficient_run_fails():
    # Start from an honest run, then corrupt dog's recall to break R3 (recall gate).
    honest = run_pipeline(default_config)

    # ClassMetrics is a dataclass, so dataclasses.replace builds a corrupted copy
    # without importing the class (it lives in eval_engine, loaded off disk).
    corrupted_metrics = [
        replace(m, recall=0.0, f1=0.0) if m.cls == "dog" else m
        for m in honest.metrics
    ]

    deficient = ExamRun(
        report_path=honest.report_path,
        n_clean=honest.n_clean,
        metrics=corrupted_metrics,
        composed_modules=honest.composed_modules,
        version=honest.version,
    )

    report = grade(deficient)
    assert report.passed is False
    failed_ids = {r.rid for r in report.failed()}
    assert "R3" in failed_ids
```

The deficient run targets the per-class recall criterion. A second deficient variant targets R2 by setting `n_clean != 10`, but one is enough to prove the gate fires: pick the one that aligns with how your rubric defines its criteria.

## tests/test_smoke.py

`tests/test_smoke.py` is the pytest entry that imports and re-runs the same checks. It does not duplicate logic; it imports `test_exam_passes` and `test_deficient_run_fails` from `smoke.py` and lets pytest collect them from a standard path.

```python
import pathlib
import sys

_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from smoke import test_deficient_run_fails, test_exam_passes

__all__ = ["test_exam_passes", "test_deficient_run_fails"]
```

Running `python -m pytest tests/` from the exercise root is the one-command gate. The BUILD→TEST sequence is: `python pipeline.py` exits 0 and writes `report.md`; `python -m pytest tests/` reports two tests passed.

## The Skill Write-Up

`outputs/skill-integrated-exam.md` is the portfolio surface. It documents the business problem (one repo, three scripts, and a graded report), the lineage from M1 through M8, the rubric the pipeline passes, and how to run it.

The lineage is the point. `measure.py` (M1–M3) established per-class reasoning from raw data. `vectorization_report.py` (M4) composed `measure.py` to answer a production decision. `wrangle.py` (M6) built the ingestion and cleaning contract. `eval_engine.py` (M7) turned a CSV of predictions into a per-class Markdown table. `pipeline.py` (M8) composes the last two off disk and grades the result against a rubric. That arc is what the write-up documents: not what the code does, but what it proves.

## The Standards Check

| Criterion | Where it lives |
|---|---|
| Real entry point | `python pipeline.py` runs the pipeline and exits 0 |
| README frames the business problem | `exercises/module8/run-test-and-ship/README.md` opens with the integrated-pipeline problem before the spec |
| Machine-checkable acceptance gate | `python -m pytest tests/` passes both tests; `python pipeline.py` exits 0 |
| The negative case is tested | `test_deficient_run_fails` asserts a corrupted `ExamRun` fails the criterion it offends |
| Versioned, clean layout; no secrets | reports go to `outputs/`; no committed keys; the tree is legible |
| Ships a skill artifact | `outputs/skill-integrated-exam.md` is a required output |

The gate is green when `pipeline.py` exits 0, `report.md` lands in `outputs/`, and `pytest tests/` reports two tests passed. That is a machine verdict, not a judgment call.

Azure Machine Learning frames the production standard this way: model management and deployment require a reproducible, testable pipeline whose outputs are versioned and whose acceptance criteria are expressed in code, not prose ([learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment](https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment?view=azureml-api-2)). The gate you just built meets that bar.

This lesson closes Just Python. You ship a GitHub repo where `wrangle.py`, `eval_engine.py`, and `pipeline.py` all run clean, a rubric grades the result by code not opinion, and a skill write-up turns the artifact into evidence. The gap between a script that runs and a pipeline that proves is exactly this: a gate that refuses the deficient case.

## Core Concepts

- A capstone gate has two test functions: the happy path locks the oracle numbers within tolerance, and the negative case asserts the rubric rejects a deliberately deficient run; strength is proven by what the gate refuses, not only what it ships.
- `smoke.py` and `tests/test_smoke.py` run the same checks through two entry points: `python smoke.py` for a readable terminal run, `python -m pytest tests/` for the one-command CI gate; the tests live once, in `smoke.py`, and are imported.
- Float comparisons in production smoke tests use a tolerance (`abs(result - oracle) < 1e-3`), not equality; floating-point division across Python versions is not bitwise identical.
- The compounding arc is real only when each artifact is imported, not rebuilt: `pipeline.py` imports `wrangle.py` and `eval_engine.py` off disk; the exam grades what the real artifacts produce, not a copy.

<div class="claude-handoff" data-exercise="exercises/module8/run-test-and-ship/">

**Build It in Claude Code:** Write `exercises/module8/smoke.py` with `test_exam_passes` and `test_deficient_run_fails`; write `exercises/module8/tests/test_smoke.py` that imports and re-exposes both tests; and fill out `exercises/module8/outputs/skill-integrated-exam.md` with the business problem, lineage, and how-to-run. The gate is green when `python pipeline.py` exits 0 and writes `report.md`, and `python -m pytest tests/` reports two tests passed.

</div>
