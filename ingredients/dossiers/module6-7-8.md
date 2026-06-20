# Modules 6–7–8 — Migration Dossier (Artifacts + Exam)

Source: `../sub-repos/synthesis/source/module5/aefs-module5-capstone.md` (17 Part-1 capstones + 68-component
Part-2 build sequence) + `../sub-repos/synthesis/output/snapshot/artifacts-plan.md` (the reconciled
own-module + compounding plan). These three modules **apply** the teaching modules; they don't introduce new
concepts.

## The compounding design

Single agents (M6) → composed into teams (M7) → the team builds the exam system (M8). Reuse at each stage.
Every artifact solves a **real business problem** and ships an `outputs/skill-*.md`.

## Module 6 — Agent Artifacts (apply M3) — 4

| # | Artifact | Competency | Reused in M7 as |
|---|----------|-----------|-----------------|
| 01 | Terminal coding agent | the canonical harness (plan/act/observe, tools, sandbox, cost ceiling) — built on the M3 agent-workbench pack | the coder node of the SWE team |
| 08 | Production RAG chatbot (regulated vertical) | RAG + guardrails + citations + drift observability | the knowledge/retrieval service |
| 03 | Real-time voice assistant | streaming under latency budgets (ASR→LLM→TTS, barge-in) | human-interface channel |
| 16 | Issue-to-PR autonomous agent | autonomous cloud worker, scoped creds, in-sandbox CI verification | the autonomous-execution pattern |

Part-2 harness build sequence (20–29) is the buildable foundation of artifact 01.

## Module 7 — Multi-Agent Artifacts (apply M4) — 3

| # | Artifact | Competency | Compounds from |
|---|----------|-----------|----------------|
| 05 | Autonomous research agent | plan-execute-verify tree search + sub-agents + sandbox | M6 worker + orchestration |
| 06 | DevOps K8s troubleshooting agent | supervisor + specialists, read-only, HITL Slack gates | M6 agents under a supervisor |
| 10★ | Governed multi-agent fleet (FINALE) | SWE team (architect/coders/reviewer/tester via A2A) wrapped in the fleet layer: registry, budgets, HITL inbox, audit, kill-switches | M6 coding agent as coder nodes, governed (M4 fleet/loop) |

**Finale principle — elevate, don't author:** the fleet artifact reuses an existing multi-agent project and
layers fleet governance onto it (DRY).

## Module 8 — Final Systems Engineering Exam

The **M7 fleet builds the exam system end to end** — the compounding arc's terminal node. Not a new artifact
set: the governed team from M7 (artifact 10★) is pointed at a production-grade systems problem (eval-gated
pipeline / multi-tenant RAG / agentic MLOps system), using the **20 `asdg` Ch16 case studies** as reference
architectures to build *a version of*. Distributed-systems vocabulary (load balancing, caching, sharding,
async/queues, CAP for distributed agent state) is assumed/applied, not taught as a standalone module
(deviation D6).

## Cuts → antilibrary (from the capstone Part-2 sequence)

- **GPT-from-scratch (30–49)** + **distributed training (76–81)** — Optimize; the sharpest cuts.
- **Application internals** (research 50–57, multimodal 58–63, RAG 64–69) — fold into the relevant artifact or
  antilibrary; not separate builds.
- Kept buildable: harness (20–29) → M6; eval harness (70–75) + safety stack (82–87) → feed M6/M7 + M5.

## Open (Ray)

4/3 vs 4/4 artifact split — a 4th M7 artifact could elevate **13** (MCP governance) separately. Minor.

## Accounted-for check

17 Part-1 capstones: 7 kept as artifacts (4 M6 + 3 M7), 4 relocated to M5 (07/11/13/14), the rest absorbed
(RAG-over-codebase/doc-QA/video-QA → artifact 08; AI tutor/code migration → folded). Part-2: harness/eval/
safety kept; GPT-from-scratch + distributed training → antilibrary. Nothing uncatalogued.
