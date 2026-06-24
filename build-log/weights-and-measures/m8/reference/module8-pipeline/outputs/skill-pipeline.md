# Skill Pipeline — Module 8 Artifact

> The capstone. One script that composes dataset curation, LoRA fine-tune, the eval gate, the classifier, and the regression suite into a single reproducible loop. The pipeline either ships a READY artifact or BLOCKS. There is no third state.

## What this is

`module8-pipeline/` is the conductor for everything Modules 3–7 built in isolation. It wires five stages into an ordered script, enforces two hard gates, and logs the result to MLflow. The rubric grades the *code* — not the prose, not the vibes. If the pipeline skips the eval gate, the rubric returns `NEEDS WORK` and the artifact does not ship.

```
curate_data() → train_model() → eval_gate() → regress() → log_artifact()
                     │                │             │
                     │                │             └── BLOCK if regression fails
                     │                └── BLOCK if eval fails
                     └── LoRA adapter (M4) + classifier head (M6)
```

## Stages

### 1. `curate_data()` — Dataset curation (M3)

- Input: raw JSONL fixtures.
- Pattern: **validate → dedupe → split**.
- Output: `outputs/train.jsonl`, `outputs/val.jsonl`, `outputs/test.jsonl`.
- Rejects records missing required fields. Deduplicates on normalized text. 80/10/10 split with `random.seed(42)`.

### 2. `train_model()` — LoRA fine-tune (M4 + M6)

- CPU-runnable toy model: a small `torch.nn.Module` with a LoRA-injected linear (rank 4, alpha 8).
- Classifier head from M6 sits on top for the regression target.
- `torch.manual_seed(42)` before init, before each optimizer step batch.
- Checkpoint written to `outputs/adapter.pt`.

### 3. `eval_gate()` — Exact-match + F1 (M5)

- Computes exact-match accuracy and token-level F1 on the held-out validation split.
- **Gate thresholds**: exact-match ≥ 0.60 *and* F1 ≥ 0.70 (synthetic fixtures).
- Returns `BLOCK` exit code 2 on failure. No downstream stage runs.

### 4. `regress()` — Behavioral regression (M7)

- Re-runs the suite of canonical inputs from M7 against the freshly trained adapter.
- Compares outputs to pinned golden vectors.
- Drift > ε on any fixture → `BLOCK`, exit code 3.

### 5. `log_artifact()` — MLflow manifest

- `mlflow.set_tracking_uri("sqlite:///outputs/mlruns.db")` — offline sqlite backend, no network.
- Logs: dataset hash, adapter path, eval metrics, regression status, git SHA, random seed.
- Writes `outputs/manifest.json` mirroring the MLflow record for offline inspection.

## Rubric (5 criteria)

`rubric.py` is the deliverable. Each criterion is checked by code, not by reading prose.

| # | Criterion | Pass condition |
|---|-----------|----------------|
| 1 | Data quality gate | `curate_data()` ran; splits exist; dedupe count > 0 |
| 2 | Train reproducibility | Two runs with `seed=42` produce bitwise-identical adapter weights |
| 3 | Eval gate enforced | Pipeline with gate skipped → exit code != 0; with gate → metrics recorded |
| 4 | Regression gate enforced | Pinned fixtures run; drift metric present and below threshold |
| 5 | MLflow logged | `outputs/mlruns.db` contains a run with all 5 params + metrics |

Exit codes:
- `0` → **READY** (all 5 criteria pass)
- `1` → **NEEDS WORK** (any criterion fails)

## Running

```bash
# Full pipeline on synthetic fixtures
python pipeline.py --fixtures fixtures/ --seed 42

# Grade the result
python rubric.py

# Smoke (positive + negative case, < 60s CPU)
python smoke.py
```

`smoke.py` runs the pipeline twice: once normally (must succeed), once with `--skip-eval-gate` (must BLOCK). Both assertions must pass for the smoke test to exit 0.

## Files

```
module8-pipeline/
├── pipeline.py              # conductor: curate → train → eval → regress → log
├── rubric.py                # 5-criterion grader; exit 0 = READY, 1 = NEEDS WORK
├── smoke.py                 # positive + negative case, < 60s on CPU
├── lib/
│   ├── m3_curate.py         # vendored
│   ├── m4_tune.py           # vendored
│   ├── m5_eval.py           # vendored
│   ├── m6_train.py          # vendored
│   └── m7_regress.py        # vendored
├── tests/
│   └── test_pipeline.py     # pytest suite
├── outputs/
│   ├── skill-pipeline.md    # this file
│   ├── manifest.json
│   ├── mlruns.db
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
└── README.md
```

## Design notes

- **No HuggingFace.** The toy model exists to make gates runnable on CPU in under a minute, not to push SOTA. The *pipeline shape* is what matters.
- **Vendored libs are read-only.** `pipeline.py` imports them; it never monkey-patches. If a vendored module needs a different behavior, the fix is upstream in M3–M7, not here.
- **Two gates, two exit codes.** Eval gate failure is exit 2; regression failure is exit 3. The rubric distinguishes them so you can tell *which* gate blocked the ship without reading logs.
- **MLflow is offline.** Sqlite backend, no tracking server required. The manifest is the source of truth; MLflow is the index.

## Failure modes the rubric catches

1. Eval gate commented out → criterion 3 fails.
2. Regression skipped after eval passes → criterion 4 fails.
3. Random seed not fixed → criterion 2 fails (non-deterministic weights).
4. MLflow call removed → criterion 5 fails (no run recorded).
5. Dedupe removed → criterion 1 fails (split sizes don't match expectations).

Each of these is exercised by `smoke.py`'s negative case or by the pytest suite.
