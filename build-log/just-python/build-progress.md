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
| M7 | Evaluation Engine | ✅ Shipped | 2026-06-21 | Second portfolio module. overview + 4 stage-lessons + exercises building one `eval_engine.py` (read `id,prediction,label` → per-class TP/FP/FN via NumPy masks → P/R/F1 → Markdown table) + `smoke.py` (locked metrics on a 10-row sample, report renders, negative case raises, zero-division=0.0) + `outputs/skill-evaluation-engine.md`. No sklearn. Composes M2 + M3 + M5. Conductor assembled + ran the reference (green, metrics match exactly). Far less reconciliation than M6: locking the sample + expected metric values (not just structure) kept the fleet from diverging. `mdbook build` clean. Plan: `m7/PLAN.md`. | Second portfolio module: a runnable `eval_engine.py` (read `id,prediction,label` → per-class precision/recall/F1 with NumPy, no sklearn → Markdown table) + smoke gate + skill write-up. Composes M2 (masks/reductions) + M3 (read) + M5 (dataclass). Canonical structure + sample + expected metric values pre-specified. Conductor-direct. |
| M8 | Integrated Python Engineering Exam | ✅ Shipped | 2026-06-21 | The capstone. overview + 4 lessons (the-exam, compose-the-pipeline, the-rubric-and-grading, run-test-and-ship) + 4 exercises building one `pipeline.py` that **imports `wrangle.py` (M6) + `eval_engine.py` (M7) off disk** (`artifact_adapter.py`, `importlib` + `sys.modules` registration) and chains them: raw corpus → `wrangle.run` → read clean Parquet → merge predictions on `id` → `eval_engine.run` → integrated `report.md`. `rubric.py` grades the 5-field `ExamRun` by code against six criteria (R1 RUNS, R2 SCHEMA-VALID, R3 METRICS-CORRECT, R4 COMPOSED, R5 PROBLEM-FRAMED, R6 TESTED+VERSIONED); the `CRITERIA` tuple == the prose table. `smoke.py` + `tests/test_smoke.py` grade 6/6 on the locked 10-row sample (the M7 oracle reused: cat 0.750/0.750/0.750, dog 0.667/0.500/0.571, bird 0.667/1.000/0.800) and prove a deficient run fails R2+R3. No sklearn, offline. **Conductor assembled + ran the full reference harness (wrangle + eval_engine + pipeline + rubric + smoke) green** before ship. Conductor-direct (4 Sonnet authors + 2 Haiku MS-Learn fetchers). Heavy conductor reconciliation: 4 cold-worker contract bugs fixed (composed_modules `.py` suffix, `smoke_negative_passed` removed → R6 = versioned, module-level `default_config`, adapter path off-by-one + `sys.modules` registration). `mdbook build` clean. Plan: `m8/PLAN.md`. **Just Python is content-complete: 8/8 modules shipped.** |

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

M8 is the **capstone and the terminal node of the throughline**: `pipeline.py` imports `wrangle.py` (M6) +
`eval_engine.py` (M7) off disk and chains them under a six-criterion `rubric.py` graded by code. It is the
clearest demonstration of the orchestration playbook learned across M4/M6/M7: the conductor pre-locked the
harness structure, the `pipeline.py`/`ExamRun`/`rubric.py` contracts, and the test oracle (reusing the M7
metric values), then dispatched 4 Sonnet authors with 2 Haiku MS-Learn fetchers feeding verified URLs into
the briefs (the "Sonnet authors, Haiku fetchers" division). Even with the contracts pre-locked, four cold
workers still drifted on the cross-file seams: `composed_modules` value (`wrangle` vs `wrangle.py`), an
`smoke_negative_passed` field the rubric read but the dataclass never had, a `default_config` defined inside
`__main__` (so the smoke gate could not import it), and an adapter path off by one `..` plus the missing
`sys.modules` registration that makes an off-disk frozen dataclass importable on Python 3.12. The conductor
caught all four by **assembling and running the full reference harness end to end** (reference wrangle +
eval_engine + the M8 files), then reconciled every committed lesson and README to the verified contract. The
lesson reinforced: pre-locking structure narrows divergence but does not eliminate it on a multi-file shared
artifact; the conductor reference run is the gate that catches the seams. `mdbook build` clean. With M8,
**Just Python is content-complete: 8 of 8 modules shipped.**
