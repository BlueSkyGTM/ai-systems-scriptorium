# CONTEXT — Machine Math (PLANNED)

A planned book filling antilibrary gap rows 3 + 6 from
`build-log/sans-python/antilibrary-gap-report.md`: classic ML fundamentals (regression, trees,
boosting, AUC-ROC, feature engineering) paired with the math each one requires (linear algebra /
calculus / probability / information theory), at applied depth. The thesis: math arrives bolted to the
fundamental that needs it. Neither half is taught alone.

**Scope boundary (recorded):** PyTorch, deep-model training, fine-tuning, and neural-network math are
OUT of scope. They are split into a separate planned book ("Tasteful Tuning"). This book ends where
the neural network begins. Classic ML only; the math it requires only.

**Post-Sans-Python positioning:** Sans Python is the core roadmap (LLM engineering, agents, fleet,
deploy). Machine Math branches from it for readers who need the MLE-adjacent layer: the ML-system-design
interview, feature work, and the math the interviewer assumes fluency in.

**Not started.** Starting it is gated at `GATE-NAME-BOOK` (propose the real title first; lead
candidate is "Machine Math"). See `README.md` for the full blueprint.

## Ore (in the vault — not yet distilled)

- `ai-engineering-from-scratch` Phase 01 (Math Foundations) + Phase 02 (ML Fundamentals): the primary
  ore for both halves of this book.
- `made-with-ml` classic-ML notebook and evaluation pipeline (`data.py`, `evaluate.py`, `predict.py`,
  holdout dataset): evaluation and artifact ore. Training internals (`train.py`, `models.py`) are
  antilibrary for mwml and remain excluded here (PyTorch / deep-training seam).
- Survey both at process-ore time via `vault/MANIFEST.md` and `ingredients/source/_repos/`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown. The
same page serves either party.

## Load / don't-load

- **Load (when it graduates):** this folder's `README.md`, the named vault ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book; other planned books; any `made-with-ml` training
  internals (`train.py`, `models.py`, `tune.py`); anything under `skills/` or `gstack/`.

## Handoff & gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
