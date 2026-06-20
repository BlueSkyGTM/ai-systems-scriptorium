# CATALOG — the books

The library index and status. For cross-cutting work items see [`BACKLOG.md`](BACKLOG.md); for
routing to a book see [`CONTEXT.md`](CONTEXT.md).

| Book | Status | Location | Notes |
|---|---|---|---|
| **Sans Python — Production AI Engineering** | ✅ Completed | [`library/completed/sans-python`](library/completed/sans-python/CONTEXT.md) | 8 modules shipped; `mdbook build` passes; M6/M7/M8 portfolio artifacts runnable. The reference book and the proof the engine works. |
| **Just Python** | 📋 Planned | [`library/planned/just-python`](library/planned/just-python/CONTEXT.md) | The applied-Python gap (NumPy/Pandas/vectorization — the 94% screen). Gap-report row 1. Needs `GATE-NAME-BOOK`. |
| **ML in Proportion** | 📋 Planned | [`library/planned/ml-in-proportion`](library/planned/ml-in-proportion/CONTEXT.md) | Classic ML fundamentals + the math they need (gap-report rows 2/3/6), applied depth. Needs `GATE-NAME-BOOK`. |
| **Upstream** | 📋 Planned | [`library/planned/upstream`](library/planned/upstream/CONTEXT.md) | SQL + the data platform beyond the Docling front-door (gap-report row 4, 52% screen). Needs `GATE-NAME-BOOK`. |
| **Show, Don't Tell** | 📋 Planned | [`library/planned/show-dont-tell`](library/planned/show-dont-tell/CONTEXT.md) | Interview + systems-design — the portfolio is the resume. Ore: `vault/ai-system-design-guide` (interview half). Needs `GATE-NAME-BOOK`. |
| **Simple Systems** | 📋 Planned | [`library/planned/simple-systems`](library/planned/simple-systems/CONTEXT.md) | Approachable systems-design book. Ore: `vault/ai-system-design-guide`. Needs `GATE-NAME-BOOK`. |

> **Dual-use + blueprint.** Every book is written to be read by a human learner *and* ingested by an LLM
> — dense, linked, plain markdown; the same page serves either party. **Sans Python is the core roadmap
> and blueprint**; the planned books branch from its
> [antilibrary gap report](build-log/sans-python/antilibrary-gap-report.md) (the retired "Avec Python"
> umbrella, now split into focused books).

## Status legend

- ✅ **Completed** — shipped; all stages passed; lives under `library/completed/`.
- 🚧 **In progress** — actively authoring; lives under `library/in-progress/`.
- 📋 **Planned** — dossier/ore identified, not yet started; lives under `library/planned/`. Starting
  one is gated at `GATE-NAME-BOOK` (see [`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md)).

## How a book moves

`planned/` → (`GATE-NAME-BOOK`) → `in-progress/` → author via the
[pipeline](platform/pipeline/CONTEXT.md) (`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP` per stage) →
`completed/`. Publishing a public copy is a separate decision gated at `GATE-PUBLISH`.
