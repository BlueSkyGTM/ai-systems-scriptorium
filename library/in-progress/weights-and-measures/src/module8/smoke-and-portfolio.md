# The Smoke Test Proves the Rubric Fires

The pipeline is not finished when it runs. It is finished when the smoke test proves the rubric passes a clean run and fails a broken one.

A smoke test that only checks the happy path proves nothing. You need two assertions: the full pipeline earns a passing grade, and a sabotaged pipeline earns a failing grade. Both outcomes must hold. 

The contract is documented in the entrypoint.

```python
"""smoke.py — end-to-end oracle for the Module 8 pipeline artifact.

Proves the composition and the grader, in both directions:
  1. Full pipeline run: every stage produces its summary; the manifest is written.
  2. rubric.py grades that run READY (all five criteria pass).
  3. Deficient run (eval gate skipped): the pipeline still completes...
  4. ...but rubric.py grades it NEEDS WORK, tripping exactly the eval-gate criterion.
"""
```

Run the full validation suite in a single chain.

```
python smoke.py && python -m pytest tests/ -v && python rubric.py
```

The happy path exercises every stage in order. The pipeline composes curation, training, the eval gate, and the regression suite into a single loop.

```
curate_data  -> m3_curate : validate, dedupe, split the raw tickets
train_model  -> m6_train  : train the classifier (via the m4_tune loop)
eval_gate    -> m5_eval   : accuracy + macro-F1 vs baseline; BLOCK if it fails
regress      -> m7_regress: pinned golden tickets must route correctly; BLOCK if not
log_artifact -> write outputs/manifest.json
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