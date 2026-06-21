# Answer Engineering — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Framework | ✅ Shipped | 2026-06-21 | Overview + 2 lessons (decompose-the-question, construct-the-answer) + 2 exercises. Installs the four-step Algorithm (decompose, identify the signal, construct, stress-test) and the four AI-Eng signal categories. Seeds the **prep dossier** throughline (`exercises/prep/`): `decomposition-log` + `answers-log` + the `check_prep.py` validator (with pytest, negative case tested); ships `exercises/CLAUDE.md`. First module of this book, so it also distilled the book's first ingredient from raw `asdg` ore (`ingredients/source/answer-engineering/`) and stood up the mdBook scaffold. Plan: `m1/PLAN.md`. |
| M2 | The Algorithm in Detail | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (the-question-behind-the-question, reading-the-room, thinking-out-loud, the-weak-answer-audit) + 4 exercises. Deepens each Algorithm step on the hard cases: latent/level-dependent decomposition, real-time signal reading, live delivery + recovery, the systematic weak-answer audit at a senior-vs-staff bar. **Extends the prep dossier and grows `check_prep.py` to v2 in place** (`--module` flag; M1 checks intact; 24/24 tests). Distilled a delivery/leveling ingredient from the remaining `asdg` ore. Plan: `m2/PLAN.md`. |
| M3 | Behavioral Interviews | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (ownership-stories, conflict-stories, failure-stories, influence-stories) + 4 exercises. The behavioral example bank: each lesson runs two worked examples that show the Algorithm reasoning to a STAR-L answer (not canned scripts), names the category-specific signal + failure modes, and ends in a weak-answer audit. Examples 5 and 6 are intentionally reused across two lessons, constructed toward **different** signals, to demonstrate the book's thesis (method transfers, words do not). **Extends the prep dossier and grows `check_prep.py` to v3 in place** (`--module 3` gates the four behavioral-bank artifacts: STAR-L category, fields, audit verdict; M1/M2 checks intact; 31/31 tests). Plan: `m3/PLAN.md`. |
| M4–M8 | per blueprint | ⬜ Not started | — | Phase 2 example banks (technical, systems-design) + Phase 3 portfolio layer. The prep dossier + `check_prep.py` extend through these; M8 composes and grades the full dossier. |

## Provenance

M1 graduated the book through `GATE-NAME-BOOK` (title "Answer Engineering" chosen 2026-06-21, was
"Anatomy of an Answer"/`interview-algorithm`) and ran the full AUTHOR → VERIFY → BUILD/TEST → SHIP
cycle. `GATE-LOCK-PLAN` was cleared by Ray's "GO FOR BROKE" against a pre-vetted draft (low wasted-work
risk); `GATE-APPROVE-SHIP` was presented and approved before the commit.

Authored **conductor-direct, no handler tier** (one small cluster, per the Just Python A/B result in
`platform/ORCHESTRATION.md`). Round 1: one Sonnet worker distilled the raw `asdg` interview ore
(`vault/ai-system-design-guide/00-interview-prep/`, 8 files) into the book's first reusable ingredient
(a signal taxonomy + frameworks catalog + M1 dossier), while the conductor scaffolded the book and
authored the intro + overview. Round 2: two Sonnet lesson-writers + one exercises/validator worker ran
in parallel, each briefed cold with STYLE + STANDARDS + AUTHORING + the voice exemplar + the ingredient
+ the connector instruction.

VERIFY (conductor): caught and fixed 5 fourth-wall leaks (the workshop term "the ore" and source-internal
"Example N" numbering leaking into reader-facing prose) and aligned a lesson handoff with the exercise's
real design. Every Microsoft Learn citation was **fetched live and confirmed to match its claim** (Azure
Well-Architected AI application-design + operations, Azure AI Foundry observability); zero fabricated
citations (the fix for the JP M2/M3 problem). Every worked example traces to the real `asdg` ore (no
invented questions or transcripts). BUILD/TEST: `mdbook build` clean; `check_prep.py` exits cleanly and
its pytest passes 9/9 (positive + negative cases).

The career-artifact pattern is established here: the proof is a **document** (the prep dossier) gated by
a structured-completeness validator, the same shape Local Metal uses for a hardware module where no
code-execution gate exists.

M2 stepped up to the house cadence (overview + 4 lessons + 4 exercises) and ran conductor-direct: one
Sonnet worker augmented the ore with the delivery/leveling material M1 left undistilled, then four
lesson-writers + one exercises/validator worker ran in parallel. The load-bearing decision (locked at
`GATE-LOCK-PLAN` via "go for it") was the **M1/M2 dedup**: M1 owns the loop on clean questions, M2 owns
one step per lesson at depth on the hard cases; every M2 lesson opens by naming what M1 established and
goes past it. M2 is the first module to **extend the throughline validator in place** rather than seed a
new one: `check_prep.py` grew to v2 with a `--module` flag, keeping the M1 checks byte-identical while
adding the four M2 dossier artifacts (24/24 tests, M1 backward-compat + M2 + the flag). VERIFY: zero
fourth-wall leaks this round (the M1 discipline held), L3's two MS-Learn citations re-confirmed live,
behavioral/leveling craft grounded on the ore with MS-Learn not forced. `mdbook build` clean.

M3 opened Phase 2 (the example banks) and ran conductor-direct. Round 1: one Sonnet worker distilled the
remaining `asdg` interview ore into the behavioral bank ingredient (`asdg-behavioral-bank.md`: all six
STAR-L worked examples + the four signal categories + the red-flags table + the question→category
mapping), every claim traced to `vault/ai-system-design-guide/00-interview-prep/`, no invented questions
or transcripts. Round 2: four Sonnet lesson-writers (one per category: ownership, conflict, failure,
influence) + one exercises/validator worker ran in parallel, each briefed cold with STYLE + STANDARDS +
AUTHORING + the voice exemplar + the ingredient. The load-bearing design decision (locked at
`GATE-LOCK-PLAN`): the lessons teach **reasoning, not memorization** — every worked example shows the
Algorithm constructing the answer, and examples 5 and 6 are deliberately built twice toward different
signals (ownership vs. failure; conflict vs. influence) with the contrast taught in-prose, turning the
anti-memorization thesis into a demonstration. VERIFY: clean — zero fourth-wall leaks, zero STYLE
kill-words, no comp figures, all six examples grounded on the ore. `check_prep.py` grew to v3 (the
`--module 3` artifacts) keeping M1/M2 byte-identical (31/31 tests). `mdbook build` clean;
`check_prep.py --module 3` exits 1 cleanly against an empty dossier. `GATE-APPROVE-SHIP` presented and
approved before this commit.
