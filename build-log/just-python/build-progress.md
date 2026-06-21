# Just Python — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | Python as a Data Engine | ✅ Shipped | 2026-06-20 | 5 lessons (overview + the-cost-of-a-python-list, why-numpy-exists, dtypes-and-what-they-cost, shape-ndim-and-strides) + 4 exercises. Seeds the `measure.py` throughline; ships `exercises/CLAUDE.md`. Plan: `m1/PLAN.md`. |
| M2 | NumPy in Depth | ✅ Shipped | 2026-06-21 | 5 lessons (overview + vectorized-math-and-ufuncs, broadcasting, advanced-indexing, memory-layout-and-contiguity) + 4 exercises. De-duped against M1 (M1 owns dtypes + strides/view model; M2 owns the operational API). Extends `measure.py` with `broadcast_allocates` + `time_contiguous_vs_strided`, handing M4 a live artifact. VERIFY caught fabricated MS-Learn citations (resolved to grounded URLs); `mdbook build` clean; all 4 exercise gates pass deterministically. Plan: `m2/PLAN.md`. |
| M3 | Pandas for AI Pipelines | ✅ Shipped | 2026-06-21 | 5 lessons (overview + series-and-dataframe, reading-and-writing-ai-formats, groupby-merge-apply, cleaning-and-missing-data) + 4 exercises. Ore: `vault/pandas-docs` (reference-grade) + made-with-ml `data.py` applied. Extends `measure.py` with `frame_bytes`. VERIFY caught fabricated MS-Learn citations (grounded to real URLs); `mdbook build` clean; all 4 exercise gates pass. Authored **conductor-direct (no handler tier, the orchestration A/B)**. Plan: `m3/PLAN.md`. |
| M4 | Vectorization Discipline | ✅ Shipped | 2026-06-21 | 5 lessons (overview + profile-before-you-optimize, when-the-array-wins, the-hidden-cost-of-apply, when-not-to-vectorize) + 4 exercises. First module to **compose** the throughline: `vectorization_report.py` imports `measure.py` off disk and composes `time_sum` + `broadcast_allocates` into a vectorize-or-not decision tool (verified runnable). Authored conductor-direct; workers grounded MS-Learn claims against real URLs via the connector (no fabrications). `mdbook build` clean. Plan: `m4/PLAN.md`. |
| M5 | Python Idioms at Interview Speed | ✅ Shipped | 2026-06-21 | 5 lessons (overview + comprehensions-and-generators, decorators, type-hints, dataclasses) + 4 self-contained exercises. Thin ore (no python-docs subtree): grounded in made-with-ml applied code + the book's own artifacts + the MS-Learn connector. L2/L3/L4 cite real verified MS-Learn URLs; L1 (comprehensions/generators) carries none by design (no real MS-Learn page exists; the standing rule = state plainly, never fabricate). Conductor-direct; all 4 exercise gates pass; `mdbook build` clean. Plan: `m5/PLAN.md`. |
| M6 | Data Wrangling Artifact | ✅ Shipped | 2026-06-21 | First portfolio module. overview + 4 stage-lessons + exercises building one `wrangle.py` (ingest JSONL → clean/dedup → reshape/validate → emit Parquet) + `smoke.py` (pytest: row accounting 8→6, Parquet round-trip with `pandas.api.types` predicate dtypes, negative case raises at the gate) + `outputs/skill-data-wrangling.md`. Composes M3 + M5 + made-with-ml `data.py`. Conductor assembled + ran the reference artifact (green). Heavy conductor reconciliation needed (one shared artifact, 4 cold workers): fixed clean arity, label-dtype, corpus filename/defects, Parquet `str`-dtype round-trip. `mdbook build` clean. Plan: `m6/PLAN.md`. | First portfolio module: a runnable `wrangle.py` (ingest JSONL → clean/dedup → reshape/validate → emit Parquet) held to STANDARDS Part 2 (README problem-framing, `pytest` smoke gate incl. negative case, skill write-up). Composes M3 Pandas + M5 idioms + made-with-ml `data.py`. Canonical `wrangle.py` structure pre-specified to avoid M4-style divergence. Conductor-direct. |
| M7–M8 | per blueprint | ⬜ Not started | — | M7 Evaluation Engine (portfolio), M8 Integrated Exam (capstone). See `library/in-progress/just-python/README.md`. |

## Provenance

M1 is the **first module produced by the tiered orchestration pattern** (`platform/ORCHESTRATION.md`):
one Opus handler drove four Sonnet workers in parallel (one lesson each), while a scaffold worker built
the skeleton and shared theme concurrently; the conductor reviewed every draft against `STYLE.md` and the
central `STANDARDS.md` before it landed. Sourced from the vault `numpy-docs` subtree + the `draft/`
preview + Microsoft Learn. `mdbook build` clean. It is the proof the book-production engine works beyond
Sans Python, and the first book held to the central Standards Contract.

M2 is the **first module run through a full AUTHOR → VERIFY → BUILD/TEST cycle with the live MS-Learn
connector.** One Opus handler drove four Sonnet workers (one lesson each); the conductor reviewed every
draft against `STYLE.md` + `STANDARDS.md`, ran VERIFY against the connector (which caught and removed
fabricated MS-Learn citations the workers had invented), authored the overview, and folded shared state
(`SUMMARY.md`, `exercises/CLAUDE.md`). `mdbook build` clean; the four exercise gates pass deterministically.

M3 ran the **orchestration A/B: conductor-direct, no handler tier.** Four Sonnet workers managed directly by
the conductor matched M2's handler-tier run on quality with one fewer tier; `platform/ORCHESTRATION.md` was
updated to relax the "3+ workers → handler" rule (handler when concurrent gates or multiple clusters, not by
count). VERIFY again caught fabricated MS-Learn citations (reproduced from M2); BUILD/TEST caught two bugs the
worker self-reports missed (stale `frame_bytes` byte numbers, a wrong-variable assert). `mdbook build` clean;
all four exercise gates pass. The `ingredients/dossiers` distillation machinery stayed unexercised:
`vault/pandas-docs` is reference-grade, so M1–M3 all bypassed distillation.

M4 is the **first module to compose the throughline** rather than add to it: the exercise builds
`vectorization_report.py`, which imports `measure.py` off disk and composes `time_sum` +
`broadcast_allocates` into a vectorize / keep-the-loop / chunk-it decision tool (the artifact-chaining the
STANDARDS contract reserves for the late modules; the conductor verified it runs end to end). Authored
**conductor-direct** (no handler tier). The standing rule landed: workers **used the MS-Learn connector
while authoring** and grounded every production-pattern claim in a real, verified URL (Azure Well-Architected
PE:07, the NumPy/Pandas training unit, Azure ML batch-scoring) — zero fabricated citations, the fix for the
M2/M3 problem. The conductor reconciled the four cold workers' inconsistent `vectorization_report.py`
paths/imports into one canonical design (without which the composition would not run). `mdbook build` clean;
the composed artifact runs and all four exercise gates pass.
