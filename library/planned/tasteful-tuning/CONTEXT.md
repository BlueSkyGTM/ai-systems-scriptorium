# CONTEXT — Weights and Measures (PLANNED)

A planned book covering the **PyTorch and model-training gap** Sans Python deliberately left
thin: the 78% hiring screen (row 2 of `build-log/sans-python/antilibrary-gap-report.md`) that
M5 L13 addresses only at fine-tune-vs-RAG-vs-prompt literacy depth. Where Sans Python teaches
the decision, this book teaches the build: PyTorch mechanics, adapter fine-tuning, and the eval
pipeline that proves a tune is actually good. Thesis: a model's weights are earned through honest
evaluation, not blindly produced. Quality gates, not loss curves, are the deliverable.

Post-Sans-Python entry point. The reader has already made the fine-tune decision; this book
builds the thing. Split out from the older `ml-in-proportion` stub: PyTorch/training lives here,
classic ML (regression/trees/boosting) stays in `ml-in-proportion`.

**Not started.** Starting it is gated at `GATE-NAME-BOOK` (propose the real title first).

## Ore (in the vault — not yet distilled)

- `ai-engineering-from-scratch` Phase 03 (Deep Learning Core / PyTorch intro) and Phase 07
  (Transformers deep dive); Phase 10 capstone training-loop and eval items (lessons 36-41, 49,
  73-75). Survey via `ingredients/source/_repos/ai-engineering-from-scratch/antilibrary.md`.
- `ai-performance-engineering` Chapter 13 (PyTorch profiling, AMP, memory tuning — the
  single-GPU subset; kernel-authoring chapters 01-12 remain out of seam). Survey via
  `ingredients/source/_repos/ai-performance-engineering/antilibrary.md`.
- `made-with-ml` training internals (`train.py`, `tune.py`, `models.py`, `evaluate.py`) — the
  material antilibrary'd out of Sans Python's M4 seam is squarely in scope here. Survey via
  `ingredients/source/_repos/made-with-ml/antilibrary.md`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain
markdown. The same page serves either party.

## Load / don't-load

- **Load (when it graduates):** this folder's `README.md`, the named vault ore via
  `vault/MANIFEST.md`, `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book, other planned books, any path containing
  `skills/` or `gstack/`, `vault/` ore not named above.

## Handoff & gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
