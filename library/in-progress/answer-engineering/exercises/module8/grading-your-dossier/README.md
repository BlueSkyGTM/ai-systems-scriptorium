# Exercise: Grading Your Dossier

**Goal:** Run `python grade_dossier.py`, read the per-stage readiness report, and
close the one gap that blocks the most stages.

**Why:** `check_prep.py` measures completeness: are the required fields filled, are
the entries present, is the placeholder text gone. `grade_dossier.py` measures
readiness: given what is in the dossier, are you actually prepared for each stage?
These are different questions. A complete dossier can still have a gap verdict if a
signal category is below calibration threshold, if a required validator fails, or if
a loop-plan entry is missing. The grader composes your whole dossier into a single
report and names the exact reason for each gap. Your job in this exercise is to read
that report honestly and close the one gap that blocks the most stages.

## Steps

1. Confirm your dossier passes the completeness gate first:

   ```
   python check_prep.py --module 8
   ```

   If this exits 1, fix the completeness issues before running the grader. The grader
   reads the same files; incomplete files produce misleading grader output.

2. Run the capstone grader:

   ```
   python grade_dossier.py
   ```

   Read the full output. For each stage that shows GAP, note the reason listed. The
   reason will be one of:

   - A validator failed (the artifact is incomplete or fails field checks).
   - A signal category is not ready (fewer than the threshold reps in calibrate.py,
     or the latest rep was not clean).
   - A loop-plan entry is missing or has a placeholder Plan field.

3. Count which gap reason blocks the most stages. If "category 'ownership' not ready"
   appears for three stages, closing that category gap unblocks three stages at once.
   That is the gap to close first.

4. Do the work to close that gap:

   - If the blocker is a validator failure: open the relevant artifact, fix the
     missing or placeholder field, and re-run `python check_prep.py --module 8`
     to confirm the file now passes.
   - If the blocker is a category not ready: run `python calibrate.py` to see the
     per-category scorecard. Add reps in `deliberate-practice.md` targeting that
     category. Re-run `python calibrate.py` until the category shows ready.
   - If the blocker is a missing loop-plan entry: re-read Exercise 2 and fill in
     the Plan field for that stage.

5. After closing the highest-impact gap, re-run the grader:

   ```
   python grade_dossier.py
   ```

   If the verdict is still NOT READY, identify the next highest-impact gap and
   close it. Repeat until the grader exits 0 or until you have closed all gaps
   you can close in this session.

## Done When

```
python grade_dossier.py
```

exits 0 (VERDICT: READY) from `exercises/prep/`. This means every stage in the
loop is READY: validators pass, all required categories are calibrated-ready, and
all five loop-plan entries have non-placeholder Plan fields.

If you cannot reach READY in one session because a calibration gap requires more
practice reps, stop after closing the highest-impact gap and continue in the next
session. The next exercise (closing-the-loop) is the final drive to READY.

## Stretch

After the grader shows READY for all stages, look at the stages that were furthest
from READY at the start of this exercise. Write one paragraph in your
`deliberate-practice.md` as a DP entry using the systems-design category, describing
the architectural gap that was hardest to close and what you did to close it. Score
the four steps honestly. This turns the gap-closing work into a scored rep and locks
in the lesson.
