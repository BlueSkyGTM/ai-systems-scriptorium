# Module 1 — The PyTorch Operator — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21** (Ray: "Lock as recommended"). All four open decisions resolved as
recommended below. `GATE-NAME-BOOK` cleared 2026-06-21: title **Weights and Measures**, graduated
slug **`weights-and-measures`** (legacy planned-dir slug was `tasteful-tuning`). The in-progress
directory graduation (`git mv` + route-manifest + CATALOG + root router) is held until SHIP; its
former blocker — the concurrent Answer Engineering M6 ship — **landed at `c52b1e8`**, so the
shared-file race window is closed and graduation can proceed when M1 ships.

## The stage in one line

The hiring screen says "PyTorch"; the job means "can you read, run, and modify a training script
without flailing, and know what each part asserts about your data and model." M1 builds exactly that
surface — tensors, autograd, `nn.Module`, the training loop, `DataLoader`, optimizers — and installs
the book's through-line question on lesson one: **how do I know this is doing what I think?** It is
the PyTorch foundation every later module modifies (adapter insertion in M4, the eval gate in M5),
and it lays the first segment of the runnable spine the portfolio artifacts (M6–M8) are built from.

## THE decision to lock: M1 is mechanics-only; loss curves move to M2

The existing `library/planned/tasteful-tuning/draft/` scaffold frames M1 as **two** lessons —
`01-tensor-autograd-loop` and `02-loss-curves-overfit`. The locked 8-module blueprint
(`README.md`) instead reserves loss curves, train/val discipline, overfitting, and early stopping
for **M2, "Fitting and Not Fitting."** These disagree, and the disagreement shapes both modules.

**Recommendation: follow the blueprint.** M1 is the PyTorch *operator* module — the mechanics of
making a loop run and verifying it before it burns compute. M2 is the *judgment* module — the
vocabulary of "is it working" (loss curves, the overfitting signal, early stopping). Keeping loss
curves in M2 (a) matches the blueprint's deliberate 8-module arc, (b) gives M1 a clean single
thesis (read/run/modify/verify a loop) instead of two, and (c) lets M2 open on the loss-curve
content the draft already wrote — that draft (`02-loss-curves-overfit.md`) becomes M2 input, not M1.
The strong existing `draft/01-tensor-autograd-loop.md` is split and reused as M1 input (see split
below); the drafts are ungraduated, so they are treated as raw input, not committed content.

If this is wrong, it changes the M1/M2 lesson counts and what feeds forward into M4.

## Locked-on-the-blueprint decisions

1. **Stage = module.** Same ICM shape as the shipped books; writes `build-log/weights-and-measures/m1/`,
   hands the PyTorch surface forward to M2 (fitting/overfitting) and M4 (adapters on this loop).
2. **Held to the Style Contract** (`platform/conventions/STYLE.md`) and the three central
   contracts (`STANDARDS.md`): difficulty bar, project rubric, artifact-chaining. House voice as set
   by the shipped Local Metal / Just Python technical lessons (the closest tonal kin — runnable code,
   "what you should see," verify-before-you-scale discipline).
3. **House cadence: overview + 4 lessons + 4 exercises.**
4. **Grounded, not fabricated.** Every code block is authored and **run** by the conductor (the
   Local Metal pattern: Opus owns + tests each artifact, pastes byte-identical into worker briefs;
   near-zero drift). Published numeric outputs are labeled "what you should see"; the reader confirms
   on their own machine. PyTorch/CUDA claims are grounded in real docs — MS-Learn (Azure ML PyTorch
   training, device/compute config) where it fits, plus PyTorch's own docs via the Haiku fetch tier.
5. **Runnable from M1 (proposed spine, see throughline).** Unlike Local Metal/AE, this book's code
   needs PyTorch (not stdlib); the offline `--selftest` contract becomes a **CPU, <30s** smoke run.

## Proposed M1 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The mechanics and the verify-discipline | Ore |
|---|---------------|-----------------------------------------|-----|
| 0 | `00-overview` | The PyTorch the job actually tests; the through-line question installed; what M1 feeds forward. | blueprint + draft 00 |
| 1 | `tensors-and-autograd` | Tensor = array + `device` + `requires_grad`; the three attributes to check (`shape`/`dtype`/`device`); the autograd DAG; `loss.backward()`; gradient accumulation and `zero_grad`. Verify gradients by hand on a toy before trusting the engine. | aefs P03 `03-backpropagation`, `11-intro-to-pytorch`; draft 01 (split) |
| 2 | `the-module-and-the-loop` | `nn.Module` as the model contract (`__init__`/`forward`/`state_dict`); the canonical five-step loop; the trainable-vs-total parameter-count check (the M4 LoRA-freeze precondition); what to log per batch. | aefs P03 `10-mini-framework`; mwml `models.py`,`train.py`; draft 01 (split) |
| 3 | `data-optimizers-checkpoints` | `DataLoader` (batch size, shuffle, `num_workers`, `pin_memory`); optimizers and one LR schedule; checkpointing via `state_dict`; GPU transfer and the CPU/CUDA device-mismatch error. | aefs P03 `06-optimizers`,`09-learning-rate-schedules`; mwml `train.py` |
| 4 | `reading-a-real-train-py` | The payoff: read an unfamiliar `train.py`, name what each section asserts, run the **two-batch smoke test** (loss decreases, right params trainable, shapes match) before scaling. Debugging neural nets as verification, not vibes. | aefs P03 `13-debugging-neural-networks`; mwml `train.py` |

