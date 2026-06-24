# The Rubric

The rubric is code, not prose. You cannot talk your way past it.

A write-up claims the pipeline passed every gate. The rubric checks. Five criteria, each falsifiable, each enforced by inspecting the artifact on disk. If the eval gate never ran, criterion three fails. Rewording the README changes nothing.

The grading instrument opens with its contract:

```python
"""
rubric.py — Module 8 pipeline grading rubric.

Grades the M8 fine-tune pipeline artifact on 5 hard criteria:
    1. Data quality gate   — dataset curation ran, dedupe + split recorded
    2. Train reproducible  — seed pinned, run hash recorded, deterministic
    3. Eval gate enforced  — M5 exact-match + F1 gate recorded as PASS
    4. Regression enforced — M7 behavioral regression recorded as PASS
    5. MLflow logged       — offline sqlite backend has >=1 run

Exit codes:
    0 = READY         (all 5 criteria pass)
    1 = NEEDS WORK    (one or more criteria failed)

The rubric is the deliverable: it grades by code, not prose.
"""
```

Each criterion names a concrete artifact: a deduped dataset, a pinned seed, a PASS record from the eval gate, a PASS record from the regression suite, an MLflow run in sqlite. None of them ask whether the write-up sounds convincing.

The criteria are a tuple, not a feeling:

```python
CRITERIA: Tuple[str, ...] = (
    "data_quality",
    "train_reproducible",
    "eval_gate_enforced",
    "regression_gate_enforced",
    "mlflow_logged",
)
```

Each criterion maps to a threshold the pipeline must record and meet:

```python
# Minimum thresholds the gate must explicitly record and meet.
EVAL_EM_THRESHOLD = 0.50
EVAL_F1_THRESHOLD = 0.60
REGRESSION_MAX_DELTA = 0.10  # abs drift allowed vs baseline
```

The exit is binary. Zero means every criterion passed. One means at least one failed. There is no partial credit.

The proof that the rubric cannot be gamed lives in smoke.py. Two scenarios, both asserted:

```python
Two scenarios are exercised and BOTH outcomes are asserted:
  1. Happy path     : full pipeline (data → train → eval gate → regress → log)
                      rubric.py MUST exit 0 (READY).
  2. Deficient path : eval gate skipped.
                      rubric.py MUST exit 1 (NEEDS WORK).
```

The deficient path is the falsification test. Skip the eval gate, run the rubric, watch criterion three fail. The rubric does not read your explanation for why you skipped it. It checks the PASS record. No record, no pass.

## Core Concepts

1. The rubric grades the artifact, not the write-up; each criterion inspects files on disk or rows in sqlite.
2. Five criteria, each falsifiable: data quality, train reproducibility, eval gate enforcement, regression gate enforcement, MLflow logging.
3. The exit is binary: 0 (READY) requires all five to pass; 1 (NEEDS WORK) means at least one failed.
4. The deficient-run test in smoke.py proves the rubric catches a skipped eval gate by asserting exit 1.

<div class="claude-handoff" data-exercise="exercises/module8/the-rubric/">
**Build It in Claude Code** · Exercise · exercises/module8/the-rubric/
</div>

The moment a rubric accepts prose as evidence, it stops being a rubric; a Production AI Engineer makes the verdict unfakeable by putting the evaluator in code.