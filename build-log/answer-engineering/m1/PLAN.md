# Module 1 — The Framework — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` cleared via Ray's "GO FOR BROKE").** First
authoring stage for Answer Engineering (graduated to `library/in-progress/answer-engineering`
2026-06-21). M1 turns the blueprint's Phase 1 opener + the `asdg` interview ore into finished mdBook
lessons + Claude Code exercises, in the locked Style Contract voice, at the STANDARDS difficulty bar,
under AUTHOR → VERIFY → BUILD/TEST → SHIP. Scope is the already-vetted draft in `draft/` (low
wasted-work risk, which is why the lock is cheap here); the authoring upgrades that draft, grounds it
in the real ore, and brings it to ship quality. Stops at `GATE-APPROVE-SHIP` before folding into `src/`.

## The stage in one line

M1 installs the Algorithm: a four-step internal process (decompose the question, identify the signal,
construct the answer, stress-test it) that lets a candidate answer interview questions they have never
seen. Seam: a Production AI Engineer has built the Sans Python portfolio but can lose the offer by
explaining it badly under pressure; M1 is the first move from "built it" to "can prove it cold."

## Settled decisions (from the blueprint + the contracts + the ore)

1. **Stage = module.** Same module-as-stage ICM shape as Sans Python, Just Python, and Local Metal:
   M1 reads its sources, writes `build-log/answer-engineering/m1/output/{author,verify,ship}/`, and
   hands the locked voice/exemplars forward to M2.
2. **Held to the three contracts.** AUTHORING (process + three-source rule), `STANDARDS.md`
   (difficulty ramp + strong-project rubric + the artifact contract), `STYLE.md` (voice). Every
   worker brief carries all three plus a canonical voice exemplar (Just Python's `src/README.md` +
   `module1/why-numpy-exists.md`, until Answer Engineering locks its own) — cold workers do not
   inherit them.
3. **The blueprint's Phase-1 split is M1's spine.** M1 introduces the Algorithm and gives the reader
   the first working pass through it as a decompose/construct pair. M2 ("The Algorithm in Detail")
   deepens each of the four steps; M1 does not pre-empt that depth.
4. **The career artifact is a document, not code.** Like Local Metal's hardware module, the checkable
   done-when is a structured-document validator, not pytest. The throughline is the reader's prep
   dossier; M1 seeds it and ships the validator that gates it.
5. **Ground the framework in named, real frameworks.** The draft currently leans on generic "STAR"
   and invented examples. M1 grounds the construction step in the ore's actual, named frameworks
   (SPIDER, STAR-L, the tradeoff and debugging frames) and draws every worked example from the real
   `asdg` question bank — no fabricated questions or transcripts (the Just Python M2/M3 fix).

## Ore processing (the first move — author against ingredients, not raw vault)

The `asdg` interview-prep chapter (`vault/ai-system-design-guide/00-interview-prep/`, 8 files) is raw
ore, never distilled. Root CLAUDE.md forbids authoring directly against `vault/`. So M1 opens with a
distillation pass that produces the book's first ingredient, reusable by M2–M8's example banks:

- `ingredients/source/answer-engineering/asdg-interview-frameworks.md` — the five named frameworks
  (SPIDER, ETA, tradeoff, debugging, STAR-L) reframed under the Algorithm, plus the pitfalls catalog.
- `ingredients/source/answer-engineering/asdg-question-taxonomy.md` — the question bank distilled to a
  signal taxonomy (the four AI-Eng signal categories) with representative real questions per category,
  and the behavioral STAR-L worked examples.
- `ingredients/dossiers/answer-engineering-m1.md` — the keep/cut/frame ruling for M1: what of the ore
  belongs in M1 vs. held for M3 (behavioral bank) / M5 (systems-design) / M6 (portfolio narrative).

This is a Tier-2 narrowing of AUTHORING's `ingredients/source/moduleN/` convention: the book scopes
its ingredient under `ingredients/source/answer-engineering/` (book-named, not Sans-Python-module-
numbered) because its ore is book-specific. Logged here so it is intentional, not drift.

## Locked M1 split (overview + 2 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind | Source slice |
|---|---------------|----------|------|--------------|
| 0 | `00-overview` | Memorization fails because real questions arrive in forms you never rehearsed; the Algorithm is the transferable alternative. Here is the four-step loop and the arc of the module. | concept | blueprint M1 + `03-common-pitfalls` |
| 1 | `decompose-the-question` | Every question is an instrument for a hiring hypothesis; separate what it says from what it is for, assign it to one of four signal categories, name the primary hypothesis. | concept | `asdg` question taxonomy + `01-question-bank` + `03-common-pitfalls` |
| 2 | `construct-the-answer` | Build the answer backward from the hypothesis: specific enough that a weak candidate could not give it, structured so the interviewer can follow, complete enough to close the loop; then stress-test. | concept | `asdg-interview-frameworks` (SPIDER/STAR-L) + `05-behavioral` worked examples |

