# The Graded Result

The rubric is the final examiner. Its exit code is the verdict.

## The Grader Refuses to Lie

The grader inspects your work across six criteria. Each is worth one point. There are no partial credits and no style points. The exit code tells the truth: zero means pass, one means fail.

```python
"""rubric.py — the Module 8 grader. Six criteria, each worth one point.

Grades the submitted fix by running it and diagnosing the result:
  1. Defect 1 fixed   - the freshness check uses the real 'now', not a future date.
  2. Defect 2 fixed   - capture_lineage records the eval verdict.
  3. Defect 3 fixed   - the freshness gate fails loud (raises) on a stale source.
  4. Lineage complete - the answer -> verdict chain can be walked end to end.
  5. Healthy run      - a freshly loaded corpus passes the gate and runs clean.
  6. Stale run blocks - a stale corpus raises FreshnessBreach (no silent success).

Exit 0 = PASS (all six), 1 = FAIL. The grade is the deliverable.
"""
```

The grader does not read your explanation. It runs the candidate pipeline twice, on a fresh corpus and a stale one, runs `diagnose.py` against the result, and checks all six criteria. Two of them are behavioural: a healthy corpus must run clean, and a stale corpus must raise.

```python
LOADED = "2026-06-24 12:00:00"
NOW_FRESH = "2026-06-24 12:05:00"   # 5 minutes later -> fresh
NOW_STALE = "2026-06-26 18:00:00"   # ~54 hours later -> stale (> 25h SLO)
```

## The Smoke Test Proves Both Directions

The smoke test is the orchestrator. It runs the broken pipeline, the fixed pipeline, the diagnostic checks, and the rubric in sequence. It exits zero only when every assertion holds, including the negative cases.

The negative group runs the broken pipeline and asserts `diagnose.py` reports `found=True` on all three defects, and that the grader fails it:

```python
check("rubric.py exits 1 on broken_pipeline", _run("rubric.py", "--pipeline", "broken_pipeline") == 1)
```

The positive group runs `fix.py`, asserts every check goes dark (`found=False`), the stale corpus raises, and the grader passes:

```python
check("rubric.py exits 0 on the fix", _run("rubric.py") == 0)
```

The defects must be detectable before you fix them, and gone after.

## Run the Full Suite

```bash
python smoke.py && python -m pytest tests/ -q && python rubric.py
```

If the smoke test passes, the rubric passes. If it fails, fix the failure first.

## Core Concepts

- The rubric exits zero when all six criteria are satisfied and one otherwise. There is no third state.
- The smoke test asserts both directions: the broken pipeline must fail the grade, and the fixed pipeline must pass it.
- `diagnose.py` reports `found=True` against the broken run and `found=False` against the fixed one; the grader reads those flags plus the run's behaviour.
- Two criteria are behavioural: a healthy corpus runs clean, a stale corpus raises rather than shipping in silence.

<div class="claude-handoff" data-exercise="exercises/module8/the-graded-result/">
**Build It in Claude Code** · Exercise · exercises/module8/the-graded-result/
</div>

The pipeline either passes the rubric or it isn't done, and for a Production AI Engineer that binary exit code is the only status report worth shipping.
