# Hiring-Loop Map — M8 Reference Ingredient (the schema)

The schema the M8 capstone grader and the M8 lessons both derive from: the interview loop's stages, what
each evaluates, and which prep-dossier artifacts prepare it. The grader (`grade_dossier.py`) maps the
dossier onto these stages and grades each; the lessons teach the reader to sequence preparation against
them. Date: 2026-06-21. The technical coding screen (Module 4) is deferred and is NOT a graded stage here;
it is named in the lessons as the one stage the reader sources separately.

## The five graded stages

| Stage | What it evaluates | Dossier artifacts that prepare it | Calibrate categories that must be READY |
|---|---|---|---|
| **recruiter-screen** | a crisp self-pitch and one portfolio headline; can you say what you do and what you built in two minutes | the portfolio-narrative overview; Algorithm fluency from the answers log | (none specific) |
| **hiring-manager** | behavioral depth: ownership, influence, how you operate | the behavioral bank | ownership, influence |
| **systems-design-round** | an open-ended design under a clock, production reasoning over reference architecture | the systems-design log | systems-design |
| **portfolio-deep-dive** | walking your real artifact's decisions, tradeoffs, failure modes | the portfolio-narrative document | (none specific) |
| **panel** | a mix: behavioral plus a portfolio walk, often conflict and failure | the behavioral bank; the portfolio-narrative document | conflict, failure |

## What "ready for a stage" means (the grading rule)

A stage is READY only when all three hold:
1. **Artifacts complete:** every dossier artifact that prepares the stage passes its completeness check
   (the same checks `check_prep.py` runs).
2. **Practice ready:** every calibrate category the stage needs is READY in the calibration scorecard
   (enough reps, latest rep clean).
3. **Planned:** the reader has written a non-placeholder plan for that stage in `loop-plan.md`.

The whole dossier is READY-to-interview only when every stage is READY. That is the capstone verdict.

## The reader's loop plan (loop-plan.md)

One entry per stage:

```
### Stage recruiter-screen
**Dossier pieces:** <which of your artifacts you draw on for this stage>
**Readiness:** ready | gap
**Plan:** <what you will do before this stage; for a gap, the specific thing to close>
```

## Sequencing guidance (for the lessons)

- Build the framework and the answers log first; they feed every stage.
- The behavioral bank covers the most stages (hiring-manager, panel), so it has the highest leverage.
- The systems-design log is the single-stage, highest-difficulty artifact; budget the most reps there.
- The portfolio-narrative document is reused across recruiter-screen, portfolio-deep-dive, and panel; one
  strong document pays off three times.
- The deferred technical coding screen is sourced separately; name it so the reader is not surprised by it.
