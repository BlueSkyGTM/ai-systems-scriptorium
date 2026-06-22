# Grading Your Dossier

The loop will grade you stage by stage, with no partial credit for the rounds you skipped. The dossier grader applies the same discipline before you walk in.

You have run the completeness checker on your artifacts and the calibration scorer on your practice log. The grader composes both and maps the result onto five stages: recruiter screen, hiring manager, systems-design round, portfolio deep-dive, and panel. Each stage gets a verdict. One gap in any stage holds the overall verdict at NOT READY. Run it from the `exercises/prep/` directory:

```
python grade_dossier.py
```

## What You Get Back

Here is the full report on an empty dossier:

```
Answer Engineering Dossier Readiness Report
============================================

  recruiter-screen         GAP: validator portfolio_narrative failed, validator answers failed, loop-plan entry missing or empty
  hiring-manager           GAP: validator behavioral_bank failed, category 'ownership' not ready, category 'influence' not ready, loop-plan entry missing or empty
  systems-design-round     GAP: validator systems_design_log failed, category 'systems-design' not ready, loop-plan entry missing or empty
  portfolio-deep-dive      GAP: validator portfolio_narrative failed, loop-plan entry missing or empty
  panel                    GAP: validator behavioral_bank failed, validator portfolio_narrative failed, category 'conflict' not ready, category 'failure' not ready, loop-plan entry missing or empty

VERDICT: NOT READY. Close: recruiter-screen, hiring-manager, systems-design-round, portfolio-deep-dive, panel.
```

Read each line as a named list of work still on the table.

## Reading the Gap Types

Each gap message is one of three kinds, and each points back to a specific artifact.

**A failed validator** means a required dossier artifact is missing or incomplete. The completeness checker from Module 1 runs on each artifact and the grader collects the result. "Validator portfolio_narrative failed" means your `portfolio-narrative.md` did not pass `check_prep.py`'s test for that document: it is absent, empty, or still has placeholder text. Return to the module that owns that artifact, finish it until `check_prep.py` passes it in isolation, and re-run the grader.

**A category not ready** means the calibration scorer from Module 7 says that signal category does not yet have three reps with a clean latest rep. "Category 'ownership' not ready" means you have not satisfied the `calibrate.py` threshold for that category. Return to your deliberate-practice log, drill the gap, and re-run `calibrate.py` to confirm it clears before re-running the grader.

**Loop-plan entry missing or empty** means you have not written a concrete preparation plan for that stage in `loop-plan.md`. The grader looks for a filled-in `**Plan:**` field under each stage heading. A placeholder or a blank value fails the check. Open `loop-plan.md`, write a real plan for the stage, and re-run.

When a stage is fully prepared, its line reads:

```
  recruiter-screen         READY
```

When every stage reads READY, the verdict flips:

```
VERDICT: READY. All interview stages are prepared.
```

And the process exits 0.

## How the Grader Composes the Earlier Tools

The grader does not invent a new standard. It borrows the two standards you have already applied.

The completeness result for each dossier artifact comes from `check_prep.py`, the same validator you used in Module 1 to confirm each artifact was built. The calibration result for each signal category comes from `calibrate.py`, the same scorer you used in Module 7 to read your practice readiness. The grader runs both, then maps the combined results onto the five-stage structure. A gap in the report is the same gap you would have found in the individual tool; the grader just shows you which stages it blocks.

This is why a gap in the report names exactly which artifact or category to fix: the source of the gap has not changed, only the stage context in which it shows up.

## Closing the Gaps in the Right Order

Not all gaps are equal. Some artifacts appear in a single stage; others appear in several. The portfolio-narrative artifact shows up in three stages: recruiter screen, portfolio deep-dive, and panel. Fixing it closes three gaps at once. Start there before touching a gap that blocks only one stage.

Here is the leverage map, read from the empty report above:

- `portfolio_narrative` blocks recruiter-screen, portfolio-deep-dive, and panel.
- `behavioral_bank` blocks hiring-manager and panel.
- `answers` blocks recruiter-screen only.
- `systems_design_log` and the `systems-design` category both block systems-design-round.
- The `ownership` and `influence` categories block hiring-manager.
- The `conflict` and `failure` categories block panel.

Fix the highest-leverage gap first, re-run the grader, and read the updated report. Do not try to fix everything in one pass; the report after each run tells you where the remaining effort is concentrated.

The loop is the same discipline you used with the calibration scorer: run, read, close one gap, re-run. The grader exits 0 when the dossier earns it.

## Core Concepts

- The dossier grader composes the completeness checker and the calibration scorer; a gap in the report is the same gap you would find running either tool individually.
- Each gap type names its fix: a failed validator points back to a dossier artifact; a category not ready points back to the practice log; a missing loop-plan entry points to `loop-plan.md`.
- Close high-leverage gaps first: fixing an artifact that appears in three stage rows eliminates three gap lines in one move.
- Readiness is exit 0 awarded by the grader when every stage clears all three checks; it is not a judgment call.

<div class="claude-handoff" data-exercise="exercises/module8/grading-your-dossier/">

**Try It in Claude Code:** run the dossier grader, read the readiness report, close the gap that blocks the most stages, and re-run until more stages report READY.

</div>
