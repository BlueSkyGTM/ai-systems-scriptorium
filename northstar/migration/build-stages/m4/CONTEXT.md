# M4 stage — CONTEXT

Read `PLAN.md` (this folder) first — it is the locked spec. Stage pipeline: AUTHOR → VERIFY → SHIP, on the
proven M3 engine. Reads from `synthesis/source/module3/` (multi-agent + fleet/loop subset; see PLAN's positive
inclusion list). Writes drafts → `output/author/`, verdicts → `output/verify/`, ship record → `output/ship/`.

## Conventions that bind every M4 drafter
- **Voice is law.** `STYLE.md` wins every disagreement; match `src/preface.md` + the shipped `src/module3/*`.
  No template endings; vary rhythm (STYLE §8).
- **Positive inclusion list** (PLAN): load ONLY your chapter's source files. fleet-*/loop-* are M4's now (they
  were forbidden in M3). Never load the M3-shipped sources or any path containing `skills/`/`gstack/`.
- **Antilibrary fence:** ch02 is operational safety ONLY — the Ph15 research/policy half (STaR, AlphaEvolve,
  DGM, RSP, FSF, METR, CAIS) stays cut. Do not pull it in.
- **De-dup rule** (PLAN): kill-switch / HITL / verification are defined once in ch02 and referenced (not
  re-taught) at fleet scale in ch03.
- **Throughline:** every exercise extends `module4-fleet/` (built on `module3-agent/`); the `_harness/` starter
  is the substrate. Control plane Python; registries JSON/YAML; typed contracts TS (reuse M3 MCP).
- **Authority markers:** leave `[MS-Learn: …]` / `[verify: <source>]` markers for VERIFY; zero markers is a smell.
