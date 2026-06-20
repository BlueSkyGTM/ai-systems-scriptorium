# CATALOG — the books

The library index and status. For cross-cutting work items see [`BACKLOG.md`](BACKLOG.md); for
routing to a book see [`CONTEXT.md`](CONTEXT.md).

| Book | Status | Location | Notes |
|---|---|---|---|
| **Sans Python — AI Platform Engineering** | ✅ Completed | [`library/completed/sans-python`](library/completed/sans-python/CONTEXT.md) | 8 modules shipped; `mdbook build` passes; M6/M7/M8 portfolio artifacts runnable. The reference book and the proof the engine works. |
| **Everything Else** (antilibrary submissions) | 🚧 In progress | [`library/in-progress/everything-else`](library/in-progress/everything-else/CONTEXT.md) | The antilibrary-submissions / "Avec Python" book. Seed: `library/completed/sans-python/src/antilibrary.md`. |
| **Getting Hired** | 📋 Planned | [`library/planned/getting-hired`](library/planned/getting-hired/CONTEXT.md) | Interview + systems-design material. Ore: `vault/ai-system-design-guide` (interview half) + interview material across the vault. Needs `GATE-NAME-BOOK`. |
| **Simple Systems** | 📋 Planned | [`library/planned/simple-systems`](library/planned/simple-systems/CONTEXT.md) | Approachable systems-design book. Ore: `vault/ai-system-design-guide`. Needs `GATE-NAME-BOOK`. |

## Status legend

- ✅ **Completed** — shipped; all stages passed; lives under `library/completed/`.
- 🚧 **In progress** — actively authoring; lives under `library/in-progress/`.
- 📋 **Planned** — dossier/ore identified, not yet started; lives under `library/planned/`. Starting
  one is gated at `GATE-NAME-BOOK` (see [`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md)).

## How a book moves

`planned/` → (`GATE-NAME-BOOK`) → `in-progress/` → author via the
[pipeline](platform/pipeline/CONTEXT.md) (`GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP` per stage) →
`completed/`. Publishing a public copy is a separate decision gated at `GATE-PUBLISH`.
