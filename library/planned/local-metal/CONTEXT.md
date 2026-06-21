# CONTEXT — Local Metal (PLANNED)

The Scriptorium's home production environment (the 7th book). Progress-agnostic and
home-scale: a companion to Sans Python in the Simple Systems spirit, not an enterprise feat.
Teaches the Production AI Engineer to build a homebrew inference machine, run a local model
stack, and wire Claude Code to delegate work to it; the full arc runs from the Micro Center
parts counter to a networked local-model host with a routing layer. It is where the rest of
the library comes to run, and it gets more cutting-edge as those books are ingested.

Not started. Starting is gated at `GATE-NAME-BOOK` (propose the real title first;
candidates listed in this folder's `README.md`).

## Ore (primary source + vault depth)

- **Cthulhu SPEC** (`C:\Users\raymo\OneDrive\Claude Cowork\Github\specs\cthulhu\SPEC.md`):
  the exact hardware BOM (Ryzen 7 7700X, RTX 4060 Ti 16GB, 64GB DDR5-6000, Fractal Ridge
  SFF), the six How-To steps, the open architecture questions, and the aipe reference. This
  is the spine of the curriculum; treat its hardware and steps as authoritative.
- **`ai-performance-engineering`** (`vault/ai-performance-engineering/`; prefix `aipe`;
  725M): GPU profiling, CUDA tuning, quantization tradeoffs, serving throughput. Feeds M3,
  M4, M7. This ore was deliberately antilibraried OUT of Sans Python; it is squarely in
  scope here. Survey via `vault/MANIFEST.md` and
  `ingredients/source/_repos/ai-performance-engineering/` at process-ore time.

## Dual-Use

Written to be read by a human learner and ingested by an LLM: dense, linked, plain
markdown. Stable section anchors; machine-parseable BOM and module tables in `README.md`.

## Load / Don't-Load

- **Load (when it graduates):** this folder's `README.md`, the Cthulhu SPEC, the aipe ore
  via `vault/MANIFEST.md`, `ingredients`, `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book, other planned books, any path containing
  `skills/` or `gstack/`.

## Handoff & Gates

`GATE-NAME-BOOK` → process ore via `vault/CONTEXT.md` → `platform/pipeline/CONTEXT.md`
(`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`). See `platform/HUMAN-GATES.md`.
