# Answer Engineering — Build Progress

Per-stage authoring status. One row per module.

| Module | Title | Status | Shipped | Notes |
|--------|-------|--------|---------|-------|
| M1 | The Framework | ✅ Shipped | 2026-06-21 | Overview + 2 lessons (decompose-the-question, construct-the-answer) + 2 exercises. Installs the four-step Algorithm (decompose, identify the signal, construct, stress-test) and the four AI-Eng signal categories. Seeds the **prep dossier** throughline (`exercises/prep/`): `decomposition-log` + `answers-log` + the `check_prep.py` validator (with pytest, negative case tested); ships `exercises/CLAUDE.md`. First module of this book, so it also distilled the book's first ingredient from raw `asdg` ore (`ingredients/source/answer-engineering/`) and stood up the mdBook scaffold. Plan: `m1/PLAN.md`. |
| M2 | The Algorithm in Detail | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (the-question-behind-the-question, reading-the-room, thinking-out-loud, the-weak-answer-audit) + 4 exercises. Deepens each Algorithm step on the hard cases: latent/level-dependent decomposition, real-time signal reading, live delivery + recovery, the systematic weak-answer audit at a senior-vs-staff bar. **Extends the prep dossier and grows `check_prep.py` to v2 in place** (`--module` flag; M1 checks intact; 24/24 tests). Distilled a delivery/leveling ingredient from the remaining `asdg` ore. Plan: `m2/PLAN.md`. |
| M3 | Behavioral Interviews | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (ownership-stories, conflict-stories, failure-stories, influence-stories) + 4 exercises. The behavioral example bank: each lesson runs two worked examples that show the Algorithm reasoning to a STAR-L answer (not canned scripts), names the category-specific signal + failure modes, and ends in a weak-answer audit. Examples 5 and 6 are intentionally reused across two lessons, constructed toward **different** signals, to demonstrate the book's thesis (method transfers, words do not). **Extends the prep dossier and grows `check_prep.py` to v3 in place** (`--module 3` gates the four behavioral-bank artifacts: STAR-L category, fields, audit verdict; M1/M2 checks intact; 31/31 tests). Plan: `m3/PLAN.md`. |
| M5 | AI/ML Systems-Design Interviews | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (reading-the-design-prompt, justify-every-box, production-reasoning-as-the-differentiator, the-full-design-under-pressure) + 4 exercises. The systems-design example bank: SPIDER is taught as the domain-specific "construct" motion (the analogue of M3's STAR-L), the worked designs reason from production constraints rather than reproduce reference architectures, and the finale lesson runs one full timed design + a weak-design audit + the "same prompt, different stress" coda that makes the anti-memorization thesis concrete. **Authored M5 before M4 (Ray-confirmed reorder)** because the vault has abundant systems-design ore but no live-coding-screen ore; M4 deferred until its ore is sourced. **Grows `check_prep.py` to v4 in place** (`--module 5` gates the systems-design log: SPIDER scope, justified design, the four production-reasoning pillars, audit verdict; M1-3 byte-identical; 40/40 tests). Plan: `m5/PLAN.md`. |
| M4 | Technical Screens | ⏸️ Deferred | — | Reordered after M5. The vault interview-prep chapter has no live-coding-screen worked examples; building M4 as scoped would require fabricating coding problems, which the no-fabrication rule forbids. Deferred until its ore is sourced (likely reframed around the real Sans Python portfolio code). |
| M6 | The Sans Python Portfolio as Resume | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (the-artifact-walkthrough, foreground-the-decisions, tailoring-to-the-role, the-portfolio-narrative-document) + 4 exercises. **Phase 3 opens.** Teaches the reader to walk an interviewer through a real artifact as a decision tour (the reasoning), not a code reading: the 60-second overview + the four-beat defended decision (decision / alternative / tradeoff / failure mode guarded), the same artifact narrated three ways for three role types (the anti-memorization thesis on the portfolio), and the written portfolio-narrative document + a 7-category weak-walkthrough audit. Worked examples are the REAL Sans Python portfolio artifacts (terminal coding agent; production RAG chatbot). **Grows `check_prep.py` to v5 in place** (`--module 6` gates the portfolio-narrative: artifact, overview, key decisions, tradeoffs, failure modes, role tailoring, audit verdict; M1-3+M5 byte-identical; 49/49 tests). Plan: `m6/PLAN.md`. |
| M7 | Live Practice and Calibration | ✅ Shipped | 2026-06-21 | Overview + 4 lessons (deliberate-practice-not-rote, the-self-review-rubric, reading-your-calibration, simulating-the-room) + 4 exercises. The practice engine: a rep is a fresh question run through the full Algorithm and self-scored on the four steps; **the self-review rubric is CODE** (`calibrate.py`, conductor-built + `--selftest`-tested), which reads the deliberate-practice log and prints a calibration scorecard (per-category reps, per-step strong/partial/weak distribution, weakest step, readiness verdict, exit 0 = READY). First throughline artifact that **scores** rather than just checks completeness. **Grows `check_prep.py` to v6 in place** (`--module 7` gates the deliberate-practice log: 5+ reps across all five categories, valid step scores, no placeholders; prior modules byte-identical; 61/61 tests). The literal realization of "code, don't write; good writing is one big schema handoff." Plan: `m7/PLAN.md`. |
| M8 | The Hiring Loop End-to-End | ✅ Shipped | 2026-06-21 | Phase 3 capstone; the book is content-complete (7 of 8 modules; M4 deferred). Overview + 4 lessons (sequencing-the-preparation, the-stages-of-the-loop, grading-your-dossier, closing-the-loop) + 4 exercises. Sequences the whole prep dossier across the five interview-loop stages (recruiter-screen, hiring-manager, systems-design-round, portfolio-deep-dive, panel) and **grades the dossier in code**: the capstone artifact `grade_dossier.py` composes `check_prep` (completeness) + `calibrate` (practice readiness), maps the dossier onto the stages, prints a per-stage readiness report, exit 0 = READY. The honest coding-screen gap (M4) is named, not papered over. **Grows `check_prep.py` to v7 in place** (`--module 8` gates `loop-plan.md`: five `### Stage` entries with Dossier pieces / Readiness / Plan, stage-name + readiness-value validation; prior modules byte-identical; 75/75 tests). The Just Python M8 pattern (a runnable grader chaining the prior artifacts) applied to the career dossier. Plan: `m8/PLAN.md`. |

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

M5 opened the systems-design half of Phase 2 and was the first module to use the **Haiku-fetch tier
feeding Sonnet authors** (Ray's directive: "finish the job; offload to sonnets, throw in haikus for
fetching"). `GATE-LOCK-PLAN` cleared via Ray's "LOCK IT"; the M5-before-M4 reorder was Ray's call after
an ore survey (a read-only Haiku) found the vault rich in systems-design ore (SPIDER + 9 whiteboard
exercises + the pitfalls + ch.11-17) but empty of live-coding-screen worked examples. Round 1, parallel:
a Haiku surveyed asdg ch.11-14 for production-reasoning anchors while a Sonnet distilled the
interview-prep ore into `asdg-systems-design.md` (SPIDER + the 9 designs + 20+ weak-design red flags +
the design-prompt taxonomy); the conductor (Opus) then verified the MS-Learn anchors live and appended
the production-reasoning section, and authored `00-overview` + SUMMARY. Round 2, parallel: four Sonnet
lesson-writers + one Sonnet exercises/validator worker, each briefed cold with the three contracts + the
M2/M3 voice exemplars + the ingredient. VERIFY (conductor): clean, zero fixes — no em-dashes, no
fourth-wall leaks, no fabrication, the anti-reference-architecture guardrail held in every worked design,
and the two MS-Learn citations (Azure Well-Architected AI design principles; Azure AI Foundry
observability) were **fetched live and confirmed to match their claims** (the "Trade-off: Cost
Optimization and Performance Efficiency" framing; the offline-gate + sampled-online + scheduled-drift
eval pattern); no other URLs invented. BUILD/TEST: `mdbook build` clean; `check_prep.py` v4 with 40/40
pytest (M1-3 backward-compat + the M5 systems-design log + the `--module 5` gate); `check_prep.py
--module 5` exits 1 cleanly against an empty dossier. `GATE-APPROVE-SHIP` cleared via Ray's standing
"finish the job" directive (the same directive under which the concurrent Local Metal session shipped per
module); committed and pushed as it landed.

M6 opened Phase 3 (the portfolio layer) and ran on the Haiku-fetch / Sonnet-author tier. `GATE-LOCK-PLAN`
self-cleared under the standing directive ("you're doing fine keep it up" = go for Phase 3). Round 1: a
read-only Haiku surveyed the two featured Sans Python portfolio artifacts (terminal coding agent +
production RAG chatbot) for their decisions/tradeoffs/failure-modes; the conductor (Opus) wrote the
`portfolio-artifact-catalog.md` ingredient from that survey and authored `00-overview` + SUMMARY. Round 2:
four Sonnet lesson-writers + one Sonnet exercises/validator worker, parallel. VERIFY (conductor): clean,
zero fixes — no em-dashes, no fourth-wall leaks, no fabrication, the walkthrough-is-reasoning-not-code
guardrail held in every lesson, MS-Learn correctly not forced (portfolio narration is interview craft).
BUILD/TEST: `mdbook build` clean; `check_prep.py` v5 with 49/49 pytest (M1-3+M5 backward-compat + the M6
portfolio-narrative + the `--module 6` gate); `check_prep.py --module 6` exits 1 cleanly against an empty
dossier. This module marks Ray's sharpened mandate: **code, don't write; good writing is one big schema
handoff** — the ingredient is the schema, the Sonnet authoring is the handoff, and the M7/M8 throughline
artifacts ahead are scorers in code, not essays. `GATE-APPROVE-SHIP` cleared under the standing directive;
committed and pushed as it landed.

M7 made "code, don't write" literal: the self-review rubric IS a runnable scorer, `calibrate.py`
(conductor-built, stdlib-only, `--selftest`-tested; reads the deliberate-practice log and prints a
calibration scorecard with a readiness verdict and exit 0 = READY). `GATE-LOCK-PLAN` self-cleared. The
conductor (Opus) built + tested `calibrate.py` and captured its verbatim scorecard, then the four Sonnet
lesson-writers quoted that real interface and output (no code/prose drift); a fifth Sonnet extended
`check_prep.py` to v6 (the `--module 7` completeness gate over the practice log: 5+ reps across all five
categories, valid step scores) and never touched `calibrate.py`. VERIFY (conductor): clean, zero fixes —
no em-dashes, no fourth-wall leaks, the scorecard quoted in L3 matches the tool byte-for-byte, the rubric
scale in L2 is grounded in the four Algorithm steps, no MS-Learn forced. BUILD/TEST: `mdbook build` clean;
`check_prep.py` v6 with 61/61 pytest; `calibrate.py --selftest` PASS; both `--module 7` and `calibrate.py`
exit cleanly against an empty dossier. Note (Ray, mid-M7): the `ponytail` lean-code plugin now defaults on
for Opus + "no excessive coding on your part, that's what the sonnets are for" — so M8's grader will be
Sonnet-built to a conductor-specified contract, Opus reviewing. `GATE-APPROVE-SHIP` cleared under the
standing directive; committed and pushed as it landed.

M8 closed the book (content-complete: 7 of 8 modules; M4 deferred). The capstone is a grader:
`grade_dossier.py` composes `check_prep` + `calibrate`, maps the dossier onto the five interview-loop
stages (the `hiring-loop-map.md` schema), and returns a per-stage readiness report (exit 0 = READY) — the
Just Python M8 pattern applied to the career dossier. Per the ponytail directive the conductor (Opus)
SPECCED the grader and a Sonnet BUILT + `--selftest`-tested it (composition over new code: it imports and
reuses the prior validators rather than reimplementing them); Opus reviewed. The four lessons + the v7
validator extension (`--module 8` over `loop-plan.md`) were the parallel Sonnet fleet. The fleet first hit
the daily session limit (the M8 lessons + validator did not land that turn); on resume after Ray's go the
five Round-2 Sonnets completed. VERIFY (conductor): caught + fixed one fabrication — L4 ("closing-the-loop")
invented a "CIRCLE scaffolding" framework the book never taught; corrected to the real **STAR-L** (M3). No
other fixes: no em-dashes, no fourth-wall leaks, the grader output quoted in L3 matches the tool, the
coding-screen gap named honestly. BUILD/TEST: `mdbook build` clean; `check_prep.py` v7 with 75/75 pytest;
`calibrate.py --selftest` + `grade_dossier.py --selftest` both PASS; `check_prep.py --module 8` and
`grade_dossier.py` exit cleanly against an empty dossier. `GATE-APPROVE-SHIP` cleared under the standing
directive; committed and pushed as it landed. **Answer Engineering is content-complete.**
