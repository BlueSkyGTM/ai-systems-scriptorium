# Frameworks and the four primitives

Every new agent framework arrives with its own vocabulary and its own marketing. The engineers who reach for each one before their architecture is clear spend months learning a tool that doesn't fit the problem — then unwinding it.

## The four knobs

Every agent framework is a point in a four-dimensional design space. Learn the four knobs once and you can read any new framework in a paragraph.

**Agent.** The unit of reasoning — one model call with a tool registry and a stop condition. Everything else in this list describes how agents relate to each other or to the world.

**Handoff.** The transfer of control from one agent to another. In the simplest systems a handoff is just a function call. In complex ones it carries context, session state, and a routing decision.

**Shared state.** Whether agents read and write a common store — a typed object, a message bus, a database row — or each carry private state they never expose. Shared state enables coordination; it also creates contention and coupling.

**Orchestrator.** Whether there is an authority that decides which agent runs next (a supervisor, a manager, a graph edge), or whether agents self-route. An orchestrator makes the control flow explicit and auditable; without one the system is peer-to-peer and harder to trace.

These four dimensions determine how your system behaves, how it fails, and how you debug it. A framework is a set of decisions made for you about all four. The ones that fit your problem feel invisible. The ones that don't add weight every week.

## The major frameworks as points in the space

**LangGraph** models the agent as a state machine. State is typed and immutable — each node receives it and returns a new version. Edges are conditional; the graph decides the next node based on state contents. A checkpoint fires after every step: if a 40-step run fails at step 38, it resumes from step 38, not zero. Control flow is explicit and drawable because it literally is a graph. Use LangGraph when the architecture has branches, loops, and conditional routing you can diagram before you start.

```python
# LangGraph: the shape in a few lines
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    messages: list[str]
    step: int

graph = StateGraph(AgentState)
graph.add_node("plan", plan_node)
graph.add_node("act", act_node)
graph.add_conditional_edges("act", route_or_finish, {"continue": "plan", "done": END})
app = graph.compile(checkpointer=sqlite_checkpointer)
```

The four primitives: Agent (each node), no Handoff (graph edges route, not agents), Shared state (the typed `AgentState`), Orchestrator (the compiled graph is the authority).

