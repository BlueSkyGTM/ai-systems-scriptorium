# Module 3 — agent foundations

The single-agent spine: `Agent = Reasoning Model + Tool Use + Persistent Memory + Environment Feedback`. You
build one agent that works, runs reliably, and ships — a mixed-language artifact, `module3-agent/`, that grows
a lesson at a time. The **complexity ladder** governs from the first page: don't reach for an agent until the
problem demands one.

The fifteen lessons follow the agent from a bare loop to a workbench-ready system:

**The loop (01–03)** — the reasoning core. The agent loop and ReAct; planning (ReWOO, plan-then-execute);
learning from failure (Reflexion, self-critique). This is the Python harness you keep extending.

**TypeScript break-in (04–05)** — the second language enters at point-of-use, the moment you write a tool the
model calls by name and need a contract the compiler can check. Typed tool definitions, then the typed product
layer (generics, discriminated unions) that the rest of the module builds on.

**Tools & MCP (06–09)** — tool use, then the canonical MCP spine: fundamentals (server, client, transports),
capabilities (resources, prompts, sampling), and security & scale (OAuth, gateways, the boundary you defend).
MCP is the bridge — the Python loop calls a TypeScript MCP server over the protocol, one artifact, two
languages, one contract between them.

**Memory (10–11)** — memory tiers and stores (working/episodic/semantic, MemGPT virtual context, hybrid
Mem0), then memory that improves (Letta typed blocks, checkpointing, the write that survives the session).

**Frameworks & patterns (12–13)** — the framework landscape reduced to four primitives and a selection rule;
then the design patterns that ship and the anti-patterns that page you at 3 a.m.

**The workbench (14–15)** — the seven surfaces that decide whether an agent is shippable: instructions, state,
scope, feedback (I); verification, review, handoff (II) — closing on the agent-workbench pack that seeds the
Module 6 coding-agent artifact.

**Multi-agent is Module 4.** Single-agent foundations come first — the same single↔multi seam the AI-Agents
roadmap draws. **→ Culminates in Module 6 (Agent Artifacts).**
