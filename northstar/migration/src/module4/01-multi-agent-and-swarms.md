# Multi-Agent & Swarms

> **Migrated from** `aefs-module3-agent-engineering` (Ph16, 25 lessons) + `asdg-module3-agentic-systems`
> (Ch07.04). The multi-agent coordination spine.

## Why multi-agent (the ceiling)

The single-agent ceiling: context overflow, mixed expertise in one prompt, sequential bottleneck. The smart
move past it is **not a bigger agent but more agents** — and only when a task needs more context than one
window, different expertise at different stages, or parallelizable work. Multi-agent is a deliberate choice
with real costs (latency, debugging difficulty), not a default. `[GAP 2: complexity ladder]`

## Communication protocols

The four-protocol stack as layers (with the FIPA-ACL heritage that shows which "innovations" are reinventions):
- **MCP** — agent ↔ tool discovery/execution
- **A2A** — agent ↔ agent collaboration (Agent Cards, task lifecycle)
- **ACP** — enterprise audit/runs/trajectory metadata
- **ANP** — decentralized identity (DID), trust

Build real wire-format implementations; agents discover tools via MCP and delegate via A2A. Passing raw
strings between agents fails on misinterpretation, deadlock, and cross-team scale.

## The four primitives & orchestration

Every framework is a point in a four-dimensional space: **Agent, Handoff, Shared state, Orchestrator.** Learn
the four knobs once, read any framework in a paragraph. Orchestration patterns: **supervisor-worker, swarm/
peer-to-peer, hierarchical, debate.** 2026 guidance: do supervision through direct tool calls rather than
supervisor libraries for finer context control.

## Debate & failure modes

- **Multi-agent debate ("Society of Minds")** — N instances propose, then critique over R rounds to converge;
  sparse topology (star/ring) matches full-mesh accuracy at far lower token cost.
- **Failure modes (MASFT)** — 14 documented multi-agent failure modes; the five recurring ones (hallucinated
  actions, scope creep, cascading errors, context loss, tool misuse) are **design flaws, not base-model
  limitations** — better models don't fix them.