**Microsoft Agent Framework** (the direct successor to both AutoGen and Semantic Kernel, built by the same teams) uses a data-flow model where typed messages route along explicit edges between executors — agents, functions, or sub-workflows. Unlike AutoGen's broadcast-based GroupChat, Agent Framework routes data point-to-point with strong types, built-in checkpointing via `FileCheckpointStorage` or `CosmosCheckpointStorage`, and HITL request-response that can pause a workflow and wait for human input. The executor model from AutoGen survives: each executor has local state and handles one message type. The enterprise features — session management, telemetry, Entra identity, middleware — come from Semantic Kernel's lineage. ([Microsoft Agent Framework — Workflows overview](https://learn.microsoft.com/agent-framework/workflows/))

```python
# Microsoft Agent Framework: typed workflow shape
from agent_framework import WorkflowBuilder, Agent

builder = WorkflowBuilder()
builder.add_agent(researcher, id="research")
builder.add_agent(writer, id="write")
builder.add_edge("research", "write")  # typed data flows point-to-point
workflow = builder.build()
```

The four primitives: Agent (executors), Handoff (typed edges), Shared state (cross-executor `ctx.set_state()`), Orchestrator (the Workflow or a Magentic manager).

([AutoGen to Microsoft Agent Framework Migration Guide](https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/))

**CrewAI** is role-based. An Agent has a role, a goal, and a backstory; a Task assigns work to an agent; a Crew ties them into a process. The split that matters in production is Crews vs Flows. A Crew is autonomous — the manager LLM decides sequence — which is exploratory but brittle. A Flow is event-driven and deterministic, where you own the control graph explicitly. The production recommendation: start with a Flow. Add a Crew only when the task genuinely requires the manager LLM to choose who runs next.

The four primitives: Agent (role-based Agent), Handoff (task delegation within a process), Shared state (shared Crew memory), Orchestrator (Crew manager or Flow event graph).

**OpenAI Agents SDK** names its four primitives almost directly: `Agent` (the reasoning unit), `Handoff` (modeled as a `transfer_to_<agent>` tool — the model initiates it naturally through function calling), `Guardrail` (input/output/tool safety checks run in parallel or blocking mode), `Session` (persistent conversation state). Tracing ships by default in W3C span format. The whole system runs on the Responses API.

```python
# OpenAI Agents SDK: handoff as a tool
from agents import Agent, handoff

triage = Agent(name="triage", handoffs=[handoff(billing), handoff(support)])
```

The four primitives: Agent, Handoff (as a first-class SDK concept), no built-in Shared state (Session is conversation state, not inter-agent), Orchestrator (the SDK runtime routes handoffs).

**Claude Agent SDK** is the Claude Code harness packaged as a library. You get built-in tools (bash, text_editor, computer), subagents for parallelism and context isolation, lifecycle hooks (`PreToolUse`, `PostToolUse`, `SessionStart`, `PreCompact`), and a session store with `--session-mirror` for long-running tasks. The model ID to use is `claude-opus-4-8` for orchestrators or `claude-haiku-4-5` for high-throughput subagents. The raw Anthropic Client SDK gives you the ReAct loop with no harness; the Agent SDK gives you the full Claude Code loop as a composable unit.

```typescript
// Claude Agent SDK: subagent dispatch (TypeScript harness, Claude Code native)
import { query } from "@anthropic-ai/claude-agent-sdk";

const result = await query({
  prompt: "Analyze this codebase and summarize the architecture",
  options: { model: "claude-opus-4-8", maxTurns: 10 },
});
```

The four primitives: Agent (the harness instance), Handoff (subagent dispatch), Shared state (session store), Orchestrator (lifecycle hooks + the parent harness).

**Agno** (Python) targets ~2 µs agent instantiation — stateless, session-scoped, built for FastAPI backends where you spin up a fresh agent per request and cannot afford framework startup cost. **Mastra** (TypeScript, built on the Vercel AI SDK) gives you Agents, Tools, and Workflows with Zod type inference end-to-end, a local `mastra dev` playground, and suspend/resume workflow state. Both are "just the loop, fast" — no supervision topology, no role system, no actor runtime. They are the right answer when the architecture is a single agent with tools and the overhead of LangGraph or Agent Framework would be pure cost.

```typescript
// Mastra: typed agent in a few lines (TypeScript-native)
import { Agent } from "@mastra/core";
import { z } from "zod";

const agent = new Agent({
  name: "summarizer",
  model: { provider: "anthropic", name: "claude-haiku-4-5" },
  tools: { summarize },
});
```

DSPy sits outside this space entirely — it optimizes prompts and few-shot examples against a metric, which is a different problem from runtime orchestration. It's worth knowing it exists for the moment your evaluation loop points to prompt quality as the bottleneck; it is not a framework for the agent runtime itself.

## The decision rule

Refuse a framework until the architecture draws cleanly as one of four shapes: a graph (LangGraph, Agent Framework), an org chart (CrewAI with a manager, Agent Framework Magentic), a chat (OpenAI Agents SDK handoffs, CrewAI peer process), or a single agent with tools (Claude Agent SDK, Agno, Mastra).

If you cannot draw the shape, adding a framework will not make it clearer. Build the from-scratch loop first — Module 2's complexity ladder still applies here — then reach for the framework that matches the shape.

Azure AI Foundry Agent Service offers two deployment paths: prompt agents (fully managed, no runtime code) and hosted agents, where you bring your own framework — Agent Framework, LangGraph, OpenAI Agents SDK, or custom code — packaged as a container, and Foundry handles scaling, identity, and endpoints. The distinction matters when you're choosing whether to run the four primitives yourself or hand that surface to a managed platform. ([Azure AI Foundry Agent Service — agent types overview](https://learn.microsoft.com/azure/foundry/agents/overview#agent-types))

The four knobs don't change when you add a hosting layer. What changes is where the orchestrator lives.

## Core concepts

- Every agent framework is a point in the four-primitive design space: Agent, Handoff, Shared state, Orchestrator — learn these four knobs and any new framework becomes readable in a paragraph.
- LangGraph uses typed shared state and a compiled graph as the orchestrator, buying durable checkpointing and conditional routing; Microsoft Agent Framework evolves this into a data-flow model with strong types, HITL pause-resume, and enterprise identity.
- CrewAI's split between Crews (manager-LLM-driven, autonomous) and Flows (event-driven, deterministic) is a decision about how much control to delegate to the model — start with a Flow, add a Crew only when the manager must choose at runtime.
- Refuse a framework until the architecture draws as a graph, org chart, chat, or single agent with tools — adding a framework before the shape is known is a liability, not an accelerant.

<div class="claude-handoff" data-exercise="exercises/module3/12-frameworks-and-the-four-primitives/">

**Build It in Claude Code** — take the from-scratch ReAct loop you built in lessons 01–03 and re-implement it in LangGraph: define the same task as a `StateGraph`, add the same tool, wire the same stop condition as a conditional edge, and enable checkpointing. Compare what the framework buys (checkpointing, streaming, conditional routing) against what it costs (setup, dependency footprint, compilation step). Open the repo and run the exercise for this lesson.

</div>
