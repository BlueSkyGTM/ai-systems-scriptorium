# Exercises: for Claude Code (a learner is driving)

When a learner pastes an exercise into you, they are here to build, not to watch. Coach; do not solve.

## Before You Touch Code

- Read the lesson in `src/moduleN/<lesson-slug>.md` first, then the exercise `README.md` beside it.
  The lesson holds the why; the README holds the brief.
- Find the module's throughline artifact and read its current state before adding to it. You are
  continuing a build, not starting one.

  **Module 1–3 throughline: `exercises/module1/the-cost-of-a-python-list/measure.py`**
  This is the reusable benchmark helper the reader builds across the M1 lessons and keeps extending
  through M2 and M3. It starts as a skeleton in M1 lesson 1 (the-cost-of-a-python-list) and grows with
  each lesson: M1 adds `list_bytes`, `array_bytes`, and `time_sum`; M2 adds `broadcast_allocates` (the
  broadcasting lesson) and `time_contiguous_vs_strided` (the memory-layout lesson); M3 adds
  `frame_bytes` (the series-and-dataframe lesson). Before any M1, M2, or M3 exercise that touches it:
  open `measure.py`, read what is already there, and understand where in the build the learner is. Do
  not re-implement what exists. Do not reset state you did not write.

  **Module 4 composes the throughline: `exercises/module4/vectorization_report.py`**
  M4 does not add to `measure.py`; it builds a new artifact, `vectorization_report.py`, that **imports
  `measure.py` off disk** (`time_sum`, `broadcast_allocates`) and composes those functions into a
  vectorize-or-not decision tool, built up across the four M4 lessons (profile → speedup table → apply
  tax → memory check + recommendation). Before any M4 exercise: open `vectorization_report.py`, read its
  current state, and add to it. Never rebuild `measure.py`; import it. This is the artifact-composition
  pattern the M6/M7/M8 portfolio modules use.

  **Module 5 idioms are self-contained demos (no shared throughline file): `exercises/module5/<lesson>/`**
  M5 (comprehensions-and-generators, decorators, type-hints, dataclasses) teaches the screened Python
  idioms; each exercise is a standalone script and does **not** extend `measure.py` or
  `vectorization_report.py` (a deliberate call to avoid four cold workers refactoring one shared file).
  The lessons demonstrate each idiom by refactoring a snippet of the reader's own artifacts; the idioms
  themselves are the polish M6's `wrangle.py` is written with.

  **Module 6 is the first portfolio artifact: `exercises/module6/wrangle.py`**
  M6 builds one runnable pipeline across four lessons (ingest -> clean -> reshape_and_validate -> emit),
  composed by `run()` returning a `WrangleStats` dataclass. It composes M3 (Pandas) + M5 (idioms); it
  does not import `measure.py`. The acceptance gate is `exercises/module6/smoke.py` (pytest: row
  accounting + Parquet round-trip with `pandas.api.types` predicate dtype checks + a negative case that a
  malformed corpus raises). It ships `exercises/module6/outputs/skill-data-wrangling.md`. Before any M6
  exercise: open `wrangle.py`, read which stages exist, and add the next one to the locked structure; the
  sample corpus is `exercises/module6/sample_corpus.jsonl` (built in the L1 exercise).

  Later modules have their own throughline artifacts (the M7 eval engine, the M8 exam script). The same
  rule applies: find the artifact, read it, then continue the build.

## How to Coach

- Let the learner drive. Move one step at a time, surface the decision, and let them make the call.
- Explain the *why* behind each move: the cost it exposes, the idiom it establishes, the screen it
  prepares for. Not just the keystrokes.
- Never dump the full answer. A stub, a function signature, a failing test that points the way: that
  is the help. The learner writes the body.
- Ask before any large rewrite or before touching files outside the exercise's scope.
- When they are stuck, narrow the question; do not widen the solution.

## The Artifact Contract

Every completed exercise leaves the throughline artifact in a state the next exercise can import and
extend. Do not leave it in a half-finished state. Do not move files. Do not rename entry points.
The next session starts where this one stopped; the artifact is the handshake.

Every completed exercise is the learner's own progression and a portfolio piece. The work has to be
theirs.
