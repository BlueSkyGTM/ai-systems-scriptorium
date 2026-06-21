# Module 1 — The Build — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared).** First authoring stage for Local
Metal (graduated to `library/in-progress/local-metal` 2026-06-21). **No hardware exists** —
"Cthulhu" is the codename for the reference build (the SPEC's BOM), not a machine that is built;
this book is the curriculum that takes a reader from buying the parts to managing a networked
local-model host. M1 turns the blueprint's first module + the SPEC's Step 1 into finished mdBook
lessons + Claude Code exercises, in the locked Style Contract voice, at the STANDARDS difficulty
bar, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Decisions 1, 3, 4 locked as recommended;
decision 2 corrected (no live rig — author from grounded sources, reader verifies on their own build).

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

## Locked decisions (GATE-LOCK-PLAN, 2026-06-21)

1. **Hardware done-when — LOCKED.** With no code to pytest, M1's checkable done-when is a
   structured-document validator (`check_hardware.py` over `HARDWARE.md`); live command output
   (`nvidia-smi`, `ollama`, latency logs) becomes the done-when once the stack is up (M3+).
2. **Live-rig access for VERIFY — VOIDED (no hardware exists).** Correction 2026-06-21: there is
   no built machine; "Cthulhu" was only a codename for the spec. M1 is authored from grounded
   sources (the SPEC BOM + the aipe ore + vendor/NVIDIA docs), not from live readouts. Any
   hardware output shown in a lesson (`nvidia-smi`, a stress-test summary, a tok/s figure) must
   be a **real, published, representative** value for the exact parts, clearly framed as "what
   you should see" on the reference build — never invented, never presented as captured from a
   live rig. The done-when stays the `check_hardware.py` document validator: the reader fills
   `HARDWARE.md` from their own build. If/when a rig is actually built, live verification can be
   added back then.
3. **Granularity — LOCKED at 5 lessons.** The "why own compute" argument and the "why these
   parts" argument are distinct and both load-bearing.
4. **MS-Learn substitution in M1 — LOCKED.** M1 grounds on vendor/NVIDIA + the aipe ore;
   MS-Learn returns as the default grounding source in M2 (Linux/CUDA). Forcing MS-Learn
   citations onto a consumer-build module is exactly the fabricated-citation risk fixed in JP.

## Grounding note (decision 2, corrected)

No machine exists to query, so every hardware-specific number or readout in M1 must trace to a
real published source (NVIDIA/vendor spec sheets, the aipe ore, Ollama/distro docs) and be
framed as the expected result on the reference build — not presented as captured from a live
rig. Representative `nvidia-smi`/stress output is shown as an illustrative example the reader
reproduces on their own machine. Zero fabricated numbers: this is the same anti-fabrication
discipline as the MS-Learn citation rule (the Just Python M2/M3 fix), applied to hardware
output. VERIFY checks that each such figure carries a real source.

On lock: the fleet scaffolds the book + authors M1, VERIFY gates it (voice + claims +
grounding), BUILD/TEST runs `mdbook build` + `check_hardware.py`, and the stage stops at
`GATE-APPROVE-SHIP` before folding into `src/` and `exercises/`.
