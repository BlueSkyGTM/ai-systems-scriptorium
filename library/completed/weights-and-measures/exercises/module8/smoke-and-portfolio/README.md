# Exercise: Smoke and Portfolio

## Goal

Write `smoke.py` so it proves the rubric fires in both directions, then complete the
portfolio write-up.

## Why

The pipeline is finished when the smoke test proves the rubric passes a clean run and fails
a deficient one. Without the deficient case, a green run tells you nothing.

## What You Are Building

A `smoke.py` that runs the full pipeline (rubric READY), then a deficient run (rubric NEEDS
WORK), asserting both, and a completed `outputs/skill-pipeline.md`.

## Steps

1. Run `run_pipeline()` and assert each stage's manifest summary: dedupe happened, the split
   is disjoint, training cleared the floor, the eval gate passed, every golden case passed,
   the manifest was written.

2. Grade the run with `rubric.run_rubric()`; assert all five criteria pass and the verdict is
   READY. Run `rubric.py` as a subprocess; assert exit 0.

3. Run `run_pipeline(skip_eval=True)`. Grade it; assert `eval_gate_enforced` is False and the
   verdict is NEEDS WORK. Run `rubric.py` against that manifest; assert exit 1.

4. Count assertions, print a PASS summary, exit 0 only if there are zero failures.

5. Run the full suite together:

   ```bash
   python smoke.py && python -m pytest tests/ -q && python rubric.py
   ```

6. Fill in `outputs/skill-pipeline.md` with the real stage results and the rubric verdict.
