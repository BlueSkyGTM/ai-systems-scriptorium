# Exercise: The Stages of the Loop

**Goal:** Fill the **Plan** field for each stage entry in `exercises/prep/loop-plan.md`
by mapping what each stage evaluates to a concrete action you will take before that
stage.

**Why:** A plan that says "review my notes before the call" is not a plan; it is a
hope. A real per-stage plan names what the evaluator is trying to determine, which
artifact covers that signal, and what specific preparation closes the gap between
where you are and where you need to be. The plan is the diff between your current
dossier state (captured in the Readiness mark from Exercise 1) and a ready verdict.
Without it, you will prepare in the wrong order, spend time on material that is already
strong, and walk into the stage that exposes your gap without having closed it.

## Steps

1. Before you start, read `loop-plan.md` to confirm that all five stage entries have
   filled **Dossier pieces** and **Readiness** values from Exercise 1. Do not proceed
   if any stage still has placeholder text in those fields.

2. For each stage, read the lesson's stage description (Module 8, the relevant section
   for that stage). Then answer three questions and write the answers as your **Plan**:

   a. What is this stage trying to determine about you? (One sentence, specific.)
   b. Which artifact in your dossier is the primary coverage for that signal?
   c. If your Readiness mark is `gap`: what is the one action you will take before
      this stage to close that gap? Name the artifact, the section, and the metric
      or outcome you are driving toward (for example: "run two more DP reps in the
      systems-design category until calibrate.py reports that category ready").

   If your Readiness mark is `ready`: your plan should still name the artifact you
   will review before the stage and the one thing you will confirm is solid.

3. Write each **Plan** field in `loop-plan.md` as a short, direct paragraph (three to
   five sentences). The plan must name the artifact, name the gap or the confirmation
   action, and end with a concrete outcome (what done looks like).

4. After filling all five Plan fields, run:

   ```
   python check_prep.py --module 8
   ```

   If this exits 1, read the output. The failure messages will name which stage
   entries still have placeholder text or missing fields. Fix those entries and
   re-run.

5. When `check_prep.py --module 8` exits 0, also run:

   ```
   python grade_dossier.py
   ```

   Read the readiness report. Note which stages are READY and which are GAP, and
   what the gap reasons are. The grade_dossier.py grader looks at the actual dossier
   artifacts and your calibration scores, not just the loop-plan entries. If a stage
   you marked `ready` in loop-plan.md shows as GAP in the grader output, the grader
   is right and your Readiness mark was optimistic. Update the mark.

## Done When

```
python check_prep.py --module 8
```

exits 0 from `exercises/prep/`. This requires that all five stage entries in
`loop-plan.md` have:

- **Dossier pieces** filled (from Exercise 1).
- **Readiness** set to `ready` or `gap` (from Exercise 1).
- **Plan** filled with a non-placeholder, non-empty plan (from this exercise).

`python grade_dossier.py` will likely still exit 1 at this point if there are real
gaps. That is the input for Exercise 3.

## Stretch

Compare your per-stage plans against the lesson's recommended preparation sequence.
If the lesson says to prepare for the systems-design-round before the hiring-manager,
but your gaps are concentrated in the behavioral categories, the sequence that closes
the most risk first is the right one regardless of loop order. Reorder your preparation
priorities to close the highest-impact gap first. Write one sentence at the top of
your loop-plan.md naming the priority order you chose and why.
