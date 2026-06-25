# The Pipeline Artifact

Five vendored modules form the body. One conductor script wires them into an ordered loop, and the rubric grades the conductor, nothing else.

## The Five-Step Loop

The pipeline composes Modules 3 through 7 into a single script. Each stage is a vendored module, mapped in `pipeline.py`:

```
curate_data  -> m3_curate : validate, dedupe, split the raw tickets
train_model  -> m6_train  : train the classifier (via the m4_tune loop)
eval_gate    -> m5_eval   : accuracy + macro-F1 vs baseline; BLOCK if it fails
regress      -> m7_regress: pinned golden tickets must route correctly; BLOCK if not
log_artifact -> write outputs/manifest.json
```

Two gates sit in the middle. If eval fails, the pipeline raises `PipelineBlocked`. If regression fails, it raises `PipelineBlocked`. There is no soft pass. The README defines completion with one sentence:

> The pipeline is not "complete" when it runs; it is complete when `rubric.py` exits `0`.

## Vendoring Under lib/

You do not rewrite Modules 3 through 7. You copy them, read-only, into `lib/`. The vendoring contract treats these files as sealed dependencies: the pipeline imports from them but never edits them. `lib/__init__.py` records the registry in pipeline order:

```python
VENDORED = ("m3_curate", "m4_tune", "m6_train", "m5_eval", "m7_regress")
```

Five entries. Five submodules. The conductor is the only new code you write in this module. Everything else is frozen output from prior modules.

## What the Rubric Grades

The rubric is the deliverable. It grades code, not prose. Five hard criteria, keyed in a dict:

```python
criteria = {
    "data_curated":        bool(curated.get("dupes_removed", 0) > 0 and curated.get("disjoint")),
    "model_trained":       bool(trained.get("train_acc", 0.0) >= TRAIN_ACC_FLOOR),
    "eval_gate_enforced":  bool(eval_s is not None and eval_s.get("passed")),
    "regression_enforced": bool(regress is not None and regress.get("passed")),
    "artifact_logged":     bool(manifest.get("logged")),
}
```

Exit codes are binary: `0` = READY (all five pass), `1` = NEEDS WORK (one or more failed).

Skip the eval gate and the rubric catches it. The thresholds are pinned and non-negotiable: the rubric requires training accuracy at or above the floor, and the eval gate (in `m5_eval`) requires the tuned model to beat the baseline by at least the margin on both metrics:

```python
TRAIN_ACC_FLOOR = 0.80   # rubric.py: training accuracy must clear this
MARGIN_PP = 0.05         # m5_eval.py: beat the baseline by >= 5pp on both metrics
```

## One Command to Run

The smoke test exercises two scenarios on synthetic fixtures: a happy path where the rubric exits 0, and a deficient path where the eval gate is skipped and the rubric exits 1. Both assertions must hold. Determinism is pinned inside the vendored modules, so every run reproduces; `m6_train` seeds before it builds:

```python
torch.manual_seed(SEED)
random.seed(SEED)
```

MLflow, when installed, points at a local sqlite backend so no external service is needed:

```python
mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_DB}")
```

You run the pipeline. You run the rubric. The rubric tells you whether you are done.

## Core Concepts

1. The pipeline is a conductor that calls five vendored functions in order; the conductor is the only new code written in this module.
2. Two gates, eval and regression, exit BLOCK on failure; the pipeline has no soft-pass path.
3. The rubric grades five criteria with binary exit codes: 0 means READY, 1 means NEEDS WORK.
4. Vendored modules under `lib/` are read-only copies of M3 through M7; the pipeline imports but never edits them.

Composition means the conductor earns the grade; the five modules already proved themselves in isolation, so if the rubric fails, the defect is in how you wired them together.

<div class="claude-handoff" data-exercise="exercises/module8/the-pipeline-artifact/">
**Build It in Claude Code** · Exercise · exercises/module8/the-pipeline-artifact/
</div>