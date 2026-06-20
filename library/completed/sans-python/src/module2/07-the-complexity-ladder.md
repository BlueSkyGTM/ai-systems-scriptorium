# The Complexity Ladder

The fastest way to fail at AI system design is to add an agent before the problem requires one. The second fastest is to stay with a direct model call after the problem has outgrown it. The complexity ladder is the decision framework that keeps you on the right rung.

## The Three Rungs

**Direct model call.** A prompt goes in, a response comes out. No tools, no state, no loop. This is the default. It is fast, cheap, deterministic in structure, and easy to debug. If the problem fits a direct call, the direct call wins. Most problems fit a direct call.

Use it when: the answer comes from the model's training or a context window you've already assembled, the output is consumed once, and failure means a bad answer; not a broken workflow.

**Single agent with tools.** The model can act; read a file, query a database, call an API, write a result. The loop is: model decides → tool executes → result feeds back → model decides again. State lives in the conversation turn; the loop terminates when the model signals completion or hits a turn budget.

Use it when: the task requires actions the model can't perform alone, the sequence of actions isn't fully predictable upfront, or the output depends on real-world state at query time. The structured output and tool primitives from the previous lesson are what make this rung stable.

**Multi-agent orchestration.** Multiple agents, each with their own tools and context, coordinated by an orchestrator that decomposes the task, routes sub-tasks, and assembles results. Parallelism, specialization, and checkpointed state become possible. So does a new failure surface: inter-agent communication breaks, context doesn't transfer cleanly, and debugging requires tracing across agent boundaries.

Use it when: the task genuinely parallelizes (independent sub-problems), requires specialized sub-agents with different tool sets or personas, or exceeds the context budget of a single agent. Not when a single agent with more tools would do.

## The Governing Rule

Don't add an agent between the task and the model call unless the problem requires it.

An agent adds a reasoning loop, a state machine, a turn budget, and a new class of failure. Every one of those is overhead. The overhead earns its place only when the problem has a property the simpler rung can't handle: dynamic action sequences, parallelism, specialization, or multi-step state.

The temptation is to build agents because agents are interesting. The discipline is to build the minimum system that solves the problem; then add complexity exactly when the simpler system breaks.

## Frameworks

LangGraph models the agent as an explicit `StateGraph`; nodes are actions, edges are transitions, state is typed. The graph is compiled before it runs, which buys you checkpointing, human-in-the-loop interrupts, streaming, and time-travel debugging for free. Use it when your agent's control flow can be drawn as a graph: when branches, loops, and conditional routing are part of the design.

CrewAI fits role-playing multi-agent patterns; agents with personas collaborating on a shared task. AutoGen fits multi-agent dialogue, where agents negotiate through conversation. Agno fits high-throughput parallel fanout.

The decision principle: refuse a framework until the architecture can be drawn as a graph, an org chart, a chat, or a single agent with tools. The shape of the problem determines the tool. An agent framework chosen before the shape is known is a liability.

## The M2 → M3 Hinge

This ladder is the editorial spine of Modules 3 and 4. Module 3 builds the single-agent rung in depth; the agent loop, tool execution, MCP, memory, and evaluation. Module 4 extends to multi-agent orchestration. The sequence is deliberate: you need to own the single-agent rung before multi-agent complexity is legible.

An AI Platform Engineer adds complexity only when the problem demands it; that discipline, applied at scale, is what separates a system that holds under production load from one that collapses under its own architecture.

## Core Concepts

- The three rungs, direct model call, single agent with tools, multi-agent orchestration, each add cost, failure surface, and debugging complexity; move up only when the simpler rung can't solve the problem.
- The governing rule is: don't add an agent between the task and the model call unless the problem requires it.
- A framework should be chosen after the architecture can be drawn, not before; the shape of the problem (graph, org chart, chat, single agent) determines the tool.
- Multi-agent orchestration earns its cost only when the task genuinely parallelizes, requires specialization, or exceeds the context budget of a single agent.

<div class="claude-handoff" data-exercise="exercises/module2/07-the-complexity-ladder/">

**Try It in Claude Code**: Take one task and implement it three ways: direct model call, single agent with tools, and a two-agent orchestration. Measure latency and token cost for each. Identify the simplest rung that actually solves the problem. Open the repo and pick up from this lesson.

</div>
