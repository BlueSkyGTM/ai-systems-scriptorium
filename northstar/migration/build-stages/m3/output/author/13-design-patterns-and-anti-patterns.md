# Design Patterns and Anti-Patterns

Architecture reviews and technical interviews for AI platform roles test the same thing: whether you can name a shape and say why it fits or fails. This lesson gives you that vocabulary — and the failure modes that reveal whether someone actually ships agents or just designs them.

## Why vocabulary matters here

A pattern is a named, reusable solution to a recurring problem in a given context. In agent systems, the value of the name is precision: "Plan-and-Execute" communicates a specific decomposition strategy, failure profile, and set of tradeoffs in two words. Without the shared vocabulary, every design discussion starts from scratch and ends in ambiguity.

Module 4 builds multi-agent orchestration on top of this vocabulary. Every topology it introduces — supervisor, swarm, hierarchical nested graphs — is a composition of the patterns named here. Learn the names now; Module 4 assumes them.

## The pattern catalog (the reusable shapes)

These are the shapes that recur. Each solves one class of problem; each has a failure mode that shows up when you misapply it.

**ReAct** — the agent loop itself. Interleave reasoning and acting: the model thinks, picks a tool, observes the result, repeats. General-purpose, explainable, moderate complexity. Fails when the task is predictable enough that the dynamic loop adds pure cost; use a workflow pattern instead.

**Plan-and-Execute** — split planning from execution. One model call produces a plan; a separate execution phase runs the steps, possibly in parallel. Visible plan, easier to debug and interrupt, better for tasks where steps are known upfront. Fails when reality diverges from the plan and there is no replanner; add a replanner for long-horizon tasks.

**Evaluator-Optimizer (Critic/Verifier)** — generate, then critique. One agent produces output; a second verifies it against a criterion and feeds structured feedback back to the first. Quality is critical; tasks have a clear success criterion. Fails when the verifier uses the same model in the same configuration as the generator — the verifier inherits the generator's blind spots. Use external tools (test runners, linters, search) as the verifier when the task has a ground truth.

**Human-in-the-Loop (HITL)** — pause execution and require human approval before continuing. Required for high-stakes, irreversible actions: financial transactions, infrastructure changes, deletions. The right implementation: the loop suspends at a defined checkpoint, surfaces the pending action with full context, and resumes only on explicit approval. The wrong implementation: a yes/no prompt injected mid-run with no context.

**Hierarchical Agents / Supervisor** — one orchestrator decomposes a task and delegates sub-tasks to specialized sub-agents, each with its own tool set. Parallelism and specialization become possible. Fails when the orchestrator's context budget overflows (it must track all sub-agent outputs) or when sub-tasks are not genuinely independent. This is Module 4's primary topology.

**Swarm / Handoff** — agents self-route. No central orchestrator; each agent decides whether to hand off to a specialist or answer directly. Flexible, low-coordination-overhead, fits chatbot-style routing. Fails when the routing decisions are opaque and the control flow becomes untraceable — add W3C trace propagation from day one.

**Cascading Models / Model Routing** — route queries to the cheapest model that can handle them. Simple classification queries go to `claude-haiku-4-5`; complex reasoning goes to `claude-opus-4-8`. The pattern reduces cost at scale without sacrificing quality on hard queries. Requires a classifier and a routing table; calibrate the classifier before the threshold matters.

**Circuit Breaker** — when a dependency fails repeatedly, stop calling it and return a fast failure until it recovers. Prevents one failing service from cascading into the whole system. Required for every external tool call in production.

**Golden Set** — a curated dataset of representative inputs and expected outputs used as a regression test. Run it on every change to catch degradation before it ships. Not a pattern for building — a pattern for sustaining. A system without a Golden Set is operating blind.

