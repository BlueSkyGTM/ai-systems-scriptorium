# M3 SHIP manifest — Module 3, Agent Foundations

Shipped 2026-06-19. AUTHOR → VERIFY → **SHIP** complete. 15-lesson hybrid; first real `mdbook build` passed.

## What shipped
- 15 lessons relocated `build-stages/m3/output/author/*.md` → `src/module3/` (canonical).
- 15 exercise briefs relocated → `exercises/module3/<slug>/README.md`.
- `src/module3/README.md` rewritten: 6-chapter overview → 15-lesson arc.
- `src/SUMMARY.md` M3 section rewritten: 6 chapters → 15 lessons.
- 6 old ingredient stubs deleted from `src/module3/`.
- `mdbook build` — **PASS** (exit 0); 15 lesson pages + README rendered; M1/M2 validated in the same build.

## Stub → lesson map (the 6 ingredient chapters → 15 finished lessons)
| Old stub (deleted) | Finished lessons |
|---|---|
| 01-reasoning-and-loops | 01 The Agent Loop · 02 Planning · 03 Learning from Failure |
| 06-typescript-entry | 04 TypeScript Break-In · 05 Typing the Product Layer |
| 02-tools-and-mcp | 06 Tool Use · 07 MCP Fundamentals · 08 MCP Capabilities · 09 MCP Security and Scale |
| 03-memory-and-state | 10 Memory Tiers and Stores · 11 Memory That Improves |
| 04-frameworks-and-patterns | 12 Frameworks and the Four Primitives · 13 Design Patterns and Anti-Patterns |
| 05-the-agent-workbench | 14 The Workbench Surfaces I · 15 The Workbench Surfaces II & the Pack |

Note the reorder: TypeScript moved before Tools & MCP (point-of-use — typed tools are the first thing the
product layer needs). Per-lesson VERIFY verdicts: `build-stages/m3/output/verify/*.md`.

## Carried forward
- Docling-anchored data-ingestion thread lands at M5/M6 (see `build-stages/roadmap-coverage.md`); not retro-fitted to M3.
- Optional later polish: Docling's MCP server as a real example in lesson 07/08 (do not re-open verified M3 for it).
- One exercise README (05-typing-the-product-layer) still carries a banned "An AI Platform Engineer who…" frame — fix on next M3 touch.
