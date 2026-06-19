# Frameworks & Patterns

> **Migrated from** `aefs-module3-agent-engineering` (Ph14 13–18) + `asdg-module3-frameworks-tools` (Ch09) +
> `asdg-module3-design-patterns` (Ch15). **Merge:** one landscape + one selection guide.

## The framework landscape

- **LangGraph** — agent as a state machine: typed immutable state, pure-function nodes, conditional edges, a
  checkpoint after every step (a failed 40-step run resumes from step 38). Durable execution, streaming,
  HITL, memory; supervisor / swarm / hierarchical topologies.
- **AutoGen v0.4 → Microsoft Agent Framework** — the actor model: private state + inbox + handler, messages
  as the only IPC; fault isolation, concurrency, distribution as transport.
- **CrewAI** — role-based: Agent / Task / Crew / Process; Crews (autonomous) vs Flows (deterministic,
  auditable) — "start with a Flow."
- **OpenAI Agents SDK** — Agent / Handoff (`transfer_to_<agent>`) / Guardrail / Session / Tracing on the
  Responses API.
- **Claude Agent SDK** — the Claude Code harness as a library: built-in tools, subagents, lifecycle hooks,
  session store.
- **Agno / Mastra** — lightweight production runtimes (Python ~2μs instantiation / TypeScript on Vercel AI
  SDK) for "just the agent loop, fast."

**Selection guide:** every framework is a point in the four-primitive design space — **Agent, Handoff,
Shared state, Orchestrator**. Learn the four knobs once and read any new framework in a paragraph. Refuse a
framework until the architecture draws as a graph / org-chart / chat / single agent. (DSPy is tagged
optimize-territory — a mention, not a deep dive.)

## Design patterns & anti-patterns (asdg Ch15)

The systems-thinking vocabulary for interviews and architecture decisions: the pattern catalog plus the
anti-patterns (the "agent everything" trap, premature multi-agent, framework-as-architecture). This is the
language Module 4 multi-agent orchestration builds on.
