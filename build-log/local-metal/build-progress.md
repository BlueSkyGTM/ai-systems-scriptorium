# Local Metal — Build Progress

Per-stage authoring status. One row per module. Seven modules: six track the Cthulhu SPEC's
six How-To steps, plus a perf-and-tuning capstone (M7). See
`library/in-progress/local-metal/README.md` for the full blueprint.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Build | ✅ Authored, verified, built — awaiting `GATE-APPROVE-SHIP` | — | 5 lessons (overview + the-cost-wall-and-the-rig, why-each-part, the-micro-center-run, document-your-build) + 4 exercises. Throughline: `HARDWARE.md` + `check_hardware.py` built across L2–L4; `breakeven.py` standalone in L1. Authored conductor-direct (4 Sonnet workers; conductor wrote the preface/overview, reviewed every draft, reconciled a 3-way BOM-column divergence to one 5-column layout, and tested the validator: 1 positive + 4 negative cases pass). VERIFY: STYLE clean (zero em-dashes); every hardware number grounded to a real cited URL (no fabrication), captured to `vault/local-metal/m1-sources/PROVENANCE.md`. BUILD: `mdbook build` clean. Plan: `m1/PLAN.md`. |
| M2 | Linux and CUDA | ✅ Authored, verified, built — awaiting `GATE-APPROVE-SHIP` | — | 5 lessons (overview + the-dual-partition-plan, choosing-and-installing-linux, nvidia-drivers-and-cuda, verify-the-gpu-is-visible) + 4 exercises. Throughline: `SETUP.md` + `check_setup.py` built across L2–L4 (README-only; the repo's 2nd file, metal → OS → stack); `partition_plan.py` standalone in L1. Authored conductor-direct (4 Sonnet workers). VERIFY: STYLE clean (zero em-dashes); MS-Learn-primary grounding (WSL2 contrast) + NVIDIA/Ubuntu docs, cited URLs captured to `vault/local-metal/m2-sources/PROVENANCE.md`. Conductor reconciled an L4 schema divergence (off-spec field names → canonical Distro/Version/Kernel/Disk layout + 3 driver fields) and an L2↔L3 function-naming mismatch; final validator tested (1 positive + 4 negative cases). BUILD: `mdbook build` clean. Plan: `m2/PLAN.md`. |
| M3 | The Model Stack | ⬜ Not started | — | Ollama + Docker, 14B coding model on-card, zero VRAM overflow, OpenAI-compatible API call. First module with live command-output done-whens. |
| M4 | Unified Memory | ⬜ Not started | — | 32B–70B quantized split across GPU+DDR5; latency baseline (tok/s, TTFT). aipe ore for quantization depth. |
| M5 | The Routing Layer | ⬜ Not started | — | Routing signals (cost/latency/context/task type); `ROUTING.md`; a routing function. |
| M6 | Wire to Claude Code | ⬜ Not started | — | MCP/API wrapper; live delegation session log. The portfolio artifact. |
| M7 | Perf and Tuning | ⬜ Not started | — | aipe depth: GPU profiling, KV-cache, Q4 vs Q8, throughput under load. Before/after benchmark. |

## Provenance

Graduated to `library/in-progress/local-metal` on 2026-06-21 (`GATE-NAME-BOOK` cleared: title
**Local Metal**, slug `local-metal`). **No hardware exists** — "Cthulhu" is the codename for the
reference build (the SPEC's BOM), not a running machine; the book is the curriculum that takes a
reader from buying the parts to managing a networked local-model host. This is the seventh book
and the library's only hardware-grounded title — the place every other book eventually comes to
run. Unlike Just Python's code exercises (pytest-checkable scripts), Local Metal's done-whens are
structured-document validators plus representative **published** command output (`nvidia-smi`,
`ollama`, latency logs) the reader reproduces on their own build; the M1 plan settles how the
hardware modules meet the STANDARDS "machine-checkable done-when" bar without a live rig.
