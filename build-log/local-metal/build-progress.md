# Local Metal — Build Progress

Per-stage authoring status. One row per module. Seven modules: six track the Cthulhu SPEC's
six How-To steps, plus a perf-and-tuning capstone (M7). See
`library/in-progress/local-metal/README.md` for the full blueprint.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Build | 🔒 Plan locked | — | BOM rationale, Micro Center ProBuild, stress test, first boot. Seeds `HARDWARE.md` (the capstone repo's first committed file) + `check_hardware.py`. Plan: `m1/PLAN.md`. **`GATE-LOCK-PLAN` cleared 2026-06-21.** No hardware exists ("Cthulhu" is a codename, not a machine); authored from grounded sources (SPEC + aipe + vendor docs), reader fills `HARDWARE.md` from their own build. Ready to author. |
| M2 | Linux and CUDA | ⬜ Not started | — | Dual-partition plan, distro selection, NVIDIA driver + CUDA toolkit, verification (`nvidia-smi`). MS-Learn returns as a grounding source here (Windows 11 / WSL2 contrast). |
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
