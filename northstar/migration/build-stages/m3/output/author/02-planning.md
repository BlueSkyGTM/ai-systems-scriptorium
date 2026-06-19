# Planning

The ReAct loop is deliberate and slow by design — one tool call per turn, each observation feeding the next decision. For tasks where the steps are knowable upfront, this is wasteful: you're paying reasoning tokens to re-plan between every action when you could have planned once and executed in parallel.

## Decouple planning from execution

ReWOO (Xu et al., 2023) separates the loop into three roles: a **Planner** that produces the full plan DAG before any tool is called, a **Worker** that executes tool calls in parallel across the plan's independent nodes, and a **Solver** that synthesizes the collected evidence into a final answer.

The token count tells the story: interleaved ReAct re-conditions the reasoning model on the full observation history at every tool call. ReWOO calls the reasoning model exactly twice — once to plan, once to solve. On HotpotQA this produces roughly 5× fewer tokens and +4% accuracy, because the Solver sees a clean evidence packet instead of a reasoning trace polluted by intermediate retrieval noise.

[MS-Learn: Azure AI Foundry — multi-step agent planning and parallel tool execution]

## The plan DAG

A plan is a directed acyclic graph where each node is a tool call and each edge is a data dependency. Independent nodes execute in parallel; dependent nodes wait.

In pseudocode:

```
plan = planner(goal)
# plan is a list of nodes: {id, tool, args, depends_on}

evidence = {}
for batch in topological_batches(plan):
  results = parallel_execute(batch, evidence)
  evidence.update(results)

answer = solver(goal, evidence)
```

Each node's arguments may reference earlier node outputs by ID — `$node_2.result` — so the Worker can substitute real values at execution time. The Planner never calls tools; it only describes the shape of the work.

**Per-node failure localization** is a side benefit: when one node fails, you know which evidence piece is missing. With interleaved ReAct, a mid-run failure leaves the loop in an ambiguous state.

## Plan-and-Execute

LangChain's Plan-and-Execute generalizes ReWOO with a **Replanner** step: after the Worker finishes, the Planner can inspect the evidence and revise the remaining plan. This handles cases where early tool results change what later steps need to do — it restores adaptability without abandoning the decouple.

The tradeoff is a third model call on replan. For tasks where the plan is stable, ReWOO without a replanner is cheaper. For tasks where early evidence frequently redirects the plan, Plan-and-Execute earns its cost.

[MS-Learn: Azure AI Foundry — Plan-and-Execute agent pattern and replanning]

## Where LLM planners stop

LLM planners are good at decomposing goals described in natural language. They are not sound-by-construction — a plan they produce may be logically inconsistent, reuse a resource before it exists, or silently skip a step.

Two cases where LLM planners fail and classical planning belongs:

**Provably-correct plans.** Hierarchical Task Networks (HTN) decompose a high-level task into a tree of subtasks with explicit preconditions and effects. Every generated plan is sound by construction — the HTN verifies it before handing it to an executor. ChatHTN (2025) interleaves symbolic decomposition with LLM fallback for unstructured steps, giving you correctness guarantees on the skeleton with model flexibility on the leaves. Use HTN when the cost of an invalid plan is high — infrastructure provisioning, financial workflows, safety-critical sequences.

**Machine-checkable optimization.** When a fast, deterministic evaluator exists — unit tests, a compiler, a benchmark harness — evolutionary search (MAP-elites, AlphaEvolve-style loops) finds better solutions than an LLM planner by generating variants and keeping what scores best. The evaluator, not the model, defines "correct." LLM planners optimize for plausible; evolutionary search optimizes for the evaluator's definition of good. Use it where the evaluator is cheap to run and hard to game.

The principle behind both: the LLM is an amplifier, not a replacement. It generates candidates; a stronger external check validates them.

## The complexity ladder, applied to planning

Reach for plan-and-execute when the task has independent sub-problems that can be fetched in parallel — multi-source research, fanout lookups, batch transformations. Stay with ReAct when the next action is genuinely unknowable until the prior result arrives.

The test: draw the plan DAG. If most nodes are independent, planning wins. If each node's input depends on the previous node's output, the DAG is a chain — you have a workflow, not a planning problem, and ReAct or a simple sequential workflow is cheaper.

An AI Platform Engineer chooses between ReAct and planning by drawing the dependency graph, not by reaching for the more impressive algorithm.

## Core concepts

- Decoupling planning from execution — one plan DAG, parallel evidence fetches, one solver call — cuts token cost roughly 5× versus interleaved ReAct for tasks with independent sub-problems.
- Per-node failure localization is a structural benefit of the plan DAG: a failed node identifies the missing evidence piece rather than leaving the loop in an ambiguous state.
- LLM planners are not sound-by-construction; HTN belongs when correctness guarantees are required, and evolutionary search belongs when a fast deterministic evaluator exists.
- Apply the complexity ladder to planning: if the dependency graph is a chain, use a workflow; if it fans out, use a planner.

<div class="claude-handoff" data-exercise="exercises/module3/02-planning/">

**Build it in Claude Code** — extend `module3-agent/` with a planner: add a `Planner` that produces a plan DAG for a multi-source research task, a `Worker` that executes tool nodes in dependency order, and a `Solver` that synthesizes the results. The loop should print the plan before executing it. Open the repo and run the exercise for this lesson.

</div>
