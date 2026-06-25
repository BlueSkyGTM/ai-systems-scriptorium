# Module 8: Artifact, The Full Fine-Tune Pipeline

The full fine-tune pipeline is not a feature; it is a gate-sequence with a verdict.

## What You Build

Five vendored modules composed by `pipeline.py`, graded by `rubric.py`. The modules are sealed copies of prior work:

- `m3_curate`: dataset curation (validate + dedupe + split)
- `m4_tune`: the reusable fine-tune loop
- `m6_train`: the classifier model and its training
- `m5_eval`: exact-match + macro-F1 evaluation gate
- `m7_regress`: behavioral regression suite (pinned golden cases)

The conductor calls them in order:

```
curate_data -> train_model -> eval_gate -> regress -> log_artifact
```

Two gates block mid-flight. The eval gate raises `PipelineBlocked` if the model fails to beat the baseline. The regression gate raises `PipelineBlocked` if any pinned case fails. The pipeline ships READY or BLOCKS. No third state.

## Why The Rubric Is The Deliverable

A pipeline that runs is not a pipeline that passes. The rubric grades code, not prose:

```python
criteria = {
    "data_curated":        ...,  # duplicates removed and split disjoint
    "model_trained":       ...,  # train accuracy cleared the floor
    "eval_gate_enforced":  ...,  # the eval gate ran and passed
    "regression_enforced": ...,  # every pinned golden case passed
    "artifact_logged":     ...,  # the manifest was written
}
```

Exit `0` means READY. Exit `1` means NEEDS WORK. Skip a gate and the rubric fails loudly.

## The Vendoring Contract

Same composition contract as DC M7, different domain. Vendor prior modules as read-only dependencies. Import from them. Never edit them. The rubric verifies the composition holds.

## Module Path

**Composition.** You write `pipeline.py` to call each vendored module in sequence, thread outputs between stages, and enforce two blocking gates.

**Training And Evaluation.** The M4 fine-tune loop trains the M6 classifier. M5 enforces the eval gate: the tuned model must beat the majority-class baseline by at least 5 percentage points on both exact-match accuracy and macro-F1.

**Regression And Logging.** M7 checks a set of pinned golden tickets; one misrouted case blocks. The run manifest lands on disk (and in MLflow if installed).

**The Rubric.** You write `rubric.py` to grade the pipeline on five criteria with binary exit codes. A smoke test exercises both paths: happy, where rubric exits `0`, and deficient, where rubric exits `1`.

## Core Concepts

- The pipeline is complete when the rubric exits `0`, not when the script finishes running.
- Two blocking gates sit inside the conductor: evaluation and regression. Each exits BLOCK on failure.
- Five vendored modules are composed by `pipeline.py` and graded by `rubric.py`.
- The composition contract mirrors DC M7: vendor prior modules as read-only dependencies.

The rubric pattern is what separates a script you ran once from a pipeline you can hand to another engineer and defend in review.