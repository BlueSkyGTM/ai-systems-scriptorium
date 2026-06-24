# Module 8: Artifact, The Full Fine-Tune Pipeline

The full fine-tune pipeline is not a feature; it is a gate-sequence with a verdict.

## What You Build

Five vendored modules composed by `pipeline.py`, graded by `rubric.py`. The modules are sealed copies of prior work:

- `m3_curate`: dataset curation (validate + dedupe + split)
- `m4_tune`: LoRA adapter fine-tune
- `m5_eval`: exact-match + F1 evaluation gate
- `m6_train`: classifier / model training glue
- `m7_regress`: behavioral regression suite

The conductor calls them in order:

```
curate_data() → train_model() → eval_gate() → regress() → log_artifact()
```

Two gates block mid-flight. `eval_gate()` exits BLOCK if the model scores below threshold. `regress()` exits BLOCK on behavioral drift. The pipeline ships READY or BLOCKS. No third state.

## Why The Rubric Is The Deliverable

A pipeline that runs is not a pipeline that passes. The rubric grades code, not prose:

```python
CRITERIA: Tuple[str, ...] = (
    "data_quality",
    "train_reproducible",
    "eval_gate_enforced",
    "regression_gate_enforced",
    "mlflow_logged",
)
```

Exit `0` means READY. Exit `1` means NEEDS WORK. Skip a gate and the rubric fails loudly.

## The Vendoring Contract

Same composition contract as DC M7, different domain. Vendor prior modules as read-only dependencies. Import from them. Never edit them. The rubric verifies the composition holds.

## Module Path

**Composition.** You write `pipeline.py` to call each vendored module in sequence, thread outputs between stages, and enforce two blocking gates.

**Training And Evaluation.** M4 LoRA meets M6 classifier. M5 enforces the eval gate: exact-match must clear 0.50, F1 must clear 0.60.

**Regression And Logging.** M7 checks behavioral drift against fixed fixtures; drift above 0.10 blocks. Every artifact lands in MLflow with a sqlite backend.

**The Rubric.** You write `rubric.py` to grade the pipeline on five criteria with binary exit codes. A smoke test exercises both paths: happy, where rubric exits `0`, and deficient, where rubric exits `1`.

## Core Concepts

- The pipeline is complete when the rubric exits `0`, not when the script finishes running.
- Two blocking gates sit inside the conductor: evaluation and regression. Each exits BLOCK on failure.
- Five vendored modules are composed by `pipeline.py` and graded by `rubric.py`.
- The composition contract mirrors DC M7: vendor prior modules as read-only dependencies.

The rubric pattern is what separates a script you ran once from a pipeline you can hand to another engineer and defend in review.

<div class="claude-handoff" data-exercise="exercises/module8/00-overview/">
**Build It in Claude Code** · Exercise · exercises/module8/00-overview/
</div>