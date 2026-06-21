# Module 8: Integrated Python Engineering Exam

## What This Module Covers

Module 6 cleaned a corpus; Module 7 judged a model on one. Module 8 is the take-home that chains both. You build `pipeline.py`: it imports your `wrangle.py` (M6) and `eval_engine.py` (M7) off disk, runs a raw corpus through the wrangler, feeds the clean labels and a batch of predictions to the eval engine, and writes one integrated report. A `rubric.py` then grades the produced run against six acceptance criteria in code, not opinion.

This is the capstone, and it is not a new build. The rule of the exam is worth stating twice: compose the artifacts you already shipped; do not rebuild them. An engineer who can wire prior artifacts into a reproducible, graded pipeline is showing the thing a single script cannot: the infrastructure, not just the result.

## Arc of Lessons

| Lesson | Title | What You Do | Composes |
|--------|-------|-------------|----------|
| 1 | The Exam | Frame the take-home: two inputs in, one graded report out; bundle the sample corpus and predictions | M6, M7 |
| 2 | Compose the Pipeline | Build `pipeline.py` and `artifact_adapter.py`; import `wrangle.py` and `eval_engine.py` off disk and chain them | M6, M7 |
| 3 | The Rubric and Grading | Build `rubric.py`: the six criteria in code, matching the prose; grade by code, fail the deficient run | all |
| 4 | Run, Test, and Ship | The `pytest` smoke gate (green run plus a deficient run that fails), the skill write-up, the finished repo | all |

## Throughline Artifact

`pipeline.py` is the terminal node of the whole book. The arc has been building one structure the entire way: `measure.py` (M1 through M3) became the input `vectorization_report.py` (M4) composed; `wrangle.py` (M6) and `eval_engine.py` (M7) are the two portfolio artifacts; `pipeline.py` (M8) imports the last two off disk and chains them. The capstone composes the prior artifacts; it does not restate them. The acceptance gate is `smoke.py`: it runs the chain on a locked sample, grades it 6/6 with `rubric.py`, and proves a deliberately deficient run fails the criterion it offends. The skill write-up in `outputs/skill-integrated-exam.md` is the portfolio surface. The reader ships one GitHub repo where three scripts run clean and a rubric grades the result.

## Prerequisites

- Modules 1 through 7, especially M6 (`wrangle.py`) and M7 (`eval_engine.py`). The exam imports both off disk; they must exist and pass their own gates before M8 can run.
- A Python 3.11+ environment with pandas, numpy, pyarrow (the wrangler emits Parquet), and pytest. No sklearn, no network, no live model: the gate is deterministic and offline.
