# Module 1 — Python as a Data Engine — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN DRAFTED — awaiting `GATE-LOCK-PLAN`.** First authoring stage for Just Python
(graduated to `library/in-progress/just-python` 2026-06-20). M1 turns the blueprint's first module
into finished mdBook lessons + Claude Code exercises, in the locked Style Contract voice, at the
STANDARDS difficulty bar, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not author until Ray locks.

## The stage in one line

M1 builds the mental model behind fast numerical Python: why Python's default data structures are the
bottleneck, and why the contiguous NumPy array is the answer. It is the conceptual floor the rest of
the book stands on. Seam: a Production AI Engineer is screened on Python they were told to "just know";
M1 replaces folklore with the memory-and-cost model that makes every later vectorization decision obvious.

## Settled decisions (from the blueprint + the contracts)

1. **Stage = module.** Same module-as-stage ICM shape as Sans Python: M1 reads its sources, writes
   `output/author|verify|ship/`, and hands the locked voice/exemplars forward to M2.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md` (difficulty
   ramp + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every worker brief carries
   all three plus the canonical exemplar — cold workers do not inherit them.
3. **M1 is the conceptual "why"; M2 is the NumPy "depth."** Per the blueprint split: M1 = the data-model
   and memory mental model; M2 = the broadcasting/indexing/vectorized-math API in depth. M1 stays
   foundational (STANDARDS Part 1 floor: a runnable script, one idea, one test per lesson).
4. **Ore for M1 = the NumPy user guide subtree + the existing draft + MS Learn.** `vault/numpy-docs`
   (BSD-3, already in the vault) is the reference-grade substance; `draft/` already previews three M1
   lessons. The `made-with-ml` / `aefs` data veins feed M3 (Pandas) and the M6/M7 artifacts, not M1, so
   M1 needs no separate vault→ingredients distillation pass.

## Proposed M1 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | Python runs AI work, and its default containers are the bottleneck; this module builds the cost model. | concept | draft `00-overview.md` |
| 1 | `the-cost-of-a-python-list` | A Python list of numbers is a box of pointers to boxed objects; that overhead is why it is fat and slow. Measure it. | concept/build | draft `01-cost-of-a-python-list.md`; numpy-docs `basics.types`, `absolute_beginners` |
| 2 | `why-numpy-exists` | The answer is one dtype in one contiguous block: the array. The conceptual leap from container to buffer. | concept | numpy-docs `basics.creation`, `basics.rec` framing |
| 3 | `dtypes-and-what-they-cost` | Fixed-width types trade precision for memory and speed; float32 vs float64 is an AI-relevant decision, not a default. | build | numpy-docs `basics.types`; draft `02` dtype half |
| 4 | `shape-ndim-and-strides` | An array is a flat buffer plus a shape and strides; views share that buffer, which is power and a corruption trap. | concept/build | numpy-docs `basics.indexing`, `basics.copies`; draft `02` strides half |

Each lesson ends in a Claude Code exercise (`exercises/module1/<slug>/README.md`) with a concrete,
machine-checkable done-when (a printed measurement, a passing assertion), per STANDARDS Part 2.

## The compounding throughline (STANDARDS Part 3)

M1 seeds `measure.py`: a tiny, reusable benchmark helper the reader builds in lesson 1 (list vs array
memory + timing) and **extends** through the book — M4 (Vectorization Discipline) reuses it to prove a
vectorized op beats a loop; the M6 wrangle pipeline imports it to justify its choices. The reuse must be
real (import the prior file), not restated. M1 also ships the book's `exercises/CLAUDE.md` coaching
contract (read the lesson, find `measure.py` and read its current state, coach without solving).

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** `vault/numpy-docs/` user-guide sections named per lesson above + the `draft/` preview.
2. **Microsoft Learn** via the connector ("Explore and analyze data with Python" module + NumPy refs).
   Resolve every `[MS-Learn: …]` marker; zero markers is a smell, not a pass.
3. **Editorial seam framing** — "why does a Production AI Engineer need this?" in every lead.

## The fleet plan (orchestration pressure test)

This stage is also the live test of the tiered pattern (`platform/ORCHESTRATION.md`):

- **Conductor (Opus, this session):** locks the plan with Ray, then dispatches; integrates `SUMMARY` and
  all shared state; runs the Zinsser + STYLE + STANDARDS review gate on every draft before it lands. The
  voice and the bar are enforced at review, not delegated.
- **Handler (Opus, one):** owns M1; briefs the workers, absorbs their intake/outtake, returns one rollup.
- **Workers (Sonnet, parallel):** lessons 1–4 authored in parallel, one worker per lesson, one writer per
  file. The overview is integrated by the conductor. Each brief is self-contained: STANDARDS + STYLE + the
  Sans Python exemplar + that lesson's source slice. Workers never touch `SUMMARY.md` or other shared state.

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity.** 5 lessons (proposed) vs a finer one-idea split (lesson 4 could split shape/strides
   from views/copies → 6 lessons). Recommendation: **5**; views+strides are one mental model.
2. **M1/M2 boundary.** Confirm dtypes + strides live in M1 (as the mental model) and the broadcasting /
   fancy-indexing / vectorized-math *API depth* waits for M2. Recommendation: **yes, as drafted.**
3. **Throughline artifact.** Confirm M1 seeds `measure.py` as the reusable helper (vs M1 exercises-only,
   starting the throughline at M3). Recommendation: **seed it at M1** — the cost model is the whole point.

On lock: the fleet authors M1, VERIFY gates it, BUILD/TEST runs `mdbook build`, and the stage stops at
`GATE-APPROVE-SHIP` before folding into `src/`.
