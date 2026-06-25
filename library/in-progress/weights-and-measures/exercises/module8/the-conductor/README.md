# Exercise: The Conductor

## Goal

Write `pipeline.py` so it calls the five vendored stages in order and raises
`PipelineBlocked` the moment a gate fails.

## Why

A conductor that logs a warning and continues is not a gate, it is a suggestion. Writing the
hard-stop behavior yourself is how you internalize that a pipeline is a contract, not a
sequence of best-effort steps.

## What You Are Building

A `run_pipeline()` function that threads outputs between the five vendored modules and a
`PipelineBlocked` exception that halts the run on any gate failure.

## Steps

1. Add `lib/` to `sys.path` and import the five modules.

2. Define `PipelineBlocked(RuntimeError)`.

3. In `run_pipeline()`, call the stages in order:
   - `m3_curate.generate_raw` + `curate` -> curated data
   - `m6_train.build_and_train(curated)` -> checkpoint
   - `m5_eval.gate(checkpoint, test)` -> raise `PipelineBlocked` if not passed
   - `m7_regress.check(checkpoint)` -> raise `PipelineBlocked` if not passed
   - write `outputs/manifest.json`

4. Add a `skip_eval` parameter that omits the eval gate, so the rubric exercise can prove the
   deficient case is caught.

5. Verify: `python pipeline.py` writes a manifest; the gates never silently continue.
