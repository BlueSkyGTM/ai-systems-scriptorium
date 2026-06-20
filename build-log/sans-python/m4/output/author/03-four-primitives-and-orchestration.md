# The Four Primitives & Orchestration

In Module 3 you learned to read any agent framework as a point in a four-dimensional space — Agent, Handoff, Shared state, Orchestrator. That frame was for the single-agent-to-framework view: how one library packages the loop. Now those four knobs do harder work. They are the design space for a *system of agents*, and the choices you make on each one decide whether your fleet is a clean supervisor, an emergent swarm, or an unauditable mess.

## The same four knobs, turned up

The four primitives don't change going multi-agent. Their stakes do. A quick recap, then the part that's new.

**Agent** — the unit of reasoning: one model call with a tool registry and a stop condition. In a multi-agent system it's also a unit of *isolation*: a fresh context, a narrow tool set, one job. The thing lesson 01 told you to multiply.

**Handoff** — the transfer of control from one agent to another. Single-agent frameworks model this as a function call or a `transfer_to_<agent>` tool. Across real agents it becomes the typed wire message from lesson 02 — and the place most multi-agent bugs live, because a handoff that drops context or routes wrong fails quietly.

**Shared state** — whether agents read and write a common store or each carry private state. This is the knob that flips hardest at scale. One agent's shared state is a convenience. A fleet's shared state is a blackboard where one agent's hallucinated "fact" becomes every downstream agent's premise. Coordination and contention live on the same knob.

**Orchestrator** — whether an authority decides who runs next, or agents self-route. Single-agent, this is a graph edge or a hook. Multi-agent, it is the difference between a system you can trace and one you can only watch. The orchestrator is where auditability is won or lost.

Read a multi-agent framework the same way you read a single-agent one: name its default on each of the four knobs and you've read it in a paragraph. What's new is that the *topology* — how the agents are wired to each other — is itself a set of choices on these four knobs. Three topologies cover almost everything.

## Three orchestration patterns

**Supervisor-worker.** One lead agent plans and delegates; specialized workers execute in fresh parallel contexts and report back. The Orchestrator is explicit (the supervisor), Handoff is delegation down and results up, Shared state is usually minimal — the supervisor synthesizes, the workers never see each other. This is the workhorse, the pattern behind the research system from lesson 01, and the default you should reach for first. The lead never reads raw materials; it reads worker summaries. The workers never coordinate; they fan out and fan in.

**Swarm / peer-to-peer.** No central decider. Agents read a shared event bus or blackboard, pick up work, and write results back; control routes by who claims the next task. The Orchestrator knob is set to *none* — agents self-route — and Shared state carries the coordination. It buys scalability and loses determinism: you trade a traceable control flow for throughput on many independent sub-problems. Swarm fits work that's genuinely parallel and variable-duration. It fails on ordered workflows and anything needing a global plan, because there's no one holding the plan.

**Hierarchical.** Supervisors over supervisors over workers — an org chart. Natural for tasks that *are* org-chart shaped, with summarization at each layer so context doesn't blow up at the top. It is also the pattern most likely to collapse into managerial looping: an LLM manager re-reasons the whole org every turn from whatever is in its context, mis-assigns, misreads sub-outputs, and stalls. Failure-mode studies of real multi-agent systems put step repetition and role confusion among the most common breakdowns, and a deep hierarchy multiplies the surface for both. Reach for it only when the task is deep enough to need layers — and know that a flat sequence often beats it.

A fourth pattern, debate, gets its own lesson next — it's a coordination strategy more than a control topology.

## Supervise with tool calls, not a supervisor library

Here is the 2026 guidance that runs against the marketing. When you build the supervisor-worker pattern, don't reach for a framework's `create_supervisor()` helper by default. Implement supervision as *direct tool calls*: the supervisor agent has a tool per worker — `call_researcher(task)`, `call_writer(task)` — and delegating is just calling the tool, reading the result, deciding the next move.

The reason is context control. A supervisor helper decides for you what context flows to each worker and what comes back, and that decision is exactly the one that determines cost and quality — fresh-context-per-worker was the whole mechanism from lesson 01. Framework managers make this explicit: Microsoft's Agent Framework, for instance, ships a Magentic manager that coordinates specialized agents and keeps its own shared context, picking who acts next. That is convenient until you need to control the boundary yourself. Wire supervision as tool calls and you own it: you choose precisely what the worker sees, what it returns, and what the supervisor keeps. The library hides the knob that matters most.

This is the same instinct from Module 3's framework lesson — refuse the abstraction until the shape is clear — applied one level up. The control plane is Python; the supervisor's tools are functions that invoke workers, the way you'd invoke any tool.

```python
# Supervisor as direct tool calls — you own the context boundary.
def supervisor(task: str) -> str:
    plan = model(SUPERVISOR_PROMPT, task)          # decide who does what
    results = {}
    for step in plan.steps:
        worker = WORKERS[step.role]                 # researcher | writer
        results[step.role] = worker(step.subtask)   # fresh context per call
    return model(SYNTH_PROMPT, results)             # supervisor synthesizes
```

No supervisor framework, no hidden routing. The supervisor sees the plan and the results; each worker sees only its subtask. Every context boundary is a line you wrote.

## The seam this sits on

The four primitives are where the AI Engineer's design taste meets the MLOps engineer's need for a system that can be traced, costed, and stopped. Pick the topology by what the work needs — supervisor for delegated work, swarm for parallel independent work, hierarchical only when depth demands it — and wire supervision as tool calls so you keep the one knob, context flow, that decides both the answer's quality and the bill. Get the topology wrong and no amount of model quality saves you; the next lesson shows what that failure looks like and why better models don't fix it.

## Core concepts

- The four primitives — Agent, Handoff, Shared state, Orchestrator — are the same knobs Module 3 used to read single-agent frameworks; multi-agent raises their stakes, and a system's topology is itself a set of choices across them.
- Three orchestration patterns cover most systems: supervisor-worker (explicit orchestrator, the default), swarm/peer-to-peer (no orchestrator, scalable but non-deterministic), and hierarchical (org-chart deep, prone to managerial looping).
- In 2026, build supervision through direct tool calls rather than a supervisor library, because that keeps you in control of the context boundary — fresh context per worker — which is the knob that decides both answer quality and cost.

<div class="claude-handoff" data-exercise="exercises/module4/03-four-primitives-and-orchestration/">

**Build it in Claude Code** — turn the `module4-fleet/` harness orchestrator into a real supervisor-worker system: the supervisor delegates to the researcher and writer through direct tool calls, owning every context boundary, with no supervisor library. Map your system's defaults on all four primitives and justify the topology. Open the repo and run the exercise for this lesson.

</div>