Each lesson ends in a Claude Code exercise (`exercises/module1/<slug>/README.md`) with a
machine-checkable done-when (the prep-dossier validator, below).

## The compounding throughline (STANDARDS Part 3)

M1 seeds the reader's **prep dossier** — the portfolio artifact this book builds, the career analogue
of Sans Python's code repo:

- `decomposition-log.md` — ten real questions decomposed (literal parse, signal category, one-sentence
  hypothesis) plus a calibration section. (Exercise 1.)
- `answers-log.md` — five full Algorithm runs (all four steps) with each answer self-scored on
  specificity / structure / completeness. (Exercise 2.)
- `check_prep.py` — the validator: asserts both logs exist and are complete (all ten decompositions
  with all three parts; five answers with four steps and three scores; no placeholder text). Exit 0 is
  the done-when. This is the document analogue of Just Python's `smoke.py` and Local Metal's
  `check_hardware.py`, and the reusable checker M3 (behavioral bank), M5 (systems-design logs), M6
  (portfolio narrative) extend. M8 composes the full dossier and grades it against the rubric in code.
- `exercises/CLAUDE.md` — the coaching contract: read the lesson, find the prep dossier and read its
  current state, coach without solving (do not write the reader's answers for them).

## Sources (three-source rule)

1. **Distilled ingredient:** the new `ingredients/source/answer-engineering/` files + the M1 dossier
   (produced by the ore-distillation pass above).
2. **Authoritative external grounding — Microsoft Learn via the connector.** The AI/ML systems-design
   decomposition move (surface production constraints before designing) grounds on the Well-Architected
   Framework for AI workloads / Azure AI Foundry. Workers USE the connector and cite a real, verified
   URL inline — no bare `[MS-Learn: …]` markers left unresolved, no citations from memory (the JP
   M2/M3 fix). The behavioral/decomposition material is interview craft, not an MS-Learn domain;
   there it grounds on the `asdg` ore and is not forced to carry an MS-Learn citation.
3. **Editorial seam framing** — "why does a Production AI Engineer need this?" in every lead.

## The fleet plan (orchestration)

Per `platform/ORCHESTRATION.md` and the Just Python A/B result (handler tier only for concurrent
gates or multiple clusters, not by worker count): **conductor-direct, no handler tier.** One small
cluster.

- **Round 1 (critical path):** one ore-distillation Sonnet worker produces the two ingredient files +
  the M1 dossier. In parallel, the conductor scaffolds the book (`book.toml`, `theme/` copied from
  Just Python, `src/README.md`, `src/SUMMARY.md`, `src/module1/00-overview.md`, `exercises/README.md`,
  `exercises/CLAUDE.md`).
- **Round 2 (parallel):** Lesson-1 worker, Lesson-2 worker, and an exercises+validator worker, each
  briefed with all three contracts + the voice exemplar + the distilled ingredient + the connector
  instruction.
- **Conductor** authors `00-overview`, integrates `SUMMARY.md`, and runs the Zinsser + STYLE +
  STANDARDS review gate on every draft before it lands. No worker draft ships unreviewed.

## Locked decisions (GATE-LOCK-PLAN, 2026-06-21)

1. **Granularity — LOCKED at overview + 2 lessons.** Decompose and Construct are distinct,
   load-bearing ideas; the four Algorithm steps split 2+2 across them. Deeper per-step treatment is
   M2's job, not a reason to inflate M1.
2. **Career artifact done-when — LOCKED** to the `check_prep.py` document validator (structured-log
   completeness), mirroring Local Metal's `check_hardware.py`. No code-execution gate exists for an
   interview-craft module; completeness + no-placeholders is the machine-checkable bar.
3. **Ore distillation to a book-scoped ingredient — LOCKED.** Author against
   `ingredients/source/answer-engineering/`, not raw `vault/`. The pass runs as M1's first step and
   serves every later example-bank module.
4. **MS-Learn applied where it fits, not forced — LOCKED.** The connector grounds the systems-design
   decomposition move; the behavioral/decomposition craft grounds on the `asdg` ore. Forcing MS-Learn
   onto interview-craft prose is the fabricated-citation risk fixed in JP.

On lock: the fleet distills the ore + scaffolds the book + authors M1, VERIFY gates it (voice + claims
+ grounding + dossier validator runs), BUILD/TEST runs `mdbook build` + `check_prep.py` against a
sample dossier, and the stage stops at `GATE-APPROVE-SHIP` before folding into `src/` and `exercises/`.
