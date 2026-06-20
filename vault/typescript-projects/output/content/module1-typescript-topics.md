# Module 1 · TypeScript — Topics

> Source: `typescript-projects/projects/` (15 topics, from *Learning TypeScript*). TypeScript is the product-layer language: APIs, agent orchestration, tooling. Seam highlights: `from-javascript-to-typescript` (LLM tooling is JS-first), `generics` (type-safe tool defs / MCP contracts), `declaration-files` (untyped npm packages).

## Topics

## Arrays
This topic covers how to declare and interact with arrays in TypeScript, including specifying element types and working with fixed-size tuple types. It explores how TypeScript infers types from array members, how to use spread and rest syntax, and how to use `as const` assertions to lock down array structures.
**TypeScript concepts:** array type syntax (`[]`), parenthesized function/union array types, rest and spread elements (`...`), tuple types, type annotations, `as const` assertions.
**Sans-Python use case:** Tuples and `as const` arrays are essential for defining strict, predictable schemas for agent tools, ordered prompt templates, or MCP contract inputs where fixed-size, type-safe data structures prevent runtime errors in LLM orchestration.

## Classes
This topic covers TypeScript's class system features and syntax, including property modifiers like `readonly` and optional fields, interface implementation, class extension with override rules, and abstract classes. It provides the foundation for building structured, type-safe object hierarchies in TypeScript.

**TypeScript concepts:** class methods and properties, `readonly` properties, optional properties, classes as types, interface implementation, class extension, subclass assignability, override rules, abstract classes and methods, field type modifiers.

**Sans-Python use case:** Classes provide the scaffolding for type-safe agent and tool abstractions — defining structured tool wrappers, agent orchestrators, and MCP server implementations where instance shape is enforced at compile time, catching contract violations before runtime.

## Configuration Options
This topic covers the configuration options provided by TypeScript's compiler and TSConfig files, including output targets, strict mode flags, module systems, and multi-project orchestration. It explains how to control file inclusion, type-checking strictness, and build workflows using `tsc` and project references.

**TypeScript concepts:** `tsc` CLI (pretty mode, watch mode, `--init`), TSConfig files, `include`/`exclude`, JSX support in `.tsx`, JSON module imports, output directory/target/declaration/source map settings, `lib` configuration, strict mode flags (`noImplicitAny`, `strictNullChecks`), module systems and module resolution, `allowJs`/`checkJs`, `extends`, project references, build mode.

**Sans-Python use case:** Proper TSConfig setup is essential for production-grade LLM tooling, ensuring strict type safety across agent schemas and tool wrappers while supporting multi-package monorepos with project references for organizing MCP servers, API integrations, and shared type definitions.

## Declaration Files
This topic covers how to use declaration files (`.d.ts`) and the `declare` keyword to inform TypeScript about modules and values that aren't declared in your source code. It includes configuring built-in type definitions, declaring module types (including wildcard modules), and acquiring types from DefinitelyTyped for untyped packages.

**TypeScript concepts:** `.d.ts` declaration files, `declare` keyword, global values, global interface merges, global augmentations, target/library/DOM declarations, wildcard module declarations, package type resolution, DefinitelyTyped (`@types` packages).

**Sans-Python use case:** When integrating JS-first LLM tooling or untyped npm packages into agent systems, declaration files let you add type safety to dependencies that lack built-in types — ensuring MCP server contracts, tool wrappers, and external API clients remain type-checked without rewriting the original packages.

## From JavaScript to TypeScript
This topic introduces the context for JavaScript's main weaknesses and how TypeScript addresses them, covering JavaScript's history, pitfalls (loose documentation, weaker tooling), and TypeScript's identity as a programming language, type checker, compiler, and language service. It also clarifies what TypeScript is not and provides setup guidance for writing TypeScript on the Playground and locally.
**TypeScript concepts:** TypeScript as a language and compiler, type checking, language services, type-safe documentation, developer tooling, TypeScript Playground, local TypeScript setup.
**Sans-Python use case:** Understanding TypeScript's foundations is essential for building LLM-backed products that rely on JS-first tooling and ecosystems, ensuring type-safe agent schemas, and producing maintainable API and MCP contracts in the product layer.

## Functions
This topic covers how to define and annotate function parameters and return types in TypeScript, including inference and explicit declarations. It also explores function signatures, `void` and `never` return types, optional/default/rest parameters, and function overloads for describing varying call signatures.
**TypeScript concepts:** parameter type annotations, optional parameters, default values, rest parameters, return type annotations, `void` type, `never` type, function type declarations, function overloads.
**Sans-Python use case:** Precise function signatures are essential for building type-safe agent tool wrappers, schema-validated LLM API call boundaries, and reusable orchestration functions where parameters and return values must be strictly typed to catch errors at compile time.

## Generics
This topic covers making classes, functions, interfaces, and type aliases generic by introducing type parameters that allow constructs to work across different types while remaining type-safe. It explores explicit and implicit type arguments, constraints (`extends`), defaults, discriminated unions with generics, and how Promises and `async` functions rely on generics for asynchronous data flow.
**TypeScript concepts:** type parameters, explicit and implicit type arguments, generic interfaces, generic classes, generic type aliases, discriminated type unions with generics, default type parameters (`=`), type parameter constraints (`extends`), Promises and `async` generics, generic naming conventions.
**Sans-Python use case:** Generics are essential for building reusable, type-safe tool wrappers and agent schema utilities — such as a generic `Tool<TInput, TOutput>` interface — that work across arbitrary input/output types without losing compile-time safety. They also underpin `Promise<T>` in async LLM API calls and generic MCP server request/response contracts.

