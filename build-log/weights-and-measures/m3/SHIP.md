# SHIP RECORD — Weights and Measures M3 "Dataset Craft"

Shipped 2026-06-21. `GATE-APPROVE-SHIP` self-cleared (W&M M3–M8 straight-through, Ray-approved).

## What shipped
- `src/module3/`: overview + 4 lessons (`quality-over-quantity`, `the-jsonl-contract`,
  `deduplication-and-leakage`, `building-the-curation-gate`).
- `exercises/module3/`: 4 exercise READMEs.
- New spine tools (stdlib, no torch): `exercises/spine/check_dataset.py` (JSONL chat-contract validator
  + leakage gate) + `exercises/spine/curate.py` (drop-invalid + dedupe + seeded split + manifest).
- `ingredients/source/weights-and-measures/dataset-catalog.md`: the M3 ore ingredient.

## Verify / Build verdict
- VERIFY: STYLE clean; 3 em-dashes fixed in `the-jsonl-contract` (a role list); Core Concepts last in
  all 4 lessons; every code/number byte-identical to the frozen tools.
- BUILD/TEST: `check_dataset.py --selftest` OK (GOOD passes; 5 BAD cases fail with named reasons:
  invalid-json, role-unknown, content-empty, duplicate, leak) · `curate.py --selftest` OK (planted dup
  removed, invalid line dropped, split sizes correct, output passes the gate) · `mdbook build` clean.

## Grounding
- Canonical format = the JSONL chat contract (`messages` of `{role, content}`), grounded in the Azure
  OpenAI fine-tuning data-prep doc (the real "Clippy" example line). Concepts (dedup, leakage,
  stratified/held-out split, quality-over-quantity) grounded in `made-with-ml` + the docs, reframed as
  stdlib tooling (no Ray / Great Expectations handed to the reader).

## Fleet
Haiku-fetch (vault `made-with-ml` data pipeline + MS-Learn data-prep) / Sonnet-author (5) + a Sonnet
artifact-engineer (built + ran the two stdlib tools) / Opus-conduct (schema + review; did not hand-code).

## Next
M4 "Adapters and the Fine-Tune Build": LoRA / QLoRA / PEFT; the fine-tuning loop end to end on the
spine `trainer.py`; checkpointing; adapter merging; mixed precision (AMP). Blueprint in `README.md`.
