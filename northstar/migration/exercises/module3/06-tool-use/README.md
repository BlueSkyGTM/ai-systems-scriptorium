# Exercise 06 — Tool Use

## Goal

Wire the typed tools from `module3-agent/tools/` into the agent loop's registry with argument validation, coercion, a timeout wrapper, and a least-privilege approval hook.

## Why

The loop from lesson 01 calls `tools.execute(name, args)` with no validation. The model generates arguments from natural language — treat them as untrusted input. This exercise makes the execute step the security boundary it needs to be before lesson 07 moves it across a process boundary.

## Steps

1. Add `module3-agent/tools/registry.ts` — a `Map<ToolName, ToolDefinition>` populated with the typed tools from lesson 05.
2. Implement a `validate(args, schema)` function that checks required fields and types against the tool's `JsonSchemaObject`. Return `{ valid: true }` or `{ valid: false; errors: string[] }` — never throw.
3. Implement narrow coercion: if the schema says `number` and the value is a numeric string, coerce it. For all other mismatches, return a structured error observation.
4. Wrap every tool execution in a deadline: if the tool does not resolve within 5 seconds, return `[error] tool timed out: <name>`.
5. Add an approval hook — a function `requiresApproval(toolName: string): boolean` — that returns `true` for any tool in a `MUTATION_TOOLS` set. Wire it to auto-approve in development (log the approval, don't block). The hook must be wired into `execute()` before the tool runs.
6. Log every tool call to stdout: `[tool] <name> args=<json> duration=<ms>ms result=<ok|error>`.
7. Update the Python harness loop to call the TypeScript registry via `ts-node` or the compiled `dist/`. The loop's `tools.execute(name, args)` call must go through the new registry.

## Done when

- `npx tsc --noEmit` passes clean with `strict: true`.
- Running the agent loop against a toy goal that triggers the `search` tool prints the tool log line with name, duration, and result status.
- Passing a wrong-type argument (e.g., a number where the schema requires a string) returns a structured error observation — not an exception — and the loop continues.
- Passing an unknown tool name returns `[error] unknown tool: <name>`.
- The timeout wrapper fires and returns a timeout observation if you replace the tool's `execute` with a 10-second sleep.

## Stretch

Add a retry policy to the registry: if a tool returns a structured error observation (not a timeout), retry once with the same arguments before returning the error to the loop. Log the retry attempt.
