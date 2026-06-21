# Module 1 — The Build — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN DRAFTED — awaiting `GATE-LOCK-PLAN`.** First authoring stage for Local Metal
(graduated to `library/in-progress/local-metal` 2026-06-21; the Cthulhu rig is built and
running). M1 turns the blueprint's first module + the Cthulhu SPEC's Step 1 into finished
mdBook lessons + Claude Code exercises, in the locked Style Contract voice, at the STANDARDS
difficulty bar, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not author until Ray locks.

## The stage in one line

M1 builds the machine and makes the case for it: why each part was chosen for *inference*
(not gaming), how the SFF build comes together at the Micro Center counter, and how you prove
the rig is stable before a single model is pulled. Seam: a Production AI Engineer hits the
frontier-API cost wall; M1 is the first move toward owning a slice of compute — selecting and
verifying the metal everything else in the book runs on.

## Settled decisions (from the blueprint + the contracts + the SPEC)

1. **Stage = module.** Same module-as-stage ICM shape as Sans Python and Just Python: M1 reads
   its sources, writes `build-log/local-metal/m1/output/{author,verify,ship}/`, and hands the
   locked voice/exemplars forward to M2.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md`
   (difficulty ramp + strong-project rubric + the artifact contract), `STYLE.md` (voice).
   Every worker brief carries all three plus the canonical exemplar — cold workers do not
   inherit them.
3. **The SPEC's Step 1 is M1's spine.** The BOM is authoritative (Ryzen 7 7700X + MSI B650I
   Edge, RTX 4060 Ti 16GB, 64GB DDR5-6000 CL30, 2TB Gen4 NVMe, Fractal Ridge, Corsair SF750,
   Express ProBuild). M1 explains the *why* behind each line for an inference workload; it does
   not re-open the part selection.
4. **M1 is hardware; M2 is the OS.** M1 stops at a stable, powered, POSTing machine. Distro
   choice, partitioning, NVIDIA drivers, and CUDA are M2. No software stack in M1.
5. **The throughline starts here: `HARDWARE.md`.** M1 seeds the capstone repo's first committed
   file — the documented build (BOM as-bought, prices paid vs. SPEC estimates, stress-test +
   first-boot readouts). M2–M7 extend the same repo (CUDA notes → model configs → `ROUTING.md`
   → MCP wrapper → benchmark). The reuse is real (later modules read and append to the file on
   disk), not restated.

## Proposed M1 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | The frontier-API cost wall is real; the answer is metal you own. Here is the rig and the arc from the parts counter to a host Claude Code delegates to. | concept | SPEC intro + README thesis |
| 1 | `the-cost-wall-and-the-rig` | Why own compute at all: tokens accumulate, context overflows, the bill arrives. The SFF homebrew rig is the home-scale answer — what it is and what it will do. | concept | README positioning/thesis; SPEC role-in-fleet |
| 2 | `why-each-part` | Every BOM line is an inference decision: 16GB VRAM fits a 14B model on-card; DDR5-6000 bandwidth makes VRAM overflow tolerable; AM5 PCIe lanes; NVMe weight-loading; SFX PSU + Ridge for SFF. | build/concept | SPEC BOM table (all 7 rows) + aipe VRAM/bandwidth framing |
| 3 | `the-micro-center-run` | Buying it built: the Express ProBuild + 10-minute stress test, the open-box reality, and exactly what to verify before the machine leaves the store. | build | SPEC Step 1 + assembly row |
| 4 | `document-your-build` | First boot and the build record: confirm a clean POST and a stable stress readout, then capture the real BOM (prices paid vs. estimate) and the readouts into `HARDWARE.md`. | build | SPEC Step 1 "leave with a working machine"; STANDARDS artifact contract |

Each lesson ends in a Claude Code exercise (`exercises/module1/<slug>/README.md`) with a
concrete, machine-checkable done-when (see the hardware-done-when note + open decision 1).

## The compounding throughline (STANDARDS Part 3)

M1 seeds `HARDWARE.md` and the book's `exercises/CLAUDE.md` coaching contract (read the lesson,
find `HARDWARE.md` and read its current state, coach without solving). `HARDWARE.md` is the
first file of the portfolio repo that, by M6, becomes "the inference server Claude Code
delegates to." The M1 exercise ships a tiny validator, `check_hardware.py`, that asserts
`HARDWARE.md` has every required field filled (no placeholder text, BOM table complete, prices
present) — the hardware analogue of Just Python's `smoke.py`, and the reusable done-when checker
the later hardware modules extend.

## Sources (three-source rule, adapted for a hardware module)

1. **Ingredient:** the Cthulhu SPEC (`...\specs\cthulhu\SPEC.md`) — BOM, rationale column, and
   Step 1 — plus the aipe ore (`vault/ai-performance-engineering/`) for the
   VRAM/bandwidth/inference framing in lesson 2.
2. **Authoritative external grounding:** vendor/NVIDIA spec sheets for the exact parts and the
   aipe repo for the inference-hardware claims. **MS-Learn note:** the MS-Learn connector is the
   library's default grounding source, but consumer-PC hardware selection is outside its
   coverage; M1 grounds on vendor/NVIDIA + aipe instead and reserves the connector for M2
   (Linux/CUDA on Windows 11, the WSL2 contrast), where it applies. Flagged as a Tier-2
   narrowing to confirm at lock (open decision 4).
3. **Editorial seam framing** — "why does a Production AI Engineer need this?" in every lead.

## The fleet plan (orchestration)

Per `platform/ORCHESTRATION.md` and the Just Python A/B result (handler tier only for
concurrent gates or multiple clusters, not by worker count): **conductor-direct, no handler
tier.** One small cluster — four Sonnet workers (lessons 1–4, one writer per file) plus a
scaffold worker for the book skeleton (`book.toml`, `src/SUMMARY.md`, `src/README.md`, the
shared `theme/` copied from Just Python) and `exercises/CLAUDE.md`. The conductor authors
`00-overview`, integrates `SUMMARY.md` and all shared state, and runs the Zinsser + STYLE +
STANDARDS review gate on every draft before it lands. Workers use the connector/vendor sources
while authoring and ground every claim in a real, verified URL — no fabricated citations (the
Just Python M2/M3 fix).

## Open decisions to pressure-test (lock these with Ray)

1. **Hardware done-when.** With no code to pytest, M1's checkable done-when is a
   structured-document validator (`check_hardware.py` over `HARDWARE.md`). Confirm this is the
   accepted STANDARDS pattern for the hardware modules (M1–M2), with live command output
   (`nvidia-smi`, `ollama`, latency logs) becoming the done-when once the stack is up (M3+).
   Recommendation: **yes** — document validator now, live output later.
2. **Live-rig access for VERIFY.** The rig is built and running, but it is a separate networked
   Linux box; the authoring fleet runs on the Windows machine. Decide whether VERIFY may reach
   Cthulhu (SSH) to capture real readouts for the lessons, or whether Ray pastes the
   first-boot/stress output and the fleet authors around it. Recommendation: **Ray supplies the
   M1 readouts** (M1 is a one-time physical event); wire live access starting M3, where
   repeatable command output matters.
3. **Granularity.** 5 lessons (proposed) vs. merging lessons 1+2 (cost-wall + part rationale)
   into one → 4 lessons. Recommendation: **5**; the "why own compute" argument and the "why
   these parts" argument are distinct and both load-bearing.
4. **MS-Learn substitution in M1.** Confirm grounding M1 on vendor/NVIDIA + aipe instead of
   MS-Learn is acceptable for this module (it returns as the default in M2). Recommendation:
   **yes** — forcing MS-Learn citations onto a consumer-build module is exactly the
   fabricated-citation risk we fixed in Just Python.

On lock: the fleet scaffolds the book + authors M1, VERIFY gates it (voice + claims +
grounding), BUILD/TEST runs `mdbook build` + `check_hardware.py`, and the stage stops at
`GATE-APPROVE-SHIP` before folding into `src/` and `exercises/`.
