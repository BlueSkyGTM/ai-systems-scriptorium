# Module 8 — Artifact: The Full Fine-Tune Pipeline

> **Capstone.** Composes M3 (curation) → M4 (LoRA) → M5 (eval gate) → M6 (classifier / training shim) → M7 (regression) into a single conductor script, then grades itself.

This is the deliverable that ties *Weights and Measures* together. Every prior module contributed one sealed, vendored component; this module wires them into an end-to-end loop and *proves* the loop holds by running a rubric that fails loudly when any gate is skipped.

---

## 1. What this artifact proves

By the end of this module the reader holds a script that:

1. **Curates** a raw prompt set into a deduped, split, validated JSONL dataset (M3).
2. **Trains** a CPU-tiny model with a LoRA adapter on that dataset (M4 / M6).
3. **Evaluates** with an exact-match + token-F1 gate that *exits BLOCK* if the model regresses below threshold (M5).
4. **Regresses** against a fixed behavioral fixture set and *exits BLOCK* on drift (M7).
5. **Logs** every artifact to MLflow (sqlite backend) and writes a `outputs/` manifest.

The five steps are functions; `pipeline.py` is the conductor. The pipeline is not "complete" when it runs — it is complete when `rubric.py` exits `0`.

---

## 2. File layout

```
module8-pipeline/
├── pipeline.py              # the conductor: curate → train → eval_gate → regress → log
├── rubric.py                # grades the pipeline on 5 criteria; 0=READY, 1=NEEDS WORK
├── smoke.py                 # end-to-end on synthetic fixtures; < 60s CPU
├── tests/
│   └── test_pipeline.py     # pytest suite (unit + integration)
├── lib/                     # vendored, READ-ONLY
│   ├── m3_curate.py
│   ├── m4_tune.py
│   ├── m5_eval.py
│   ├── m6_train.py
│   └── m7_regress.py
├── fixtures/                # synthetic prompts + behavioral golden set
├── outputs/                 # generated: datasets/, adapters/, mlruns.db, manifest.json, skill-pipeline.md
└── README.md                # this file
```

The `lib/` directory is **vendored and frozen** — the same pattern introduced in Module 7. The pipeline never edits vendored code; it imports it. If a contract changes, you re-vendor the new module, you do not patch in place.

---

## 3. The pipeline stages

### 3.1 `curate_data() → JSONL`
Reads raw fixtures, validates schema, dedupes on `(prompt, completion)` pairs, splits 80/10/10, writes `outputs/datasets/{train,val,test}.jsonl`. Returns split sizes.

### 3.2 `train_model() → adapter`
Seeds `torch.manual_seed(42)`, `random.seed(42)`. Runs LoRA fine-tune on the train split, evaluates loss on val each epoch, writes the winning adapter to `outputs/adapters/`. Deterministic given the same seed and input.

### 3.3 `eval_gate() → BLOCK | PASS`
Computes exact-match and token-F1 on the held-out test split. Thresholds are constants at the top of the module. **Failing the gate calls `sys.exit(2)`** — the pipeline halts and downstream steps do not run.

### 3.4 `regress() → BLOCK | PASS`
Runs the trained model against the M7 behavioral fixture (golden prompt → expected behavior tuple). Any drift outside tolerance → `sys.exit(3)`. This is *behavioral*, not loss-based: it catches the failure modes that token-F1 misses.

### 3.5 `log_artifact() → MLflow + manifest`
`mlflow.set_tracking_uri("sqlite:///outputs/mlruns.db")`. Logs params (seed, lr, epochs, thresholds), metrics (EM, F1, regression deltas), and artifacts (adapter, dataset checksums, this README). Writes a `outputs/manifest.json` that the rubric reads.

---

## 4. The rubric

`rubric.py` grades the pipeline on **five binary criteria**. Each is checked by code, not prose:

| # | Criterion | How it is verified |
|---|-----------|--------------------|
| 1 | **Data quality gate** | `outputs/datasets/*.jsonl` exist; row counts > 0; no duplicates in train; schema validates. |
| 2 | **Train reproducibility** | Adapter checksum matches a second run with the same seed. |
| 3 | **Eval gate enforced** | `pipeline.py` source contains an `sys.exit(2)` reachable from `eval_gate()`; manifest records the gate result. |
| 4 | **Regression gate enforced** | `pipeline.py` source contains an `sys.exit(3)` reachable from `regress()`; manifest records the regression result. |
| 5 | **MLflow logged** | `outputs/mlruns.db` exists and contains a run with the expected params and metrics. |

Exit codes:

- `0` — **READY**. All five criteria pass.
- `1` — **NEEDS WORK**. One or more criteria failed. The rubric prints which.

The rubric is the deliverable. A pipeline that "works on my machine" but cannot pass the rubric has not shipped.

---

## 5. Usage

### Smoke test (the contract)

```bash
python smoke.py
```

Runs the full pipeline on synthetic fixtures, then runs `rubric.py`. The smoke test also includes a **negative case**: it clones the pipeline with the eval gate commented out, runs *that*, and asserts `rubric.py` exits `1`. Both the positive path (exit `0`) and the negative path (exit `1`) must hold for `smoke.py` to pass.

Wall-clock budget: **< 60 seconds on CPU**, no GPU, no HuggingFace.

### Rubric alone

```bash
python rubric.py
echo $?   # 0 = READY, 1 = NEEDS WORK
```

Useful after hand-editing the pipeline: did you break a gate?

### Unit + integration tests

```bash
pytest -q
```

Covers each stage in isolation plus the full conductor. Tests use the same fixtures as `smoke.py`.

### End-to-end from scratch

```bash
python pipeline.py           # runs all five stages, halts on any gate
python rubric.py             # grades what pipeline.py just produced
```

---

## 6. Design constraints

- **CPU only.** No CUDA, no `transformers`, no `accelerate`. The point of the capstone is the *pipeline*, not the model scale.
- **Seeds fixed.** `torch.manual_seed(42)` and `random.seed(42)` at the top of `train_model()`. Reproducibility is not optional — rubric criterion 2 depends on it.
- **Vendored `lib/`.** Never edited in place. Re-vendor explicitly when upgrading a module.
- **Offline MLflow.** `sqlite:///outputs/mlruns.db`. No tracking server, no network. Artifacts live on local disk.
- **stdlib + torch + sklearn.** `sklearn` is allowed only for baseline utilities (e.g., `train_test_split`, `f1_score`); it is not a model backend.
- **Exit codes are the API.** `0`/`1` from the rubric, `2`/`3` from the gates. CI reads exit codes, not log lines.

---

## 7. Outputs

After a successful run, `outputs/` contains:

```
outputs/
├── datasets/{train,val,test}.jsonl
├── adapters/lora_adapter.pt
├── mlruns.db
├── manifest.json
└── skill-pipeline.md       # human-readable summary: params, metrics, gate verdicts
```

`skill-pipeline.md` is the artifact you show a reviewer. `manifest.json` is the artifact a downstream CI step reads.

---

## 8. What this module teaches

Every prior module was a *component*. Module 8 is the moment the reader learns that **a fine-tune pipeline is not a script — it is a contract**. The contract has five clauses (the five rubric criteria), each enforceable by code, each capable of blocking a release. When the rubric exits `0`, you have not just trained a model; you have *earned the right to deploy one*.

That is the artifact the rest of the book was building toward.
