# The Agent Loop

A chatbot answers once and forgets. An agent acts, observes the result, and decides what to do next — and that difference in control flow is what makes production automation possible.

## When to reach for an agent

The complexity ladder from the previous lesson is the governor here. You already know when a direct model call wins (output comes from training or an assembled context, failure means a bad answer, not a broken workflow). The single-agent rung earns its place only when the task has a property a direct call cannot handle: the next step genuinely depends on the result of the prior one, the sequence isn't knowable upfront, or the answer requires acting on real-world state.

If you can enumerate the steps before you start, a workflow is cheaper. If you cannot — if the agent must read a file, discover it's malformed, decide to fetch a schema, then retry — an agent is what you need.

Don't reach for the loop until the problem demands it.

## The ReAct pattern

ReAct (Yao et al., 2023) names the loop that every modern agent harness runs: **Observe → Think → Act**. The agent sees the current state, reasons about what to do next, executes a tool call, and brings the result back into the loop as an observation. One cycle. Repeat.

Every harness you'll encounter — Claude Agent SDK, OpenAI Agents SDK, LangGraph, AutoGen v0.4 — runs this loop underneath. The 2026 shift is that models with native reasoning (extended thinking, encrypted reasoning passthrough) generate the `Think` step internally; you don't need to prompt for `Thought:` tokens the way the original ReAct paper did. The shape of the loop is the same.

[MS-Learn: Azure AI Agent Service — agent loop architecture and tool execution lifecycle]

## The five ingredients

A chatbot has a model and a message history. An agent adds five things:

**A message buffer.** The conversation accumulates across turns — observations from tool calls are appended as assistant turns or tool-result turns. State lives in the buffer; without it the agent has no memory of what it already tried.

**A tool registry.** A map of callable names to implementations plus input schemas. The model selects a tool by name and supplies arguments that match the schema. The registry validates, executes, and returns the result.

**A stop condition.** The loop terminates when the model signals completion — typically a final answer turn with no tool call, or a sentinel token your harness recognizes. Without a stop condition the loop runs forever.

**A turn budget.** A hard cap on the number of cycles. The stop condition handles the happy path; the turn budget handles the runaway. When the budget is exhausted, the loop stops and returns whatever was collected — or raises an error. [MS-Learn: Azure AI Foundry — configuring agent turn limits and cost controls]

**An observation formatter.** Tool results come back as raw data — JSON, error strings, file contents. The formatter shapes them into the register the model reads well. A poorly formatted observation degrades the next reasoning step as reliably as a bad prompt.

These five ingredients separate an agent from a chatbot. A chatbot lacks all five. A workflow has some but not a dynamic stop condition. An agent has all five.

## The shape of the loop

The loop in pseudocode — no TypeScript yet, just the shape:

```
agent_loop(goal, tools, max_turns):
  messages = [system_prompt, user_message(goal)]
  turn = 0

  while turn < max_turns:
    response = model(messages)

    if response.is_final_answer:
      return response.content

    tool_call = response.tool_call
    result = tools.execute(tool_call.name, tool_call.args)
    observation = format_observation(tool_call.name, result)

    messages.append(assistant_turn(tool_call))
    messages.append(tool_result_turn(observation))
    turn += 1

  return partial_result_or_error(messages)
```

The loop itself is eight lines of logic. The interesting work is in what you put in `tools`, how you write `format_observation`, and what your stop condition recognizes. Those are the surfaces a platform engineer controls.

## Safety: the kill switch

A running agent can call tools with real side effects — it can write files, call APIs, spend money. Two controls belong in every loop from day one:

A **turn budget** is the first line of defense against runaway loops. Set it low for development (5–10 turns); raise it only for tasks that genuinely need depth.

A **kill switch** is a boolean the agent reads but cannot write — a feature flag, a Redis key, an environment variable. When it is set, the loop stops before executing the next tool call. It lives outside the agent's reachable state so the agent cannot disable its own kill switch. [MS-Learn: Azure AI Foundry — implementing safety controls and agent kill switches]

These aren't advanced features. They're table stakes before you run an agent against anything that matters.

## What you build

You build the skeleton of `module3-agent/` — the artifact that every M3 exercise extends. Lesson by lesson you'll add a planner, a reflexion layer, typed tools, MCP transport, and memory tiers. This lesson scaffolds the loop itself: one stub tool, one stop condition, one turn budget, one green check.

An AI Platform Engineer who understands the five ingredients can reason about any agent harness — and knows exactly which surface to reach for when the loop breaks.

## Core concepts

- An agent earns its place only when the next step genuinely depends on the prior result; use the complexity ladder to decide before you build.
- The ReAct loop — Observe → Think → Act — runs inside every modern agent harness; in 2026 the Think step is native model reasoning, not prompted `Thought:` tokens.
- The five ingredients that separate an agent from a chatbot are a message buffer, a tool registry, a stop condition, a turn budget, and an observation formatter.
- A kill switch (a boolean the agent reads but cannot write) and a turn budget are required safety controls before any agent touches real side effects.

<div class="claude-handoff" data-exercise="exercises/module3/01-the-agent-loop/">

**Build it in Claude Code** — scaffold `module3-agent/` with a working ReAct loop: one stub tool, a stop condition, a turn budget of 5, and a kill switch. The loop should run against a toy task and print each Observe/Think/Act step. Open the repo and run the exercise for this lesson.

</div>
