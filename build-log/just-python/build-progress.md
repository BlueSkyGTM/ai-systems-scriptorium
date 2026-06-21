# Just Python — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | Python as a Data Engine | ✅ Shipped | 2026-06-20 | 5 lessons (overview + the-cost-of-a-python-list, why-numpy-exists, dtypes-and-what-they-cost, shape-ndim-and-strides) + 4 exercises. Seeds the `measure.py` throughline; ships `exercises/CLAUDE.md`. Plan: `m1/PLAN.md`. |
| M2 | NumPy in Depth | ✅ Shipped | 2026-06-21 | 5 lessons (overview + vectorized-math-and-ufuncs, broadcasting, advanced-indexing, memory-layout-and-contiguity) + 4 exercises. De-duped against M1 (M1 owns dtypes + strides/view model; M2 owns the operational API). Extends `measure.py` with `broadcast_allocates` + `time_contiguous_vs_strided`, handing M4 a live artifact. VERIFY caught fabricated MS-Learn citations (resolved to grounded URLs); `mdbook build` clean; all 4 exercise gates pass deterministically. Plan: `m2/PLAN.md`. |
| M3–M8 | per blueprint | ⬜ Not started | — | M3 (Pandas for AI Pipelines) next. See `library/in-progress/just-python/README.md`. |

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
M2 doubles as **stress-test track 1** (does the method, not Claude's built-ins, complete the books) — the
per-book log is `build-log/stress-test/just-python.md`; the running verdict is `build-log/stress-test/FINDINGS.md`.
