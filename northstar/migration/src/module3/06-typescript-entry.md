# TypeScript (Entry)

> **Threaded in from** `module1/ts-module1-typescript-topics.md`. TypeScript is installed in Module 1 but
> *taught here* — at the first point product-layer code gets written: typed tools and MCP contracts.
> ([[language-track-threading]])

TypeScript is the **product / Build layer** language (agents, tools, APIs). It arrives additively, at
point-of-use — no concentrated block.

## Break-in set (taught at entry, minimal)

The type system · From JavaScript to TypeScript · Unions & literals · Objects · Functions · basic Interfaces
· Configuration (tsconfig) · using IDE features. → *"read and write typed TS, define a typed tool, run
`tsc`."*

## Point-of-use threads

| TS topic | Pulled by |
|----------|-----------|
| Generics | reusable typed tool wrappers `Tool<TInput, TOutput>` |
| Interfaces (index sigs, declaration merging) | MCP server contracts / agent schemas |
| Type modifiers (`keyof`/`typeof`/`as const`) | derive tool-param names, agent-state enums |
| Declaration files (`.d.ts`) | typing untyped / JS-first LLM packages |
| Classes | agent / tool class scaffolding |

(Advanced type operations — mapped/conditional/template-literal — attach in Module 4 for multi-agent
contract types. Enums/namespaces and deep type-system corners → antilibrary.)

**Authoring note:** under the Sans Python thesis, the agent/tool lessons here are *authored in TypeScript* —
this is where the product-layer writing shifts from Python-literacy to TS.
