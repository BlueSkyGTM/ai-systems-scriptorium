# Module 7: Instruction-Tuned LLM with Behavioral Regression Suite

> **Artifact goal.** Ship a tiny instruction-tuned model (`LoRA` on a 2-layer
> from-scratch Transformer) plus a **behavioral regression suite** that proves the
> fine-tune added a new skill without degrading the behaviors the base already had.

This module is the capstone of the ship-it arc started in M4 (LoRA) and M6 (the
classifier artifact). It bundles the fine-tuner, the regression gate, a smoke test that
exercises a *negative* case, and a pytest suite. Everything runs on CPU, no external
services.

---

## Why This Artifact Exists

Fine-tuning a model to follow instructions is easy. *Proving you didn't break it* is the
engineering problem. The artifact codifies a release contract:

```
tune.py ──▶ outputs/adapter/ ──▶ regress.py ──▶ {PASS: exit 0, BLOCK: exit 1}
                                  │
                                  └──▶ MLflow (sqlite) run logged with metric deltas
```

A new adapter that fails `regress.py` is **blocked**, not delayed. The regression gate is
the gate.

---

## The Model and the Skills

`TinyLM` is a 2-layer decoder-only Transformer: `d_model = 64`, `n_head = 4`,
`d_ff = 128`, learned positional embeddings, causal self-attention. The vocabulary is a
small word-level set (specials, three verbs, three responses, ten names).

Sequences have a fixed shape:

```
<bos> VERB NAME <sep> RESPONSE NAME <eos>
e.g. "<bos> greet alice <sep> hello alice <eos>"
```

The base model is pretrained on two skills, `thank -> thanks` and `bye -> goodbye`. It
never sees `greet`. LoRA then teaches the third skill, `greet -> hello`, training only
the adapter while the base stays frozen. A little replay of the old skills keeps the
adapter from clobbering them.

LoRA wraps the query and value projections of both attention blocks with `rank = 8`,
`alpha = 16`. The adapter is a few thousand parameters against ~72k total.

---

## `tune.py`

```bash
python tune.py --base-epochs 300 --lora-epochs 300
```

Pretrains the base, saves `outputs/base.pt`, LoRA-tunes the new skill, and saves the
adapter to `outputs/adapter/adapter.pt`. Also writes the instruction set to
`outputs/instruct.jsonl` in chat format. Fixed seeds (`torch.manual_seed(42)`,
`random.seed(42)`); the full run finishes in a few seconds on CPU.

## `regress.py`

```bash
python regress.py            # add --no-mlflow to skip logging
echo $?                      # 0 = PASS, 1 = BLOCK
```

Runs a fixed behaviour suite against the base and the base+adapter. It **passes** iff the
tuned model matches or beats the base on **every** case (no regression) **and** strictly
improves on at least one (the new skill was learned). Otherwise it **blocks**. The checks
are string-level exact matches on the greedy-decoded response, so they are deterministic.

## `smoke.py`

```bash
python smoke.py              # exit 0 = green build
```

Tunes, confirms `regress.py` PASSES on the real adapter, swaps in a random adapter of
identical shape and confirms it BLOCKS, then restores the real adapter. The negative case
is the fuse: it proves the gate can fail, so a green run means something. 14 assertions,
under 45 seconds on CPU.

## `tests/test_regression.py`

```bash
python -m pytest tests/ -q
```

Covers the LoRA ratio, the new-skill gain, the preserved old skills, the two-sided gate,
and the scoring primitive. 8 tests.

---

## What "Shipping" Means Here

The artifact is the bundle of `outputs/base.pt` + `outputs/adapter/adapter.pt` (the
trainable delta) and a green `smoke.py` run. No green run, no ship.

---

## Relationship to Earlier Modules

- **M4 (LoRA):** the productionized form of that recipe, now wrapped in a release contract.
- **M6 (classifier artifact):** M6 established the ship-an-artifact-with-tests pattern. M7
  generalizes it to *generative* behavior, where the test oracle is harder and therefore
  more valuable.

---

## License & Scope

A teaching artifact. The model is intentionally tiny; the engineering pattern
(fine-tune, regression-gate, ship-with-proof) is the deliverable, and it generalizes to
any scale.
