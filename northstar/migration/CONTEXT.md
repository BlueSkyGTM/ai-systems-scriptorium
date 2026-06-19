# Migration — Synthesis → mdBook Course

The stage that turns the synthesis *analysis* into the actual *course*. Synthesis gave the picture
(what we have / need / don't); migration extracts the survivors into a clean, mdBook-shaped home with
every curation ruling applied. **Opus does this — no Claude Code yet.**

## Inputs

- **`../sub-repos/synthesis/source/`** — the consolidated library: 40 lesson-level extraction files under
  the *old* 5-module numbering (`module1–5/`), per-repo metadata in `_repos/`, prefixes per repo (`aefs`,
  `asdg`, `aipe`, `fleet`, `loop`, `mwml`, `ts`, `rust`, `obook`). This is the ingredient shelf.
- **`../sub-repos/synthesis/output/snapshot/`** — the decisions: `step2-flow-audit.md` (validated),
  `step3-resolutions.md` (cuts/merges), `artifacts-plan.md`, `language-tracks.md`, module1–5 prereq graphs.
- **`../SYLLABUS.md`** — canonical 8-module structure + folded antilibrary.

## What migration produces (this folder)

An mdBook project skeleton plus, per module, a **module dossier** that resolves the content:

```
migration/
├── CONTEXT.md          ← this file
├── book.toml           ← mdBook config
├── src/
│   ├── SUMMARY.md      ← the mdBook table of contents (8 modules → chapters)
│   └── moduleN/        ← per-module migrated content (one .md per chapter/lesson cluster)
└── _dossier/
    └── moduleN.md      ← migration ledger: kept / cut / merged / threaded, with source pointers
```

The **dossier** is the audit trail (what came from where, what was cut and why). The **src/** tree is the
authorable content, organized for mdBook. Authoring final prose (3-source rule — synthesis + Microsoft
Learn + editorial, `.claude/rules/10`) happens after migration; migration assembles and resolves.

## The rulings migration applies (from the snapshot)

1. **8-module renumber** — old M3 → M3 Agent Foundations + M4 Multi-Agent Systems; old M4 Deploy → M5;
   old M5 capstones → M6/M7 artifacts + M8 exam. (`step2-flow-audit.md`)
2. **Cuts → antilibrary** (do not migrate into src/; record in dossier): generative media (aefs Ph08),
   GPT-from-scratch (30–49), distributed training (76–81), frontier-safety research, mwml model-centric
   MLOps training-pipeline, pre-transformer NLP half. (`step3-resolutions.md`, SYLLABUS antilibrary)
3. **Merges → one spine**: RAG (asdg Ch06 canonical + aefs Ph11 hands-on; M1 NLP = components only);
   MCP (aefs Ph13 canonical, asdg lighter). Collapse the duplicates.
4. **Language threading**: Rust/TS are *toolchain-installed* in M1 but *taught* at point-of-use —
   TS break-in set → M3, Rust ownership on-ramp → M5. The `ts-`/`rust-module1` content files migrate to
   M3/M5, not M1. (`language-tracks.md`)
5. **Artifacts**: M6/M7/M8 src content = the artifact specs from `artifacts-plan.md` (compounding), not
   the old capstone dump.

## How To (per module)

1. Open `_dossier/moduleN.md`. List the synthesis source files feeding this module (per the mapping table
   below).
2. For each source file / lesson: keep / cut / merge / thread-out, citing the ruling. Cut → antilibrary
   note. Threaded-out → record its destination module.
3. Write the kept + merged content into `src/moduleN/` as chapter files, deduped, in prereq order.
4. Add the chapter entries to `src/SUMMARY.md`.
5. Done when every source file for the module is accounted for (kept-and-placed, merged, cut, or threaded).

## Source → 8-module mapping

| 8-module | Synthesis source files |
|----------|------------------------|
| M1 Foundations | `module1/aefs-module1-setup-tooling`, `module1/aefs-module1-nlp-transformer-forward` (attention-forward only) |
| M2 LLM Engineering | `module2/aefs-module2-llm-engineering`, `module2/asdg-module2-prompting-context`, `module2/asdg-module2-retrieval-systems`, `module2/asdg-module2-eval-guides`; `module2/aefs-module2-generative-ai` → **cut** |
| M3 Agent Foundations | `module3/aefs-module3-agent-engineering` (single-agent), `module3/aefs-module3-tools-protocols`, `module3/asdg-module3-agentic-systems`, `module3/asdg-module3-memory-state`, `module3/asdg-module3-frameworks-tools`, `module3/asdg-module3-design-patterns`; `module1/ts-module1-typescript-topics` (TS break-in, threaded here) |
| M4 Multi-Agent Systems | `module3/aefs-module3-agent-engineering` (multi-agent split), `module3/asdg-module3-tool-use-computer-agents`, all `fleet-module3-*` (5), all `loop-module3-*` (6) |
| M5 Deploy & Perf Eng | `module4/aefs-module4-infrastructure-production`, `module4/aipe-module4-*` (inference subset), `module4/asdg-module4-deploy-chapters`, `module4/asdg-module4-case-studies`, `module4/mwml-module4-deploy-scripts`; `module1/rust-module1-*` (Rust on-ramp, threaded here); mwml training-pipeline → **cut** |
| M6 Agent Artifacts | `module5/aefs-module5-capstone` (single-agent subset) + `artifacts-plan.md` |
| M7 Multi-Agent Artifacts | `module5/aefs-module5-capstone` (multi-agent subset) + `artifacts-plan.md` |
| M8 Final Exam | `module5/aefs-module5-capstone` (finale) + `asdg-module4-case-studies` (reference architectures) |

## Status

- [x] M1 Foundations — pilot, signed off
- [x] M2 LLM Engineering — dossier + 4 chapters
- [x] M3 Agent Foundations — dossier + 6 chapters
- [x] M4 Multi-Agent Systems — dossier + 4 chapters
- [x] M5 Deploy & Performance Engineering — dossier + 5 chapters
- [x] M6/M7/M8 Artifacts + Exam — combined dossier + 3 overviews
- [x] SUMMARY.md + antilibrary.md complete

**Migration ingredients-level pass DONE (2026-06-18).** All 8 modules resolved (keep/cut/merge/thread), all
src content placed, all cuts recorded in `src/antilibrary.md`.

**REPO IS NOW READY FOR CLAUDE CODE (2026-06-18).** The authoring handoff is complete:
- `src/preface.md` + `src/README.md` — the locked voice (approved worked example).
- `STYLE.md` — the Style Contract (checkable writing spec, Zinsser as engineer's spec).
- `_templates/concept-lesson.md` + `build-lesson.md` — the lesson skeletons.
- `AUTHORING.md` — the authoring contract (the curriculum Claude Code follows): 3-source rule, per-lesson
  How To, thread placement, the Zinsser pass, done-when, M1→M8 order.
- `theme/copy-to-claude.{js,css}` + `book.toml` wiring — the per-lesson copy-to-Claude-Code button.
- `exercises/README.md` — the exercise-brief convention.

**Next (Claude Code, Build phase):** author lessons module by module per `AUTHORING.md` (read `STYLE.md`
first). Then lift `migration/` out as the standalone course repo (rename `AUTHORING.md` → `CLAUDE.md`; take
`book.toml` + `src/` + `exercises/` + `theme/`; leave `_dossier/` + `STYLE.md`/`AUTHORING.md` as workshop or
carry them as agent guidance).
