# The Conductor

`pipeline.py` is not a reimplementation. It is a conductor that calls five vendored functions and enforces their sequence. Each gate either passes or exits BLOCK; there is no third state.

## Five Functions, Two Hard Gates

The conductor wires five stages into one ordered script. Here is the flow, from the artifact:

```
curate_data  -> m3_curate : validate, dedupe, split the raw tickets
train_model  -> m6_train  : train the classifier (via the m4_tune loop)
eval_gate    -> m5_eval   : accuracy + macro-F1 vs baseline; BLOCK if it fails
regress      -> m7_regress: pinned golden tickets must route correctly; BLOCK if not
log_artifact -> write outputs/manifest.json
```

Five stages. Two hard gates. The pipeline never improvises a path around a failure.

## The Conductor Calls, It Does Not Reimplement

Each stage comes from a prior module. Each is vendored into `lib/` as a read-only dependency. The pipeline imports them but never edits them; `lib/__init__.py` lists them in order:

```python
VENDORED = ("m3_curate", "m4_tune", "m6_train", "m5_eval", "m7_regress")
```

The conductor does not rewrite curation logic. It does not reimplement the eval gate. It calls the function, checks the result, and either continues or stops.

## Why Each Gate Exits BLOCK

A gate that logs a warning and continues is not a gate. It is a suggestion.

When the eval gate finds the model failing to beat the baseline, the pipeline raises `PipelineBlocked`. When the regression check finds a misrouted golden ticket, the pipeline raises `PipelineBlocked`. The rubric enforces this contract at the code level:

```python
criteria = {
    "data_curated":        ...,
    "model_trained":       ...,
    "eval_gate_enforced":  ...,
    "regression_enforced": ...,
    "artifact_logged":     ...,
}
```

If the eval gate is skipped, the rubric returns `NEEDS WORK` (exit 1) and the artifact does not ship. Silent failure is structurally impossible because the conductor treats every gate as a hard stop, not a checkpoint to acknowledge and ignore.

## The Same Pattern as DC Module 7

This conductor shape is not new. DC Module 7's `pipeline_flow.py` uses the same contract: ordered function calls, hard exits on failure, no silent degradation. Module 8 scales the pattern from two stages to five, but the principle is identical.

Call a function. Check the result. Stop on failure. Move on only when the gate passes.

## Core Concepts

- `pipeline.py` orchestrates five vendored functions in a fixed sequence; it reuses sealed modules from M3 through M7 rather than rewriting their logic.
- Each gate (`eval_gate`, `regress`) exits BLOCK on failure. No gate logs a warning and continues.
- The rubric grades the pipeline by code: if a gate is skipped, the rubric returns exit 1 (`NEEDS WORK`) and the artifact does not ship.
- The conductor pattern matches DC Module 7's `pipeline_flow.py`: ordered calls, hard exits, zero silent degradation.

<div class="claude-handoff" data-exercise="exercises/module8/the-conductor/">
**Build It in Claude Code** · Exercise · exercises/module8/the-conductor/
</div>

If a gate can be skipped without consequence, you have built a logging system, not a pipeline.