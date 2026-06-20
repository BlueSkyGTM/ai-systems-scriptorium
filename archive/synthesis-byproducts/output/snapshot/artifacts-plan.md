# Artifacts Plan (was "Capstone")

Reframes the old capstone module (17 end-to-end projects + a 68-component build sequence) into the
**three application modules** that close the 8-module curriculum: **M6 Agent Artifacts**, **M7 Multi-Agent
Artifacts**, **M8 Final Systems Engineering Exam**. Not called "capstone" — every project already ships an
`outputs/skill-*.md`, so these *are* artifacts. Reviewed via autoplan (DONE_WITH_CONCERNS); grounded on the
full local capstone source. Reconciled to the 8-module structure 2026-06-18 (supersedes the earlier
"distribute into M3/M4" call).

## Three structural calls (decided)

1. **Own modules, not distributed.** Agent Artifacts are **Module 6** (apply Module 3, Agent Foundations);
   Multi-Agent Artifacts are **Module 7** (apply Module 4, Multi-Agent Systems); the exam is **Module 8**.
   Proof gets its own module so the build-an-artifact phase is a first-class part of the arc, not a tail
   on a teaching module.
2. **Compounding artifacts.** Single agents built in **M6** are reused and composed into teams in **M7**;
   the M7 team builds the **M8** exam system. Reuse at each stage — DRY across the whole proof arc, not
   three unrelated project sets. Each artifact solves a **real business problem**.
3. **Finale: elevate, don't author.** The M7 fleet artifact (and the M8 exam) reuse an existing multi-agent
   project and layer fleet governance / exam-system integration onto it, rather than authoring a new fleet
   from scratch.

## The cut: 17 → ~7 (by seam-fit, not quota)

### Module 6 — Agent Artifacts (apply Agent Foundations) — 4

Picked for distinct single-agent competencies, no overlap. **These agents are the building blocks reused
in M7.**

| # | Artifact | Competency it proves | Reused in M7 as |
|---|----------|----------------------|-----------------|
| 01 | Terminal coding agent | the canonical agent harness — plan/act/observe, tools, sandbox, cost ceiling | the coder/worker node of the SWE team |
| 08 | Production RAG chatbot (regulated vertical) | RAG + guardrails + citations + drift observability | the knowledge/retrieval service the team queries |
| 03 | Real-time voice assistant | streaming pipeline under hard latency budgets (ASR→LLM→TTS, barge-in) | the human-interface channel (optional team I/O) |
| 16 | Issue-to-PR autonomous agent | autonomous cloud worker, scoped credentials, in-sandbox CI verification | the autonomous-execution pattern the fleet governs |

### Module 7 — Multi-Agent Artifacts (apply Multi-Agent Systems) — 3

Single agents from M6 composed into governed teams.

| # | Artifact | Competency it proves | Compounds from |
|---|----------|----------------------|----------------|
| 05 | Autonomous research agent | plan-execute-verify tree search with sub-agents + sandbox | M6 worker pattern + sub-agent orchestration |
| 06 | DevOps K8s troubleshooting agent | supervisor + specialist agents, read-only, HITL Slack gates | M6 agents under a supervisor + HITL |
| 10★ | Governed multi-agent fleet | the SWE team (architect/coders/reviewer/tester via A2A) wrapped in the fleet layer: registry, budgets, HITL inbox, audit, kill-switches | M6 coding agent (01) as the coder nodes, governed |

### Module 8 — Final Systems Engineering Exam

The **M7 fleet builds the exam system end to end** — the compounding arc's terminal node. Not a new
artifact set: the governed team from M7 (artifact 10★) is pointed at a production-grade systems problem
(eval-gated pipeline / multi-tenant RAG / agentic MLOps system), using the 20 `asdg` Ch16 case studies as
reference architectures to build *a version of*. A fleet of agents run as governed infrastructure, building
a real system = AI Platform Engineering, thesis full circle.

## Relocated (not agent artifacts) → Deploy & Performance Engineering (M5)

These ride the Optimize/Deploy ruling, not this cut:
- 07 End-to-end fine-tuning pipeline — Optimize (antilibrary-adjacent; executing the train, not deciding it)
- 14 Speculative-decoding inference server — Deploy/Optimize
- 11 LLM observability & eval dashboard — Deploy
- 13 MCP server with registry & governance — Deploy/platform (its governance also feeds the M7 fleet layer)

## Part 2 (68-component build sequence) — disposition

Bound to the **Optimize ruling** (Step 3). Splits:
- **Keep (in-seam build material):** agent harness (20–29) → feeds **M6** coding agent; eval harness
  (70–75); safety stack (82–87) — real deliverables feeding M6/M7 + Deploy.
- **Antilibrary (Optimize):** GPT-from-scratch (30–49), distributed training from scratch (76–81) —
  model-training-at-scale; the sharpest cut, decided by the one consistent Optimize ruling.
- **Application internals (fold into relevant module or antilibrary):** research (50–57), multimodal
  (58–63), RAG (64–69).

## Open (Ray)

- **4/3 vs 4/4 split** — a 4th multi-agent artifact could elevate **13** (MCP governance) into M7 separately,
  rather than relocating it to M5. Minor; the own-module structure already gives multi-agent its own home.
