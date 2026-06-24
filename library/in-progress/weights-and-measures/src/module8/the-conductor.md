# The Conductor

`pipeline.py` is not a reimplementation. It is a conductor that calls five vendored functions and enforces their sequence. Each gate either passes or exits BLOCK; there is no third state.

## Five Functions, Two Hard Gates

The conductor wires five stages into one ordered script. Here is the flow, verbatim from the artifact:

```
curate_data() → train_model() → eval_gate() → regress() → log_artifact()
                     │                │             │
                     │                │             └── BLOCK if regression fails
                     │                └── BLOCK if eval fails
                     └── LoRA adapter (M4) + classifier head (M6)
```

Five stages. Two hard gates. The pipeline never improvises a path around a failure.

## The Conductor Calls, It Does Not Reimplement

Each stage comes from a prior module. Each is vendored into `lib/` as a read-only dependency. The pipeline imports them but never edits them:

```python
_VENDORED: Dict[str, str] = {
    "m3_curate":  "lib.m3_curate",
    "m4_tune":    "lib.m4_tune",
    "m5_eval":    "lib.m5_eval",
    "m6_train":   "lib.m6_train",
    "m7_regress": "lib.m7_regress",
}
```

The conductor does not rewrite curation logic. It does not reimplement the eval gate. It calls the function, checks the result, and either continues or stops.

## Why Each Gate Exits BLOCK

A gate that logs a warning and continues is not a gate. It is a suggestion.

When `eval_gate()` detects metric regression below threshold, the pipeline exits BLOCK. When `regress()` detects behavioral drift, the pipeline exits BLOCK. The rubric enforces this contract at the code level:

```python
CRITERIA: Tuple[str, ...] = (
    "data_quality",
    "train_reproducible",
    "eval_gate_enforced",
    "regression_gate_enforced",
    "mlflow_logged",
)
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