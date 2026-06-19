# Exercise: Planning

## Goal

Extend `module3-agent/` with a Planner/Worker/Solver stack: a Planner that produces a plan DAG before any tool is called, a Worker that executes nodes in dependency order, and a Solver that synthesizes the collected evidence.

## Why

Decoupling planning from execution cuts token cost for tasks with independent sub-problems and localizes failures to specific DAG nodes — two properties an AI Platform Engineer needs before running multi-source research agents in production.

## Steps

1. Add `module3-agent/planner.py` containing three components:
   - `Planner(goal) -> Plan`: returns a list of nodes, each with `{id, tool, args, depends_on: []}`. Use a toy stub planner that always returns a fixed two-node plan: node A fetches source 1, node B fetches source 2, both independent (no `depends_on`), node C synthesizes (depends on A and B).
   - `Worker(plan, tools, evidence) -> evidence`: iterates the plan in topological batches; within each batch, execute tool calls. For this exercise, sequential execution is fine — parallel execution is the stretch goal. On tool failure, record `{id, error}` in evidence rather than raising.
   - `Solver(goal, evidence) -> answer`: a stub that formats the evidence dict into a string answer.
2. Add a `topological_batches(plan)` utility: yields lists of node IDs whose `depends_on` are all already in a completed set.
3. Wire two stub tools into the registry from `loop.py`: `fetch_source_1(query)` and `fetch_source_2(query)`, both returning canned strings.
4. Run the planner stack against the goal `"Summarize the two main causes of the French Revolution"`. Print:
   - The full plan before execution.
   - Each batch as it executes: `[Batch 1] Executing nodes: A, B`.
   - The final answer.
5. Simulate a node failure: make `fetch_source_2` raise an exception. Verify that node C's evidence shows the failure, the Solver still runs, and the answer notes the missing evidence.

## Done when

- `module3-agent/planner.py` exists and runs without errors.
- The plan is printed in full before any tool executes.
- Independent nodes execute in the same batch (printed together).
- A node failure is recorded in evidence without crashing the Worker.
- The Solver produces an answer that references the available evidence.
- No third-party planning framework is imported.

## Stretch

Replace the stub planner with a real LLM call: give the model a goal and a tool registry, ask it to return a JSON plan DAG, validate the DAG structure before handing it to the Worker. Run it against a three-source research task and compare token cost to running the same task with the base `agent_loop` from lesson 01.
