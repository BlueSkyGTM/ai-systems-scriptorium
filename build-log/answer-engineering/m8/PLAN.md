# Module 8 — The Hiring Loop End-to-End — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` self-cleared under the standing directive).** Seventh
authoring stage and the book's capstone (M1-3 + M5 + M6 + M7 shipped). After M8 the book is
content-complete; M4 (Technical Screens) stays deferred until its ore is sourced.

## The stage in one line

Every prior module built one piece of the prep dossier and a tool to check it. M8 closes the loop: it
sequences the preparation across the real interview stages (recruiter screen, hiring-manager, systems-design
round, portfolio deep-dive, panel), and it composes and GRADES the whole dossier in code, producing a
single readiness-to-interview verdict. Seam: a Production AI Engineer has built every piece but has never
graded the whole, and walks into the loop without knowing if the preparation actually holds together.

## THE decision to lock: the capstone is a grader (code, don't write)

Per Ray's mandate, the capstone is not an essay about being ready; it is `grade_dossier.py`, a runnable
grader that **composes the existing tools** (`check_prep.py` for completeness, `calibrate.py` for practice
readiness) and maps the dossier artifacts onto the interview-loop stages, then grades each stage and the
whole. Composition over new code (the ponytail line): the grader imports and reuses the validators it
already has rather than reimplementing them. **Built by a Sonnet to a conductor-specified contract,
`--selftest`-tested; Opus specs + reviews** (the "no excessive coding by Opus" directive).

## The hiring-loop stage map (the schema)

`ingredients/source/answer-engineering/hiring-loop-map.md` holds the schema both the grader and the lessons
derive from: each loop stage, what it evaluates, and which dossier artifacts prepare it. The five stages
(M4's technical coding screen is noted as deferred, not a graded stage):

| Stage | Evaluates | Dossier artifacts that prepare it |
|---|---|---|
| recruiter-screen | a crisp self-pitch + one portfolio headline | portfolio-narrative; answers-log |
| hiring-manager | behavioral depth, ownership, influence | behavioral-bank; calibrate ownership + influence READY |
| systems-design-round | open-ended design under a clock | systems-design-log; calibrate systems-design READY |
| portfolio-deep-dive | walking your real artifact's decisions | portfolio-narrative |
| panel | mixed behavioral + portfolio, conflict/failure | behavioral-bank; portfolio-narrative; calibrate conflict + failure READY |

## The two code artifacts

1. **`exercises/prep/grade_dossier.py`** (NEW capstone, Sonnet-built to this contract): imports
   `check_prep` (run each module validator -> {artifact: passed}) and `calibrate` (compute {category:
   ready}); reads `loop-plan.md`; for each stage in the map, marks READY only when its required artifacts
   pass AND its required calibrate categories are READY AND the reader has a non-placeholder plan for that
   stage; prints a per-stage readiness report + an overall verdict; exit 0 only when every stage is READY.
   `python grade_dossier.py --selftest` tests the pure grading function on synthetic status dicts. Reuses,
   never reimplements, the prior tools.
2. **`exercises/prep/check_prep.py` -> v7** (exercises worker): `--module 8` gates `loop-plan.md` (one
   `### Stage <name>` entry per the five stages, each with `**Dossier pieces:**`, `**Readiness:**`
   (ready|gap), `**Plan:**`; no placeholders). Cumulative; prior modules byte-identical. `--module 4` stays
   open.

## Proposed M8 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The move |
|---|---------------|----------|
| 0 | `00-overview` | The loop end to end; the dossier you built is the preparation; the capstone grades it. |
| 1 | `sequencing-the-preparation` | The order to prepare in; map each dossier piece to where it pays off; what to build first if time is short. |
| 2 | `the-stages-of-the-loop` | Recruiter screen, hiring-manager, systems-design, portfolio deep-dive, panel: what each evaluates and how to prep it from your dossier (the stage map taught). |
| 3 | `grading-your-dossier` | Run `grade_dossier.py`: it composes check + calibration and grades each stage; read the report, close the gaps. |
| 4 | `closing-the-loop` | Day-of and after: working the loop, the readiness verdict, the offer stage; the book's close. |

## The compounding throughline (STANDARDS Part 3)

M8 is where the throughline pays off. It adds the reader's `loop-plan.md` (the per-stage prep plan) and the
`grade_dossier.py` capstone that COMPOSES every prior artifact (the six dossier logs/banks/docs + the two
tools) into one graded readiness verdict. `check_prep.py` v7 gates the loop plan; `grade_dossier.py` grades
the whole. This is the Just Python M8 pattern (a runnable grader that chains the prior artifacts under a
rubric in code) applied to the career dossier.

## The fleet plan

Conductor (Opus) writes the stage-map ingredient + `00-overview` + SUMMARY, specs `grade_dossier.py`, and
reviews. A Sonnet builds + `--selftest`-tests `grade_dossier.py` to the contract; the conductor captures its
verbatim output. Round 2: four Sonnet lesson-writers (L3 gets the grader's real output) + one Sonnet
exercises/validator worker (check_prep v7 + the loop-plan template + 4 exercises). VERIFY (Opus): STYLE +
grounding + no code/prose drift + the grader and validator run. BUILD/TEST: `mdbook build` +
`check_prep.py` v7 pytest + `grade_dossier.py --selftest` + `calibrate.py --selftest`. Ship at
`GATE-APPROVE-SHIP` under the standing directive. After ship: the book is content-complete (7 of 8 modules;
M4 deferred).
