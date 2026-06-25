# The Diagnostic Exam

You have built a pipeline that runs; now prove you can fix one that does not.

Modules 1 through 7 taught you to build. Module 8 hands you a broken version of the [M7 multi-source corpus pipeline](module7/the-orchestrated-run.md) and demands a diagnosis, a fix, and a passing grade.

Three defects sit inside `broken_pipeline.py`. The unit tests are green. The reviewers approved the diff. The system is wrong. You find every defect using only the artifacts the pipeline produces, repair them, and clear the rubric.

## The Exam Setup

The scenario: a stale-retrieval incident at 03:14 on a Tuesday. A junior analyst flagged it last night. One stale answer reached a regulator. Legal is aware. You have until standup.

You receive `broken_pipeline.py`, read-only, and a directory. You do not receive a list of defects. You receive symptoms.

The artifact set lives in `module8-exam/`:

- `broken_pipeline.py`: the corrupted M7 pipeline. Three deliberate defects. Do not edit.
- `diagnose.py`: you write this. Six diagnostic queries against the SQLite lineage and corpus databases.
- `fix.py`: you write this. The corrected pipeline that clears all six rubric criteria.
- `rubric.py`: the grader. Six criteria, one point each. Static inspection, dynamic execution, direct database checks.

From `rubric.py`:

```
Exit codes:
  0  PASS  (all 6 criteria satisfied)
  1  FAIL  (one or more criteria failed; stderr lists which)
```

## The Diagnostic Queries

You prove the breakage from the data the system emitted, then confirm it in code. No source-diving first.

`diagnose.py` exposes six checks (`q1` through `q6`). Each returns a finding dict whose `found` flag is `True` against the broken run and `False` against the fixed one. Six queries, three defects, two angles each.

## The Fix

You produce `fix.py`: the full corrected pipeline, not a patch. Restore the real batch timestamp. Complete the lineage chain. Fail loud at the freshness gate.

The rubric runs your fix from scratch in a tempdir, checks the output databases, and inspects your code statically. Every defect must disappear.

## The Graded Result

`rubric.py` exits 1 on `broken_pipeline.py` and 0 on a correct `fix.py`. No partial credit.

`smoke.py` orchestrates the full cycle: run the broken pipeline, confirm the rubric fails, run your fix, confirm the rubric passes. The negative case is itself part of the suite. It exits 0 or it does not.

When the pager fires at 03:14, no one hands you a diff; you get a database full of clues and a deadline.

## Core Concepts

- The exam provides a broken pipeline with three injected defects and grades you on diagnosis and repair.
- You write `diagnose.py` (six checks `q1` through `q6`) and `fix.py` (the corrected pipeline); `rubric.py` grades the result.
- The rubric exits 0 on a correct fix and 1 on the broken pipeline, with no partial credit.
- `smoke.py` asserts both cases: the broken pipeline fails, the fixed pipeline passes, and the whole suite exits 0.