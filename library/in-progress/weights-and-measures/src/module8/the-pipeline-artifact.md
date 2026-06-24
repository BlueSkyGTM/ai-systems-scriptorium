# The Pipeline Artifact

Five vendored modules form the body. One conductor script wires them into an ordered loop, and the rubric grades the conductor, nothing else.

## The Five-Step Loop

The pipeline composes Modules 3 through 7 into a single script. Each stage maps to a function call:

```
curate_data() → train_model() → eval_gate() → regress() → log_artifact()
                     │                │             │
                     │                │             └── BLOCK if regression fails
                     │                └── BLOCK if eval fails
                     └── LoRA adapter (M4) + classifier head (M6)
```

Two gates sit in the middle. If eval fails, the pipeline exits BLOCK. If regression fails, the pipeline exits BLOCK. There is no soft pass. The README defines completion with one sentence:

> The pipeline is not "complete" when it runs; it is complete when `rubric.py` exits `0`.

## Vendoring Under lib/

You do not rewrite Modules 3 through 7. You copy them, read-only, into `lib/`. The vendoring contract treats these files as sealed dependencies: the pipeline imports from them but never edits them. The registry in `lib/__init__.py` maps each stage:

```python
_VENDORED: Dict[str, str] = {
    "m3_curate":  "lib.m3_curate",
    "m4_tune":    "lib.m4_tune",
    "m5_eval":    "lib.m5_eval",
    "m6_train":   "lib.m6_train",
    "m7_regress": "lib.m7_regress",
}
```

Five entries. Five submodules. The conductor is the only new code you write in this module. Everything else is frozen output from prior modules.

## What the Rubric Grades

The rubric is the deliverable. It grades code, not prose. Five hard criteria:

```python
CRITERIA: Tuple[str, ...] = (
    "data_quality",
    "train_reproducible",
    "eval_gate_enforced",
    "regression_gate_enforced",
    "mlflow_logged",
)
```

Exit codes are binary:

```python
#    0 = READY         (all 5 criteria pass)
#    1 = NEEDS WORK    (one or more criteria failed)
```

Skip the eval gate and the rubric catches it. Skip regression and the rubric catches that too. The threshold constants are pinned and non-negotiable:

```python
EVAL_EM_THRESHOLD = 0.50
EVAL_F1_THRESHOLD = 0.60
REGRESSION_MAX_DELTA = 0.10  # abs drift allowed vs baseline
```

## One Command to Run

The smoke test exercises two scenarios on synthetic fixtures: a happy path where the rubric exits 0, and a deficient path where the eval gate is skipped and the rubric exits 1. Both assertions must hold. Determinism is set before anything else runs:

```python
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
```

MLflow points at a local sqlite backend so no external service is needed:

```python
MLFLOW_URI = "sqlite:///outputs/mlruns.db"
os.environ.setdefault("MLFLOW_TRACKING_URI", MLFLOW_URI)
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