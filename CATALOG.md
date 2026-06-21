# CATALOG — the books

The library index and status. For cross-cutting work items see [`BACKLOG.md`](BACKLOG.md); for
routing to a book see [`CONTEXT.md`](CONTEXT.md).

| Book | Status | Location | Notes |
|---|---|---|---|
| **Sans Python — Production AI Engineering** | ✅ Completed | [`library/completed/sans-python`](library/completed/sans-python/CONTEXT.md) | 8 modules shipped; `mdbook build` passes; M6/M7/M8 portfolio artifacts runnable. The reference book and the proof the engine works. |
| **Just Python** | 🚧 In progress | [`library/in-progress/just-python`](library/in-progress/just-python/CONTEXT.md) | Applied Python (NumPy/Pandas/vectorization; 94% screen, gap-report row 1). **Modules 1–4 shipped** (M1 2026-06-20; M2–M4 "NumPy in Depth", "Pandas for AI Pipelines", "Vectorization Discipline" 2026-06-21 — each 5 lessons + 4 exercises, reviewed to STYLE + STANDARDS, `mdbook build` clean). M5 (Python Idioms) next. |
| **Machine Math** *(working title)* | 📋 Planned | [`library/planned/ml-in-proportion`](library/planned/ml-in-proportion/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. Classic ML paired with the math each fundamental needs (gap-report rows 3+6), applied depth. PyTorch/training split to Weights and Measures. Needs `GATE-NAME-BOOK`. |
| **Data Currents** *(working title)* | 📋 Planned | [`library/planned/upstream`](library/planned/upstream/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. Interpreting + routing data for AI systems: SQL + the data platform beyond the Docling front door (gap-report row 4, 52%); extends Sans Python M5 L14. Needs `GATE-NAME-BOOK`. |
| **Weights and Measures** *(working title)* | 📋 Planned | [`library/planned/tasteful-tuning`](library/planned/tasteful-tuning/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. PyTorch + model training with quality as the throughline (gap-report row 2, 78%): the weights you train and the measures that prove them. Needs `GATE-NAME-BOOK`. |
| **Answer Engineering** | 🚧 In progress | [`library/in-progress/answer-engineering`](library/in-progress/answer-engineering/CONTEXT.md) | Graduated 2026-06-21 (`GATE-NAME-BOOK` cleared; was "Anatomy of an Answer"/`interview-algorithm`). The getting-hired book: answer construction as an engineering discipline — a transferable reasoning framework, not memorization. Blueprint + Module 1 draft (2 lessons + 2 exercises) in `draft/`. Ore: `asdg` interview half. M1 plan next → `GATE-LOCK-PLAN`. |
| **Local Metal** | 🚧 In progress | [`library/in-progress/local-metal`](library/in-progress/local-metal/CONTEXT.md) | The home production environment: build a homebrew rig (Cthulhu SPEC) and host local models to offload Claude Code. Progress-agnostic, home-scale companion to Sans Python; grows as the other books are ingested. **Graduated to in-progress 2026-06-21** (`GATE-NAME-BOOK` cleared: title **Local Metal**, slug `local-metal`; rig built and running). M1 (The Build) plan drafted, awaiting `GATE-LOCK-PLAN`. Ore: `aipe` + the Cthulhu SPEC. |

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
