# typescript-projects — Inventory
> Module 1 · TypeScript language foundation. 15 topics from *Learning TypeScript*. TypeScript = product-layer language (APIs, agent orchestration, tooling). No antilibrary; all topics curriculum.

## Topics

| Topic | Brief description | Seam relevance (agent/API work) |
|---|---|---|
| arrays | Arrays :: _Learning TypeScript_'s **Arrays** chapter covers declaring arrays and retrieving their members: | Collection types for API responses, agent memory stores, tool result arrays |
| classes | Classes :: _Learning TypeScript_'s **Classes** chapter introduces a plethora of type system features and syntaxes around classes: | Agent/service object hierarchies, tool registration patterns, stateful orchestrators |
| configuration-options | Configuration Options :: _Learning TypeScript_'s **Configuration Options** chapter goes over many of the important configuration options provided by TypeScript: | tsconfig for monorepos, MCP server builds, strict product-layer compilation |
| declaration-files | Declaration Files :: _Learning TypeScript_'s **Declaration Files** chapter describes how to use declaration files and value declarations to inform TypeScript about modules and value | `.d.ts` for MCP contracts, ambient type definitions for external agent SDKs |
| from-javascript-to-typescript | From JavaScript to TypeScript :: _Learning TypeScript_'s **From JavaScript to TypeScript** chapter covers the context for some of JavaScript's main weaknesses, where TypeScript comes into play, | Motivation for type-safe agent orchestration; JS runtime pitfalls TypeScript prevents |
| functions | Functions :: _Learning TypeScript_'s **Functions** chapter shows how a function's parameters and return types can be inferred or explicitly declared in TypeScript: | Tool handlers, API route signatures, typed callbacks in agent pipelines |
| generics | Generics :: _Learning TypeScript_'s **Generics** chapter covers making classes, functions, interfaces, and type aliases "generic" by allowing them to work with type paramet | Reusable API clients, typed tool wrappers, schema-driven response parsing |
| interfaces | Interfaces :: _Learning TypeScript_'s **Interfaces** chapter covers how object types may be described by interfaces: | API contract shapes, MCP tool input/output schemas, agent capability interfaces |
| objects | Objects :: _Learning TypeScript_'s **Objects** chapter expands your grasp of the TypeScript type system to be able to work with objects: | Configuration objects, API request/response payloads, agent state modeling |
| syntax-extensions | Syntax Extensions :: _Learning TypeScript_'s **Syntax Extensions** chapter works with some of the JavaScript syntax extensions included in TypeScript: | Decorators for tool registration, async patterns, enum-backed configs |
| the-type-system | The Type System :: _Learning TypeScript_'s **The Type System** chapter covers how TypeScript's type system works at its core: | Foundation for all type-safe agent orchestration and API contract work |
| type-modifiers | Type Modifiers :: _Learning TypeScript_'s **Type Modifiers** chapter covers using type modifiers to take existing objects and/or types and turn them into new types: | `readonly` API responses, optional tool parameters, `Partial`/`Required` for mutations |
| type-operations | Type Operations :: _Learning TypeScript_'s **Type Operations** chapter unlocks the true power of TypeScript by operating on types in its type system: | Schema-to-type mapping, conditional MCP contracts, inference on tool outputs |
| unions-and-literals | Unions and Literals :: _Learning TypeScript_'s **Unions and Literals** chapter covers union and literal types in TypeScript, along with how its type system can deduce more specific (n | Discriminated agent states, string-literal tool names, tagged result variants |
| using-ide-features | Using IDE Features :: _Learning TypeScript_'s **Using IDE Features** chapter covers using TypeScript's IDE integrations to level up your ability to write TypeScript code: | Refactoring tooling for agent codebases, hover types for API exploration, error-driven dev |

## Test structure

Tests run via Jest with `@swc/jest` for TypeScript transformation. The suite (`test/files.test.ts`) iterates over the `projects/` directory and validates each chapter folder's `_category_.json` label/position fields, `README.md` heading, and package metadata — this is structure validation of the curriculum repository itself, not student-written exercise tests.

```typescript
test("_category_.json", () => {
    const categoryData = readFileAsJSON(
        `${chapterDirectory}/_category_.json`,
    );

    expect(categoryData).toEqual({
        label: expect.stringMatching(new RegExp(chapterTitle, "i")),
        position: expect.any(Number),
    });
});

test("README.json", () => {
    const readmeContents = fs
        .readFileSync(`${chapterDirectory}/README.md`)
        .toString();

    expect(readmeContents).toMatch(new RegExp(`^# ${chapterTitle}`, "i"));
});
```
