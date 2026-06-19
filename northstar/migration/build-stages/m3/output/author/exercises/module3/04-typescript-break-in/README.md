# Exercise: TypeScript Break-In

## Goal

Add `module3-agent/tools/` — a TypeScript typed-tool layer — with a `ToolDefinition` interface, a concrete `search.ts` tool, and a `tsconfig.json` that compiles clean under `strict: true`.

## Why

An AI Platform Engineer owns the contract between the model's untyped tool calls and the typed implementation the compiler can check — and this seam is where silent runtime failures become build-time errors.

## Steps

1. Create `module3-agent/tools/` and `module3-agent/tsconfig.json`.
2. In `tsconfig.json`, set `target: "ES2022"`, `module: "NodeNext"`, `moduleResolution: "NodeNext"`, `strict: true`, `outDir: "dist"`, `declaration: true`. Include `src/**/*` (or adjust to your layout).
3. Create `module3-agent/tools/types.ts` and export the `ToolDefinition` interface:
   ```typescript
   export interface ToolDefinition {
     name: string;
     description: string;
     parameters: Record<string, unknown>; // JSON Schema object
     execute: (args: Record<string, unknown>) => Promise<string>;
   }
   ```
4. Create `module3-agent/tools/search.ts`. Export a `searchTool: ToolDefinition` with:
   - `name: "search"`
   - `description`: one sentence describing what it does.
   - `parameters`: a JSON Schema object with a single required `query: string` property.
   - `execute`: an async function that reads `args["query"]` as a string and returns a stub result string.
5. Create `module3-agent/tools/registry.ts`. Export a `toolRegistry: Map<string, ToolDefinition>` populated with `searchTool`. Expose an `execute(name: string, args: Record<string, unknown>): Promise<string>` function that looks up the tool by name and calls it — matching the `tools.execute(name, args)` call in the lesson 01 `agent_loop`.
6. Run `npx tsc --noEmit` from `module3-agent/`. Fix any type errors until it exits clean.
7. Write a quick smoke test (a `main()` or a plain script) that calls `execute("search", { query: "Paris" })` and prints the result. Run it with `node --experimental-vm-modules` or compile and run `dist/`.

## Done when

- `module3-agent/tools/types.ts`, `search.ts`, and `registry.ts` exist and export the described shapes.
- `npx tsc --noEmit` exits with no errors under `strict: true`.
- `execute("search", { query: "Paris" })` prints a non-empty string result.
- `execute("unknown", {})` throws or returns a clear error — not a silent `undefined`.
- No `any` annotations remain in the tool files (strict mode catches them; fix them with proper types or `unknown` + a narrowing cast).

## Stretch

Replace the stub `execute` in `search.ts` with a real call to `claude-haiku-4-5` using the Anthropic SDK (`@anthropic-ai/sdk`). Pass the query as a user message, return the text content of the first response block. Add a `.d.ts` declaration (or rely on `declaration: true`) and confirm the emitted type file matches the `ToolDefinition` interface. Measure: input tokens and latency for a single search call.
