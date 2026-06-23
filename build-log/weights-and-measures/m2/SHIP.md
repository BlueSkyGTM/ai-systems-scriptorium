# SHIP RECORD — Weights and Measures M2 "Fitting and Not Fitting"

Shipped 2026-06-21. `GATE-APPROVE-SHIP` self-cleared (W&M M2–M8 run straight through under Ray's
standing "go / finish the job" directive, same posture as Machine Math + Data Currents).

## What shipped
- `src/module2/`: overview + 4 lessons (`the-held-out-set`, `reading-loss-curves`,
  `early-stopping-as-a-policy`, `instrumenting-the-run`).
- `exercises/module2/`: 4 exercise READMEs (one per lesson; the capstone gates on `check_loop --module 2`).
- Spine extended in place: `exercises/spine/trainer.py` gained `evaluate()` + `fit()` (early stopping,
  best-checkpoint save/restore); `exercises/spine/check_loop.py` gained `--module 2`. M1 byte-identical.
- `ingredients/source/weights-and-measures/fitting-catalog.md`: the M2 ore ingredient.

## Verify / Build verdict
- VERIFY: 27 em/en-dashes swept (trainer.py 9, lessons 2, catalog 15, +1 review-gate fix moving a
  misplaced `## Core Concepts` to last in `instrumenting-the-run`); every code block byte-identical to
  the frozen source; every output real.
- BUILD/TEST: `check_loop.py --selftest` OK (both modules) · `check_loop.py --module 2 trainer.py` PASS
  · M1 default PASS · `py_compile` OK · `trainer.py` re-ran (M1 demo `0.0534`; overfit demo best epoch
  4, early-stops after epoch 7) · `mdbook build` clean, 0 warnings.

## Grounding
- Primary input: the in-book draft `draft/02-loss-curves-overfit.md`. Enriched by `aefs` Phase 03
  (`07-regularization`, `13-debugging-neural-networks`) + `made-with-ml` `train.py` + live docs.
- Verified anchors: the overfit-demo trajectory (best epoch 4, `valid_loss=1.5141`, early stop epoch 7);
  the real Azure AI Foundry `results.csv` metric names; core torch has NO built-in `EarlyStopping` (the
  `fit` hand-rolled pattern is the example, no invented API).

## Fleet
Haiku-fetch (vault ore + live docs) / Sonnet-author (5: overview + 4 lessons + exercises) + a Sonnet
spine-engineer (wrote + ran `evaluate`/`fit` + `check_loop --module 2`) + a Sonnet VERIFY worker /
Opus-conduct (designed the schema, ran the review gate, moved the misplaced Core Concepts; did NOT
hand-author or hand-code).

## Next
M3 "Dataset Craft": curating fine-tuning data (quality signals, deduplication, the JSONL contract,
held-out set design; why small + clean beats large + noisy). Blueprint in `README.md`.
