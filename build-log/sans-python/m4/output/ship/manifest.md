# M4 SHIP manifest — Module 4, Multi-Agent Systems

Shipped 2026-06-19. AUTHOR → VERIFY → **SHIP** complete. 15-lesson plan; `mdbook build` PASS with M1–M4 live.

## What shipped
- 15 lessons relocated `build-stages/m4/output/author/*.md` → `src/module4/` (canonical).
- 15 exercise briefs + the `_harness/` starter relocated → `exercises/module4/`.
- `src/module4/README.md` rewritten: 4-chapter overview → 15-lesson arc.
- `src/SUMMARY.md` M4 section rewritten: 4 chapters → 15 lessons.
- 4 old ingredient stubs deleted from `src/module4/`.
- `mdbook build` — **PASS** (exit 0); 15 lesson pages + README; M1/M2/M3 validated in the same build.

## Stub → lesson map (4 ingredient chapters → 15 finished lessons)
| Old stub (deleted) | Finished lessons |
|---|---|
| 01-multi-agent-and-swarms | 01 Why Multi-Agent · 02 Communication Protocols · 03 Four Primitives & Orchestration · 04 Debate & MAST |
| 02-autonomous-and-operational-safety | 05 Long-Horizon & Durable Execution · 06 Action Budgets · 07 Kill Switches/Breakers/Canaries · 08 HITL & Checkpoints · 09 Guardrails |
| 03-fleet-and-loop-engineering | 10 The Loop · 11 Loop Patterns · 12 The Fleet · 13 Fleet Patterns & Governance-as-Code |
| 04-computer-use-coding-voice | 14 Computer-Use & Coding Agents · 15 Voice Agents & Benchmark Literacy |

## Carried forward
- `module4-fleet/` throughline + `_harness/` starter live in `exercises/module4/`; lesson 13's governed-fleet capstone is the package **M7** imports.
- ch14/15 are thin by ruling — the coding agent (M6 artifact 01) and voice assistant (M6 artifact 03) are the realizations.
- VERIFY ledger: `build-stages/m4/output/verify/SUMMARY.md` (defects caught + fixed; antilibrary fence clean; de-dup held).
- Next build step: **M5 (Deploy & Performance Engineering)** — includes the locked MLOps-inventory pass + the Docling data-ingestion lesson (see `build-stages/roadmap-coverage.md`) + the Rust entry lesson + the dry-run cloud strategy. Write `build-stages/m5/PLAN.md` first.
