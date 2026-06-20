# Exercise: The Complexity Ladder

## Goal

Implement one task three ways — direct model call, single agent with tools, two-agent orchestration — then measure latency and token cost for each and identify the simplest rung that solves the problem.

## Why

An Production AI Engineer adds complexity only when the problem demands it; measuring the cost of each rung is how you know where the line is.

## Steps

1. Pick a task: "Summarize the five most recently modified files in the current directory and identify which file changed most." This task requires file system access.
2. **Rung 1 — direct model call:** pass the file listing and contents directly in the context window (read the files yourself in Python, inject them as text). Measure: wall-clock time, input tokens, output tokens.
3. **Rung 2 — single agent with tools:** give the model a `list_files` tool and a `read_file` tool from your registry in the previous exercise. Let the model decide which files to read and in what order. Measure: wall-clock time, total input tokens across all turns, total output tokens, number of tool calls.
4. **Rung 3 — two-agent orchestration:** an orchestrator agent decomposes the task into sub-tasks (one sub-task per file) and dispatches each to a worker agent that reads and summarizes its assigned file. The orchestrator collects the summaries and writes the final report. Measure: wall-clock time, total tokens, number of agent-to-agent messages.
5. Print a comparison table: rung, wall-clock time, total tokens, cost estimate (use a fixed price per million tokens of your choice), and a one-line note on what broke or worked.
6. Write one sentence in comments identifying which rung you'd use in production and why.

## Done when

- All three rungs produce a correct summary of the same five files.
- The comparison table prints with actual measurements (not hardcoded).
- The code for each rung is in its own function or file — they don't share mutable state.
- The production recommendation comment is present.

## Stretch

Run Rung 2 with a 10-file corpus and a 3-tool-call turn budget. Observe what happens when the agent hits the budget before finishing. Add a fallback that summarizes whatever was collected when the budget is exhausted.
