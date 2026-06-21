# CONTEXT — library/ (THE BOOKS)

What's here: every book the Scriptorium produces, bucketed by lifecycle. Each book is
self-contained (`src/` + `exercises/` + `theme/` + `book.toml`) so a single one could be copied out.

## Buckets

- `library/completed/` — shipped books. Currently: `sans-python`.
- `library/in-progress/` — actively authoring. Currently: `only-python`.
- `library/planned/` — dossier/ore identified, not started. Currently: `show-dont-tell`,
  `simple-systems`, `ml-in-proportion`, `upstream`, `tasteful-tuning`, `interview-algorithm`,
  `local-metal`.

## Route in

Go to the specific book's `CONTEXT.md` — that is where the per-book intent sub-router lives:

- Author / fix / publish / status of the shipped book → `library/completed/sans-python/CONTEXT.md`.
- Start a planned book → its `CONTEXT.md` (stops at `GATE-NAME-BOOK`).

## Load / don't-load

- **Load:** only the one book you're working in, plus what its `CONTEXT.md` directs.
- **Do NOT load:** other books, the `vault` raw ore (author against `ingredients`, not raw),
  pipeline internals unless you're authoring.

## Handoff & gates

Authoring/verifying/shipping is driven by `platform/pipeline/CONTEXT.md`. Gates by ID:
`GATE-NAME-BOOK`, `GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`, `GATE-PUBLISH` — defined in
`platform/HUMAN-GATES.md`.

The book index + status lives in `CATALOG.md`.
