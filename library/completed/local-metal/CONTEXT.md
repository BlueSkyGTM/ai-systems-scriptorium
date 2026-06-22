# CONTEXT — Local Metal (COMPLETED)

The Scriptorium's home production environment (the 7th book) and the place the rest of the
library comes to run. Progress-agnostic and home-scale: a companion to Sans Python in a
keep-it-simple spirit, not an enterprise feat. Teaches the Production AI Engineer to build a
homebrew inference machine (the reference build is codenamed Cthulhu in the SPEC), run a local
model stack, and wire Claude Code to delegate work to it; the arc runs from the Micro Center
parts counter to a networked local-model host with a routing layer. It gets more cutting-edge as
the other books are ingested.

**Graduated to in-progress 2026-06-21; relocated to `library/completed/local-metal` on
content-completion 2026-06-21.** `GATE-NAME-BOOK` cleared (title **Local Metal**, slug
`local-metal`). **No hardware exists yet** — "Cthulhu" is the codename for the reference build
(the SPEC's BOM), not a machine; this book is the curriculum that takes a reader from buying the
parts to managing a networked local-model host. It is authored from grounded sources (the SPEC +
the aipe ore + vendor/NVIDIA + Ollama/distro docs); the reader confirms outputs on their own
build. **ALL 7 MODULES SHIPPED 2026-06-21 — the book is content-complete** (`GATE-APPROVE-SHIP`
cleared per module): M1 "The Build" (`HARDWARE.md` + `check_hardware.py` + `breakeven.py`), M2 "Linux
and CUDA" (`SETUP.md` + `check_setup.py` + `partition_plan.py`), M3 "The Model Stack" (`MODELS.md` +
`check_models.py` + the runnable `ollama_client.py` seed + `stack_check.py`), M4 "Unified Memory"
(`LATENCY.md` + `check_latency.py` + `bench.py` + `vram_fit.py`), M5 "The Routing Layer" (`ROUTING.md`
+ `check_routing.py` + `route.py`), M6 "Wire to Claude Code" (`mcp_server.py` + `.mcp.json` +
`DELEGATION.md` + `check_delegation.py`), and M7 "Perf and Tuning" (`TUNING.md` + `check_tuning.py` +
`loadbench.py`). 35 lessons + 28 exercises; 7 portfolio documents (HARDWARE/SETUP/MODELS/LATENCY/
ROUTING/DELEGATION/TUNING.md) + the runnable spine `ollama_client.py` -> `route.py` -> `mcp_server.py`;
`mdbook build` clean; zero em-dashes book-wide; every code artifact tested. See
`build-log/local-metal/build-progress.md`. **Relocated to `library/completed/local-metal`
2026-06-21 (the cataloguing move, no gate). A public copy remains the separate `GATE-PUBLISH`.**

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

- **Load:** this folder's `README.md`, the Cthulhu SPEC, the aipe ore via `vault/MANIFEST.md`,
  `ingredients`, `platform/conventions` (AUTHORING + STANDARDS + STYLE), `platform/pipeline`.
- **Do NOT load:** the shipped Sans Python book, other books, any path containing `skills/`
  or `gstack/`.

## Handoff & Gates

The book is content-complete (all 7 modules shipped). To **fix or edit a shipped lesson**: read the
lesson in `src/moduleN/` + its exercise `README.md` + the `build-log/local-metal/` verify verdict,
make the change, re-run the affected validator and `mdbook build`; this is autonomous (no gate).
**Publishing a public copy** is the separate `GATE-PUBLISH`. The historical authoring route (draft
`build-log/local-metal/mN/PLAN.md` -> `GATE-LOCK-PLAN` -> pipeline -> `GATE-APPROVE-SHIP`) is
preserved in `build-log/local-metal/m{1..7}/PLAN.md`. See `platform/HUMAN-GATES.md`.
