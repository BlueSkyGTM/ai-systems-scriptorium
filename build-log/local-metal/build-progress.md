# Local Metal — Build Progress

Per-stage authoring status. One row per module. Seven modules: six track the Cthulhu SPEC's
six How-To steps, plus a perf-and-tuning capstone (M7). See
`library/in-progress/local-metal/README.md` for the full blueprint.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Build | 📝 Plan drafted | — | BOM rationale, Micro Center ProBuild, stress test, first boot. Seeds `HARDWARE.md` (the capstone repo's first committed file) + `check_hardware.py`. Plan: `m1/PLAN.md`. Awaiting `GATE-LOCK-PLAN`. |
| M2 | Linux and CUDA | ⬜ Not started | — | Dual-partition plan, distro selection, NVIDIA driver + CUDA toolkit, verification (`nvidia-smi`). MS-Learn returns as a grounding source here (Windows 11 / WSL2 contrast). |
| M3 | The Model Stack | ⬜ Not started | — | Ollama + Docker, 14B coding model on-card, zero VRAM overflow, OpenAI-compatible API call. First module with live command-output done-whens. |
| M4 | Unified Memory | ⬜ Not started | — | 32B–70B quantized split across GPU+DDR5; latency baseline (tok/s, TTFT). aipe ore for quantization depth. |
| M5 | The Routing Layer | ⬜ Not started | — | Routing signals (cost/latency/context/task type); `ROUTING.md`; a routing function. |
| M6 | Wire to Claude Code | ⬜ Not started | — | MCP/API wrapper; live delegation session log. The portfolio artifact. |
| M7 | Perf and Tuning | ⬜ Not started | — | aipe depth: GPU profiling, KV-cache, Q4 vs Q8, throughput under load. Before/after benchmark. |

## Provenance

Graduated to `library/in-progress/local-metal` on 2026-06-21 (`GATE-NAME-BOOK` cleared: title
**Local Metal**, slug `local-metal`; the Cthulhu rig is built and running). This is the
seventh book and the library's only hardware-live title — the place every other book comes to
run. Unlike Just Python's code exercises (pytest-checkable scripts), Local Metal's done-whens
are real command output captured off the live rig (`nvidia-smi`, `ollama`, latency logs) plus
structured-document validators; the M1 plan settles how the hardware modules meet the STANDARDS
"machine-checkable done-when" bar.
