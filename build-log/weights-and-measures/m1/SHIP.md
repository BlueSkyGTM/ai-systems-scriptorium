# SHIP RECORD — Weights and Measures M1 "The PyTorch Operator"

Shipped 2026-06-21. `GATE-APPROVE-SHIP` cleared by Ray ("approve, ship now").

## What shipped
- `src/module1/`: overview + 4 lessons (`tensors-and-autograd`, `the-module-and-the-loop`,
  `data-optimizers-checkpoints`, `reading-a-real-train-py`).
- `exercises/module1/`: 4 exercise READMEs (one per lesson).
- `exercises/spine/`: `trainer.py` (the training-loop spine) + `check_loop.py` (the stdlib validator).
- `ingredients/source/weights-and-measures/pytorch-operator-catalog.md`: the M1 ore ingredient.

## Verify / Build verdict
- VERIFY: 23 em/en-dashes swept; STYLE clean (Title Case, no bare technical terms in prose, Core
  Concepts + handoff divs present); every code block byte-identical to the frozen source; every
  numeric output real.
- BUILD/TEST: `check_loop.py --selftest` OK · `check_loop.py trainer.py` PASS · `py_compile` OK ·
  `trainer.py` runs to final loss `0.0534` (torch 2.12.1+cpu) · `mdbook build` clean, 0 warnings.

## Grounding
- Real PyTorch idioms from `aefs 11-intro-to-pytorch` + `made-with-ml` production `train_step`/
  `eval_step` + live PyTorch / MS-Learn doc anchors. The `aefs` from-scratch code (the `Value`
  autograd class, the hand-rolled `Adam`) is fenced off as conceptual scaffolding, never handed to
  the reader as the framework.
- Verified anchors: L1 grads `tensor(-3.) tensor(-1.)`; L2 `TinyClassifier(128, 4)` = `516` params;
  L4 smoke `1.4134 → 1.1398`; demo trajectory `1.1953 → 0.0534`.

## Fleet
Haiku-fetch (vault ore + live docs) / Sonnet-author (5 authors) / Opus-conduct (designed the schema,
froze the code contract, ran the review gate; did not hand-author). A Sonnet spine-engineer wrote +
ran the torch code; a Sonnet VERIFY worker swept STYLE; a Sonnet BUILD worker scaffolded + ran mdbook.

## Graduation
Book graduated `library/planned/tasteful-tuning` → `library/in-progress/weights-and-measures` (slug
locked `weights-and-measures`); route-manifest + CATALOG + root router + `library/CONTEXT.md`
updated; `route-lint` green. Shipped in a paused-concurrent-session window to avoid a shared git-index
crossover with the other active session.

## Next
M2 "Fitting and Not Fitting" (loss curves, train/val discipline, overfitting, early stopping). The
draft `draft/02-loss-curves-overfit.md` is M2 input. Full 8-module arc in `README.md`.
