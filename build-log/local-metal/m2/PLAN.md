# Module 2 — Linux and CUDA — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared).** All five open decisions accepted as
recommended (Ubuntu 24.04 LTS spine; apt CUDA install path; nvidia-smi + deviceQuery verification,
framework-free; new `SETUP.md` + `check_setup.py` throughline; the M1 live-vs-expected rule). Second
authoring stage for Local Metal (M1 "The Build" shipped 2026-06-21). M2 turns the machine into a
development host: it picks an OS, installs it alongside Windows, lays down the NVIDIA driver and CUDA
toolkit, and proves the GPU is visible to code. Same contracts and fleet shape as M1.

## The stage in one line

M1 left a stable machine that POSTs. M2 makes it useful: a dual-boot Linux partition with the NVIDIA
driver and CUDA toolkit installed and verified, so every later module (the model stack, the routing
layer) has a working GPU runtime underneath it. Seam: the toolchain a local inference host runs on
(Ollama, Docker, CUDA kernels) targets Linux + CUDA; getting that base right once is what keeps the
rest of the book from fighting its own environment.

## Settled decisions (from the blueprint + the SPEC Step 2)

1. **Stage = module.** Same shape as M1: reads its sources, writes
   `build-log/local-metal/m2/output/{author,verify,ship}/`, hands the locked voice forward.
2. **Held to the three contracts** (AUTHORING + STANDARDS + STYLE); every worker brief carries them
   plus the M1 lessons as the now-locked voice exemplar.
3. **MS-Learn returns as a primary grounding source.** Unlike M1 (consumer hardware, vendor-grounded),
   M2 is squarely in MS-Learn's coverage: Linux/CUDA, WSL2 on Windows 11, dev-environment setup. The
   connector leads here, alongside NVIDIA's CUDA install guide and the distro's own docs. Every claim
   carries a real cited URL; sources captured to `vault/local-metal/m2-sources/PROVENANCE.md`.
4. **The portfolio repo compounds to a second file.** M1 shipped `HARDWARE.md` (the metal). M2 seeds
   `SETUP.md` (the software baseline: distro + kernel, NVIDIA driver, CUDA toolkit, the verification
   readout) and `check_setup.py` (completeness-gated, same pattern as `check_hardware.py`). The repo
   now tells the story metal -> OS -> runtime.

## Proposed M2 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | The metal is real; now make it a development host. The dual-boot plan, the distro, the driver/CUDA stack, and proving the GPU answers to code. | concept | SPEC Step 2 + M1 close |
| 1 | `the-dual-partition-plan` | Windows for gaming and firmware, Linux as the inference workhorse; split the 2TB NVMe and know why the bare Linux partition beats WSL2 for a serving host. | concept | SPEC ("dual-partition"); MS-Learn WSL2+CUDA as the contrast |
| 2 | `choosing-and-installing-linux` | Pick a distro on real criteria (LTS kernel stability, CUDA support, community, package freshness); Ubuntu LTS as the safe default; the bootable-USB-to-first-boot install. | build | distro docs; MS-Learn dev-env setup |
| 3 | `nvidia-drivers-and-cuda` | Install the NVIDIA driver and CUDA toolkit the maintainable way (the distro/CUDA apt repo), and respect the driver-vs-CUDA version matrix that breaks naive installs. | build | NVIDIA CUDA install guide; MS-Learn |
| 4 | `verify-the-gpu-is-visible` | Prove the stack: `nvidia-smi` reports the driver, CUDA version, and the RTX 4060 Ti; a minimal CUDA check (`deviceQuery` / `nvcc`) confirms code can reach the GPU. Record it. | build | NVIDIA docs; aipe |

Each lesson ends in a Claude Code exercise with a machine-checkable done-when.

## The compounding throughline (STANDARDS Part 3)

M2 seeds `SETUP.md` (built across lessons 2-4: distro + kernel in L2, driver + CUDA in L3, the
`nvidia-smi`/`deviceQuery` verification readout in L4) and `check_setup.py`, which asserts the record
is complete and that the captured `nvidia-smi` output names a CUDA version and a detected GPU. It
reuses the M1 validator pattern (sections present, no placeholders, the gate exits 0/1). Readers with
the machine capture live output; readers still pre-build record the expected readout and the validator
checks completeness, not live truth (same rule M1 set).

## Sources (three-source rule)

1. **Ingredient:** SPEC Step 2 ("Choose and install Linux"; dual-partition; CUDA drivers recognized)
   + the aipe ore for the CUDA/runtime framing.
2. **MS-Learn connector (primary here) + NVIDIA CUDA install guide + distro docs.** Use the tools;
   cite real URLs; capture to the vault. WSL2-on-Windows-11 is cited as the deliberate contrast in L1.
3. **Editorial seam framing** in every lead.

## The fleet plan

Conductor-direct (the M1 pattern that worked): 4 Sonnet workers (lessons 1-4, one writer per file) +
the conductor authoring the overview, integrating `SUMMARY.md`/shared state, reviewing every draft to
STYLE + STANDARDS, reconciling the `SETUP.md`/`check_setup.py` artifact to one canonical shape, and
testing the validator before ship. Workers use the MS-Learn connector while authoring; zero fabricated
citations.

## Locked decisions (GATE-LOCK-PLAN, 2026-06-21 — all accepted as recommended)

1. **Distro default.** Ubuntu 24.04 LTS as the book's recommended distro (largest CUDA-doc and
   community base), with Pop!_OS noted as the NVIDIA-batteries-included alternative. Recommendation:
   **Ubuntu 24.04 LTS** as the spine, Pop!_OS as a one-paragraph alternative.
2. **CUDA install path.** The distro/CUDA apt repo (driver + toolkit) as the taught path vs the NVIDIA
   `.run` installer. Recommendation: **apt repo path** (maintainable, survives kernel updates), with
   the `.run` installer named as the escape hatch.
3. **Verification depth.** `nvidia-smi` + the CUDA-samples `deviceQuery` / `nvcc --version` as the
   proof, deliberately **without** pulling in PyTorch (that is Weights and Measures). Recommendation:
   **nvidia-smi + deviceQuery**, framework-free.
4. **Throughline file.** A new `SETUP.md` + `check_setup.py` (vs extending M1's `HARDWARE.md`).
   Recommendation: **new `SETUP.md`** so the repo grows file-by-file (metal -> OS -> stack).
5. **Live vs expected output.** Same rule as M1: live capture when the reader has the machine, recorded
   expected readout otherwise, validator gates completeness. Recommendation: **keep the M1 rule.**

On lock: the fleet authors M2, VERIFY gates voice + grounding, BUILD/TEST runs `mdbook build` +
`check_setup.py`, and the stage stops at `GATE-APPROVE-SHIP` before folding in.
