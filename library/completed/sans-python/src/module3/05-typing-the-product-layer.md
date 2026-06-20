# Typing the product layer

A single typed tool is a contract. A fleet of typed tools — reusable across agents, composable into MCP servers, derivable from a single source of truth — is an architecture. The four patterns in this lesson turn the `ToolDefinition` from lesson 04 into a typed product layer the next chapter extends.

## Generics: reusable tool wrappers

The `ToolDefinition` interface from lesson 04 uses `Record<string, unknown>` for both input and output — safe, but unspecific. Every caller casts. Generics fix that by letting you parameterize the types the compiler infers at each use site.

```typescript
interface Tool<TInput, TOutput> {
  name: string;
  description: string;
  execute: (args: TInput) => Promise<TOutput>;
}
```

Now define a concrete tool with its actual shapes:

```typescript
interface SearchInput  { query: string }
interface SearchOutput { results: string[] }

const searchTool: Tool<SearchInput, SearchOutput> = {
  name: "search",
  description: "Search for information on a topic.",
  execute: async ({ query }) => ({ results: [`stub result for: ${query}`] }),
};
```

The compiler knows `searchTool.execute` returns `Promise<SearchOutput>`. Every call site gets type-safe access to `results` without a cast. Add a new tool with different shapes — `Tool<SummarizeInput, SummarizeOutput>` — and the same wrapper contract applies.

Type parameter constraints keep generics honest. A registry that needs every tool to have a `name` property can enforce it:

```typescript
function registerTool<T extends { name: string }>(tool: T): void {
  registry.set(tool.name, tool as unknown as ToolDefinition);
}
```

In `@azure/ai-agents`, `ToolDefinitionUnion` is exactly this pattern — a discriminated union of `FunctionToolDefinition | CodeInterpreterToolDefinition | FileSearchToolDefinition | …` keyed on `type` (see learn.microsoft.com/javascript/api/@azure/ai-agents/tooldefinitionunion).

## Interfaces: MCP server contracts and agent schemas

Interfaces describe the shape of objects that cross process boundaries — MCP request/response pairs, agent schemas, server manifests. Two interface features matter here beyond what lesson 04 covered.

**Index signatures** describe objects whose keys are unknown at compile time but whose values share a type — exactly the shape of an MCP server's tool map or an agent's parameter schema:

```typescript
interface ToolMap {
  [toolName: string]: ToolDefinition;
}

interface JsonSchemaObject {
  type: "object";
  properties: { [key: string]: JsonSchemaProperty };
  required?: string[];
}
```

**Declaration merging** lets you augment an interface across files. If a package declares `interface AgentContext` and you need to add a field for your MCP session ID without forking the package:

```typescript
// your-extensions.d.ts
interface AgentContext {
  mcpSessionId?: string;
}
```

Both declarations merge — all consumers see the extended shape. This is how `@types/node` extends globals, and how you extend agent SDK types to carry infrastructure state without modifying the upstream package.

Interfaces are open (declaration merging works), type aliases are closed. For shapes that cross package boundaries — MCP contracts, agent schemas, SDK extension points — prefer interfaces.

The `@azure/ai-agents` SDK extends this pattern: its `Agent` interface carries `tools: ToolDefinitionUnion[]`, and `CreateAgentOptionalParams` / `UpdateAgentOptionalParams` both accept `tools?: ToolDefinitionUnion[]` — the index-signature map you define locally maps directly to what the SDK expects.

## Declaration files: typing JS-first LLM packages

Many LLM packages ship as CommonJS JavaScript with no type definitions — or with types that lag behind the JS surface. Declaration files (`.d.ts`) let you add a type layer without touching the original package.

The pattern has two cases.

**Case 1: a package you install but don't own.** Install types from DefinitelyTyped if they exist (`npm install --save-dev @types/package-name`). If they don't, write a minimal `.d.ts` in your project:

```typescript
// types/untyped-llm-package.d.ts
declare module "untyped-llm-package" {
  export interface CompletionOptions {
    model: string;
    prompt: string;
    maxTokens?: number;
  }
  export function complete(opts: CompletionOptions): Promise<string>;
}
```

**Case 2: your own compiled output.** With `"declaration": true` in `tsconfig.json`, `tsc` emits a `.d.ts` alongside every compiled `.js`. Any package that imports your tool registry gets the types automatically — no manual declaration file needed.

