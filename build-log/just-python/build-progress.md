# Just Python — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | Python as a Data Engine | ✅ Shipped | 2026-06-20 | 5 lessons (overview + the-cost-of-a-python-list, why-numpy-exists, dtypes-and-what-they-cost, shape-ndim-and-strides) + 4 exercises. Seeds the `measure.py` throughline; ships `exercises/CLAUDE.md`. Plan: `m1/PLAN.md`. |
| M2 | NumPy in Depth | ⬜ Not started | — | Broadcasting, fancy indexing, vectorized math, memory layout. |
| M3–M8 | per blueprint | ⬜ Not started | — | See `library/in-progress/just-python/README.md`. |

## Provenance

M1 is the **first module produced by the tiered orchestration pattern** (`platform/ORCHESTRATION.md`):
one Opus handler drove four Sonnet workers in parallel (one lesson each), while a scaffold worker built
the skeleton and shared theme concurrently; the conductor reviewed every draft against `STYLE.md` and the
central `STANDARDS.md` before it landed. Sourced from the vault `numpy-docs` subtree + the `draft/`
preview + Microsoft Learn. `mdbook build` clean. It is the proof the book-production engine works beyond
Sans Python, and the first book held to the central Standards Contract.
