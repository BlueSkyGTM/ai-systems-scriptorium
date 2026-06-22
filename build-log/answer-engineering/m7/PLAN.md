# Module 7 — Live Practice and Calibration — Build Plan (GATE-LOCK-PLAN input)

Status: **PLAN LOCKED 2026-06-21 (`GATE-LOCK-PLAN` self-cleared under the standing "finish the job" +
"code, don't write" directives).** Sixth authoring stage (M1-3 + M5 + M6 shipped). Phase 3 continues.

## The stage in one line

The example banks taught the reader to reason to a strong answer; M6 taught them to narrate their
portfolio. M7 is the practice engine: how to run deliberate reps across the whole example bank, score each
rep against a rubric, and read a calibration report that tells them which signal categories are ready and
which need more reps. Seam: a Production AI Engineer has the framework and the stories but walks in
uncalibrated, with no evidence of which categories they are actually strong on.

## THE decision to lock: the rubric is code, not prose (the mandate, applied)

Ray's mandate: **code, don't write; good writing is one big schema handoff.** M7's self-review rubric is
therefore a **runnable scorer**, `calibrate.py`, not a prose checklist. The rubric (the scoring
dimensions, the category set, the readiness thresholds) lives in the code as the schema; the lessons are
the handoff that teaches the reader to feed it and read its output. The conductor (Opus) builds and TESTS
`calibrate.py` itself (with an offline `--selftest`) and the lessons quote its real interface and output
verbatim, so prose and code cannot drift.

## The two code artifacts

1. **`exercises/prep/calibrate.py`** (NEW, the M7 centerpiece, conductor-owned + tested): reads
   `exercises/prep/deliberate-practice.md` and prints a calibration scorecard. Each rep is a `### DP<n>`
   entry with `**Question:**`, `**Signal category:**` (one of: ownership, conflict, failure, influence,
   systems-design), and the four Algorithm-step self-scores `**Decompose:** / **Signal:** /
   **Construct:** / **Stress-test:**` each in {strong, partial, weak}, plus `**Verdict:**`. The scorer
   reports: per-category rep counts; the strong/partial/weak distribution per step across reps; the
   weakest step and the weakest/under-practiced categories; and a **readiness verdict** (ready when every
   category has >= 3 reps and no step scored weak in each category's most recent rep). Offline,
   stdlib-only, deterministic; `python calibrate.py --selftest` builds a synthetic rep set and asserts the
   report (exit 0 on pass). The rubric IS this file.
2. **`exercises/prep/check_prep.py` -> v6** (extended in place, exercises worker): adds `--module 7`
   gating `deliberate-practice.md` for completeness (>= 5 reps covering all five categories, each with the
   required fields, no placeholders). Cumulative; M1-3+M5+M6 byte-identical. `--module 4` stays open.

## Proposed M7 split (overview + 4 lessons + 4 exercises)

| # | Lesson (slug) | The move | Code touchpoint |
|---|---------------|----------|-----------------|
| 0 | `00-overview` | Practice is reps, not rereading; calibration is evidence, not a feeling. | calibrate.py intro |
| 1 | `deliberate-practice-not-rote` | What a rep is: run the full Algorithm on a fresh question from the bank and self-score it; why reps beat rereading; logging the rep. | the DP rep format |
| 2 | `the-self-review-rubric` | The rubric as the scoring schema: the four-step dimensions, the strong/partial/weak scale, how to score honestly. The rubric is the code; this lesson teaches feeding it. | calibrate.py rubric |
| 3 | `reading-your-calibration` | Run `calibrate.py`, read the scorecard: weakest step, under-practiced categories; the practice loop (score -> calibrate -> drill the gap -> repeat). | calibrate.py output |
| 4 | `simulating-the-room` | Timed mixed practice across the full bank; the readiness verdict; what "ready" means and what to drill when it says not yet. | the readiness verdict |

## The compounding throughline (STANDARDS Part 3)

M7 EXTENDS the dossier with `deliberate-practice.md` (the reps) and adds `calibrate.py` (the scorer). The
practice reps reuse the whole example bank (behavioral M3 + systems-design M5) and the Algorithm (M1-2).
`check_prep.py` v6 gates the reps' completeness; `calibrate.py` scores them. This is the first throughline
artifact that is a **scorer**, not just a completeness validator: the step that turns the dossier from
"complete" toward "graded," teeing up M8 (which composes + grades the whole dossier in code).

## The fleet plan

Conductor (Opus) builds + tests `calibrate.py`, writes the rubric schema ingredient + `00-overview` +
SUMMARY. Round 2: four Sonnet lesson-writers (each handed the tested `calibrate.py` interface + output
verbatim) + one Sonnet exercises/validator worker (check_prep.py v6 + the deliberate-practice template +
4 exercises). VERIFY (Opus): STYLE + grounding + no code/prose drift + the validator and scorer run.
BUILD/TEST: `mdbook build` + `check_prep.py` v6 pytest + `calibrate.py --selftest`. Ship at
`GATE-APPROVE-SHIP` under the standing directive.