Both cases enforce the same guarantee: the compiler checks every call site even when the implementation is plain JavaScript. A typed schema is a validation boundary — the model's generated args hit the type wall before they reach your business logic.

Visual Studio and VS Code both auto-acquire `.d.ts` files from DefinitelyTyped for npm packages — the same repository pattern the manual `declare module` block mimics when no `@types/` package exists.

## Type modifiers: one source of truth

Three modifiers let you derive new types from existing values or types rather than maintaining parallel definitions that drift apart.

**`as const`** locks an object or array literal to its exact values, narrowing every property from `string` to its literal type. Use it to define tool names and agent state keys as a single source of truth:

```typescript
const TOOL_NAMES = {
  search:    "search",
  summarize: "summarize",
  classify:  "classify",
} as const;

type ToolName = typeof TOOL_NAMES[keyof typeof TOOL_NAMES];
// → "search" | "summarize" | "classify"
```

Change a tool name once in `TOOL_NAMES` and the `ToolName` type updates everywhere — no string literals scattered across the codebase, no silent mismatch between registry key and schema name.

**`keyof`** extracts the set of keys from a type as a union. The `ToolName` derivation above uses it. It also validates tool registry lookups at compile time:

```typescript
function getToolSchema(name: ToolName): JsonSchemaObject {
  return schemas[name]; // compiler knows name is a valid key
}
```

**`typeof`** lifts a runtime value into the type system. Capture a config object at compile time without duplicating its type:

```typescript
const agentConfig = { model: "claude-opus-4-8", maxTurns: 10, strict: true };
type AgentConfig = typeof agentConfig;
// → { model: string; maxTurns: number; strict: boolean }
```

These three work together. `as const` locks the values; `typeof` captures the locked shape; `keyof` extracts the keys. Together they let the tool registry, the parameter validator, and the MCP schema all derive from one definition instead of three.

Advanced type operations — mapped types, conditional types, template-literal types — extend this into full compile-time schema derivation. They attach in Module 4, where multi-agent contract types need them. One forward pointer: if you find yourself writing `{ [K in keyof T]: ... }`, you are in mapped-type territory and that is Module 4 material.

The `(typeof X)[keyof typeof X]` idiom is live in production Azure SDKs — `@azure/msal-common` uses `(typeof GrantType)[keyof typeof GrantType]` and `(typeof AADAuthorityConstants)[keyof typeof AADAuthorityConstants]` for exactly this purpose.

## The typed product layer in module3-agent/

After this lesson, `module3-agent/tools/` has:

```
module3-agent/tools/
├── types.ts          ← Tool<TInput, TOutput>, ToolDefinition, ToolMap
├── registry.ts       ← Map<ToolName, ToolDefinition> + execute()
├── search.ts         ← Tool<SearchInput, SearchOutput>
└── tool-names.ts     ← TOOL_NAMES as const + ToolName union
```

This typed layer is what the Tools & MCP chapter (lesson 06 onward) wires to real transports. The interfaces define the MCP server contract; the declaration files type whatever SDK packages arrive untyped; the `as const` / `keyof` / `typeof` pattern keeps the tool name registry and the JSON Schema parameter names in sync.

Without this layer, schema drift is silent — a renamed tool key in the registry and an outdated parameter name in the schema have nothing to catch them until the model calls the wrong function at runtime.

## Core concepts

- Generic `Tool<TInput, TOutput>` separates the stable wrapper shape from the per-tool data shapes, so one registry contract covers every tool without losing per-tool type safety.
- Interfaces with index signatures describe MCP server contracts and agent schemas where key sets are open; declaration merging lets you extend upstream SDK interfaces without forking them.
- Declaration files (`.d.ts`) add a type layer over JS-first LLM packages — a typed schema is a validation boundary the compiler enforces before args reach business logic.
- `as const` + `keyof` + `typeof` derive the `ToolName` union and the `AgentConfig` type from a single runtime definition, so name and type stay in sync as the tool registry grows.

<div class="claude-handoff" data-exercise="exercises/module3/05-typing-the-product-layer/">

**Build It in Claude Code** — extend `module3-agent/tools/` with a generic `Tool<TInput, TOutput>` interface, a `TOOL_NAMES as const` registry, a `ToolName` union derived with `keyof typeof`, and a minimal `.d.ts` for any untyped SDK import in the project. All files must compile clean under `strict: true`.

</div>
