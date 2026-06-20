# Module 3 — Prerequisite Snapshot

> **Renumber map (8-module, 2026-06-18). THIS MODULE SPLITS.** Old Module 3 becomes two modules at the
> single↔multi-agent seam: **Tracks A–D → M3 Agent Foundations** (agent loop, tools/MCP, memory,
> frameworks); **Tracks E–H → M4 Multi-Agent Systems** (multi-agent, autonomous/safety, fleet/loop,
> computer-use). The edge list below is renumbered accordingly (`m3:`/`m4:` node prefixes); prose retains
> the original single-module analysis. Old M4 Deploy refs→M5; old M5 capstone targets→M6 (single-agent
> artifacts) / M7 (multi-agent artifacts). The `CHECK` tags are now resolved to **ANTILIBRARY** (Step 3).
> The split introduced **zero backward edges** — every A–D→E–H edge runs forward (`step2-flow-audit.md`).

Module 3 is the **orchestration / agentic core** — the largest module by far (18 source files,
~130+ lessons across the contributing phases) and the intellectual center of the AI Platform
Engineering seam. The arc is consistent across every source: **single agent that works → runs
safely for hours → coordinates with many agents → governed as a fleet in production.** Its size
is earned: multi-agent systems are the discipline's defining hard problem (affirmed by the
platformengineering.org curriculum's multi-agent emphasis).

Source files: `aefs-module3-agent-engineering` (Ph14–16, 89 lessons), `aefs-module3-tools-protocols`
(Ph13, 23 lessons), `asdg-module3-agentic-systems` (Ch07), `asdg-module3-tool-use-computer-agents`
(Ch17), `asdg-module3-memory-state` (Ch08), `asdg-module3-frameworks-tools` (Ch09),
`asdg-module3-design-patterns` (Ch15), `fleet-module3-*` (5: patterns, reference, schemas, stories,
templates), `loop-module3-*` (6: reference, patterns, docs, skills, stories, templates).

---

## Track A — Agent fundamentals & reasoning loops (asdg Ch07, aefs Ph14)

The single-agent spine. `Agent = Reasoning Model + Tool Use + Persistent Memory + Environment Feedback`.

```
agent-loop(ReAct: observe-think-act) → reflexion(critic+memory) → tot/lats(search) → self-refine/critic(verify)
agent-loop → planning-decomposition(task DAG) → error-handling-recovery(self-correction)
[complexity-ladder thread: direct call → workflow → single agent → multi-agent, only when needed]
```

Inbound: `[M2] function-calling, langgraph`. The **complexity ladder** (`GAP 2`: should-you-build-an-agent) is the editorial spine running through every source — the anti-"agent everything" governor.

## Track B — Tool use & protocols / MCP (aefs Ph13, asdg Ch17/Ch07.03)

