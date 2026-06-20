# Exercise: The Agent Loop

## Goal

Scaffold `module3-agent/` with a working ReAct loop: one stub tool, a stop condition, a configurable turn budget, and a kill switch that halts the loop before any tool call when set.

## Why

An Production AI Engineer controls the five surfaces that separate an agent from a chatbot — message buffer, tool registry, stop condition, turn budget, and observation formatter — before reaching for any framework.

## Steps

1. Create the `module3-agent/` directory. All M3 exercises extend this artifact.
2. Implement `loop.py` (or `loop.ts` if you prefer the shape exercise in TypeScript — language-light is fine here) containing `agent_loop(goal, tools, max_turns, kill_switch_path)`.
   - **Message buffer:** a list that accumulates system prompt, user goal, assistant tool calls, and tool result turns.
   - **Tool registry:** a dict mapping tool name to a callable plus a JSON Schema for input validation. Start with one stub tool: `search(query: str) -> str` that returns a canned string.
   - **Stop condition:** the loop exits when the model returns a turn with no tool call (treat the content as the final answer).
   - **Turn budget:** the `max_turns` argument caps the loop; on exhaustion, return whatever was collected with a `budget_exhausted` flag.
   - **Observation formatter:** a function that takes a tool name and raw result and returns a formatted string the model reads well (e.g., `"[search result]\n{result}"`).
3. Implement the kill switch: before each tool execution, read the file at `kill_switch_path`. If it contains `"stop"`, halt the loop and return `{"halted": true, "reason": "kill_switch"}`. The agent cannot write this file — write it manually to test.
4. Wire a toy model stub (a function that returns a hardcoded tool call on turn 1 and a final answer on turn 2) so the loop runs without a real API key.
5. Run the loop against the goal `"Find the capital of France"`. Print each step: `[Turn N] Observe: ... Think: ... Act: ...`.
6. Verify: the loop exits on the stop condition (not the budget), prints all five surfaces in action, and halts immediately when the kill switch file is written mid-run.

## Done when

- `module3-agent/loop.py` (or equivalent) exists and runs without errors.
- The loop prints Observe/Think/Act for each turn.
- With `max_turns=2` and the stub model, the loop exits on the stop condition at turn 2.
- Setting the kill switch file halts the loop before the next tool call — verified by a test or a manual run with output showing `"halted": true`.
- No third-party agent framework is imported — the loop is from-scratch stdlib.

## Stretch

Replace the toy model stub with a real Anthropic API call using `claude-haiku-4-5` and run the loop against a genuine question that requires one tool call. Measure: wall-clock time, input tokens, output tokens, number of turns.
