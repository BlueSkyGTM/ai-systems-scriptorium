# M3 stage — CONTEXT (ICM entry doc)

This is the M3 (Agent Foundations) authoring stage. Read `PLAN.md` (this folder) for the locked
plan + the `/autoplan` review report. The build runs as a sequence of module stages M3 → M8; this
is the M3 stage.

## Reads (inputs)
- Prior stage output: M1/M2 are shipped in `src/module1/`, `src/module2/` (lessons + exemplar voice).
- Ingredients: `src/module3/*.md` (six chapter files, to become 15 lessons).
- Depth: `synthesis/source/module3/` — **single-agent subset ONLY** (aefs agent-engineering Ph14
  01–18/31–42 + tools-protocols Ph13; asdg agentic-systems Ch07, memory-state Ch08, frameworks-tools
  Ch09, design-patterns Ch15, tool-use-computer-agents thin). **Never glob this folder** — `fleet-*`
  and `loop-*` are M4.
- Contracts: `../../AUTHORING.md`, `../../STYLE.md`, `../../_dossier/module3.md`.

## Pipeline (this stage)
1. **(pre) M2 VERIFY** — runs first, tightly scoped (fix the prefill defect + prove the gate).
2. **AUTHOR** — Sonnet drafters, one per chapter-group → `output/author/`. Throughline artifact:
   `module3-agent/`. TypeScript for new tool/MCP examples; Python for workbench surface scripts.
3. **VERIFY** (hard gate) → `output/verify/<lesson>-verdict.md` per lesson: a claim ledger
   (every non-obvious technical/source/API claim traced to source or primary spec / MS-Learn,
   ≥1 logged MS-Learn validation per technical lesson), STYLE full-read, `mdbook build`, exercise
   sanity. No verdict file = SHIP cannot run.
4. **SHIP** → land lessons into `src/module3/`, update `src/SUMMARY.md` (topological sort of
   `dependencies.md`), delete superseded ingredient files, mark DONE, commit + push → `output/ship/`.

## Writes (outputs)
- `output/author/`, `output/verify/`, `output/ship/`, plus a threads-forward note for the M4 stage.

## Locked decisions
Granularity = Hybrid 15 (see PLAN.md). 15 hardening items accepted. See
`../../build-progress.md → M3 stage — plan locked`.
