# Module 7 — Instruction-Tuned LLM with Behavioral Regression Suite

> **Artifact goal.** Ship a tiny instruction-tuned model (`LoRA` on a 2-layer synthetic
> GPT-like Transformer) along with a **behavioral regression suite** that proves the
> fine-tuned model has not degraded on known-good behaviors relative to its base.

This module is the capstone of the "ship-it" arc started in M4 (LoRA fine-tuning) and
M6 (classifier artifact). It bundles the fine-tuner, the regression gate, a smoke
test that exercises a *negative* case, and a pytest suite. Everything runs on CPU
with no external services.

---

## Why this artifact exists

Fine-tuning a model to follow instructions is easy. *Proving you didn't break it*
is the actual engineering problem. The artifact codifies a release contract:

```
tune.py ──▶ outputs/adapter/ ──▶ regress.py ──▶ {PASS: exit 0, BLOCK: exit 1}
                                  │
                                  └──▶ MLflow (sqlite) run logged with metric deltas
```

A PR that lands a new adapter without a green `regress.py` run is **blocked**, not
delayed. The regression gate is the gate.

---

## Directory layout

```
module7-instruct/
├── tune.py                      # LoRA fine-tune, saves outputs/adapter/
├── regress.py                   # behavioral regression gate (exit 0 / 1)
├── smoke.py                     # 10-sample end-to-end, incl. negative case
├── README.md                    # this file
├── outputs/
│   ├── adapter/                 # trained LoRA weights (saved by tune.py)
│   ├── skill-instruct.md        # human-readable skill card
│   ├── mlruns.db                # MLflow offline store (sqlite)
│   └── regress_report.json      # last regression run summary
├── data/
│   └── instruct.jsonl           # 20-50 instruction-following examples (chat format)
└── tests/
    └── test_regression.py       # pytest suite
```

---

## Design constraints (and why they exist)

| Constraint | Rationale |
|---|---|
| **`torch` + stdlib only, no HuggingFace** | Reproducible builds in a book. No `transformers` version drift, no model hub fetches. |
| **2-layer synthetic GPT-like Transformer** | Runs on a laptop CPU in seconds. Big enough to demonstrate the technique; small enough to not be the lesson. |
| **LoRA, not full fine-tune** | Adapter is ~tens of KB; safe to ship and roll back. |
| **String-level regression assertions** | Exact prefix match and keyword match are deterministic. "Semantic similarity" in a regression gate is a footgun. |
| **Fixed seeds everywhere** | `torch.manual_seed(42)`, `random.seed(42)`, `numpy` (if used) seeded. Bit-reproducible across runs. |
| **MLflow via local sqlite** | `mlflow.set_tracking_uri("sqlite:///outputs/mlruns.db")`. No server. Inspect with `mlflow ui --backend-store-uri sqlite:///outputs/mlruns.db`. |

---

## The model

`BaseGPT` is a 2-layer decoder-only Transformer with:

- vocab size `V = 256` (byte-level tokenizer — keeps preprocessing in stdlib),
- `d_model = 64`, `n_heads = 4`, `d_ff = 256`,
- learned absolute positional embeddings,
- causal self-attention + standard pre-LN blocks.

LoRA wraps the query/value projections of both attention layers with `rank = 4`,
`alpha = 8`. The base weights are frozen; only the LoRA matrices are trained.
At inference we recompute `W_base + (alpha / r) * B @ A` and swap it in.

The base model is intentionally under-trained on a tiny corpus so that
fine-tuning *moves* its behavior measurably — that is the point of the demo.

---

## The dataset

`data/instruct.jsonl` contains 20–50 lines, each:

```json
{"instruction": "Complete: The capital of France is",
 "response": " Paris."}
```

Tokenized as `instruction + "\n" + response` (no special tokens beyond byte
encoding). The model is trained to predict only the `response` tokens
(instruction tokens are masked out of the loss). This is the absolute minimum
viable chat format; in production you'd swap in a real chat template, but the
artifact's *contract* — that regression tests gate the adapter — is identical.

---

## `tune.py`

```
python tune.py \
    --base-seed 42 \
    --train-seed 42 \
    --epochs 8 \
    --lr 1e-3 \
    --data data/instruct.jsonl \
    --out outputs/adapter
```

- Constructs `BaseGPT` from a fixed seed.
- Initializes LoRA adapters on attention.
- Trains with AdamW on CPU; full run completes in **< 90 seconds**.
- Writes `outputs/adapter/lora.pt` and `outputs/adapter/config.json`.
- Logs final loss to MLflow under the experiment `m7-instruct-tune`.

