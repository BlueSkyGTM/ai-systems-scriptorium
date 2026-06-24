# The Graded Result

The rubric is the final examiner. Its exit code is the verdict.

## The Grader Refuses to Lie

The grader inspects your work across six criteria. Each criterion is worth one point. There are no partial credits and no style points. The exit code tells the truth: zero means pass, one means fail.

```python
"""
rubric.py
The Module 8 grader. Six criteria, each worth one point.

The grader works by:
  1. Static inspection of the student's fix.py (text + AST)
  2. Dynamic execution of fix.py against a fresh tempdir
  3. Execution of diagnose.py against the resulting lineage + corpus DBs
  4. Direct inspection of the lineage DB for the previously-broken edge

Exit codes:
  0  PASS  (all 6 criteria satisfied)
  1  FAIL  (one or more criteria failed; stderr lists which)

Usage:
  python rubric.py
  python rubric.py --fix ./broken_pipeline.py   # negative-case self-check
  python rubric.py --skip-runtime               # static-only grade

Contract honored for smoke.py:
  - rubric.py against the *broken* pipeline exits 1 (negative case)
  - rubric.py against a correct fix.py exits 0 (positive case)
"""
```

The grading process runs four phases. Static inspection reads your fix.py as text and AST. Dynamic execution runs fix.py in a fresh tempdir. Your diagnose.py runs against the resulting databases. The grader then inspects the lineage DB directly for the previously broken edge.

The constants leave no room for ambiguity:

```python
DEFAULT_FIX = Path(__file__).resolve().parent / "fix.py"
DEFAULT_DIAGNOSE = Path(__file__).resolve().parent / "diagnose.py"
DEFAULT_LIB = Path(__file__).resolve().parent.parent / "lib"

PASS = 0
FAIL = 1
```

## The Smoke Test Proves Both Directions

The smoke test is the orchestrator. It runs the broken pipeline, the fixed pipeline, the diagnostic queries, and the rubric in sequence. It exits zero only when every assertion holds, including the negative case.

The negative assertion group runs first. It feeds `broken_pipeline.py` to the rubric and asserts the exit code is one. It runs `diagnose.py` against the broken output and asserts every finding is non-None. The defects must be detectable before you fix them.

The positive assertion group runs second. It feeds `fix.py` to the rubric and asserts the exit code is zero. It runs `diagnose.py` against the clean output and asserts every finding is None. The fixes must be complete.

The test suite pins this contract explicitly:

```python
"""
  * rubric.py exits 1 on broken_pipeline.py and 0 on fix.py.
  * smoke.py exits 0 (the negative case is itself part of the suite).
"""
```

## Run the Full Suite

```
python smoke.py && python rubric.py
```

If the smoke test passes, the rubric should pass. If the smoke test fails, fix the failure first.

## Core Concepts

- The rubric exits zero when all six criteria are satisfied. It exits one otherwise. There is no third state.
- The smoke test asserts both directions: the broken pipeline must fail the rubric, and the fixed pipeline must pass it.
- `diagnose.py` must return non-None findings against the broken artifacts and None findings against the fixed artifacts.
- The grader combines static inspection, dynamic execution, diagnostic queries, and direct lineage inspection across its four phases.

<div class="claude-handoff" data-exercise="exercises/module8/the-graded-result/">
**Build It in Claude Code** · Exercise · exercises/module8/the-graded-result/
</div>

The pipeline either passes the rubric or it isn't done, and for a Production AI Engineer that binary exit code is the only status report worth shipping.