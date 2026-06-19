# Exercise: Typing the Product Layer

## Goal

Extend `module3-agent/tools/` into a full typed product layer: a generic `Tool<TInput, TOutput>` wrapper, a `TOOL_NAMES as const` registry with a derived `ToolName` union, and a `.d.ts` declaration file for any untyped package in the project.

## Why

An AI Platform Engineer who controls the schema boundary — where every model-generated arg and every MCP tool call passes through compiler-checked types — ships agent systems that fail at build time, not at 2 AM.

## Steps

1. In `module3-agent/tools/types.ts`, replace the plain `ToolDefinition` with a generic version:
   ```typescript
   export interface Tool<TInput, TOutput> {
     name: string;
     description: string;
     parameters: Record<string, unknown>; // JSON Schema
     execute: (args: TInput) => Promise<TOutput>;
   }
   // Keep ToolDefinition as an alias for backward compat:
   export type ToolDefinition = Tool<Record<string, unknown>, string>;
   ```
2. Create `module3-agent/tools/tool-names.ts`:
   ```typescript
   export const TOOL_NAMES = {
     search:    "search",
     summarize: "summarize",
   } as const;

   export type ToolName = typeof TOOL_NAMES[keyof typeof TOOL_NAMES];
   ```
3. Update `module3-agent/tools/search.ts` to use the typed generic form:
   - Define `SearchInput = { query: string }` and `SearchOutput = { results: string[] }`.
   - Type the export as `Tool<SearchInput, SearchOutput>`.
   - Name field must use `TOOL_NAMES.search` — no duplicated string literals.
4. Add a second tool: `module3-agent/tools/summarize.ts`. Use `Tool<SummarizeInput, SummarizeOutput>` with `input: string` and `summary: string`. Stub the execute.
5. Update `module3-agent/tools/registry.ts`:
   - Key the `Map` on `ToolName`, not plain `string`.
   - The `execute` function signature: `(name: ToolName, args: Record<string, unknown>) => Promise<string>`.
   - Pass an unknown name and confirm the TypeScript error appears at the call site (a `ToolName` check narrows it).
6. If the project imports any untyped package (e.g., a plain JS helper, an older SDK), create `module3-agent/types/<package-name>.d.ts` and add at minimum a `declare module` block that types the one function you actually call. Add `"typeRoots": ["./types", "./node_modules/@types"]` to `tsconfig.json` `compilerOptions`.
7. Run `npx tsc --noEmit`. Fix every error. If you see `any` in a hover, replace it — use `unknown` and a narrowing cast or a proper interface.
8. Write a small `index.ts` that imports from `registry.ts` and calls both tools. Confirm the `ToolName` type rejects a call with `"nonexistent"` at compile time.

## Done when

- `npx tsc --noEmit` exits clean with zero errors, `strict: true` active.
- `ToolName` is a derived union (`"search" | "summarize"`), not a hand-written string union.
- Changing a value in `TOOL_NAMES` propagates to `ToolName` automatically — verify by renaming one key and watching the registry enforce the change.
- A call to `execute("nonexistent", {})` is a TypeScript error at compile time.
- At least one `.d.ts` file exists under `module3-agent/types/` (even if the package is already typed — write one as a deliberate exercise to learn the syntax).
- No unresolved TypeScript errors remain in any file under `module3-agent/tools/`.

## Stretch

Add a `ToolMap` interface (index signature: `[name: string]: ToolDefinition`) and extend it via declaration merging in a second file to add a `defaultTimeout?: number` field. Confirm the merged shape is visible in the hover type. Then add a third tool — `classify.ts` — and derive the updated `ToolName` union automatically from `TOOL_NAMES` without touching `tool-names.ts`'s type definition. Replace one tool's stub `execute` with a real `claude-haiku-4-5` call via `@anthropic-ai/sdk` and return the typed `SearchOutput` or `SummarizeOutput` from the response content.
