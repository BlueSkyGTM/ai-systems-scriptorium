# TypeScript Break-In

The agent loop you built in lesson 01 calls `tools.execute(name, args)` — a Python dict with no contract the model or the compiler can check. TypeScript enters here because typed tool definitions are the first thing the product layer needs that Python's runtime duck-typing cannot safely provide.

## Why TypeScript Now

The Sans Python thesis is point-of-use, not upfront tax. You have been reading TypeScript in examples since Module 1 — the ecosystem is JS-first, LLM SDKs ship as npm packages, and MCP is a TypeScript-native protocol. The moment you write a tool the model calls by name, you need a contract: a shape the compiler enforces before the model ever sees it. That moment is now.

LLM tooling is JavaScript-first for a reason. The browser, the edge, the node server, and the MCP transport all speak JS. TypeScript is JavaScript with a type layer on top — you compile it away, ship the JS, and keep the guarantees. Nothing you know about JS becomes false.

## From JavaScript to TypeScript

JavaScript lets you write this:

```javascript
function search(args) {
  return fetch(args.query); // args could be anything
}
```

TypeScript makes you be honest:

```typescript
function search(args: { query: string }): Promise<string> {
  return fetch(args.query).then(r => r.text());
}
```

The compiler checks every call site. Pass a number where a string belongs and `tsc` stops the build. The model — which generates `args` from natural language — is a source of type violations; the compiler is the first line of defense.

Azure SDK quickstarts use this same `tsconfig.json` shape — `"strict": true`, `"module": "NodeNext"`, `"target": "ES2022"` — across every TypeScript SDK sample on Microsoft Learn.

## The Type System in Three Minutes

TypeScript's type system is structural: a value fits a type if its shape matches, regardless of how it was declared. Three building blocks cover most of the product layer:

**Primitive types.** `string`, `number`, `boolean`. TypeScript infers them from assignment; annotate when the inference isn't what you want.

```typescript
const model: string = "claude-opus-4-8";
const maxTurns: number = 10;
```

**Unions and literals.** A union (`A | B`) says a value can be one of several types. A literal type narrows it to an exact value. Together they define the discriminated shapes that tool results and agent states need.

```typescript
type ToolStatus = "success" | "error" | "timeout";

type ToolResult =
  | { status: "success"; output: string }
  | { status: "error";   message: string };
```

The compiler knows which branch you're in after a narrowing check — `if (result.status === "success")` — so `result.output` is safe inside that branch and an error outside it.

**Object types.** Describe a value's required shape inline or with a named interface. Use an interface when the shape recurs or gets extended.

```typescript
interface ToolCall {
  name: string;
  args: Record<string, unknown>;
}
```

## Functions with Typed Signatures

A function signature is a promise to every caller. Annotate parameters and return types; the compiler holds you to the promise.

```typescript
function formatObservation(toolName: string, result: string): string {
  return `[${toolName} result]\n${result}`;
}
```

Optional parameters carry `?`; rest parameters carry `...`. Return `void` when there is nothing to return; `never` when the function always throws. `async` functions return `Promise<T>` — the `T` is what `await` unwraps.

```typescript
async function callModel(messages: Message[]): Promise<string> {
  // ...
}
```

## Defining a Typed Tool

The loop from lesson 01 executes tools by name from a registry. Here is the typed version of that contract:

```typescript
interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, unknown>; // JSON Schema object
  execute: (args: Record<string, unknown>) => Promise<string>;
}
```

And a concrete tool that satisfies it:

```typescript
const searchTool: ToolDefinition = {
  name: "search",
  description: "Search for information on a topic.",
  parameters: {
    type: "object",
    properties: {
      query: { type: "string", description: "The search query." },
    },
    required: ["query"],
  },
  execute: async (args) => {
    const query = args["query"] as string;
    return `[stub] results for: ${query}`;
  },
};
```

This is the TypeScript surface the loop calls. Production agent SDKs use this same shape — name, description, parameters as JSON Schema, a typed handler — which means the contract you define here wires directly into agent infrastructure without reshaping. (In `@azure/ai-agents`, `FunctionToolDefinition` nests these under a `function: FunctionDefinition` property; the concept is identical, the path is one level deeper.)

## Configuration: Tsconfig

`tsc` reads `tsconfig.json` to know what to check and where to emit. The minimal config for this project:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "outDir": "dist",
    "declaration": true
  },
  "include": ["src/**/*"]
}
```

`"strict": true` is non-negotiable for production agent code — it enables `noImplicitAny`, `strictNullChecks`, and a half-dozen more checks that catch the category of bugs that surface as silent wrong-tool calls at runtime. `"declaration": true` emits `.d.ts` files alongside your compiled JS — important when other packages import your typed tools.

The `"strict": true` flag and `"NodeNext"` module resolution appear in every Azure AI SDK TypeScript quickstart on Microsoft Learn (learn.microsoft.com/azure/ai-foundry/) — they are the baseline, not a preference.

## IDE Features

TypeScript's language service runs inside VS Code continuously. The three moves you use constantly:

- **Go to definition** (`F12` / `Cmd+click`) — jump to where a type, interface, or function is declared. Essential for tracing where `ToolDefinition` comes from in an imported package.
- **Hover for type** — hover any symbol to see its inferred or annotated type. The fastest way to verify a tool's parameter shape before calling it.
- **Quick fix** (`Ctrl+.` / `Cmd+.`) — the language service shows you the error and offers a fix. Missing property in an interface? The quick fix adds it.

These aren't conveniences — they are how you navigate a typed codebase without reading every file.

## Running Tsc

```bash
npx tsc --noEmit   # type-check only, no output files
npx tsc            # type-check and emit to dist/
```

`--noEmit` is the fast check during development. Add it to your pre-commit hook. A clean `tsc` means every tool contract, every function signature, every interface is consistent — the compiler ran the review.

## What You Build

You add `module3-agent/tools/` — the TypeScript layer of the mixed-language artifact. One file: `search.ts`, exporting a `ToolDefinition` whose shape matches the loop's `tools.execute(name, args)` contract from lesson 01. The next chapter connects the two over MCP — TypeScript tools, Python harness, one protocol between them. You write `tsconfig.json`, run `tsc --noEmit` clean, and confirm the contract lines up.

The compiler is now the first reviewer — every tool call the model generates has to pass `tsc` before it reaches your business logic.

## Core Concepts

- TypeScript is JavaScript with a structural type layer that compiles away — the ecosystem is JS, the safety is TS, and LLM tooling is JS-first by necessity.
- A typed tool definition — name, description, JSON Schema parameters, typed execute handler — is the compiler-enforced contract between the model's tool calls and your implementation.
- `"strict": true` in `tsconfig.json` is required for production agent code; it enables the checks that catch silent wrong-tool calls before runtime.
- Union types with discriminants (`status: "success" | "error"`) let the compiler narrow tool result shapes — the same discriminated-union pattern that `@azure/ai-agents`' `ToolDefinitionUnion` uses to distinguish `FunctionToolDefinition`, `CodeInterpreterToolDefinition`, and other built-in tool types.

<div class="claude-handoff" data-exercise="exercises/module3/04-typescript-break-in/">

**Build It in Claude Code** — Add `module3-agent/tools/` with a typed `ToolDefinition` interface, a `search.ts` tool implementation, and a `tsconfig.json` that compiles clean. The typed tool must satisfy the `tools.execute(name, args)` contract from lesson 01.

</div>
