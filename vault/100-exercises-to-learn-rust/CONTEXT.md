# 100-exercises-to-learn-rust — Extraction Context

<!-- Claude Code: read this file, then work through Extraction Targets in order. -->

## Role in Curriculum

Rust curriculum for Module 1. Runs concurrent with Build modules — not a side track. Rust is the serving layer, CLI tooling, and performance-critical components. The exercises are structured as 8 topic areas with numbered sub-exercises. The book/ directory provides narrative context for each topic.

## Curriculum Mapping

| Module | Section | Source (path) |
|--------|---------|----------------|
| Module 1 | Language Foundation: Rust | `exercises/`, `book/`, `helpers/` |

## Extraction Targets

Work through these in order.

### Target 1: Exercise inventory
- **Source:** `exercises/` directory
- **What:** List all 8 topic folders. For each topic: list sub-exercise folders with their names. Count total exercises.
- **Output:** `output/inventory.md`
- **Format:** Table: topic number | topic name | sub-exercises (list) | seam relevance note
- **If missing:** Log and stop — required first step

### Target 2: Book structure
- **Source:** `book/`
- **What:** List all chapters/sections in the book. For each: title and 1–2 sentence description of what Rust concept it introduces.
- **Output:** `output/content/module1-rust-book-structure.md`
- **Format:** Ordered list of chapters. Each: chapter name, concept covered, exercise numbers it corresponds to.
- **If missing:** Log in inventory.md and continue

### Target 3: Topic-by-topic exercise summary
- **Source:** `exercises/01_intro/` through `exercises/08_futures/`
- **What:** For each of the 8 topics, extract the intro file (`00_intro/` or first sub-exercise README). Produce a summary of what the topic teaches.
- **Output:** `output/content/module1-rust-exercises-by-topic.md`
- **Format:** 8 sections (one per topic). Each: topic name, Rust concepts covered (list), why it matters for AI Systems Engineering (serving layer, CLI, concurrency, async).
- **If missing:** Log in inventory.md and continue

### Target 4: Seam relevance mapping
- **Source:** All topic summaries from Target 3
- **What:** Map each topic to its Sans Python use case. Threads/concurrency → serving layer. Futures/async → async tool calls, concurrent agent tasks. Traits/structs → CLI tooling and type-safe agent schemas.
- **Output:** `output/curriculum-map.md`
- **Format:** Table: topic | Rust concept | Sans Python use case | module where it surfaces
- **If missing:** Not applicable if Target 3 completed

### Target 5: Helpers
- **Source:** `helpers/`
- **What:** List helper utilities and their purpose. These likely support running the exercises.
- **Output:** Append to `output/inventory.md` as a "Helpers" section.
- **Format:** One entry per helper: filename | purpose
- **If missing:** Log in inventory.md and continue

### Target 6: Visuals
- **Source:** Any `*.png`, `*.svg` + Mermaid diagrams in `*.md` files
- **What:** Collect any diagrams from the book or exercise READMEs.
- **Output:** `output/visuals/` for images; `output/visuals/diagrams.md` for embedded diagrams
- **If missing:** Log "no visuals found" in inventory.md and continue

## Repo Notes

- **Exercise structure:** Each sub-exercise folder typically has a `src/` with a Rust file and a README. Extract README content (the problem statement), not the solution code.
- **Book vs. exercises:** The book provides narrative explanation; the exercises provide hands-on practice. Both are curriculum material.
- **08_futures is critical:** The async/futures topic maps directly to concurrent agent tasks and async tool calls — this is high-value seam material.
- **No antilibrary here:** All 8 topics are curriculum-relevant. The exercises are the curriculum.

## Done Checklist

_All targets complete and verified 2026-06-18. Generation by glm-5.1 (thinking disabled) via repo-local `skills/glm-extractor/` (single | topics). Problem statements sourced from the book (exercises have no READMEs). Zero failed/empty outputs._

- [x] `output/inventory.md` — 8 topics (98 exercises) + Helpers section (common, ticket_fields, json2redirects.sh)
- [x] `output/curriculum-map.md` — 8-topic → Sans-Python use-case map (07_threads→serving, 08_futures→async agent tasks)
- [x] `output/content/module1-rust-book-structure.md` — full mdBook structure (8 topics, sections → exercise mapping)
- [x] `output/content/module1-rust-exercises-by-topic.md` — 8 topic summaries (Rust concepts + seam relevance)
- [x] `output/antilibrary.md` — noted empty (all 8 topics are curriculum; nothing out of seam)
- [x] `output/visuals/diagrams.md` — "no visuals found" (no images, no Mermaid)
