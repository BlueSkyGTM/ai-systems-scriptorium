# Exercise: The Rubric

## Goal

Write `rubric.py` so it reads the pipeline manifest and grades five criteria, exiting READY
(0) or NEEDS WORK (1).

## Why

A write-up can claim anything. A rubric in code cannot be talked past: it inspects the
manifest and returns a binary verdict. The deficient-run case is the proof the rubric
actually bites.

## What You Are Building

A `grade(manifest)` function returning the five criteria and a READY verdict, plus a
`run_rubric()` that reads `outputs/manifest.json` and a `main()` that exits on the verdict.

## Steps

1. Read `outputs/manifest.json`.

2. Grade five criteria, each a boolean from the manifest:

   ```python
   criteria = {
       "data_curated":        curated["dupes_removed"] > 0 and curated["disjoint"],
       "model_trained":       trained["train_acc"] >= TRAIN_ACC_FLOOR,
       "eval_gate_enforced":  eval_s is not None and eval_s["passed"],
       "regression_enforced": regress is not None and regress["passed"],
       "artifact_logged":     manifest["logged"],
   }
   ```

3. `ready = all(criteria.values())`. Print which criteria passed.

4. `main()` returns 0 if ready else 1.

5. Verify both directions: grade a full run (READY), then a `skip_eval` run, and confirm
   `eval_gate_enforced` is the criterion that fails.
