# Module 4 — Vectorization Discipline — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 decisions
accepted, incl. the composition artifact + connector-at-author-time).** **SHIPPED 2026-06-21
(`GATE-APPROVE-SHIP` cleared).** Fourth
authoring stage for Just Python. M1–M3 shipped.
M4 turns the blueprint's fourth module into finished mdBook lessons + Claude Code exercises, in the locked
Style Contract voice, at the STANDARDS difficulty bar, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not
author until Ray locks.

## The stage in one line

M1 built the cost model, M2 the NumPy operations, M3 the Pandas layer. M4 is the **judgment** that ties them
together: profile before you optimize, know when an array beats a loop and by how much, recognize `apply` as
the disguised loop M3 warned about, and know the cases where vectorizing is the wrong call. Seam: a Production
AI Engineer is not paid to vectorize everything; they are paid to measure, decide, and justify the decision.

## Settled decisions (from the blueprint + the contracts)

1. **Stage = module.** M4 reads its sources, writes `output/author|verify|ship/`, and hands its locked
   exemplars + the **composed** `measure.py` forward to M5.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md` (difficulty ramp
   + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every worker brief carries all three
   plus the M1–M3 exemplar lessons (the book's own voice).
3. **M4 is the first module to COMPOSE the throughline (STANDARDS Part 3 payoff).** M1–M3 each *added* one
   function to `measure.py` (`time_sum`, `broadcast_allocates`, `time_contiguous_vs_strided`, `frame_bytes`).
   M4 is where the reader **imports those off disk and composes them** into a vectorization decision tool, the
   way the contract says a later artifact must ("the capstone composes the prior artifacts, it does not
   rebuild them"). This is the module that makes the artifact-chaining real, not just additive.
4. **De-dup against M2 and M3.** M2 taught *how* to vectorize (ufuncs, broadcasting, layout); M3 taught the
   Pandas layer and first flagged `apply` as a disguised loop. **M4 does not re-teach the mechanics** — it
   teaches the *decision*: measuring the speedup, quantifying the `apply` cost, and the cases against
   vectorizing. M4 uses M2's ufuncs and M3's `apply` finding; it does not re-derive them.
5. **M4 is the Core-build rung closing into Composition (STANDARDS Part 1).** Four build/concept lessons,
   each runnable with a machine-checkable done-when; difficulty earned from a real profile-and-decide task,
   not API breadth. No forward dependencies.

## Proposed M4 split (5 lessons, one idea each)

Ramp order: measure first, then prove the win, then quantify the trap, then learn the limits.

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | M1–M3 gave you the tools; M4 is the judgment: profile, decide, justify. When the array wins, when `apply` costs you, and when vectorizing is the wrong call. | concept | conductor-integrated; frames the four below |
| 1 | `profile-before-you-optimize` | You cannot optimize what you have not measured; reach for `measure.py`'s `time_sum` (and `%timeit`/`perf_counter`) before you rewrite a loop, because the bottleneck is rarely where you guess. | concept/build | numpy-docs `basics.performant_code`; reuse `measure.py` `time_sum` |
| 2 | `when-the-array-wins` | A vectorized op replaces the Python interpreter's per-element overhead with one C loop; measure the speedup on a real reduction and watch it scale with array size. | build | numpy-docs `basics.performant_code`; reuse `measure.py` `time_sum` + `time_contiguous_vs_strided` |
| 3 | `the-hidden-cost-of-apply` | `df.apply(axis=1)` is the per-row Python loop M3 named; profile it against the vectorized column op and put a number on the tax, then learn the few cases where `apply` is genuinely unavoidable. | build | pandas-docs `enhancingperf` + `user_defined_functions` |
| 4 | `when-not-to-vectorize` | Vectorizing is not free: a broadcast can blow up memory (reuse `broadcast_allocates`), and a clever one-liner can cost readability; the discipline is a decision rule, not a reflex. | concept/build | numpy-docs `basics.performant_code`; reuse `measure.py` `broadcast_allocates` |

Each lesson ends in a Claude Code exercise (`exercises/module4/<slug>/README.md`) with a concrete,
machine-checkable done-when (a printed speedup/ratio, a passing assertion, exit 0), matching the M1–M3 format.

## The compounding throughline (STANDARDS Part 3) — the composition payoff

M4's exercise builds **`vectorization_report.py`**, which **imports the existing `measure.py` off disk** and
composes its functions into a decision tool: it calls `time_sum` to profile a loop vs a vectorized version
(L1/L2), reuses `broadcast_allocates` to check whether the vectorized path blows up memory (L4), and emits a
"vectorize / keep the loop" recommendation with the numbers behind it. The reuse is **real composition** (import
+ call the prior artifact), the exact pattern the contract reserves for the late-stage modules and the M6/M7/M8
artifacts. M4 leaves `measure.py` unchanged and `vectorization_report.py` as the new composed artifact M5/M6
can build on.

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** `vault/numpy-docs/basics.performant_code` + `vault/pandas-docs/enhancingperf` +
   `user_defined_functions`, plus the existing `measure.py` (read its current state). Read at author time by
   the worker; not loaded into the conductor.
2. **Microsoft Learn** via the connector — **workers query `microsoft_docs_search` / `microsoft_docs_fetch`
   while authoring** to ground every production-pattern claim in a real page with a real URL and to fill gaps
   (the standing rule after M2/M3: do not leave bare `[MS-Learn]` markers, and never invent a citation; if no
   real page backs a claim, state it plainly). The conductor's VERIFY pass is then a check, not the first time
   the connector is consulted.
3. **Editorial seam framing** — "why does a Production AI Engineer need this?": the batch job that times out,
   the `apply` that doesn't scale, the broadcast that OOMs the box.

## The fleet plan (conductor-direct, per the M2-vs-M3 finding)

Per `platform/ORCHESTRATION.md` (updated after the M2-vs-M3 comparison): a single ≤4-worker cluster with no
concurrent gate runs **conductor-direct, no handler tier.**

- **Conductor (Opus, this session):** locks the plan, briefs and dispatches 4 Sonnet workers directly,
  authors/integrates `00-overview`, and runs the Zinsser + STYLE + STANDARDS review gate on every draft. The
  `vectorization_report.py` composed artifact is folded/verified by the conductor.
- **Workers (Sonnet, parallel):** lessons 1–4, one worker per lesson, one writer per file. Each brief is
  self-contained: AUTHORING + STANDARDS + STYLE + the M1–M3 exemplars + that lesson's source slice + the
  current `measure.py` state, **and the instruction to use the live MS-Learn connector while authoring.**
  Workers never touch `SUMMARY.md`, `measure.py`, or `exercises/CLAUDE.md` (conductor-folded shared state).

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity.** 5 lessons (proposed). Recommendation: **5** — profile / win / apply-cost / limits is a
   clean decision arc, one idea each.
2. **The composition artifact.** Confirm M4's exercise builds `vectorization_report.py` that **imports**
   `measure.py` and composes `time_sum` + `broadcast_allocates` into a vectorize-or-not recommendation, vs
   adding yet another standalone `measure.py` function. Recommendation: **compose** — M4 is where the
   artifact-chaining contract is supposed to pay off, and a decision tool is the honest M4 artifact.
3. **The M3/M4 `apply` boundary.** Confirm M3 owns "`apply` is a disguised loop, prefer the column op" and
   M4 owns "profile the cost, put a number on it, know the unavoidable cases." Recommendation: **yes** —
   M4 quantifies and decides; it does not re-introduce.
4. **MS-Learn at author time.** Confirm worker briefs instruct active use of the connector (ground claims +
   fill gaps), not bare markers. Recommendation: **yes** (the standing rule after M2/M3's fabrications).

On lock: the fleet authors M4, VERIFY gates it against STYLE + the live MS-Learn connector, BUILD/TEST runs
`mdbook build` + each exercise's smoke path (including `vectorization_report.py` importing `measure.py`), and
the stage stops at `GATE-APPROVE-SHIP` before folding into `src/`.
