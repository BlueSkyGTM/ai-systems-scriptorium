# Exercise: Sequencing the Preparation

**Goal:** Draft `exercises/prep/loop-plan.md` with all five stage entries filled
in: which dossier artifacts each stage draws on, and an honest **Readiness** mark
(ready or gap) for each stage.

**Why:** The hiring loop is not one conversation. It is five distinct evaluations,
each with a different evaluator, a different artifact set, and a different failure
mode. A candidate who treats the loop as a single undifferentiated event under-prepares
for the stages that expose their weakest material and over-prepares for stages that
are already solid. Sequencing your preparation means knowing which artifact covers
which stage, where your coverage is thin, and which gap to close first. The
**Readiness** mark is the honest accounting: you either have the material or you do not.

## Steps

1. Before you touch `loop-plan.md`, run the completeness gate for the prior modules:

   ```
   python check_prep.py --module 7
   ```

   If this exits 1, stop here and complete the M7 dossier first. The loop plan is
   only meaningful when the material it draws on is finished.

2. Copy `loop-plan.template.md` to `loop-plan.md` in `exercises/prep/`:

   ```
   cp loop-plan.template.md loop-plan.md
   ```

3. For each of the five stages below, read the lesson's stage-map table (Module 8,
   section "What Each Stage Evaluates") and decide which of your completed dossier
   artifacts that stage draws on. Fill in the **Dossier pieces** field with the
   artifact names:

   - recruiter-screen
   - hiring-manager
   - systems-design-round
   - portfolio-deep-dive
   - panel

4. For each stage, make an honest **Readiness** call:

   - `ready` means you believe your current dossier material covers that stage with
     no further work needed.
   - `gap` means there is a known hole: a category below threshold, an artifact
     section that is thin, or a question type you have not practiced.

   Do not mark yourself `ready` based on feeling. Look at the artifact. Read the
   relevant section. If you are unsure, mark `gap`. The grader will tell you the
   truth in the next exercise; an honest gap is easier to close than a false ready.

5. Leave the **Plan** field for each stage as the template stub for now. You will
   fill it in during the next exercise.

6. When all five **Dossier pieces** and **Readiness** fields are filled and free of
   placeholder text, run:

   ```
   python check_prep.py --module 8
   ```

   This will fail on the **Plan** fields (still stubs). That is expected. Confirm
   the only failures are the five unfilled Plan fields, not missing stages or invalid
   Readiness values.

## Done When

All five stage entries in `loop-plan.md` have:

- **Dossier pieces** filled with the actual artifact names (no placeholder text).
- **Readiness** set to `ready` or `gap` (no placeholder text, no other value).

`python check_prep.py --module 8` exits 1 at this point (Plan fields still stub)
and that is correct. The gate closes in Exercise 4.

## Stretch

After filling in the Readiness marks, count the gaps. If three or more stages are
marked `gap`, go back to the dossier before moving forward: the sequencing exercise
has surfaced a coverage problem that the plan cannot paper over. Identify the one
artifact that, if completed, would close the most gaps, and schedule that work before
continuing to Exercise 2.