Microsoft Agent Framework implements HITL through a request-response mechanism: any executor calls `ctx.request_info()` to pause the workflow and emit a `RequestInfoEvent`; the caller responds, and the workflow resumes. Checkpoints persist pending requests, so a paused workflow survives a process restart. ([Microsoft Agent Framework — Human-in-the-loop](https://learn.microsoft.com/agent-framework/workflows/human-in-the-loop))

## The anti-patterns that matter most

Anti-patterns are not just mistakes — they are recurring mistakes with recognizable shapes. Naming them is how you stop arguing about whether a design is "good" and start diagnosing what specifically it does wrong.

**Agent everything.** The trap: you reach for an agent because agents are interesting. The cost: a reasoning loop, a state machine, a turn budget, and a new failure surface, all added to a problem that a direct model call or a deterministic workflow would have solved. The fix: run the complexity ladder (M2/07) before you build anything. Ask: does the next step genuinely depend on the prior result, in a way I cannot enumerate upfront? If not, the agent is overhead, not value.

**Premature multi-agent.** You split the work across two or three agents before a single agent with more tools would do. Multi-agent earns its cost only when the task genuinely parallelizes, requires specialization with distinct tool sets, or exceeds a single agent's context budget. Moving to multi-agent before any of those conditions hold adds inter-agent communication, context transfer bugs, and debugging complexity that a single well-equipped agent avoids entirely.

**Framework-as-architecture.** You choose the framework before the architecture is drawn. The framework's primitives then constrain the architecture instead of serving it. The result: the system is shaped by LangGraph's state machine or CrewAI's role model because those were the tools on hand, not because the problem called for them. The fix is the decision rule from the previous lesson: draw the shape first (graph, org chart, chat, single agent), then pick the framework that matches.

**The God Prompt.** One massive prompt that handles every case — routing, formatting, domain logic, safety rules, persona. The model struggles with conflicting instructions; context bloat degrades every answer; any change requires re-testing the whole surface. The fix: route queries to specialized handlers, each with a focused system prompt and a minimal tool set.

**Infinite loop risk.** No hard termination conditions on the agent loop. Turn budget absent or set to infinity. Cost controls absent. The model can loop forever on ambiguous stopping criteria, and the bill arrives at the end of the month. The fix from lesson 01: turn budget + kill switch, present from the first run.

**Vibes-based evaluation.** "It looks good" as the acceptance criterion. No Golden Set, no scoring metric, no regression harness. Every prompt change is a gamble. The fix: 100+ labeled examples, a scoring function, a test runner. This is not advanced infrastructure — it is the minimum to know whether the system is improving or regressing.

Microsoft Agent Framework's Magentic orchestration exposes explicit termination knobs — `max_round_count`, `max_stall_count`, `max_reset_count` — precisely because unbounded loops are a known production failure mode. ([AutoGen to Microsoft Agent Framework Migration Guide — Multi-Agent Feature Mapping](https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/#multi-agent-feature-mapping))

## A small artifact inspection

Open the `module3-agent/` harness you built in lessons 01–03. Find one instance of each of the following in the code or its absence:

1. The turn budget and kill switch — the infinite-loop guard.
2. The observation formatter — the shape that prevents the God Prompt anti-pattern inside the loop itself.
3. The stop condition — what decides "done" and whether it is explicit or implicit.

Name what pattern each one implements and which anti-pattern it prevents. If any of the three is missing, that is the first finding — note what it would cost if the agent ran against a real API without it.

Azure AI Foundry Agent Service enforces hard service limits — 128 tools per agent, 100,000 messages per thread — and applies rate limits at the model deployment level, not the agent level. Cost control requires monitoring which tools the agent actually invokes, not just which ones are registered. ([Azure AI Foundry Agent Service — limits, quotas, and observability](https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions))

Pattern vocabulary and anti-pattern recognition are the same skill: both require knowing what a shape is called before you can argue about whether it belongs here.

## Core concepts

- A pattern is a named, reusable solution to a recurring problem; naming it precisely — ReAct, Plan-and-Execute, HITL, Circuit Breaker — prevents design discussions from starting from scratch every time.
- The three anti-patterns that cause the most expensive rewrites are agent everything (adding agent overhead before the problem requires it), premature multi-agent (splitting before a single agent with more tools would do), and framework-as-architecture (choosing the framework before the shape is drawn).
- Vibes-based evaluation — accepting "it looks good" as the only quality signal — is an operational anti-pattern, not just a testing gap; a Golden Set with a scoring function is the minimum that makes a system improvable rather than just changeable.
- Every anti-pattern in this lesson has a fix that costs less than the rewrite it prevents; the fix is always simpler than the problem it avoids.

<div class="claude-handoff" data-exercise="exercises/module3/13-design-patterns-and-anti-patterns/">

**Inspect it in Claude Code** — open the `module3-agent/` harness and produce a pattern audit: identify which patterns from this lesson are present (with file and line), which anti-patterns exist or are one missed line away, and what a production-ready version of the harness would add. No building required — this is a read and annotate exercise. Open the repo and run the exercise for this lesson.

</div>