---

## `regress.py`

Behavioral regression is a **paired comparison**: run N frozen prompts through
the *base* model and the *tuned* model, score each with string-level checks, and
gate the adapter only if the tuned model is at least as good on every case.

Three check types are supported:

1. **`exact_prefix`** — first N characters must match a literal string.
2. **`keyword_any`** — output must contain at least one of the listed keywords.
3. **`exact_match`** — full decoded output must equal the expected string.

Each test case carries a numeric score (0–1). The run **passes** iff
`tuned_score >= base_score` for every one of the N cases *and* the mean
tuned score is strictly greater than the mean base score. Otherwise it **blocks**.

Exit codes:

- `0` — PASS, adapter is shippable.
- `1` — BLOCK, adapter regressed something. Logged to MLflow with per-case deltas.

```
python regress.py \
    --base outputs/adapter/lora.pt \
    --tests tests/cases.json \
    --report outputs/regress_report.json
```

The report is the artifact you attach to the PR. MLflow gets:

- metrics: `base.mean_score`, `tuned.mean_score`, `delta.mean`, `n_cases_passed`
- tags: `release_gate = {pass, block}`, `git_sha`, `adapter_path`

---

## `smoke.py`

The smoke test is the integration test for the whole pipeline:

1. Run `tune.py` on a 10-sample fixture (subsampled deterministically).
2. Run `regress.py` against the resulting adapter. Assert exit code `0`.
3. **Negative case**: build an adapter with random, untrained weights, point
   `regress.py` at it, and assert that the gate **blocks** it (`exit 1`).
   This proves the gate actually fails when it should — a gate that cannot
   fail is not a gate.
4. Assert total wall-clock **< 45 seconds** on CPU.

All seeds are reset between sub-steps so the smoke run is reproducible.

```
python smoke.py
# exit 0 — green build
```

---

## `tests/test_regression.py`

A pytest suite covering:

- Tokenizer round-trip (encode/decode identity on the alphabet).
- LoRA forward equivalence: with `A=0, B=0`, the LoRA-wrapped model must equal
  the base model bit-for-bit.
- `regress.py` scoring functions on canned inputs.
- A 3-prompt mini-regression run that must pass on a fixture adapter.

```
pytest tests/test_regression.py -v
```

---

## Inspecting runs

```bash
# Tune
python tune.py

# Run the gate
python regress.py

# Inspect history
mlflow ui --backend-store-uri sqlite:///outputs/mlruns.db --port 5000
```

Each `regress.py` run creates an MLflow run tagged `release_gate = pass|block`
with metrics per case and an aggregate `delta.mean` (positive = tuned better).

---

## What "shipping" means here

The artifact is the **bundle** of:

1. `outputs/adapter/lora.pt` + `config.json` — the trainable delta.
2. `outputs/regress_report.json` — proof the gate passed.
3. `outputs/skill-instruct.md` — the human-readable skill card: what the model
   can do, what it cannot do, and the regression cases it is pinned to.

A green run of `smoke.py` is the release signal. No green run, no ship.

---

## Failure modes the gate catches

- **Catastrophic forgetting** on one of the N cases → keyword check fails → block.
- **Truncation drift**: tuned model now stops one token earlier → exact-prefix
  check fails → block.
- **Random adapter** (the negative smoke case) → tuned score is noise,
  `delta.mean < 0` → block.
- **Tokenizer mismatch**: an adapter trained against a different base config
  fails the LoRA-shape check at load time → hard error before scoring.

---

## Relationship to earlier modules

- **M4 (LoRA)**: this is the productionized form of that recipe — same rank/alpha
  choices, same freeze-base discipline, now wrapped in a release contract.
- **M6 (classifier artifact)**: M6 established the "ship an artifact with tests
  and a README" pattern. M7 generalizes it to *generative* behavior, where
  the test oracle is harder and therefore more valuable.

---

## Reproducibility checklist

- [x] `torch.manual_seed(42)` and `random.seed(42)` in every entry point.
- [x] No network calls at training or inference time.
- [x] No HuggingFace dependency.
- [x] Byte-level tokenizer — no external vocab file.
- [x] Adapter config written next to weights; mismatches are loud failures.
- [x] `regress.py` exits non-zero on any regression — no silent warnings.
- [x] Smoke test includes a *must-fail* case to prove the gate bites.

---

## License & scope

This is a teaching artifact. The model is intentionally tiny — it is not
useful for real work. The **engineering pattern** (fine-tune → regression-gate →
ship-with-proof) is the deliverable, and it generalizes to any scale.
