# The Rubric and Grading

Opinion is not a gate. Build `rubric.py`: a six-criterion acceptance rubric that reads the `ExamRun` your pipeline produced and returns a verdict in code.

## What You Build

You build three things: `CRITERIA`, the tuple that is the single source of truth for both this lesson's prose table and the checker; `grade(exam) -> RubricReport`, which reads the captured `ExamRun` and evaluates each criterion; and the worked example that shows a good run scoring 6/6 and a deficient run failing the criterion it offends.

## The Invariant

The rubric exists in two forms: a `CRITERIA` tuple in `rubric.py` and the prose table in this lesson. They must match, clause for clause. If you change a criterion here, change it there. This is not a style preference; it is the control. A rubric where the code checks one thing and the prose describes another is not a rubric; it is two separate opinions that happen to co-exist.

The `CRITERIA` tuple is the single source of truth because code runs. Prose describes.

## The Six Criteria

These are the criteria `grade` checks. The `CRITERIA` tuple in `rubric.py` carries the same six IDs and statements, in this order.

| ID | Criterion | Passes When |
|----|-----------|-------------|
| R1 | RUNS | the pipeline ran end to end and wrote `report.md`: `exam.report_path` exists on disk |
| R2 | SCHEMA-VALID | the wrangle stage validated the data: `exam.n_clean == 10` (no null labels, no duplicate ids leaked through) |
| R3 | METRICS-CORRECT | every per-class precision, recall, and F1 matches the locked oracle within 1e-3 |
| R4 | COMPOSED | the run imported the real `wrangle.py` and `eval_engine.py` off disk: `composed_modules` lists both; nothing re-implemented inline |
| R5 | PROBLEM-FRAMED | the report names the dataset, the metric, and the headline finding (the weakest class) |
| R6 | TESTED+VERSIONED | the run declares a version (`exam.version`); the smoke suite enforces the negative case |

## Why R3 and R5 Both Matter

A single accuracy number hides the failing class. On the ten-row sample, the macro-average F1 is 0.707. That number does not tell you that `dog` has recall 0.500: two of its four actual instances were predicted as something else. The per-class table surfaces it.

