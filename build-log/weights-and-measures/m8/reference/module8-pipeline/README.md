# Module 8: Artifact: The Full Fine-Tune Pipeline

> **Capstone.** Composes five vendored modules (curation, the fine-tune loop, the
> classifier, the eval gate, the regression suite) into a single conductor script, then
> grades itself with a rubric in code.

This is the deliverable that ties *Weights and Measures* together. Every prior module
contributed one sealed, vendored component; this module wires them into an end-to-end loop
and *proves* the loop holds by running a rubric that fails loudly when any gate is skipped.

---

## 1. What This Artifact Proves

By the end of this module the reader holds a script that:

1. **Curates** raw support tickets into a deduped, validated, split dataset (M3).
2. **Trains** a CPU-tiny classifier using the reusable fine-tune loop (M4 + M6).
3. **Evaluates** with an exact-match + macro-F1 gate that raises `PipelineBlocked` if the
   model fails to beat the baseline (M5).
4. **Regresses** against a set of pinned golden tickets and raises `PipelineBlocked` on any
   misroute (M7).
5. **Logs** a run manifest to disk (and MLflow if installed).

The five steps are vendored modules; `pipeline.py` is the conductor. The pipeline is not
"complete" when it runs; it is complete when `rubric.py` exits `0`.

---

## 2. File Layout

```
module8-pipeline/
├── pipeline.py              # the conductor: curate -> train -> eval_gate -> regress -> log
├── rubric.py                # grades the run on 5 criteria; 0=READY, 1=NEEDS WORK
├── smoke.py                 # end-to-end on synthetic fixtures; a few seconds on CPU
├── tests/
│   └── test_pipeline.py     # pytest suite (stages + conductor + rubric)
├── lib/                     # vendored, READ-ONLY
│   ├── __init__.py          # the VENDORED registry
│   ├── m3_curate.py
│   ├── m4_tune.py
│   ├── m6_train.py
│   ├── m5_eval.py
│   └── m7_regress.py
├── outputs/                 # generated: checkpoint.pt, manifest.json, mlruns.db
│   └── skill-pipeline.md    # the portfolio write-up
└── README.md
```

The `lib/` directory is **vendored and frozen**, the same pattern introduced in Module 7.
The pipeline never edits vendored code; it imports it. If a contract changes, you re-vendor
the new module, you do not patch in place.

---

## 3. The Pipeline Stages

| Stage | Module | What it does |
|---|---|---|
| `curate_data` | `m3_curate` | Validate schema, drop duplicates, split into disjoint train/test. |
| `train_model` | `m6_train` (via `m4_tune`) | Train the classifier with the reusable fine-tune loop; save the checkpoint. |
| `eval_gate` | `m5_eval` | Exact-match accuracy + macro-F1 vs the majority-class baseline. Raises `PipelineBlocked` if the model fails to beat the baseline by 5pp on both. |
| `regress` | `m7_regress` | Run pinned golden tickets through the model. Raises `PipelineBlocked` if any is misrouted. |
| `log_artifact` | conductor | Write `outputs/manifest.json` (and MLflow if installed). |

Each gate raises `PipelineBlocked`, so the conductor halts loud rather than shipping a bad
model.

---

## 4. The Rubric

`rubric.py` reads `outputs/manifest.json` and grades **five binary criteria**, each checked
by code:

| # | Criterion | How it is verified |
|---|-----------|--------------------|
| 1 | `data_curated` | duplicates were removed and the train/test split is disjoint |
| 2 | `model_trained` | training accuracy cleared `TRAIN_ACC_FLOOR` (0.80) |
| 3 | `eval_gate_enforced` | the eval gate ran and recorded PASS |
| 4 | `regression_enforced` | every pinned golden case passed |
| 5 | `artifact_logged` | the manifest was written |

Exit `0` = READY (all five pass). Exit `1` = NEEDS WORK (one or more failed; the rubric
prints which). The rubric is the deliverable: a pipeline that runs but cannot pass the
rubric has not shipped.

---

## 5. Usage

```bash
python smoke.py                 # full run + rubric READY, deficient run + rubric NEEDS WORK
python -m pytest tests/ -q      # stages, conductor gating, rubric
python pipeline.py              # run all five stages -> outputs/manifest.json
python rubric.py ; echo $?      # grade the last run: 0 = READY, 1 = NEEDS WORK
```

`smoke.py` includes the **negative case**: it runs the pipeline with the eval gate skipped
and asserts the rubric grades it NEEDS WORK. Both the positive path (READY) and the negative
path (NEEDS WORK) must hold. A few seconds on CPU, no GPU, no HuggingFace.

---

## 6. Design Constraints

- **CPU only.** No CUDA, no `transformers`. The point of the capstone is the *pipeline*.
- **Seeds fixed.** `torch.manual_seed(42)`, `random.seed(42)` inside the vendored modules.
- **Vendored `lib/`.** Never edited in place; re-vendor explicitly when upgrading a module.
- **Offline MLflow, optional.** `sqlite:///outputs/mlruns.db`; the run still grades without it.
- **Exit codes are the API.** `0`/`1` from the rubric; CI reads exit codes, not log lines.

---

## 7. What This Module Teaches

Every prior module was a *component*. Module 8 is the moment the reader learns that **a
fine-tune pipeline is not a script, it is a contract**. The contract has five clauses (the
five rubric criteria), each enforceable by code, each capable of blocking a release. When
the rubric exits `0`, you have not just trained a model; you have earned the right to deploy
one. That is the artifact the rest of the book was building toward.
