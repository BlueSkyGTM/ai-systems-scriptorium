# CONTEXT — Weights and Measures (IN PROGRESS)

The PyTorch and model-training book. It fills the gap Sans Python left thin: the 78% PyTorch +
model-training hiring screen (row 2 of `build-log/sans-python/antilibrary-gap-report.md`). Where
Sans Python teaches the fine-tune-vs-RAG decision, this book teaches the build: PyTorch mechanics,
adapter fine-tuning, and the eval pipeline that proves a tune is actually good. Thesis: a model's
weights are earned through honest evaluation, not blindly produced. Quality gates, not loss curves,
are the deliverable.

`GATE-NAME-BOOK` cleared 2026-06-21 (title **Weights and Measures**, slug `weights-and-measures`).

## Status

- **M1 "The PyTorch Operator" + M2 "Fitting and Not Fitting" shipped 2026-06-21** (each overview + 4
  lessons + 4 exercises). PLANs + ship records under `build-log/weights-and-measures/m1/` and `m2/`.
- **M3–M8 to author.** The 8-module arc is in `README.md` (the blueprint). M3 is "Dataset Craft"
  (curating fine-tuning data: quality signals, dedup, the JSONL contract, held-out set design).

## The throughline (the runnable spine)

- `exercises/spine/trainer.py` — the training-loop spine, extended in place each module (M1 the bare
  verified loop; M2 train/val + early stop; M4 the LoRA adapter; M5 the eval gate), landing as the
  M6–M8 portfolio `train.py`.
- `exercises/spine/check_loop.py` — the stdlib validator gating a loop's five steps in order + the
  trainable-parameter check (`--selftest` green). The rubric is code, not prose.

## Ore (in the vault — distil via `ingredients`, never author against raw ore)

- `ai-engineering-from-scratch` Phase 03 (Deep Learning Core / PyTorch) + Phase 07 (Transformers) +
  Phase 10 capstone training/eval items.
- `ai-performance-engineering` Ch 13 (PyTorch profiling, AMP, memory tuning; the single-GPU subset).
- `made-with-ml` training internals (`train.py`, `models.py`, `evaluate.py`).
M1 ore is distilled at `ingredients/source/weights-and-measures/pytorch-operator-catalog.md`.

## Load / don't-load

- **Load:** this folder's `README.md` (blueprint) + the module you are authoring; the named ore via
  `ingredients/source/weights-and-measures/`; `platform/conventions`; `platform/pipeline`.
- **Do NOT load:** other books; the `vault` raw ore (author against `ingredients`); any path
  containing `skills/` or `gstack/`.

## Dual-use

Written to be read by a human learner and ingested by an LLM: dense, linked, plain markdown. The
same page serves either party.

## Handoff & gates

Authoring is driven by `platform/pipeline/CONTEXT.md` (AUTHOR → VERIFY → BUILD/TEST → SHIP). Gates by
ID: `GATE-LOCK-PLAN` (per stage), `GATE-APPROVE-SHIP` (per stage), `GATE-PUBLISH` (public copy),
defined in `platform/HUMAN-GATES.md`. The book index + status lives in `CATALOG.md`.
