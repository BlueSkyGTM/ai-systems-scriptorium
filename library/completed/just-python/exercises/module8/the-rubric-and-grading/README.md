# Exercise: The Rubric and Grading

A pipeline that runs is not a pipeline that is right. Build `rubric.py`: the acceptance checker that reads the `ExamRun` your pipeline produced and returns a graded verdict in code.

## The Business Problem

Correctness is a claim. The rubric makes it checkable. Without a checker, "the pipeline passed" means someone looked at the output and felt good about it. With a checker, it means six specific criteria evaluated to `True` against a captured record, and any of them can be inspected, reproduced, or failed independently.

The exam's rubric is the hireability strong-project bar applied to a data pipeline: does it run, does it clean correctly, are the numbers right, did it compose real modules, does the report frame a finding, and is it tested and versioned. Each criterion is a pass/fail check. The verdict is computed, not judged.

## What You Build

Build `exercises/module8/rubric.py`. It exports three things:

1. `CRITERIA`: a tuple of `(id, statement)` pairs, one per criterion, in the order below.
2. `grade(exam) -> RubricReport`: reads the captured `ExamRun` and evaluates each criterion.
3. `RubricReport` and `CriterionResult`: the return types.

## The Invariant

The prose table in the lesson (`src/module8/the-rubric-and-grading.md`) and the `CRITERIA` tuple in your `rubric.py` are one rubric in two forms. They must match, clause for clause. If you change a criterion in the code, update the lesson. Change the lesson, update the code. The `CRITERIA` tuple is the single source of truth because it runs.

## The Six Criteria

Implement these six, in this order, with these IDs:

| ID | Criterion | Passes When |
|----|-----------|-------------|
| R1 | RUNS | `exam.report_path` exists on disk |
| R2 | SCHEMA-VALID | `exam.n_clean == 10` |
| R3 | METRICS-CORRECT | every per-class P/R/F1 matches the oracle within 1e-3 |
| R4 | COMPOSED | `exam.composed_modules` contains both `"wrangle.py"` and `"eval_engine.py"` |
| R5 | PROBLEM-FRAMED | the report at `exam.report_path` names the dataset, the metric, and the weakest class |
| R6 | TESTED+VERSIONED | `exam.version` is set; the smoke suite enforces the negative case |

The locked oracle for R3 (tolerance 1e-3):

| class | precision | recall | F1 | support |
|-------|-----------|--------|----|---------|
| cat | 0.750 | 0.750 | 0.750 | 4 |
| dog | 0.667 | 0.500 | 0.571 | 4 |
| bird | 0.667 | 1.000 | 0.800 | 2 |

The weakest class is `dog` at recall 0.500. R5 passes only when the report names it.

## The ExamRun Contract

`grade` receives an `ExamRun` with these fields (produced by `pipeline.py` from lesson 2):

```python
@dataclass
class ExamRun:
    report_path:      str             # path to the written report.md (may not exist)
    n_clean:          int             # rows after wrangle stage
    metrics:          list            # list of ClassMetrics; each has .cls, .precision, .recall, .f1, .support
    composed_modules: list            # names of modules imported off disk (["wrangle.py", "eval_engine.py"])
    version:          str             # version string declared by the run
```

`grade` reads these fields only. It never re-runs the pipeline, never touches the CSV, never re-imports the model. R6's "tested" half is enforced by the smoke suite in lesson 4, not by a field on the run: `test_deficient_run_fails` must pass for the gate to be green.

## The Signatures

```python
from __future__ import annotations
from dataclasses import dataclass

CRITERIA = (
    ("R1", "RUNS: ..."),
    # ... fill in all six
)

@dataclass
class CriterionResult:
    rid:       str
    statement: str
    passed:    bool
    detail:    str

@dataclass
class RubricReport:
    results: list      # list[CriterionResult]
    passed:  bool      # True only when all six pass

    def failed(self) -> list: ...   # returns only the failing CriterionResults
    def as_lines(self) -> list: ... # returns a printable verdict, one line per criterion


def grade(exam) -> RubricReport:
    ...
```

Start with `CRITERIA`. Then write one criterion check at a time. After each, confirm it can pass and fail independently.

## Acceptance Check

Your `rubric.py` passes when:

1. `grade(good_exam)` returns `passed == True` with all six criteria passing (6/6 in `.as_lines()`).
2. `grade(deficient_exam)` returns `passed == False` and `.failed()` contains exactly the criterion the deficient run offends, not more, not fewer.

Test both directions. For the deficient run, use a corrupted prediction that shifts `dog`'s recall (e.g., set `n_clean=12` to offend R2, or pass `dog.recall=0.667` to offend R3). Confirm the failing criterion is the right one.

A rubric that passes a deficient run is not a gate; it is a rubber stamp. The negative case is not optional.

## Files to Create

- `exercises/module8/rubric.py`: the checker (the only file this exercise asks for).

Do not edit `wrangle.py`, `eval_engine.py`, `pipeline.py`, or `smoke.py`: those are other lessons' artifacts. Do not re-implement their logic inline; R4 checks that you composed the real modules, not rebuilt them.

## Skill Write-Up

When the gate is green, write `exercises/module8/outputs/skill-rubric-and-grading.md`. Frame it as a portfolio piece: the problem it solves, what the rubric enforces, and why grading-by-code is stronger than grading-by-feel.