## Interfaces
TypeScript interfaces provide a way to describe the shape of object types, offering an alternative to type aliases with support for optional, read-only, function, and method properties. The chapter covers index signatures for catchall properties, interface composition via nesting and `extends` inheritance, and declaration merging when multiple interfaces share the same name.

**TypeScript concepts:** interface declarations, optional properties, read-only properties, function properties, method properties, index signatures, nested interfaces, interface inheritance via `extends`, declaration merging.

**Sans-Python use case:** Interfaces are essential for defining type-safe agent schemas, MCP server contracts, and tool input/output shapes, ensuring that structured data passed between LLMs, tools, and orchestration layers is statically verified at compile time.

## Objects
This topic covers how TypeScript's type system models object shapes, including object literal types, nested and optional properties, and union/intersection types. It also explores type narrowing techniques such as discriminated unions, enabling robust modeling of complex data structures.

**TypeScript concepts:** object type literals, nested properties, optional properties, union types, type narrowing, discriminated unions, discriminants, intersection types.

**Sans-Python use case:** Object types are essential for defining type-safe agent schemas, tool argument contracts, and structured LLM response shapes in TypeScript-based agent systems, while discriminated unions enable safe routing and handling of heterogeneous tool-call results or multi-modal agent messages.

## Syntax Extensions
This topic covers TypeScript's syntax extensions that go beyond standard JavaScript, including class parameter properties, decorators, enums, namespaces, and type-only imports/exports. These features provide ergonomic ways to declare and organize code structures.
**TypeScript concepts:** class constructor parameter properties, decorators for classes and fields, enums, namespaces, type-only imports and exports.
**Sans-Python use case:** Decorators and parameter properties enable clean, declarative definitions of agent classes and tool wrappers, while enums and namespaces help organize domain-specific concepts like tool names, agent roles, or MCP contract schemas in large LLM-backed TypeScript codebases.

## The Type System
This topic covers the fundamentals of TypeScript's type system, including what types and type systems are, how type errors differ from syntax errors, and how types are inferred or explicitly annotated on variables. It also addresses object shape checking and declaration scoping differences between module and script files.
**TypeScript concepts:** primitive types, type system mechanics, type errors vs. syntax errors, inferred variable types, variable assignability, type annotations, evolving `any` types, object member checking, module vs. script declaration scoping.
**Sans-Python use case:** Understanding the type system is the bedrock for defining type-safe agent schemas, validating LLM I/O contracts, and building reliable tool wrappers — ensuring that data flowing through orchestration pipelines and MCP server boundaries is statically checked before runtime.

## Type Modifiers
This topic covers type modifiers that transform existing objects and types into new ones, including top types (`any` and `unknown`), type operators (`keyof` and `typeof`), type assertions, and `as const` narrowing. It explains how to flexibly reshape types while understanding the tradeoffs of each modifier approach.

**TypeScript concepts:** `any`, `unknown`, `keyof`, `typeof`, type assertions, `as const` assertions, type narrowing.

**Sans-Python use case:** Essential for building type-safe agent schemas and MCP contracts where you derive new types from existing tool definitions or API response shapes — for example, using `keyof` to extract valid tool parameter names, `typeof` to capture runtime config objects as types, and `as const` to lock down literal union types for agent state enums.

## Type Operations
This topic covers advanced TypeScript type system features that allow developers to programmatically transform and derive new types from existing ones. It explores mapped types, conditional types, the `never` type, and template literal types for pattern-based string type representation.
**TypeScript concepts:** mapped types, conditional types, `never` type (intersections, unions, conditional types, mapped types), template literal types, combining template literal types with mapped types for key modification.
**Sans-Python use case:** These type-level operations are essential for building type-safe agent schemas and MCP server contracts, enabling automatic derivation of input/output types from tool definitions and ensuring compile-time correctness when orchestrating LLM-backed workflows.

## Unions and Literals
This topic covers union types, literal types, and TypeScript's type narrowing capabilities — how the type system deduces more specific types based on code structure. It also addresses strict null checking, explicit and implicit `undefined`, and using type aliases to simplify complex union types.

**TypeScript concepts:** union types, literal types, type narrowing, `const` vs `let` type inference, strict null checking, explicit `| undefined`, implicit `| undefined`, type aliases.

**Sans-Python use case:** Union and literal types are essential for defining discriminated agent tool schemas and restricted LLM output formats (e.g., `"text" | "json" | "tool_call"`), while type narrowing enables safe runtime handling of heterogeneous agent responses and optional MCP contract fields.

## Using IDE Features
This topic covers TypeScript's IDE integrations and language service features that accelerate development workflows. It explores navigation commands, code automation, refactoring tools, and strategies for understanding type information and resolving errors directly within the editor.
**TypeScript concepts:** context menus on types and values, finding definitions, finding references, finding implementations, name completions, automatic imports, rename refactors, code actions, language service errors, type inspection.
**Sans-Python use case:** Fluency with IDE navigation and refactoring is essential for working efficiently in complex TypeScript agent codebases, where tracing types across tool wrappers, schema definitions, and API contracts requires rapid lookups and safe renames rather than grep-and-hope edits.
