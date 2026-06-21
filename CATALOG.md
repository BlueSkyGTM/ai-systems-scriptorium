# CATALOG — the books

The library index and status. For cross-cutting work items see [`BACKLOG.md`](BACKLOG.md); for
routing to a book see [`CONTEXT.md`](CONTEXT.md).

| Book | Status | Location | Notes |
|---|---|---|---|
| **Sans Python — Production AI Engineering** | ✅ Completed | [`library/completed/sans-python`](library/completed/sans-python/CONTEXT.md) | 8 modules shipped; `mdbook build` passes; M6/M7/M8 portfolio artifacts runnable. The reference book and the proof the engine works. |
| **Just Python** | 🚧 In progress | [`library/in-progress/just-python`](library/in-progress/just-python/CONTEXT.md) | Applied Python (NumPy/Pandas/vectorization; 94% screen, gap-report row 1). **Module 1 shipped 2026-06-20** (5 lessons + 4 exercises, authored by the tiered fleet, reviewed to STYLE + STANDARDS). M2 next. |
| **Machine Math** *(working title)* | 📋 Planned | [`library/planned/ml-in-proportion`](library/planned/ml-in-proportion/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. Classic ML paired with the math each fundamental needs (gap-report rows 3+6), applied depth. PyTorch/training split to Weights and Measures. Needs `GATE-NAME-BOOK`. |
| **Data Currents** *(working title)* | 📋 Planned | [`library/planned/upstream`](library/planned/upstream/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. Interpreting + routing data for AI systems: SQL + the data platform beyond the Docling front door (gap-report row 4, 52%); extends Sans Python M5 L14. Needs `GATE-NAME-BOOK`. |
| **Weights and Measures** *(working title)* | 📋 Planned | [`library/planned/tasteful-tuning`](library/planned/tasteful-tuning/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. PyTorch + model training with quality as the throughline (gap-report row 2, 78%): the weights you train and the measures that prove them. Needs `GATE-NAME-BOOK`. |
| **Anatomy of an Answer** *(working title)* | 📋 Planned | [`library/planned/interview-algorithm`](library/planned/interview-algorithm/CONTEXT.md) | Blueprint + Chapter 1 drafted 2026-06-20. The getting-hired book: deconstruct the right answers (and the questions behind them) to their core; a reasoning framework, not memorization. Ore: `asdg` interview half. Supersedes Show, Don't Tell's interview angle. Needs `GATE-NAME-BOOK`. |
| **Local Metal** *(working title)* | 📋 Planned | [`library/planned/local-metal`](library/planned/local-metal/CONTEXT.md) | Blueprint scaffolded 2026-06-20. The home production environment: build a homebrew rig (Cthulhu SPEC) and host local models to offload Claude Code. Progress-agnostic, home-scale companion to Sans Python; grows as the other books are ingested. Ore: `aipe` + the Cthulhu SPEC. Needs `GATE-NAME-BOOK`. |
| **Show, Don't Tell** | 📋 Planned | [`library/planned/show-dont-tell`](library/planned/show-dont-tell/CONTEXT.md) | Stub only. Systems-design angle; the interview angle moved to Anatomy of an Answer. Overlaps Simple Systems; reconcile before starting. Needs `GATE-NAME-BOOK`. |
| **Simple Systems** | 📋 Planned | [`library/planned/simple-systems`](library/planned/simple-systems/CONTEXT.md) | Stub only. Approachable systems-design book; kin to Local Metal's simple-at-home principle. Ore: `vault/ai-system-design-guide`. Needs `GATE-NAME-BOOK`. |

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
