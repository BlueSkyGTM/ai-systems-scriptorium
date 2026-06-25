# Skill Pipeline: Module 8 Artifact

> The capstone. One conductor that composes dataset curation, the fine-tune loop, the
> classifier, the eval gate, and the regression suite into a single reproducible run. The
> run either grades READY or the rubric returns NEEDS WORK. There is no third state.

## What This Is

`module8-pipeline/` is the conductor for everything Modules 3 through 7 built in isolation.
It wires five vendored stages into an ordered run, enforces two hard gates, and writes a run
manifest. The rubric grades the *manifest*, not the prose. If the pipeline skips the eval
gate, the rubric returns NEEDS WORK and the artifact does not ship.

```
curate_data  -> m3_curate : validate, dedupe, split the raw tickets
train_model  -> m6_train  : train the classifier (via the m4_tune loop)
eval_gate    -> m5_eval   : accuracy + macro-F1 vs baseline; BLOCK if it fails
regress      -> m7_regress: pinned golden tickets must route correctly; BLOCK if not
log_artifact -> write outputs/manifest.json
```

## Stages

1. **`curate_data` (M3).** Validate schema, drop duplicate texts, split into a disjoint
   train/test set. Rejects malformed rows.
2. **`train_model` (M4 + M6).** Train the support-ticket classifier with the reusable
   `m4_tune.fit` loop; `torch.manual_seed(42)`, `random.seed(42)`. Checkpoint saved to
   `outputs/checkpoint.pt`.
3. **`eval_gate` (M5).** Exact-match accuracy + macro-F1 against the majority-class
   baseline. Raises `PipelineBlocked` unless the model beats the baseline by at least 5pp on
   both.
4. **`regress` (M7).** Run pinned golden tickets through the model. Raises `PipelineBlocked`
   if any one is misrouted.
5. **`log_artifact`.** Write `outputs/manifest.json` (and MLflow if installed).

## Rubric (5 Criteria)

`rubric.py` reads the manifest and checks each criterion by code:

| # | Criterion | Pass condition |
|---|-----------|----------------|
| 1 | `data_curated` | duplicates removed and the split is disjoint |
| 2 | `model_trained` | training accuracy at or above 0.80 |
| 3 | `eval_gate_enforced` | the eval gate ran and recorded PASS |
| 4 | `regression_enforced` | every pinned golden case passed |
| 5 | `artifact_logged` | the manifest was written |

Exit `0` = READY (all five pass); exit `1` = NEEDS WORK.

## Running

```bash
python pipeline.py          # run all five stages -> outputs/manifest.json
python rubric.py            # grade it: exit 0 = READY, 1 = NEEDS WORK
python smoke.py             # positive + negative (deficient) case
```

`smoke.py` runs the pipeline twice: once normally (rubric READY), once with the eval gate
skipped (rubric NEEDS WORK). Both assertions must hold.

## Failure Modes the Rubric Catches

1. Eval gate skipped -> `eval_gate_enforced` fails.
2. A retrain misroutes a golden ticket -> `regression_enforced` fails.
3. Curation dedupe removed -> `data_curated` fails.
4. Training collapses below the floor -> `model_trained` fails.

Each is exercised by `smoke.py`'s deficient case or the pytest suite.