Azure AI Language Services states this directly: precision measures how many of the predicted classes are correctly labeled; recall measures how many of the actual class instances were found ([learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics](https://learn.microsoft.com/azure/ai-services/language-service/custom-text-classification/concepts/evaluation-metrics)). Low recall on a class means the model is systematically missing it, not predicting it falsely. Those are different failure modes with different fixes, and they only separate when you look at the per-class breakdown.

R3 locks the numbers so a grader cannot accidentally accept a run with corrupted predictions. R5 requires the report to name the finding: the dataset, the metric, and which class is weakest. A report that prints a table without interpreting it is not framed; it is output.

The locked oracle for R3:

| class | precision | recall | F1 | support |
|-------|-----------|--------|----|---------|
| cat | 0.750 | 0.750 | 0.750 | 4 |
| dog | 0.667 | 0.500 | 0.571 | 4 |
| bird | 0.667 | 1.000 | 0.800 | 2 |
| **macro avg** | **0.694** | **0.750** | **0.707** | **10** |

The weakest class is `dog` at recall 0.500. R5 passes only when the report names it.

## The rubric.py Shape

`rubric.py` has four pieces. The `CRITERIA` tuple is first because it is the source of truth. Then two dataclasses. Then `grade`.

```python
from __future__ import annotations
from dataclasses import dataclass
import pathlib

# The six criteria, in order. (id, one-line statement).
# This tuple is the single source of truth: the prose table in the lesson
# and this tuple are one rubric; change one, change both.
CRITERIA = (
    ("R1", "RUNS: the pipeline ran end to end and wrote report.md"),
    ("R2", "SCHEMA-VALID: n_clean == 10 (no null labels, no duplicate ids)"),
    ("R3", "METRICS-CORRECT: per-class P/R/F1 matches the oracle within 1e-3"),
    ("R4", "COMPOSED: run imported wrangle.py and eval_engine.py off disk; nothing re-implemented inline"),
    ("R5", "PROBLEM-FRAMED: report names the dataset, the metric, and the weakest class"),
    ("R6", "TESTED+VERSIONED: the run declares a version; the smoke suite enforces the negative case"),
)


@dataclass
class CriterionResult:
    rid:       str
    statement: str
    passed:    bool
    detail:    str


@dataclass
class RubricReport:
    results: list
    passed:  bool

    def failed(self) -> list:
        return [r for r in self.results if not r.passed]

    def as_lines(self) -> list:
        lines = []
        for r in self.results:
            mark = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{mark}] {r.rid}  {r.statement}")
            if not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append("")
        lines.append(
            f"  VERDICT: {'PASS' if self.passed else 'FAIL'} "
            f"({sum(r.passed for r in self.results)}/{len(self.results)} criteria)"
        )
        return lines
```

`grade` reads only the captured `ExamRun` fields. It never re-runs the pipeline.

```python
# Locked oracle for R3 (per-class; tolerance 1e-3)
_ORACLE = {
    "cat":  {"precision": 0.750, "recall": 0.750, "f1": 0.750, "support": 4},
    "dog":  {"precision": 0.667, "recall": 0.500, "f1": 0.571, "support": 4},
    "bird": {"precision": 0.667, "recall": 1.000, "f1": 0.800, "support": 2},
}
_TOL = 1e-3


def grade(exam) -> RubricReport:
    """Grade a captured ExamRun against the six criteria.

    Reads exam.report_path, exam.n_clean, exam.metrics (list of ClassMetrics
    with .cls/.precision/.recall/.f1/.support), exam.composed_modules,
    and exam.version.

    Returns a RubricReport whose .passed is True only when all six pass.
    """
    # R1 RUNS: the report file exists on disk.
    r1 = bool(exam.report_path) and pathlib.Path(exam.report_path).exists()
    r1_detail = (
        f"report_path={exam.report_path!r} does not exist"
        if not r1 else
        f"report written to {exam.report_path}"
    )

    # R2 SCHEMA-VALID: the wrangle stage produced exactly 10 clean rows.
    r2 = exam.n_clean == 10
    r2_detail = (
        f"n_clean={exam.n_clean} (expected 10): null labels or duplicate ids leaked through"
        if not r2 else
        f"n_clean={exam.n_clean}"
    )

    # R3 METRICS-CORRECT: per-class P/R/F1 match the oracle within 1e-3.
    by_class = {m.cls: m for m in exam.metrics}
    r3_misses = []
    for cls, expected in _ORACLE.items():
        if cls not in by_class:
            r3_misses.append(f"{cls} missing from metrics")
            continue
        m = by_class[cls]
        for field in ("precision", "recall", "f1"):
            diff = abs(getattr(m, field) - expected[field])
            if diff > _TOL:
                r3_misses.append(
                    f"{cls}.{field}: got {getattr(m, field):.4f}, expected {expected[field]:.4f}"
                )
    r3 = len(r3_misses) == 0
    r3_detail = (
        "; ".join(r3_misses) if not r3 else
        "all per-class P/R/F1 within 1e-3 of oracle"
    )

    # R4 COMPOSED: both modules appear in composed_modules; nothing re-implemented inline.
    composed = set(exam.composed_modules or [])
    required = {"wrangle.py", "eval_engine.py"}
    missing = required - composed
    r4 = len(missing) == 0
    r4_detail = (
        f"missing from composed_modules: {sorted(missing)}"
        if not r4 else
        f"composed_modules includes {sorted(composed)}"
    )

    # R5 PROBLEM-FRAMED: report content names dataset, metric, and weakest class.
    report_text = ""
    if exam.report_path and pathlib.Path(exam.report_path).exists():
        report_text = pathlib.Path(exam.report_path).read_text(encoding="utf-8").lower()
    framing_checks = {
        "dataset name": any(
            word in report_text for word in ("predictions", "dataset", "ten-row", "sample")
        ),
        "metric named": any(
            word in report_text for word in ("f1", "precision", "recall")
        ),
        "weakest class named": "dog" in report_text,
    }
    missing_framing = [k for k, v in framing_checks.items() if not v]
    r5 = len(missing_framing) == 0
    r5_detail = (
        f"report missing: {', '.join(missing_framing)}"
        if not r5 else
        "report names dataset, metric, and weakest class"
    )

    # R6 TESTED+VERSIONED: the run declares a version. The smoke suite enforces
    # the negative case (test_deficient_run_fails must pass for the gate to be green).
    r6 = bool(exam.version)
    r6_detail = (
        f"version={exam.version!r} is missing"
        if not r6 else
        f"version={exam.version}"
    )

    flags = {
        "R1": (r1, r1_detail), "R2": (r2, r2_detail),
        "R3": (r3, r3_detail), "R4": (r4, r4_detail),
        "R5": (r5, r5_detail), "R6": (r6, r6_detail),
    }
    results = [
        CriterionResult(rid, statement, flags[rid][0], flags[rid][1])
        for rid, statement in CRITERIA
    ]
    return RubricReport(results=results, passed=all(r.passed for r in results))
```

## The Worked Example: Two Runs

`grade` reads `ExamRun` fields; it never touches the model or the CSV. The verdict is reproducible from the record. Same run, same grade, every time.

**The good run (6/6 PASS):**

```
ExamRun(
    report_path="outputs/report.md",        # file exists on disk
    n_clean=10,                             # wrangle passed
    metrics=[...],                          # per-class P/R/F1 matches oracle
    composed_modules=["wrangle.py", "eval_engine.py"],
    version="1.0",
)
```

```
  [PASS] R1  RUNS: the pipeline ran end to end and wrote report.md
  [PASS] R2  SCHEMA-VALID: n_clean == 10 (no null labels, no duplicate ids)
  [PASS] R3  METRICS-CORRECT: per-class P/R/F1 matches the oracle within 1e-3
  [PASS] R4  COMPOSED: run imported wrangle.py and eval_engine.py off disk; nothing re-implemented inline
  [PASS] R5  PROBLEM-FRAMED: report names the dataset, the metric, and the weakest class
  [PASS] R6  TESTED+VERSIONED: run declares a version and the smoke gate is green including the negative case

  VERDICT: PASS (6/6 criteria)
```

**The deficient run (R2 and R3 FAIL):**

A wrangle stage that skips deduplication lets duplicate rows through. `n_clean` becomes 12. Now the counts are wrong, and dog's recall shifts because the duplicate rows added fake instances.

```
ExamRun(
    report_path="outputs/report.md",        # file exists
    n_clean=12,                             # deduplication skipped: 2 duplicate rows leaked
    metrics=[                               # corrupted: dog recall is now 0.667, not 0.500
        ClassMetrics("cat",  0.750, 0.750, 0.750, 4),
        ClassMetrics("dog",  0.667, 0.667, 0.667, 6),   # wrong support, wrong recall
        ClassMetrics("bird", 0.667, 1.000, 0.800, 2),
    ],
    composed_modules=["wrangle.py", "eval_engine.py"],
    version="1.0",
)
```

```
  [PASS] R1  RUNS: ...
  [FAIL] R2  SCHEMA-VALID: n_clean=12 (expected 10): null labels or duplicate ids leaked through
         -> n_clean=12 (expected 10): null labels or duplicate ids leaked through
  [FAIL] R3  METRICS-CORRECT: per-class P/R/F1 matches the oracle within 1e-3
         -> dog.recall: got 0.6667, expected 0.5000; dog.f1: got 0.6667, expected 0.5710
  [PASS] R4  COMPOSED: ...
  [PASS] R5  PROBLEM-FRAMED: ...
  [PASS] R6  TESTED+VERSIONED: ...

  VERDICT: FAIL (4/6 criteria)
```

The deficient run fails exactly the criteria it offends. R2 and R3 fail; R1, R4, R5, and R6 pass. That precision is the point: the rubric tells you which criterion broke, which tells you where to look. A rubber stamp returns PASS or FAIL. A gate returns which.

## Core Concepts

- `CRITERIA` is the single source of truth: the prose table in this lesson and the tuple in `rubric.py` are one rubric in two forms; change one, change both.
- `grade` reads the captured `ExamRun` and never re-runs the pipeline; the verdict is reproducible from the record, so grading is deterministic and auditable.
- A deliberately deficient run must fail the criterion it offends: R2 fails when `n_clean != 10`; R3 fails when any per-class metric drifts past 1e-3; a rubric that passes a corrupted run is not a gate, it is a rubber stamp.
- Per-class precision, recall, and F1 surface the failing class that a single accuracy number hides; R5 requires the report to name it, because a table without an interpretation is not a finding.

<div class="claude-handoff" data-exercise="exercises/module8/the-rubric-and-grading/">

**Build It in Claude Code:** Build `exercises/module8/rubric.py` with the `CRITERIA` tuple and `grade(exam) -> RubricReport`. Verify that `grade` on the good `ExamRun` returns `passed == True` with 6/6, and that `grade` on a deficient `ExamRun` (corrupted dog recall, or `n_clean` wrong) returns `passed == False` failing the exact criterion it offends. The prose table in this lesson and your `CRITERIA` tuple are one rubric; they must match.

</div>
