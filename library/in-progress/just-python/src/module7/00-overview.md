# Module 7: Evaluation Engine

## What This Module Covers

Module 6 produced a clean dataset; Module 7 judges a model against one. You build `eval_engine.py`: it reads a batch-prediction file (`id, prediction, label`), computes per-class precision, recall, and F1 with NumPy, and writes a Markdown evaluation table. The metric math is written by hand, no sklearn, because the point is to understand precision and recall as counts, not as an import.

This is the second portfolio artifact, and the second take-home. A single accuracy number hides which class a model fails; the per-class table is what an engineer puts in a model card or a pull request, and computing it from three boolean masks is the Module 2 vectorization lesson applied to a real metric.

## Arc of Lessons

| Lesson | Title | Stage of `eval_engine.py` | Composes |
|--------|-------|---------------------------|----------|
| 1 | Load the Predictions | Read `id`/`prediction`/`label` into a typed DataFrame; an `EvalConfig` names the columns | M3, M5 |
| 2 | Confusion Counts with NumPy | Per-class TP/FP/FN as three boolean masks and a sum, no sklearn | M2 |
| 3 | Precision, Recall, and F1 | Counts to P/R/F1 in a `ClassMetrics` record; safe zero-division | M2, M5 |
| 4 | Emit, Test, and Ship | Render the Markdown table, compose `run`, the `pytest` gate + skill write-up | all |

## Throughline Artifact

`eval_engine.py` is the portfolio artifact, and it composes the book: M2 (the mask-and-reduce metric math), M3 (the read), M5 (the `ClassMetrics` dataclass and type hints). It pairs with M6 in the data layer (M6 makes the dataset, M7 evaluates predictions over it), and it links back to the Sans Python M7 evaluation tables. The acceptance gate is `smoke.py`: it asserts the per-class metrics on a locked ten-row sample, that the report renders, and that a malformed prediction file raises. The skill write-up in `outputs/skill-evaluation-engine.md` is the portfolio surface. Module 8 chains M6 and M7 under a graded rubric.

## Prerequisites

- Modules 1 through 6, especially M2 (boolean masks and reductions), M3 (Pandas), and M5 (dataclasses, type hints). M7 composes them; it does not re-teach them.
- A Python 3.11+ environment with pandas and numpy. No sklearn (the metric math is by hand) and no pyarrow (the output is Markdown).
