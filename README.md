# AI Systems Scriptorium

A private, AI-engineering-specialized **library of books** plus the **AI system that builds them**.
Not a course platform and not a single course — a workshop where finished books and the engine that
produces them live together, and where an arriving agent can navigate and do the work on its own.

## What it is

Four things, in one repo:

1. **The books** (`library/`) — technical books on AI systems engineering, each self-contained
   (`src/` + `exercises/` + `theme/` + `book.toml`, built with mdBook). The first, *Sans Python —
   Production AI Engineering*, is **done**: 8 modules, every lesson in one voice, with runnable
   portfolio artifacts.
2. **The engine** (`platform/`) — the AI-eng-specialized build system: the AUTHOR→VERIFY→BUILD/TEST→SHIP
   pipeline, the Zinsser-grade `STYLE.md` writing contract, the templates, and the human-gate registry.
   It grounds in Microsoft Learn + curated AI-eng ore — on purpose. It is **not** a generic "any-domain"
   book builder; that framing is retired.
3. **The ore** (`vault/`) — nine raw source repos the books are distilled from, plus `ingredients/`,
   the distilled, in-git inputs the pipeline actually authors against.
4. **The lab** (`extra-credit/`) — a sandbox where the agent generates repo scaffolds on demand, for
   experiments and keeper tools, each one born connected to the logged material. Where the work stays
   active between curriculum phases.

## Why artifacts

The outward value is the **artifacts**, not rough-draft courses. The M6/M7/M8 portfolio pieces — a
governed multi-agent fleet, reference architectures, a fleet-reuse exam — are the proof an employer
wants; the books are how they get built.

## How the AI works here (the ICM)

The folder system is a **routing system**, not just storage. Every routed boundary carries a
`CONTEXT.md` that tells an arriving agent what's here, what to load and what NOT to load, where to
hand off next, and which decisions are human-gated. A cold agent opens [`CONTEXT.md`](CONTEXT.md) —
the **task router** — maps its intent (author · fix · process ore · publish · status) to a start
directory and a load-list, and does the routine work independently, stopping only at the points the
gates mark. This is the Interpreted Context Methodology (ICM), and it's enforced mechanically by
`platform/bin/route-lint`.

## Start here

- **Routing:** [`CONTEXT.md`](CONTEXT.md) — the task router.
- **AI contract:** [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md) — start at CONTEXT, follow
  the routing, stop at the gates; the precedence rule.
- **What's built / next:** [`CATALOG.md`](CATALOG.md) (books + status) · [`BACKLOG.md`](BACKLOG.md).
- **The engine:** [`platform/CONTEXT.md`](platform/CONTEXT.md).
- **The progress system (spec):** [`progression/CONTEXT.md`](progression/CONTEXT.md).

## Build the shipped book

```
mdbook build library/completed/sans-python   # static site -> library/completed/sans-python/book
python platform/bin/route-lint               # verify the routing layer is sound
```
