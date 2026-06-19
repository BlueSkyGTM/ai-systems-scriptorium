# Module 4 — Migration Dossier (Multi-Agent Systems)

Source: `../sub-repos/synthesis/source/module3/` (Tracks E–H) — the **multi-agent** half of the old-M3 split,
plus fleet + loop. The seam's defining material: single agent → runs safely for hours → coordinates with
many → governed as a fleet.

## Source files in

| Source file | Verdict | Destination / note |
|-------------|---------|--------------------|
| `aefs-module3-agent-engineering.md` (Ph16, 25 lessons) | **KEEP — multi-agent** | → `src/module4/01`. Why-multi-agent, communication protocols, primitives, orchestration, debate, failure modes. |
| `aefs-module3-agent-engineering.md` (Ph15, 22 lessons) | **SPLIT** | Operational-safety half → `src/module4/02`. Research/policy half → **antilibrary** (below). |
| `asdg-module3-tool-use-computer-agents.md` (Ch17) | **KEEP — thin** | Computer-use / tool agents → `src/module4/04` (thin teaching, realized in artifacts). |
| `fleet-module3-*.md` (5: patterns, reference, schemas, stories, templates) | **KEEP — seam core** | → `src/module4/03`. Fleet governance. |
| `loop-module3-*.md` (6: docs, patterns, reference, skills, stories, templates) | **KEEP — seam core** | → `src/module4/03`. Loop engineering. |

## The Phase 15 split (the keystone Optimize ruling)

**KEEP → `src/module4/02` (operational agent safety = platform engineering):**
long-horizon agents, durable execution, action budgets / cost governors, kill switches / circuit breakers /
canary tokens, HITL propose-then-commit, checkpoints / rollback, Constitutional AI & rule overrides, Llama
Guard input/output classification, the autonomous-coding-agent landscape, Claude Code permission modes,
browser-agent attack surface.

**CUT → antilibrary (frontier-safety research/policy & self-improvement research):**
STaR/V-STaR/Quiet-STaR, AlphaEvolve, Darwin Gödel Machine, AI Scientist v2, Automated Alignment Research,
Recursive Self-Improvement theory, Bounded Self-Improvement designs, RSP v3.0, OpenAI PF / DeepMind FSF,
METR time horizons, CAIS/CAISI societal risk. (AI-safety-researcher / policy-analyst material, not
platform-build. [[optimize-archetype-ruling]])

## Track H (thin teaching, realized in artifacts)

Computer-use (Claude/CUA/Gemini), coding agents (OpenHands/Aider/Cline), voice agents (Pipecat/LiveKit),
benchmarks (SWE-bench/GAIA/WebArena/OSWorld) — taught lightly here; the heavy realization is the artifacts
they seed (coding → M6 artifact 01; voice → M6 artifact 03).

## Fleet & Loop (the strongest pure-seam material)

"Loops live inside fleets." Loop = single agent-system ops (trigger → action → verification → budget/
kill-switch); Fleet = 3+ loops / 5+ agents governance (registry → identity → permissions → inbox-HITL →
audit → economics → kill-switch). Both carry machine-readable registries + schemas (everything-as-code).

## Accounted-for check

Ph16 kept; Ph15 split (operational kept, research/policy cut); fleet+loop kept as seam core; Ch17 thin.
Nothing uncatalogued.
