# The Standards Contract — Difficulty and Project Strength

The bar every Scriptorium book is held to. `STYLE.md` governs how a lesson *reads*; this file governs
how *hard* it is and how *strong* its artifact is. Together they are the quality law: a cold authoring
fleet reads both, and the conductor reviews every draft against both before it lands.

**Read this with `AUTHORING.md` and `STYLE.md` before authoring or reviewing a lesson.** Where this
contract and a draft disagree, the contract wins.

## Why This Exists

The infrastructure, the ore, and the orchestration are solved. The remaining risk in producing the
book lineup is *drift*: a fleet of cold workers, each knowing only its brief, will re-invent the rigor
and the books will diverge in difficulty and project quality. The rubric that makes Sans Python strong
lived only inside its own exercises. This lifts it out, book-agnostic, so any book inherits the same bar
without the conductor hand-checking each one. It is the central fix for the "cold workers do not inherit
the contract" crack in `platform/ORCHESTRATION.md`.

## Part 1 — The Difficulty Bar

### Difficulty Comes From Real Problems, Not Artificial Complexity

The curriculum's own complexity ladder applies to its design: add difficulty only when a real task
demands it; never manufacture it. A lesson is hard because the *problem* is real (a corpus that will not
fit in memory, an eval that must be sliced, a merge that must be human-approved), not because the prose
is dense or the API surface is wide. The test for "hard enough" is the hiring screen: would shipping
this artifact survive a take-home or a live interview? If not, the lesson is a toy and fails the bar.

### The Ramp (Every Book Follows This Shape)

Books mirror the eight-module Sans Python shape; the difficulty ramps and never doubles back:

| Phase | Modules (typical) | What the reader does | Difficulty floor |
|-------|-------------------|----------------------|------------------|
| **Foundations** | 1–2 | Build the mental model; first single-file artifacts | A runnable script, one idea, one test |
| **Core build** | 3–5 | Ship real components; the throughline artifact grows; threads enter in sequence | Multi-part artifact, framed, tested |
| **Composition** | 6–7 | Portfolio artifacts that *reuse* earlier work, not rebuild it | A strong project (Part 2), reuse is real |
| **Operate / Exam** | 8 | Integrate and judge against a rubric expressed in code | Reuses the composition; graded by code, not opinion |

Two ramp rules are non-negotiable:

- **No forward dependencies.** A lesson may only rely on what an earlier lesson established. Earlier
  modules are prerequisites; the threads (a second language, eval, safety, the data layer) only make
  sense in order.
- **One idea per lesson** (STYLE §3). Difficulty accrues across lessons, not by cramming one.

### The Per-Lesson Difficulty Self-Check

Before a lesson ships, the reviewer answers all three:

1. **Real artifact?** A build lesson ships runnable code with a real entry point, not a notebook or a
   snippet. A concept lesson ends in a concrete thing to run, inspect, or measure.
2. **Earned, in-ramp difficulty?** It depends only on prior lessons and pulls its weight; it is neither
   a toy nor a leap past its rung.
3. **Screen-survivable?** The work would hold up in a hiring screen for the book's target archetype
   (the Production AI Engineer).

A "no" on any of the three sends the lesson back.

## Part 2 — The Project-Strength Rubric

Every build lesson and every artifact is held to the **strong-project checklist**. This is the Sans
Python `module7`/`module8` bar, lifted and made book-agnostic.

- [ ] **Real entry point, not a notebook.** It runs with one command (`python smoke.py`, `pytest`, a
      documented invocation).
- [ ] **README frames the business problem before the code.** Why this artifact exists, for the target
      archetype, comes first.
- [ ] **A concrete acceptance gate.** The done-when is verifiable by a machine: a test passes, an
      endpoint responds, a metric prints, an exit code is 0. Never "looks good."
- [ ] **Tests, and a BUILD→TEST gate.** The smoke path is deterministic and offline where possible
      (standard library plus the minimum deps); a live model or service is opt-in behind a seam.
- [ ] **Versioned, clean layout; no secrets.** No committed keys; `.env` is opt-in; the tree is legible.
- [ ] **Ships a skill artifact** (`outputs/skill-<name>.md`): the reader's write-up of what they built
      and learned. This is the portfolio surface and the progress signal (`progression/`).
- [ ] **The negative case is tested.** A deficient run fails the gate it offends (an unapproved action,
      a tripped guard, a thin spec). Strength is proven by what it refuses, not only what it ships.

### The Capstone Rubric (Generalized)

Each book's final exam reuses the composition artifact and judges it against an **acceptance rubric of
N criteria, expressed in two forms that must match: a rubric checker in code, and the same rubric in the
guide prose.** Sans Python's seven (RUNS, EVAL-GATED, AUDITED, BUDGET-BOUNDED, HITL-GOVERNED,
PROBLEM-FRAMED, TESTED+VERSIONED) are the template. A book keeps the criteria that fit its domain and
drops the ones that do not (a data book has no HITL-merge criterion; it has a schema-validation one).
The invariant is the shape: **grade by code, not opinion; the same rubric in prose and in a checker; a
deliberately deficient run must fail.**

## Part 3 — Compounding and the Artifact Contract

Two requirements make the curriculum teach the way an AI engineer actually works: progress is read from
artifacts, and projects chain.

### Every Book Has a Compounding Throughline

- Name the throughline artifact(s) in the book's plan. Later artifacts **import and extend** earlier
  ones; the reuse must be real, not restated. The capstone **composes** the prior artifacts (imports
  them off disk), it does not rebuild them. Sans Python is the reference: the M6 coding agent becomes an
  M7 fleet node, and M8 operates the M7 fleet via `fleet_adapter.py`.
- **Progress is artifact-measured.** A module is "done" when its artifacts exist and pass their gates,
  not when a box is checked (`progression/README.md`). Author the artifacts so this is true.

### Every Book Ships the Artifact-Reading Coaching Contract

Every book includes an `exercises/CLAUDE.md` that instructs the coaching agent, at minimum, to:

1. Read the lesson, then the exercise brief, before touching code.
2. **Find the throughline artifact and read its current state before adding to it. It is continuing a
   build, not starting one.**
3. Coach, do not solve: let the learner drive; the help is a stub, a signature, a failing test, never
   the finished answer.

This is a required output of authoring, not an optional nicety. A book without it does not graduate to
ship.

## How This Is Enforced

- **The fleet brief carries this contract.** A cold worker is given STANDARDS (or pointed at it) in
  every brief, alongside STYLE and the canonical example. Workers do not inherit it by being in the repo.
- **The conductor reviews against the rubric at the gate.** No artifact ships unreviewed against Part 2;
  no lesson ships unchecked against Part 1's self-check.
- **`route-lint` guards the structural edges** (planned: assert every book ships an `exercises/CLAUDE.md`
  and that a capstone has a rubric checker). The taste calls stay with the conductor and the human gates.

## Where This Sits

`STYLE.md` is the voice law (Tier-1). This Standards Contract is its difficulty-and-strength counterpart;
it is currently a Tier-2 convention that **narrows, never loosens**, the parent contracts. Promoting it
to the Tier-1 policy set in `CLAUDE.md` is a precedence-rule change and is the human's call. Relationship
to the rest: `AUTHORING.md` is the process, `PALETTES.md` is the color signature, `progression/` is how
progress is read; this file is how hard and how strong.
