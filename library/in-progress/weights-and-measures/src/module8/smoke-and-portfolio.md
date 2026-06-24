# The Smoke Test Proves the Rubric Fires

The pipeline is not finished when it runs. It is finished when the smoke test proves the rubric passes a clean run and fails a broken one.

A smoke test that only checks the happy path proves nothing. You need two assertions: the full pipeline earns a passing grade, and a sabotaged pipeline earns a failing grade. Both outcomes must hold. 

The contract is documented in the entrypoint.

```python
"""smoke.py — end-to-end smoke test for the Module 8 pipeline.

Runs ``pipeline.py`` on synthetic fixtures, then ``rubric.py``.

Two scenarios are exercised and BOTH outcomes are asserted:
  1. Happy path     : full pipeline (data → train → eval gate → regress → log)
                      rubric.py MUST exit 0 (READY).
  2. Deficient path : eval gate skipped.
                      rubric.py MUST exit 1 (NEEDS WORK).
"""
```

Run the full validation suite in a single chain.

```
python smoke.py && python -m pytest tests/ -v && python rubric.py
```

The happy path exercises every stage in order. The pipeline composes curation, training, the eval gate, the classifier, and the regression suite into a single loop.

```python
curate_data() → train_model() → eval_gate() → regress() → log_artifact()
                     │                │             │
                     │                │             └── BLOCK if regression fails
                     │                └── BLOCK if eval fails
                     └── LoRA adapter (M4) + classifier head (M6)
```

The deficient path sabotages the loop by skipping the eval gate. The rubric grades the code, detects the missing gate, and exits with a failure status.

```python
    0 = READY         (all 5 criteria pass)
    1 = NEEDS WORK    (one or more criteria failed)
```

If the deficient path passes, your rubric is broken. The pipeline either ships a READY artifact or BLOCKS.

## Core Concepts

1. A smoke test must assert both the happy path and the deficient path to prove the rubric enforces gates.
2. The happy path requires the rubric to exit 0; the deficient path requires it to exit 1.
3. The full validation suite executes `python smoke.py`, `python -m pytest tests/ -v`, and `python rubric.py`.
4. The pipeline blocks on any failure: there is no third state between READY and NEEDS WORK.

<div class="claude-handoff" data-exercise="exercises/module8/smoke-and-portfolio/">
**Build It in Claude Code** · Exercise · exercises/module8/smoke-and-portfolio/
</div>

Skip the deficient case in CI and you ship a rubric that rubber-stamps broken pipelines.