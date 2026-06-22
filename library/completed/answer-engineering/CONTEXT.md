# CONTEXT — Answer Engineering (COMPLETED)

The career book. Where every other Scriptorium book builds the skills, this one teaches the reader
to demonstrate those skills under pressure: an internal framework for reasoning to a strong answer,
not a script to recite. It treats answer construction as an engineering discipline. It covers the
AI Engineer hiring loop in full — behavioral, technical, and AI/ML systems-design interviews — and
positions the Sans Python portfolio artifacts as the resume.

**COMPLETED 2026-06-21; all 8 modules shipped; relocated to `library/completed/answer-engineering`.**
`GATE-NAME-BOOK` cleared (title **Answer Engineering**, slug `answer-engineering`). M1 "The Framework" (overview + 2 lessons + 2 exercises)
installs the four-step Algorithm and seeds the prep-dossier throughline (`exercises/prep/` +
`check_prep.py`). M2 "The Algorithm in Detail" (overview + 4 lessons + 4 exercises) deepens each step on
the hard cases and grows the validator to v2 in place. M3 "Behavioral Interviews" (overview + 4 lessons +
4 exercises) is the behavioral example bank: each lesson reasons two worked examples to a STAR-L answer,
two examples reused toward different signals to demonstrate method-over-memorization; validator grown to
v3 in place. M5 "AI/ML Systems-Design Interviews" (overview + 4 lessons + 4 exercises) is the systems-design example
bank: SPIDER taught as the domain-specific construct motion, worked designs that reason from production
constraints (not reference architectures), and a finale with a weak-design audit + a "same prompt,
different stress" anti-memorization coda; validator grown to v4 in place (`--module 5`). **M5 was authored
before M4 (Ray-confirmed reorder):** the vault has rich systems-design ore but no live-coding-screen ore,
so M4 is deferred until its ore is sourced. M5 introduced the Haiku-fetch / Sonnet-author tier. All
authored conductor-direct, reviewed to STYLE + STANDARDS with MS-Learn citations verified live, built
clean (`mdbook build`), and shipped (`GATE-APPROVE-SHIP`, 2026-06-21). M6 "The Sans Python Portfolio as
Resume" (overview + 4 lessons + 4 exercises) opens Phase 3: walking an interviewer through a real artifact
as a decision tour (not a code reading), the four-beat defended decision, the same artifact narrated three
ways per role, and the written portfolio-narrative document + a weak-walkthrough audit; worked examples are
the real Sans Python portfolio artifacts; validator grown to v5 in place (`--module 6`). M7 "Live Practice and Calibration"
(overview + 4 lessons + 4 exercises) is the practice engine: deliberate reps run through the Algorithm and
self-scored, with the self-review rubric realized as code (`calibrate.py`, a calibration scorer with a
readiness verdict); first throughline artifact that scores rather than just checks completeness; validator
grown to v6 in place (`--module 7`). M8 "The Hiring Loop End-to-End" (overview + 4 lessons + 4 exercises)
is the capstone: it sequences the dossier across the five interview-loop stages and **grades it in code**
via `grade_dossier.py` (which composes `check_prep` + `calibrate`, exit 0 = READY); validator grown to v7
in place (`--module 8`). M4 "Technical Screens" (overview + 4 lessons + 4 exercises) was authored last and
resolved the deferral: the live-coding screen taught as the communication layer, worked tasks grounded in
the real Sans Python portfolio code (no fabrication), validator grown to v8 in place (`--module 4`, a
sibling gate). **The book is COMPLETE: all 8 modules shipped.** See
`build-log/answer-engineering/build-progress.md`.

## Ore (in the vault — not yet distilled)

- `vault/ai-system-design-guide` (`asdg`) — primary ore. Chapter `00-interview-prep/` (8 files,
  routed out of Sans Python's extraction as the "Ahab" interview block) contains the interview
  prep material this book supersedes with its framework framing. The systems-design interview
  material from chapters `11–17` (already distilled into `ingredients/source/module4/`) is
  supporting ore for the systems-design interview section.
- `vault/ai-system-design-guide` — `COURSES.md` and `GLOSSARY.md` reference files: curated
  course list and terminology, useful for the portfolio-narrative and prep appendix.
- Survey additional vault sources at process-ore time via `vault/MANIFEST.md`.

## Dual-use

Written to be **read by a human learner and ingested by an LLM** — dense, linked, plain markdown.
A candidate and a coaching LLM are both valid consumers; the reasoning-framework structure
makes it especially legible to both.

## Load / don't-load

- **Load:** this folder's `README.md` and `draft/`, `vault/ai-system-design-guide` chapter `00`
  via `vault/MANIFEST.md`, `ingredients/source/module4/asdg-*`, `platform/conventions` (AUTHORING +
  STANDARDS + STYLE), `platform/pipeline`.
- **Do NOT load:** the shipped book, other planned books.

## Handoff & gates

`GATE-NAME-BOOK` cleared; **all 8 modules (M1–M8) shipped. The book is COMPLETE.** No authoring remains.
Remaining options for Ray: (a) relocate the book to `library/completed/answer-engineering` (a cataloguing
move, no gate; run `route-lint` after); (b) `GATE-PUBLISH` for a public copy. See `platform/HUMAN-GATES.md`.
