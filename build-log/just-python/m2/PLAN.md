# Module 2 — NumPy in Depth — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 open decisions
accepted as recommended — 5 lessons, M1/M2 de-dup boundary as drawn, extend `measure.py`, ufuncs-first
order).** **SHIPPED 2026-06-21 (`GATE-APPROVE-SHIP` cleared).** Second authoring stage for Just Python. M1 shipped
2026-06-20 (5 lessons + 4 exercises, the `measure.py` throughline seeded, `mdbook build` clean). M2 turns
the blueprint's second module into finished mdBook lessons + Claude Code exercises, in the locked Style
Contract voice, at the STANDARDS difficulty bar, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not author
until Ray locks.

## The stage in one line

M1 built the *why* — the array exists because Python's boxed containers waste memory bandwidth. M2 builds
the *how*: the four operations that make the contiguous buffer pay off — vectorized math (ufuncs),
broadcasting, advanced indexing, and the memory layout that decides whether any of them is actually fast.
Seam: this is the exact NumPy API surface a take-home or a live screen tests, and the rung M4
(Vectorization Discipline) stands on.

## Settled decisions (from the blueprint + the contracts)

1. **Stage = module.** Same module-as-stage ICM shape: M2 reads its sources, writes
   `output/author|verify|ship/`, and hands its locked exemplars + the extended `measure.py` forward to M3.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md` (difficulty
   ramp + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every worker brief carries
   all three plus the canonical exemplar — now the **M1 lessons themselves** (`src/module1/*.md`), the
   book's own voice, not just Sans Python's. Cold workers do not inherit them.
3. **De-dup against M1 (the M1/M2 boundary, already half-settled).** The blueprint's M2 row reads
   "Arrays, dtypes, broadcasting, indexing, vectorized math, memory layout," but M1 already shipped
   `dtypes-and-what-they-cost` (dtypes) and `shape-ndim-and-strides` (the strides + view/copy *mental
   model*). The M1 PLAN's locked decision #2 drew this line: **M1 owns dtypes and the strides/view/copy
   mental model; M2 owns the operational API.** So M2 does **not** re-teach dtypes or re-introduce
   strides/views — it *uses* the view/copy distinction M1 established (e.g. "fancy indexing copies, unlike
   M1's slice-view") and spends its depth on broadcasting, ufuncs/reductions, advanced indexing as working
   tools, and layout-for-speed. This is in-ramp (no forward or backward dependency) and dodges the single
   most likely M2 failure: re-explaining M1.
4. **M2 stays the Core-build floor (STANDARDS Part 1).** Foundations (M1–2) floor is "a runnable script,
   one idea, one test." M2's four build lessons each ship a runnable script with a machine-checkable
   done-when; the module is not yet a multi-file portfolio artifact (that is M6+).
5. **Ore = the numpy-docs user guide + MS Learn.** `vault/numpy-docs/` (BSD-3, already in the vault) holds
   exactly the M2 sections (confirmed present: `basics.ufuncs`, `basics.broadcasting` + `theory.broadcasting`,
   `basics.indexing`, `basics.copies`, `basics.performant_code`). No vault→ingredients distillation pass is
   needed: reference-grade source, named per lesson below, read by the worker at author time — **not loaded
   into the conductor's context.** There is no `draft/` preview for M2 (M1 had one); the three-source rule
   carries the slack.

## Proposed M2 split (5 lessons, one idea each)

Ramp order chosen so each lesson depends only on the prior (STANDARDS Part 1, no forward dependencies):
element-wise first, then broadcasting (element-wise across mismatched shapes), then selection, then the
layout that governs all three.

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | M1 said *why* the array exists; M2 is *how you drive it* — ufuncs, broadcasting, advanced indexing, and the layout that makes them fast. The API a screen actually tests. | concept | conductor-integrated; frames the four below |
| 1 | `vectorized-math-and-ufuncs` | A ufunc runs one typed C loop across the whole buffer, and a reduction collapses an axis; `arr.mean(axis=0)`, `argmax`, `np.where` replace the Python loop. The shift M4 will formalize. | build | numpy-docs `basics.ufuncs` |
| 2 | `broadcasting` | NumPy stretches a smaller array across a larger one by aligning trailing dims and expanding size-1 axes — no copy until it must. The rule that makes "subtract the batch mean from 512×1536 embeddings" one line. | concept/build | numpy-docs `basics.broadcasting` + `theory.broadcasting` (+ diagrams) |
| 3 | `advanced-indexing` | Boolean masks filter and fancy indexing gathers — and both **copy**, unlike M1's slice-view. The tools that select the hard examples and the top-k rows from an eval table. | build | numpy-docs `basics.indexing` + `how-to-index` |
| 4 | `memory-layout-and-contiguity` | One buffer, two orders (C vs Fortran); contiguity decides whether a vectorized op is fast or silently copies. `ascontiguousarray` and `reshape`'s copy rule are the levers. Bridges to M4. | concept/build | numpy-docs `basics.copies` + `basics.performant_code` |

Each lesson ends in a Claude Code exercise (`exercises/module2/<slug>/README.md`) with a concrete,
machine-checkable done-when (a printed measurement, a passing assertion, exit 0), per STANDARDS Part 2 and
matching the M1 exercise format (`exercises/module1/shape-ndim-and-strides/README.md` is the shape exemplar).

## The compounding throughline (STANDARDS Part 3)

M2 **extends the existing `exercises/module1/measure.py`** — it imports and grows the M1 artifact, it does
not start a new one (the reuse must be real, per the contract and the `exercises/CLAUDE.md` coaching rule):

- **L2 (broadcasting)** adds `broadcast_allocates(...)`: a probe that uses `np.shares_memory` / `nbytes` to
  show whether a broadcasted op materializes a large intermediate (the embedding-mean case) or stays lazy.
- **L4 (layout)** adds `time_contiguous_vs_strided(...)`: times a reduction over a C-contiguous array vs a
  transposed/strided view, proving the layout cost in milliseconds.

These two are the exact hooks **M4 (Vectorization Discipline)** reuses to prove a vectorized op beats a loop
and a contiguous op beats a strided one. M2 leaves `measure.py` in a state M4 imports off disk, not rebuilds.
The book's `exercises/CLAUDE.md` already names `measure.py` as the M1 throughline; M2 authoring updates that
note to reflect the two new functions so the coaching agent reads the current state before extending.

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** `vault/numpy-docs/` sections named per lesson above. Read at author time by the worker;
   not loaded into the conductor.
2. **Microsoft Learn** via the connector ("Explore and analyze data with Python" — the NumPy operations
   section — plus NumPy ufunc/broadcasting refs). Resolve every `[MS-Learn: …]` marker at VERIFY; zero
   markers is a smell, not a pass. (The M1 lessons cite this same module — keep the citation consistent.)
3. **Editorial seam framing** — "why does a Production AI Engineer need this?" in every lead: ufuncs +
   reductions = cosine similarity and metric aggregation without loops; broadcasting = batch-normalizing
   embeddings; advanced indexing = filtering an eval set / top-k retrieval; layout = the hidden perf cost
   M4 formalizes.

## The fleet plan (orchestration pressure test)

Same tiered pattern that produced M1 (`platform/ORCHESTRATION.md`), now with the book's own M1 lessons as
the voice anchor:

- **Conductor (Opus, this session):** locks the plan with Ray, then dispatches; integrates the `SUMMARY` and
  shared state; runs the Zinsser + STYLE + STANDARDS review gate on every draft before it lands; authors/
  integrates `00-overview` itself. Voice and bar are enforced at review, not delegated.
- **Handler (Opus, one):** owns M2; briefs the four workers, absorbs their intake/outtake, returns one rollup.
- **Workers (Sonnet, parallel):** lessons 1–4 authored in parallel, one worker per lesson, one writer per
  file. Each brief is self-contained: AUTHORING + STANDARDS + STYLE + the M1 exemplar lessons + that
  lesson's numpy-docs slice. Workers never touch `SUMMARY.md`, `measure.py`, or other shared state; the
  conductor folds the `measure.py` extensions (L2, L4) so two workers never write the same file.

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity.** 5 lessons (proposed) vs a 6-lesson split (separate `boolean-masking` from
   `fancy-indexing` in L3). Recommendation: **5** — boolean and fancy indexing are one "advanced indexing"
   mental model (select-by-condition vs select-by-position), and STYLE §3's one-idea rule is satisfied by
   "advanced indexing copies; basic slicing views."
2. **The M1/M2 de-dup boundary** (settled decision #3). Confirm M2 does **not** re-teach dtypes or the
   strides/view/copy mental model (M1 owns them) and instead teaches the operational API (ufuncs,
   broadcasting, advanced indexing, layout-for-speed). Recommendation: **yes, as drawn** — re-teaching M1
   is the main M2 risk and this removes it.
3. **Throughline.** Confirm M2 extends `measure.py` with the broadcast-allocation probe (L2) and the
   contiguity-timing probe (L4), vs leaving M4 to start its reuse cold. Recommendation: **extend at M2** —
   it makes M2's "layout decides speed" claim measurable and hands M4 a live artifact.
4. **Lesson order.** ufuncs → broadcasting → advanced-indexing → layout (proposed), vs leading with
   broadcasting as the headline concept. Recommendation: **ufuncs first** — broadcasting is "what a ufunc
   does when shapes differ," so it should build on the ufunc lesson, not precede it.

On lock: the fleet authors M2, VERIFY gates it against STYLE + MS Learn, BUILD/TEST runs `mdbook build` +
each exercise's smoke path, and the stage stops at `GATE-APPROVE-SHIP` before folding into `src/`.
