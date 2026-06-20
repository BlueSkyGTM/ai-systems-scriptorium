# typescript-projects — Curriculum Map
> Module 1 · TypeScript. Maps each topic to its Sans-Python (AI systems) application.

| Topic | TypeScript concept | Sans-Python application | Module where it surfaces |
|---|---|---|---|
| Arrays | Array types, tuples, rest/spread, `as const` assertions | Tuples and `as const` arrays for strict schemas in agent tools, ordered prompt templates, and MCP contract inputs | Module 1 |
| Classes | Class properties, `readonly`, interface implementation, abstract classes | Scaffolding for type-safe agent/tool abstractions, structured tool wrappers, agent orchestrators, MCP server implementations | Module 1 |
| Configuration Options | `tsc`, TSConfig, strict mode flags, project references | Strict type safety across agent schemas; multi-package monorepos for MCP servers, API integrations, shared type defs | Module 1 |
| Declaration Files | `.d.ts` files, `declare` keyword, global augmentations, `@types` packages | Adding type safety to untyped npm/LLM packages; ensuring MCP server contracts and external API clients remain type-checked | Module 1 |
| From JavaScript to TypeScript | TypeScript as language/compiler/type checker, language services | Building LLM-backed products on JS-first tooling and ecosystems; type-safe agent schemas, API and MCP contracts | Module 1 |
| Functions | Parameter/return type annotations, `void`, `never`, function overloads, rest parameters | Type-safe agent tool wrappers, schema-validated LLM API call boundaries, reusable orchestration functions | Module 1 |
| Generics | Type parameters, constraints (`extends`), generic interfaces/classes, Promise generics | Reusable type-safe tool wrappers (`Tool<TInput, TOutput>`), generic MCP request/response contracts, `Promise<T>` in async LLM calls | Module 1 |
| Interfaces | Interface declarations, optional/read-only properties, index signatures, declaration merging | Defining type-safe agent schemas, MCP server contracts, tool input/output shapes | Module 1 |
| Objects | Object type literals, union/intersection types, discriminated unions, type narrowing | Type-safe agent schemas, tool argument contracts, structured LLM response shapes; discriminated unions for heterogeneous tool-call results | Module 1 |
| Syntax Extensions | Parameter properties, decorators, enums, namespaces, type-only imports/exports | Declarative agent class/tool definitions; enums/namespaces for tool names, agent roles, MCP contract schemas | Module 1 |
| The Type System | Primitive types, type inference, assignability, object member checking, module scoping | Bedrock for type-safe agent schemas, validating LLM I/O contracts, reliable tool wrappers | Module 1 |
| Type Modifiers | `any`, `unknown`, `keyof`, `typeof`, type assertions, `as const` | Deriving types from tool definitions/API responses; `keyof` for tool param names, `typeof` for config objects, `as const` for agent state enums | Module 1 |
| Type Operations | Mapped types, conditional types, `never`, template literal types | Automatic derivation of input/output types from tool definitions; compile-time correctness in LLM workflow orchestration | Module 1 |
| Unions and Literals | Union types, literal types, type narrowing, strict null checking, type aliases | Discriminated agent tool schemas, restricted LLM output formats (`"text" | "json" | "tool_call"`), safe runtime handling of agent responses | Module 1 |
| Using IDE Features | Find definitions/references/implementations, rename refactors, type inspection, code actions | Efficient navigation in complex agent codebases; tracing types across tool wrappers, schema definitions, API contracts | Module 1 |

## Notes

No antilibrary; all 15 topics are Module 1 curriculum.
