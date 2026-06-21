# Module 5 — Python Idioms at Interview Speed — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared — Ray locked as drafted: all 4 decisions
accepted — 4 content lessons, self-contained exercises, made-with-ml + connector ore, connector at author
time).** **SHIPPED 2026-06-21 (`GATE-APPROVE-SHIP` cleared).** Fifth authoring stage for Just Python.
M1–M4 shipped.
M5 turns the blueprint's fifth module into finished mdBook lessons + Claude Code exercises, in the locked
Style Contract voice, at the STANDARDS difficulty bar, under AUTHOR → VERIFY → BUILD/TEST → SHIP. Do not
author until Ray locks.

## The stage in one line

M1–M4 made the reader fast with data; M5 makes them fluent in the Python a screen actually tests. The five
idioms a take-home or a live round assumes you know cold are comprehensions, generators, decorators, type
hints, and dataclasses. Seam: these are not trivia. They are the difference between code that reads like an
engineer wrote it and code that reads like a beginner, and a reviewer judges that in the first ten lines.

## Settled decisions (from the blueprint + the contracts)

1. **Stage = module.** M5 reads its sources, writes `output/author|verify|ship/`, and hands its locked
   exemplars forward to M6 (the first portfolio artifact).
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md` (difficulty ramp
   + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every worker brief carries all three
   plus the M1–M4 exemplar lessons.
3. **The ore is thin here, and that is expected.** Unlike M1–M4, there is **no reference-grade docs subtree**
   in the vault for Python-language idioms (no `python-docs`). These are core language features the drafters
   know well; the three-source rule is satisfied by **applied grounding**, not a docs subtree: the ingredient
   is real code that *uses* the idiom (made-with-ml's `config.py` / `data.py` / `utils.py`, plus the reader's
   own M1–M4 artifacts), Microsoft Learn supplies the production pattern (queried at author time), and the
   seam framing is the hiring-screen lens. This makes the **MS-Learn-connector-at-author-time rule
   load-bearing for M5** more than any prior module.
4. **De-dup against M1–M4.** M1–M4 used these idioms in passing (comprehensions to build test data, type
   hints on signatures, the `@dataclass`-shaped dicts in `measure.py`). M5 makes each idiom **the subject**,
   names the screen it prepares for, and shows the idiomatic form against the beginner form. It does not
   re-teach NumPy/Pandas.
5. **M5 is the Composition rung's on-ramp (STANDARDS Part 1).** Four build/concept lessons, each runnable with
   a machine-checkable done-when; the idioms are the polish the reader applies to the M6 portfolio artifact.

## Proposed M5 split (5 lessons, one idea each)

Comprehensions and generators are paired (a generator expression is a lazy comprehension; the eager-vs-lazy
contrast is one idea). Type hints and dataclasses stay separate (each is interview-meaty on its own).

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | M1–M4 made you fast; M5 makes you fluent. The five idioms a screen assumes: comprehensions, generators, decorators, type hints, dataclasses. | concept | conductor-integrated; frames the four below |
| 1 | `comprehensions-and-generators` | A comprehension builds the whole sequence eagerly; a generator yields one item at a time and never holds the full result, so it streams a corpus that would not fit in memory. Same syntax, opposite memory profile. | build | made-with-ml `data.py` (dataset iteration / label maps); MS Learn (Python iteration) |
| 2 | `decorators` | A decorator wraps a function to add behavior without touching its body; `functools.wraps` keeps the identity intact. You build `@timed`, the production-grade version of the manual timing you have done since M1. | build | made-with-ml `utils.py` (helper/wrapper patterns); MS Learn |
| 3 | `type-hints` | Type hints are a contract the reader and the tooling both read; `list[float]`, `Optional`, `Callable`, and `Protocol` make a signature self-documenting and `mypy`-checkable, which is exactly what a code reviewer scans for. | concept/build | made-with-ml signatures (typed throughout); MS Learn (typing) |
| 4 | `dataclasses` | `@dataclass` turns a bag-of-fields into a typed record with `__init__`, `__repr__`, and `==` for free; it replaces the dict-of-stuff that `measure.py` returns with a self-describing object. | build | made-with-ml `config.py` (config object pattern); MS Learn (dataclasses) |

Each lesson ends in a Claude Code exercise (`exercises/module5/<slug>/README.md`) with a concrete,
machine-checkable done-when (a printed result, a passing assertion, exit 0), matching the M1–M4 format.

## The compounding throughline (STANDARDS Part 3)

M5's idioms are the **polish the reader applies to the artifacts they already built and the M6 artifact they
are about to build.** Each lesson *demonstrates* the idiom by refactoring a snippet of the reader's own
`measure.py` / `vectorization_report.py` (the `@timed` decorator generalizes their timing; the `@dataclass`
replaces a dict return; type hints harden the signatures). To avoid the four-cold-workers-on-one-file
fragility seen in M4, the **exercises are self-contained** (each builds the idiom on a focused, deterministic
task), while the **lessons show the refactor in context**. The named forward link: these five idioms are the
ones M6's `wrangle.py` is written with from the first line. (Open Decision 2 settles how far to push the
direct-refactor.)

## Sources (three-source rule, non-negotiable)

1. **Ingredient:** real code that uses the idiom — made-with-ml `config.py` / `data.py` / `utils.py` (read
   the actual usage at author time) and the reader's own M1–M4 artifacts. No docs subtree exists; the applied
   code IS the ingredient.
2. **Microsoft Learn** via the connector — **workers query `microsoft_docs_search` / `microsoft_docs_fetch`
   while authoring** to ground each idiom's production pattern in a real page with a real URL and to fill gaps.
   This is load-bearing for M5 given the thin ore: no bare `[MS-Learn]` markers, no invented citations; if no
   real page backs a claim, state it plainly.
3. **Editorial seam framing** — "why does a screen test this?": the comprehension a reviewer expects instead
   of a `for`-append loop, the generator that streams a corpus, the decorator that adds timing without
   touching logic, the type hint that makes a signature reviewable, the dataclass that replaces a fragile dict.

## The fleet plan (conductor-direct, per the M2-vs-M3 finding)

Single ≤4-worker cluster, no concurrent gate: **conductor-direct, no handler tier** (`ORCHESTRATION.md`).

- **Conductor (Opus, this session):** locks the plan, briefs and dispatches 4 Sonnet workers directly,
  authors/integrates `00-overview`, and runs the Zinsser + STYLE + STANDARDS review gate on every draft.
- **Workers (Sonnet, parallel):** lessons 1–4, one worker per lesson, one writer per file. Each brief is
  self-contained: AUTHORING + STANDARDS + STYLE + the M1–M4 exemplars + the named made-with-ml applied file +
  **the instruction to use the live MS-Learn connector while authoring** (load-bearing here). Workers never
  touch `SUMMARY.md`, `measure.py`, or `exercises/CLAUDE.md` (conductor-folded shared state).

## Open decisions to pressure-test (lock these with Ray)

1. **Granularity.** 4 content lessons (proposed: pair comprehensions + generators) vs 5 content lessons (one
   per idiom). Recommendation: **4** — a generator expression is a lazy comprehension, so eager-vs-lazy is
   one idea; type hints and dataclasses each get a full lesson.
2. **Throughline depth.** Lessons *demonstrate* the idiom refactoring the reader's `measure.py` /
   `vectorization_report.py`, but exercises stay **self-contained** (vs each exercise directly editing the
   shared artifacts). Recommendation: **self-contained exercises** — M4 showed four cold workers on one shared
   file needs heavy conductor reconciliation; keep the refactor illustrative in the lesson, conflict-free in
   the exercise.
3. **Ore.** Confirm M5 grounds in made-with-ml applied code + the book's own artifacts + the MS-Learn
   connector (no docs subtree exists). Recommendation: **yes** — and lean hard on the connector, since the
   ore is thin.
4. **MS-Learn at author time.** Confirm worker briefs instruct active connector use (load-bearing for M5).
   Recommendation: **yes** (standing rule; matters most here).

On lock: the fleet authors M5, VERIFY gates it against STYLE + the live MS-Learn connector, BUILD/TEST runs
`mdbook build` + each exercise's smoke path, and the stage stops at `GATE-APPROVE-SHIP` before folding into
`src/`.
