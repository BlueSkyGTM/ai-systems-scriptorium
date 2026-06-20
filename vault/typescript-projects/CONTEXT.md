# typescript-projects — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

TypeScript curriculum for Module 1. TypeScript is the product layer language: APIs, agent orchestration, tooling. The 15 project topics in `projects/` cover the type system and language features students need before they start building with LLM APIs. Runs concurrent with Build modules.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 1 | Language Foundation: TypeScript | `projects/` (all 15 topics) |

## Extraction Targets

Work through these in order.

### Target 1: Project inventory
- **Source:** `projects/` directory listing + each project's README.md (first 10 lines)
- **What:** List all 15 project topics with their titles. For each, extract the first line or title of its README.
- **Output:** `output/inventory.md`
- **Format:** Table: topic name | brief description | seam relevance for agent/API work
- **If missing:** Log and stop — required first step

### Target 2: Topic summaries
- **Source:** `projects/*/README.md` (all 15)
- **What:** For each of the 15 topics, extract the README summary. Identify what TypeScript concept it covers and why it matters for agent orchestration and API work.
- **Output:** `output/content/module1-typescript-topics.md`
- **Format:** 15 sections. Each: topic name, TypeScript concepts covered (list), Sans Python use case (why this matters for building LLM-backed products and agents).
- **If missing:** Log in inventory.md and continue

### Target 3: Seam relevance mapping
- **Source:** Topic summaries from Target 2
- **What:** Map each topic to its Sans Python application. Type system → safe agent schemas and tool interfaces. Generics → reusable agent tool wrappers. Async → concurrent LLM calls. Interfaces → MCP server contracts.
- **Output:** `output/curriculum-map.md`
- **Format:** Table: topic | TypeScript concept | Sans Python application | module where it surfaces
- **If missing:** Not applicable if Target 2 completed

### Target 4: Test structure
- **Source:** `test/` directory, `jest.config.js`
- **What:** Note the test setup and how exercises are validated. This reveals the learning structure (do students write tests? run tests to verify?).
- **Output:** Append to `output/inventory.md` as a "Test structure" section.
- **Format:** Description of how tests work + example test pattern (1–2 tests, not all of them)
- **If missing:** Log in inventory.md and continue

### Target 5: Visuals
- **Source:** Any `*.png`, `*.svg` + Mermaid diagrams in `*.md` files
- **What:** Collect any diagrams from READMEs.
- **Output:** `output/visuals/` for images; `output/visuals/diagrams.md` for embedded diagrams
- **If missing:** Log "no visuals found" in inventory.md and continue

## Repo Notes

- **15 project topics:** arrays, classes, configuration-options, declaration-files, from-javascript-to-typescript, functions, generics, interfaces, objects, syntax-extensions, the-type-system, type-modifiers, type-operations, unions-and-literals, using-ide-features.
- **from-javascript-to-typescript:** High-value seam material — most LLM ecosystem tooling is JavaScript-first. Understanding the JS→TS migration path matters for working with real codebases.
- **generics:** Critical for reusable, type-safe agent tool definitions and MCP server contracts.
- **declaration-files:** Relevant for working with npm packages that lack TypeScript types (common in LLM ecosystem).
- **No antilibrary here:** All 15 topics are curriculum-relevant for TypeScript foundation.

## Done Checklist

_All targets complete and verified 2026-06-18. Generation by glm-5.1 (thinking disabled) via repo-local `skills/glm-extractor/` (single | topics). Zero failed/empty outputs._

- [x] `output/inventory.md` — 15 topics (description + seam relevance) + Test structure section (jest/@swc, `_category_.json` validation)
- [x] `output/curriculum-map.md` — 15-topic → Sans-Python application map (generics→tool wrappers/MCP, interfaces→MCP contracts, async→concurrent LLM calls)
- [x] `output/content/module1-typescript-topics.md` — 15 topic summaries (TS concepts + Sans-Python use case)
- [x] `output/antilibrary.md` — noted empty (all 15 topics are Module 1 curriculum)
- [x] `output/visuals/diagrams.md` — "no visuals found" (no Mermaid; only a book-cover PNG, not a curriculum diagram)
