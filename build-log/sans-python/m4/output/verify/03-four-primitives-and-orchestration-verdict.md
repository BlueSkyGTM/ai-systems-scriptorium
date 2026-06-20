# VERIFY verdict — Lesson 03: The Four Primitives & Orchestration

**Lesson:** `build-stages/m4/output/author/03-four-primitives-and-orchestration.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch01 Multi-Agent & Swarms)
**Date:** 2026-06-19

## Markers resolved (2 of 2)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: hierarchical orchestration failure modes — Cemri et al., MAST taxonomy]` (line 25) | MAST paper (arXiv 2503.13657) — Specification & System Design failures include Step Repetition (15.7%) and role-spec failures; hierarchy multiplies surface | **FIXED → removed.** Softened to a defensible, sourced statement: "Failure-mode studies of real multi-agent systems put step repetition and role confusion among the most common breakdowns, and a deep hierarchy multiplies the surface for both." No specific unverified stat asserted. |
| `[MS-Learn: Microsoft Agent Framework — orchestration and the supervisor / Magentic manager pattern]` (line 33) | MS Learn connector: "Microsoft Agent Framework Workflows Orchestrations — Magentic" + "Workflow orchestrations" table | **PASS → removed.** Confirmed verbatim: MS Agent Framework ships a **Magentic manager** that "coordinates a team of specialized agents, selecting which agent should act next" and "maintains a shared context." Rewrote into clean prose naming Magentic as the concrete example of a framework-provided supervisor. |

## Claim ledger

| Claim | Source consulted | Verdict |
|---|---|---|
| Four primitives — Agent, Handoff, Shared state, Orchestrator — carried from M3 framework lens | M3 prior art (course throughline) | PASS |
| Multi-agent raises the stakes on each knob; topology is itself choices across them | Editorial; consistent with asdg §04 | PASS |
| Three topologies: supervisor-worker, swarm/peer-to-peer, hierarchical | aefs §28 "supervisor-worker, swarm/peer-to-peer, hierarchical, debate"; asdg §04 | PASS |
| Supervisor-worker is the workhorse / default; the research-system pattern | Anthropic post (orchestrator-worker); aefs §28 | PASS |
| Swarm: no central decider, shared event bus/blackboard, self-route, scalable but non-deterministic | asdg §04 (Swarms/Handoffs, Shared Blackboard); aefs §28 | PASS |
| Hierarchical: org-chart deep, summarization per layer, prone to managerial looping | aefs §06 "Hierarchical Architecture and Its Failure Mode"; MAST step-repetition/role data | PASS (softened, sourced) |
| Debate gets its own lesson next | PLAN lessons 03→04 | PASS |
| 2026 guidance: build supervision via direct tool calls, not a supervisor library, for context control | aefs §28 (verbatim): "2026 LangChain guidance is to do supervision through direct tool calls rather than supervisor libraries for finer context control" | PASS |
| Framework managers hide the context-flow knob (Magentic example) | MS Learn — Magentic manager "maintains a shared context… selects which agent should act next" | PASS (verified, rewritten from marker) |
| `create_supervisor()` named as a framework helper | LangGraph `langgraph-supervisor` / aefs §28 lists `create_supervisor` | PASS |
| Python control plane; supervisor's tools are functions invoking workers | PLAN line 79 (control plane = Python) | PASS |
| Code block: supervisor as direct tool calls, fresh context per worker | Editorial; coherent and matches the lesson's thesis | PASS |

## STYLE result — PASS

- H1 single; second person, present tense, one voice. ✓
- Seam-framed lead (line 3): reframes the M3 four-knob lens as the multi-agent design space; no throat-clearing. ✓
- One `## Core concepts` block (3 propositions); handoff div well-formed. ✓
- Ending (line 52): cost/consequence shape ("Get the topology wrong and no amount of model quality saves you") → forward hook; not the banned template. ✓
- Acronyms: LLM standard; no unexpanded new acronyms. ✓
- Python code block earns its place (shows the direct-tool-call boundary the prose argues for). ✓
- Rhythm varied. ✓

## Overall verdict: **FIX-APPLIED** (2 markers resolved, 0 hard defects — both fixes were marker-to-prose conversions with one softening; 0 FLAGGED). Ship-ready.
