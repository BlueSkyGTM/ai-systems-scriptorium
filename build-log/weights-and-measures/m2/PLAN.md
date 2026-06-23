# Module 2 — Fitting and Not Fitting — Build Plan

Status: **PLAN LOCKED 2026-06-21** (`GATE-LOCK-PLAN` self-cleared under Ray's standing "finish the job /
go" directive; W&M M2–M8 run straight through, same posture as Machine Math M2–M8 and Data Currents
M2–M8). Second authoring stage of Weights and Measures (M1 shipped, `582a8917`).

## The stage in one line

M1 made a loop run; M2 teaches whether it is working. This is the vocabulary of fit: the held-out
set and why you trust it, reading the train-vs-validation divergence off a loss curve, the
overfitting signal, and early stopping as a checkpoint-promotion policy (not a knob). It extends the
spine with a validation pass and an early-stopping loop, and it carries the book's thesis to the
loss-curve level: the verdict is held-out validation loss, never training loss.

## THE locked decision: validation loss is the verdict, not training loss

"Loss went down" ends most tutorials; this module makes it the start of a question (which loss,
versus what). Every checkpoint-promotion decision in the book is grounded in `valid_loss` on a clean
held-out set, not in how low training loss got. M2 installs that discipline (M5's eval gate later
formalizes it). If this framing is wrong it reshapes every lesson, so it is locked first.

## Locked-on-the-blueprint decisions

1. **Stage = module.** Writes `build-log/weights-and-measures/m2/`; hands the validation + early-stop
   discipline forward to M4 (overfitting-aware adapter training) and M5 (the eval gate).
2. **Held to the Style Contract + STANDARDS.** House voice as set by shipped M1 + Local Metal.
3. **House cadence: overview + 4 lessons + 4 exercises.**
4. **Grounded, not fabricated.** Primary input is the in-book draft `draft/02-loss-curves-overfit.md`
   (already dense + grounded). Enriched by `aefs` Phase 03 (`07-regularization`,
   `13-debugging-neural-networks`) + `made-with-ml` `train.py` (val loop, `ReduceLROnPlateau` on
   `val_loss`) + the MS-Learn Azure AI Foundry fine-tuning metrics doc (`results.csv`: `train_loss`,
   `full_valid_loss`, `train_mean_token_accuracy`, `full_valid_mean_token_accuracy`). Every code block
   is Sonnet-written + RUN; every output real.
5. **Real PyTorch only** (the M1 grounding rule holds): the validation loop, schedulers, and
   checkpoint pattern are real `torch`; no from-scratch scaffolding handed to the reader as framework.

## Proposed M2 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The move | Ore |
|---|---------------|----------|-----|
| 0 | `00-overview` | "Is it working?" as the module thesis; the four lessons; what feeds forward to M4/M5. | draft + blueprint |
| 1 | `the-held-out-set` | Why a held-out set is trustworthy; train/val/test discipline; the leak that silently invalidates a val set; the real validation loop (`model.eval()` + `torch.no_grad()`, both required). | draft §"Two Losses"/"Validation Loop"; mwml `eval_step` |
| 2 | `reading-loss-curves` | The divergence pattern (the worked epoch table where best checkpoint = epoch 3); the generalization gap; token accuracy as a companion not a substitute (near-100% = overfit signal); LR and curve shape (jagged=too high, flat=too low). | draft §divergence/token-acc/LR; aefs `13` |
| 3 | `early-stopping-as-a-policy` | Early stopping as an auditable promotion policy (patience N=2–5; save best `valid_loss`); checkpoint what you will promote (state_dict + optimizer state + `valid_loss` key). | draft §early-stopping/checkpointing; mwml `train.py` |
| 4 | `instrumenting-the-run` | The payoff: instrument a run to catch overfitting before it wastes GPU; deliberately induce it and confirm the saved checkpoint is pre-divergence; the debug-order checklist ("fix the plumbing before the knobs"). The module's gated deliverable. | draft §"From Loss Curves to Promotion"; aefs `13` |

## The compounding throughline (extend in place)

- `exercises/spine/trainer.py` gains `evaluate(model, loader, loss_fn, device)` (the real validation
  loop, `model.eval()` + `no_grad`, returns loss + token accuracy) and an early-stopping training
  wrapper (`fit(...)`: per-epoch train + validate, track best `valid_loss`, patience, save best
  checkpoint with optimizer state). M1's `train_one_epoch` + `smoke_two_batches` stay unchanged.
- `exercises/spine/check_loop.py` grows a **`--module 2`** mode: on top of the M1 five-step + param
  checks, it requires a validation pass (`model.eval()` + a `no_grad`/`inference_mode` context) and an
  early-stopping / best-checkpoint signal (`best` + `valid`/`patience`). M1 behavior (no flag) stays
  byte-identical; `--selftest` covers both. The rubric keeps compounding.

## The fleet plan (conductor-direct, under the code-don't-write mandate)

**Round 1 (fetch).** One Haiku reads the in-book draft + the named vault ore (`aefs` `07`/`13`,
`mwml train.py`) and returns a per-lesson fact-pack with verbatim val-loop / early-stop / overfit code.
One Haiku confirms the live MS-Learn Azure AI Foundry fine-tuning metrics doc (URL + the four metric
names) + PyTorch scheduler/eval anchors.

**Round 2 (build + author).** One **Sonnet spine-engineer** extends `trainer.py` (`evaluate` + `fit`
early-stopping) and `check_loop.py` (`--module 2`), installs torch-CPU, RUNS everything (the val loop,
an induced-overfit demo that shows divergence, `check_loop --selftest` for both modules), and writes a
`FREEZE-VERIFIED.md` with real output. Then **5 Sonnet authors** (overview + 4 lessons + an
exercises/SUMMARY worker) fill the schema against STYLE/STANDARDS + the frozen code.

**Opus (me): design the schema (this PLAN + the fetch/author briefs), run the review gate (em-dash +
STYLE + grounding + the no-API-tour guardrail), do NOT hand-author or hand-code** (Ray's correction:
"no excessive coding on your part, that's what the sonnets are for").

**VERIFY → BUILD/TEST → SHIP.** VERIFY gates voice + grounding + verbatim code. BUILD runs
`check_loop.py --selftest` (both modules) + the trainer demo + `mdbook build` (SUMMARY gains M2). SHIP
folds into `src/module2/` + `exercises/module2/`, updates CATALOG, route-lint to 0, commits W&M paths
only in a clean window (the M1 shared-index discipline).

## Open decisions (resolved at self-lock)

1. THE verdict-is-validation-loss framing (above).
2. Four lessons: held-out set → reading curves → early stopping → instrumenting the run.
3. Spine: `trainer.py` gains `evaluate` + `fit`; `check_loop.py` gains `--module 2`; M1 byte-identical.
4. Draft `02-loss-curves-overfit.md` is primary input, split across L1–L4 (not shipped as one lesson).