The tool interface and the protocol stack. **MCP is covered four times over** (aefs Ph13's 23 lessons go deepest) — a major dedup/layering job, like RAG in M2.

```
tool-interface(describe-decide-execute-observe) → function-calling → structured-output/constrained-decoding
→ mcp-fundamentals → mcp-server → mcp-client → mcp-transports → resources/prompts → sampling
→ roots/elicitation → async-tasks → mcp-apps → mcp-security(poisoning) → oauth-2.1 → gateways/registries
→ a2a-protocol → otel-genai → llm-routing → skills/agent-sdks
```

Inbound: `[M1] ts:generics/interfaces` (typed tool/MCP contracts), `[M2] structured-outputs, mcp`. Outbound: `otel-genai → [M4] observability`.

## Track C — Memory & state (asdg Ch08, aefs Ph14 memory lessons)

```
memory-architectures(L1 working / L2 episodic / L3 semantic) → short-term-context(KV/paged-attn)
→ long-term-memory(vector+graph) → agentic-memory(Mem0/Letta/MemGPT) → semantic-caching
→ state-management(stateful agent graphs, checkpointing)
```

Inbound: `[M2] context-engineering, vector-databases`. Note: KV-cache/paged-attention here overlaps M4 serving (layering).

## Track D — Frameworks (asdg Ch09)

```
langchain → langgraph → langsmith ; llamaindex ; dspy[optimize] ; semantic-kernel/ms-agent-framework
crewai ; claude/openai/google SDKs ; pydantic-ai/mastra(typed) → framework-selection-guide
```

Overlaps M2 (LangGraph introduced there as state machine; here the full landscape). Layering, not duplication. `[seam]` core build frameworks; DSPy tagged `[optimize-territory]`.

## Track E — Multi-agent & swarms (aefs Ph16, asdg Ch07.04)

**The seam's defining material.**

```
why-multi-agent(single-agent ceiling) → communication-protocols(MCP/A2A/ACP/ANP) → multi-agent-primitives(Agent/Handoff/SharedState/Orchestrator)
→ orchestration-patterns(supervisor/swarm/hierarchical/debate) → multi-agent-debate → failure-modes(MASFT 14 modes)
```

Inbound: Track A (single agent) + Track B (A2A). The complexity ladder gates entry: multi-agent only past the single-agent ceiling.

## Track F — Autonomous systems & safety (aefs Ph15) — SEAM CHECK

Two halves with different seam fit:

```
SEAM (operating agents safely — keep):
long-horizon-agents → durable-execution → action-budgets/cost-governors → kill-switches/circuit-breakers
→ HITL-propose-then-commit → checkpoints/rollback → guardrails(Llama-Guard) → constitutional-ai

CHECK (research/policy survey — antilibrary candidate):
self-improvement(STaR/AlphaEvolve/DGM/AI-Scientist) → RSI-capability-vs-alignment → bounded-self-improvement
→ RSP-v3/OpenAI-PF/DeepMind-FSF → METR-time-horizons → CAIS/CAISI societal-risk
```

**Audit flag:** the operational-safety half (budgets, kill switches, HITL, checkpoints, guardrails) is squarely seam — it's how you run agents in production. The frontier-safety-policy + self-improvement-research half (RSP, FSF, METR, alignment research, RSI theory) is survey/`Learn` that's the M3 analog of the Optimize-archetype question: how much AI-safety *research/policy* belongs in an AI Platform *Engineering* build track vs antilibrary? Surface at Step 3.

## Track G — Fleet & Loop engineering (fleet 5 + loop 6) — SEAM CORE

The **production operational layer** — the clearest AI Platform Engineering material in M3. Explicit relationship from the source: **"Loops live inside fleets."**

```
LOOP (single agent-system ops): trigger → action → verification → budget/kill-switch
  patterns: daily-triage, pr-babysitter, dependency-sweeper, ci-sweeper, issue-triage (L1/L2/L3 autonomy, worktrees, verifiers)
FLEET (3+ loops / 5+ agents governance): registry → identity → permissions → inbox-HITL → audit → economics → kill-switch
  patterns: team-registry, cross-agent-audit, fleet-budget-guard, hierarchical-delegation, shared-inbox-HITL, agent-clone-fork
```

This is the infrastructure-for-running-agents that *is* the seam (matches platformengineering.org's "infrastructure platform engineering" + multi-agent emphasis). Loop graduates to Fleet at the 3-loop/5-agent threshold. Both carry machine-readable registries + schemas (the "everything as code" platform-eng vocabulary applies directly here).

## Track H — Computer-use, coding & voice agents (asdg Ch17, aefs Ph14/16)

```
computer-use-agents(screenshot-reason-act) ; coding-agents(Claude Code/OpenHands/Cursor) ; voice-agents(Pipecat/LiveKit)
benchmarks: SWE-bench/GAIA/AgentBench/WebArena/OSWorld
```

Outbound: → `[M5]` capstones (terminal coding agent, voice assistant, devops agent, multi-agent SWE team).

---

## Module 3 — flow observations (feed Step 2)

1. **Correctly the largest module** — it's the seam's center, and the single→multi→fleet arc is internally consistent across all four source repos. No backward-edge violations.
2. **The complexity ladder is the editorial through-line** (asdg + aefs Ph14/15/16 all carry `GAP 2`). It's the thesis-aligned governor: don't reach for an agent (or multi-agent, or self-modification) until the problem demands it. This thread should survive as a spine, not be cut.
3. **MCP is covered 4× deep** — biggest M3 dedup/layering job (aefs Ph13 is the canonical deep version; asdg Ch17 + Ch07.03 + aefs Ph14 tool lessons are lighter passes). Curation, not resequencing.
4. **Track F splits cleanly into seam (operational safety) vs CHECK (frontier-safety research/policy).** The research/policy half (RSP, FSF, METR, RSI, alignment research) is the M3 Optimize-analog — resolve consistently with the M4/M5 training-track decision.
5. **Fleet + Loop (Track G) are the strongest pure-seam material in the entire library** — agent infrastructure/governance. This is where Northstar most *is* AI Platform Engineering, and it's the natural home for the platform-eng vocabulary (golden paths, IDP, everything-as-code, registries).
6. **Framework + memory + KV overlaps with M2/M4** — all layering decisions (introduce in earlier module, deepen here), not duplication to cut.

## Edge list (machine-readable)
```
# Track A — Agent Foundations (M3)
M2:function-calling -> m3:agent-loop
m3:agent-loop -> m3:reflexion
m3:reflexion -> m3:tot-lats
m3:tot-lats -> m3:self-refine-critic
m3:agent-loop -> m3:planning-decomposition
m3:planning-decomposition -> m3:error-handling
# Track B — Agent Foundations (M3)
m3:tool-interface -> m3:function-calling-deep
m3:function-calling-deep -> m3:structured-output
m3:structured-output -> m3:mcp-fundamentals
m3:mcp-fundamentals -> m3:mcp-server
m3:mcp-server -> m3:mcp-client
m3:mcp-client -> m3:mcp-transports
m3:mcp-transports -> m3:mcp-resources-prompts
m3:mcp-resources-prompts -> m3:mcp-sampling
m3:mcp-sampling -> m3:mcp-async-tasks
m3:mcp-fundamentals -> m3:mcp-security
m3:mcp-security -> m3:mcp-oauth
m3:mcp-oauth -> m3:mcp-gateways-registries
m3:mcp-client -> m3:a2a-protocol
M1:ts-generics -> m3:tool-interface
M2:mcp -> m3:mcp-fundamentals
m3:otel-genai -> M5:observability-stack
# Track C — Agent Foundations (M3)
m3:memory-architectures -> m3:short-term-context
m3:memory-architectures -> m3:long-term-memory
m3:long-term-memory -> m3:agentic-memory
m3:agentic-memory -> m3:semantic-caching
m3:memory-architectures -> m3:state-management
M2:context-engineering -> m3:short-term-context
# Track D — Agent Foundations (M3)
M2:langgraph -> m3:frameworks-langgraph
m3:frameworks-langchain -> m3:frameworks-langgraph
m3:frameworks-langgraph -> m3:framework-selection
m3:frameworks-dspy -> ANTILIBRARY:optimize-territory
# Track E — Multi-Agent Systems (M4) — seam core
m3:agent-loop -> m4:why-multi-agent
m4:why-multi-agent -> m4:communication-protocols
m3:a2a-protocol -> m4:communication-protocols
m4:communication-protocols -> m4:multi-agent-primitives
m4:multi-agent-primitives -> m4:orchestration-patterns
m4:orchestration-patterns -> m4:multi-agent-debate
m4:orchestration-patterns -> m4:failure-modes
# Track F — Multi-Agent Systems (M4) — autonomous + operational safety
m3:agent-loop -> m4:long-horizon-agents
m4:long-horizon-agents -> m4:durable-execution
m4:durable-execution -> m4:action-budgets
m4:action-budgets -> m4:kill-switches
m4:kill-switches -> m4:hitl-propose-commit
m4:hitl-propose-commit -> m4:checkpoints-rollback
m4:long-horizon-agents -> m4:guardrails
m4:self-improvement-star-alphaevolve -> ANTILIBRARY:research-policy
m4:rsp-fsf-metr -> ANTILIBRARY:research-policy
# Track G — Multi-Agent Systems (M4) — fleet + loop, seam core
m3:agent-loop -> m4:loop-engineering
m4:loop-engineering -> m4:loop-patterns
m4:loop-patterns -> m4:fleet-engineering
m4:multi-agent-primitives -> m4:fleet-engineering
m4:fleet-engineering -> m4:fleet-patterns(registry/audit/budget/inbox/delegation)
m4:action-budgets -> m4:fleet-budget-guard
m4:hitl-propose-commit -> m4:shared-inbox-hitl
# Track H — Multi-Agent Systems (M4) — thin teaching, realized in artifacts
m3:agent-loop -> m4:coding-agents
m3:tool-interface -> m4:computer-use-agents
m4:coding-agents -> M6:terminal-coding-agent
m4:orchestration-patterns -> M7:multi-agent-swe-team
M1:rust-async -> m4:durable-execution
```
