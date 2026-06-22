# CONTEXT — Machine Math (IN PROGRESS)

Classic ML fundamentals (regression, trees, boosting, AUC-ROC, feature engineering) paired with the
math each one requires (linear algebra / calculus / probability / information theory), at applied
depth. The thesis: math arrives bolted to the fundamental that needs it. Neither half is taught alone.
Fills antilibrary gap rows 3 + 6 from `build-log/sans-python/antilibrary-gap-report.md`.

**Graduated to in-progress 2026-06-21; Module 1 shipped.** `GATE-NAME-BOOK` cleared (title **Machine
Math**, slug `machine-math`; lead candidate from the blueprint, the two-word house-style pairing of
"machine" and "math"). **M1 "The Shape of Data"** (overview + 2 lessons + 2 exercises) installs the
row-is-a-point reframing and seeds the from-scratch `exercises/ml/` package throughline (`distances.py`
+ `knn.py`, each `pytest`-gated; negative case tested). Authored under the Haiku-fetch / Sonnet-author /
Opus-conduct division of labor; `mdbook build` clean, reference harness 10/10, zero em-dashes, 7
Microsoft Learn citations verified live. See `build-log/machine-math/build-progress.md` for per-module
status and `README.md` for the full seven-module blueprint.

**Scope boundary (recorded):** PyTorch, deep-model training, fine-tuning, and neural-network math are
OUT of scope. They are split into a separate planned book ("Weights and Measures"). This book ends
where the neural network begins. Classic ML only; the math it requires only.

**Post-Sans-Python positioning:** Sans Python is the core roadmap (LLM engineering, agents, fleet,
deploy). Machine Math branches from it for readers who need the MLE-adjacent layer: the ML-system-design
interview, feature work, and the math the interviewer assumes fluency in.

## Ore (in the vault — not yet distilled)

- `ai-engineering-from-scratch` (`aefs`) Phase 01 (Math Foundations) + Phase 02 (ML Fundamentals): the
  primary ore for both halves of this book.
- `made-with-ml` (`mwml`) classic-ML notebook and evaluation pipeline (`data.py`, `evaluate.py`,
  `predict.py`, holdout dataset): evaluation and artifact ore. Training internals (`train.py`,
  `models.py`, `tune.py`) are antilibrary for mwml (PyTorch / deep-training seam) and remain excluded.
- Survey both at process-ore time via `vault/MANIFEST.md` and `ingredients/source/_repos/`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown. An
LLM using this book as context for an ML-system-design question should be able to cite the relevant
math and the relevant fundamental in the same sentence, because the book stores them adjacent.

## Load / don't-load

- **Load:** this folder's `README.md` and `draft/`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/conventions` (AUTHORING + STANDARDS + STYLE), `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book; other books; any `made-with-ml` training internals
  (`train.py`, `models.py`, `tune.py`); anything under `skills/` or `gstack/`.

## Handoff & gates

`GATE-NAME-BOOK` cleared; M1 shipped (`GATE-LOCK-PLAN` + `GATE-APPROVE-SHIP` cleared 2026-06-21). Ray
approved self-clearing `GATE-APPROVE-SHIP` for M2–M7 to run the book straight through. For the next
module: distill its `aefs` ore slice into `ingredients/source/machine-math/`, draft its
`build-log/machine-math/m<n>/PLAN.md`, lock it, then the Haiku-fetch / Sonnet-author fleet runs it via
`platform/pipeline/CONTEXT.md` (AUTHOR → VERIFY → BUILD/TEST) with Opus conducting and gating; commit
and push each module as it lands. See `platform/HUMAN-GATES.md` and `build-log/machine-math/build-progress.md`.