Each lesson ends in a `## Core Concepts` block and a `claude-handoff` to its exercise, matching the
shipped books. Exercises mirror the lesson slugs under `exercises/module1/<slug>/`.

## The compounding throughline (proposed — for Ray to lock)

Every shipped book has a compounding artifact: Local Metal's `ollama_client.py → route.py →
mcp_server.py` spine; Answer Engineering's `check_prep.py` prep-dossier validator; Just Python's
M6+M7 → M8 chain. Weights and Measures should not be the exception.

**Proposal:** a runnable spine `trainer.py` the reader builds in M1 and **extends in place** each
module — M1 the bare verified loop, M2 the train/val split + early-stopping hook, M3 the dataset
contract, M4 the LoRA adapter insertion, M5 the eval gate — landing as the M6 portfolio `train.py`.
Plus a stdlib **`check_loop.py`** completeness/contract validator in the `check_*.py` family (same
`[^\S\n]` field-regex pattern as Local Metal / AE), so the structure is gated by code even though the
PyTorch run is the reader's. M1's exercise = build the verified five-step loop with the two-batch
smoke test; `check_loop.py` confirms the loop has all five steps wired in the right order and the
param-count check present, without importing torch.

This makes the eval-gate thesis ("most tutorials end at 'loss went down'; this book ends at 'the
gate passed'") concrete from lesson one, and gives the verify/build stage a torch-free gate to run.

## Ore augmentation (the first move, on lock)

A distillation pass produces `ingredients/source/weights-and-measures/pytorch-operator-catalog.md`:
for each M1 lesson, the minimal correct code (authored + run by the conductor), the real expected
output, the one verification discipline, and the grounded doc anchor. Author against this ingredient,
not the raw vault tree. Sources: aefs Phase 03 (lessons named above), `made-with-ml`
`train.py`/`models.py`, and live PyTorch + MS-Learn docs via the Haiku fetch tier.

## The fleet plan (Haiku-fetch / Sonnet-author tier, conductor-direct)

**Round 1 (ground + frame).** One **Haiku** fetches the live PyTorch docs for the M1 surface
(`torch.Tensor`, autograd, `nn.Module`, `DataLoader`, `optim`) + the MS-Learn Azure ML PyTorch
training page, returning URLs/facts; one **Sonnet** distills `pytorch-operator-catalog.md` from the
Haiku facts + the named ore. The conductor (Opus) **writes and runs** every code block on a
torch-CPU env, fixes drift, and freezes the verified snippets. Conductor authors `00-overview` +
the SUMMARY wiring.

**Round 2 (author).** Four **Sonnet** lesson-writers (one per L1–L4) + one **Sonnet**
exercises/validator worker, parallel, each briefed with the Style Contract + STANDARDS + the
shipped Local-Metal voice exemplars + the ingredient + the conductor's frozen code blocks (pasted
byte-identical). The conductor runs the Zinsser + STYLE + STANDARDS review gate, watches the
recurring risks (em-dash leaks; code-in-prose instead of fenced; any lesson drifting from
"verify what you run" into API-tour completeness), then reconciles `trainer.py` + `check_loop.py`.

**Verify / Build / Ship.** VERIFY gates voice + grounding + the no-API-tour guardrail; BUILD/TEST
runs `mdbook build` + `check_loop.py` + the torch-CPU smoke (`<30s`) + pytest; SHIP folds lessons
into `src/module1/` and exercises into `exercises/module1/` at `GATE-APPROVE-SHIP`.

## Open decisions (for Ray at lock)

1. **The M1/M2 boundary** — adopt the blueprint (M1 mechanics-only, loss curves → M2) over the
   draft's 2-lesson framing? (Recommended: yes.)
2. **The runnable spine + `check_loop.py` throughline** — establish the compounding `trainer.py` +
   stdlib validator from M1? (Recommended: yes; it carries the eval-gate thesis and gives the build
   stage a torch-free gate.)
3. **The test-gate's torch dependency** — does the repo's BUILD/TEST run a torch-CPU smoke for the
   code artifacts, or does the conductor author+verify them off-repo (Local Metal "what you should
   see" pattern) with only the stdlib validator in CI? (Recommended: conductor verifies off-repo +
   stdlib validator in CI, so the repo's gate stays torch-free and fast; the reader runs torch.)
4. **Graduation timing** — confirm the directory graduation + slug `weights-and-measures` lands as a
   single staged commit *after* the concurrent AE M6 ship, to avoid a shared-file race.
