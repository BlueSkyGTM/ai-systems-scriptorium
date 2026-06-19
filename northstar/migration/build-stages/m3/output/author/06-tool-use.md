# Tool Use

The model cannot execute anything — you can. That separation is the security boundary, and keeping it sharp is the first job of tool use.

## The four-step loop

Every tool call follows the same invariant: **describe → decide → execute → observe**.

**Describe.** The tool registry hands the model a JSON Schema definition for each tool — its name, a description the model uses for selection, and a `parameters` object that defines the argument shape. This is the contract. The model reads it; you enforce it.

**Decide.** The model emits a `tool_use` intent — a name and a blob of arguments it generated from the description. The model does not call the tool. It signals that a call should happen. You receive the signal.

**Execute.** Your code validates the arguments against the schema, coerces types where safe to do so, and runs the tool in a sandbox. Never pass the model's arguments directly to business logic.

**Observe.** The tool result comes back as a structured observation. You append it to the message buffer. The loop runs again.

The describe and decide steps belong to the model. Execute and observe belong to you. That line does not move.

## JSON Schema tool contracts

A tool definition in `module3-agent/tools/` carries three required fields: `name`, `description`, and `parameters` (a JSON Schema object). The typed `ToolDefinition` from lesson 04 is the TypeScript surface:

```typescript
// module3-agent/tools/types.ts
interface ToolDefinition {
  name:        string;
  description: string;
  parameters:  JsonSchemaObject;  // JSON Schema 2020-12 object
  execute:     (args: Record<string, unknown>) => Promise<string>;
}
```

The `parameters` object drives two things: the model's argument generation and your validator's expectations. Keep them identical. Any drift between the schema you advertise and the schema you validate against is a silent contract break the model cannot detect.

Schema design choices compound. A tool with an `action: string` parameter that accepts fifteen possible values forces the model to guess. Split it into fifteen specific tools — or at least enumerate the values with `"enum"`. BFCL V4 traces a measurable chunk of tool-selection failures to under-specified descriptions and under-constrained parameter schemas.

Azure AI Foundry Agent Service enforces the same contract: the `FunctionTool` interface requires `name`, `description`, and a JSON Schema `parameters` object, and the spec explicitly states that the model uses the description to decide whether to call the function — making schema quality a selection correctness problem, not just a validation one. (learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling)

## Argument validation and coercion

The model generates arguments from natural language. Treat them as untrusted input.

Validate before you execute. Check that every required field is present, every type matches, and every enum value is in the allowed set. If validation fails, return a structured error observation — not an exception — so the model can retry with corrected arguments.

Coerce narrowly. If the schema says `number` and the model sends `"42"` (a string), coerce it. If the schema says `"asc" | "desc"` and the model sends `"ascending"`, reject it and tell the model why. Broad coercion hides schema design problems; narrow coercion surfaces them.

```typescript
// module3-agent/tools/registry.ts
function validate(
  args: Record<string, unknown>,
  schema: JsonSchemaObject
): { valid: true } | { valid: false; errors: string[] } {
  const errors: string[] = [];
  for (const key of schema.required ?? []) {
    if (!(key in args)) errors.push(`missing required field: ${key}`);
  }
  // type checks per property ...
  return errors.length ? { valid: false, errors } : { valid: true };
}
```

The validator sits between the model's output and your implementation. It is the type wall.

Azure AI Foundry's function calling guidance is direct on this: "Treat tool arguments and tool outputs as untrusted input. Validate and sanitize values before using them." It lists returning a descriptive error as a tool output — not throwing an exception — as the recommended error path, so the model can respond to the failure rather than seeing a crash. (learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling)

## Execution sandboxing

A tool call can write files, call external APIs, spend money. The execute step runs in a context where you control what the tool can reach.

Three controls belong here from the start:

**Scope the tool's capabilities.** A search tool has no business writing files. Pass it only the clients and credentials it needs. The tool function signature is the boundary — if the implementation needs a file handle, something is wrong with the tool's scope.

**Time-bound execution.** Set a deadline on every tool call. An agent that hangs waiting for a network response blocks the whole loop. Return a timeout observation so the model can decide whether to retry or abandon.

**Least privilege for side-effecting tools.** Before any tool that mutates state — writes, deletes, POSTs — consider whether a human should approve it. The complexity ladder applies here: a tool that reads data needs no approval; a tool that sends an email does. Build the approval hook now, even if you wire it to auto-approve in development.

Azure AI Foundry's security guidance names this explicitly as a core principle: "Apply least privilege to the identity used by DefaultAzureCredential. Avoid side effects unless you explicitly intend them." For tools that change data, it recommends requiring explicit user confirmation before execution — the approval hook belongs in the design, not added later. (learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling)

## Wiring the typed tools into the loop registry

The loop from lesson 01 calls `tools.execute(name, args)`. The typed tools from lessons 04–05 now fill that registry:

```typescript
// module3-agent/tools/registry.ts
import { searchTool } from "./search.js";
import type { ToolDefinition, ToolName } from "./types.js";

const registry = new Map<ToolName, ToolDefinition>([
  [searchTool.name as ToolName, searchTool],
]);

export async function execute(
  name: string,
  args: Record<string, unknown>
): Promise<string> {
  const tool = registry.get(name as ToolName);
  if (!tool) return `[error] unknown tool: ${name}`;

  const check = validate(args, tool.parameters);
  if (!check.valid) return `[error] invalid args: ${check.errors.join("; ")}`;

  try {
    return await tool.execute(args);
  } catch (err) {
    return `[error] tool execution failed: ${String(err)}`;
  }
}
```

This is still in-process — the TypeScript tool runs in the same Node.js process as the Python loop's TS bridge. The next lesson moves it across a process boundary via MCP.

## What the BFCL numbers mean for you

The Berkeley Function-Calling Leaderboard V4 (2026 edition) tells a clean story: single-turn tool calling is near-solved. The frontier models call a single tool correctly the vast majority of the time. The failures cluster in four places: memory across turns, dynamic decisions that depend on prior results, long-horizon multi-step chains, and hallucination detection (the model confidently calls a tool that doesn't exist, or passes args that look right but aren't).

Your tool registry, your schema design, and your validator address the last failure mode. The other three are loop-level problems the next chapters address. Know which problem you're solving before you reach for a fix.

The execute step is the only place in the system where the model's intentions become real-world actions. It is also, therefore, the only place the harm can actually happen — so treat it accordingly.

## Core concepts

- The model emits a `tool_use` intent; your code executes it — that division is the security boundary and never moves.
- Every tool definition carries a JSON Schema contract that drives both the model's argument generation and your validator's expectations; drift between them is a silent failure.
- Validate arguments against the schema before executing; coerce narrowly, reject broadly, and return structured error observations so the model can retry.
- BFCL V4 shows single-turn tool calling is near-solved; the remaining failures concentrate in memory, dynamic decisions, long-horizon chains, and hallucination — your schema and validator address the last one only.

<div class="claude-handoff" data-exercise="exercises/module3/06-tool-use/">

**Build it in Claude Code** — wire the typed tools from `module3-agent/tools/` into the loop registry from lesson 01: add a JSON Schema validator, an argument coercion step, a timeout wrapper, and a least-privilege approval hook (auto-approve in dev). The registry must reject unknown tools, return structured error observations on bad args, and log every tool call with name + duration. Open the repo and run the exercise for this lesson.

</div>
