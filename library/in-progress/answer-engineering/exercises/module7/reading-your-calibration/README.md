# Exercise: Reading Your Calibration

**Goal:** Run `python calibrate.py`, read the scorecard, identify your biggest gap, and
add targeted reps to `exercises/prep/deliberate-practice.md` to close it.

**Why:** A scorecard is only useful if you read it correctly. The calibrate.py output
shows two things that are easy to misread: the per-category rep count (which measures
breadth) and the per-step average score (which measures depth). Candidates routinely
over-correct on breadth (adding reps in every category) when the verdict is driven by
depth (a weak Construct step across all categories). This exercise trains you to read
the scorecard before you add reps, not after.

## Steps

1. From `exercises/prep/`, run:

   ```
   python calibrate.py
   ```

   Read the output fully before you act. Note the two outputs that matter most:

   - **Weakest step:** The step with the lowest average score across all reps. This
     drives the verdict more than rep count does. If Construct is weak, adding more reps
     in new categories will not flip the verdict to READY.
   - **Under-practiced categories:** Categories with fewer than the minimum rep count.
     You may also have a category where reps exist but scores are low. Both matter.

2. Write down -- in the **Verdict:** field of your next rep, or on paper -- your read of
   the scorecard before you act:

   - What is your weakest step? What does a "weak" score in that step look like in your
     actual reps? Name a sentence or a pattern, not a category label.
   - Which categories are under-practiced? Is the under-practice a breadth gap (too few
     reps) or a depth gap (reps exist but step scores are low)?
   - What is the minimum number of targeted reps to move the verdict?

3. Add the targeted reps. A targeted rep means: choose a question in the category with
   the worst step scores, run the full four steps, and focus the **Construct:** and
   **Stress-test:** steps on the specific weakness you named in step 2. Do not add reps
   in categories where your scores are already strong just to raise the rep count.

4. After adding the targeted reps, re-run `python calibrate.py` and check whether the
   verdict changed. If it did not, re-read the scorecard and name what you missed.

## Done When

`python calibrate.py` shows improvement in the weakest step and you have added at least
two targeted reps in the gap category. The verdict may not yet be READY -- that is the
goal of the final exercise.

Run from `exercises/prep/` to confirm structural completeness:

```
python check_prep.py --module 7
```

Both tools serve different gates: `check_prep.py` gates "you have practiced across all
categories with no missing fields"; `calibrate.py` gates "you are actually ready." You
need both to exit 0 before the module is complete.

## Stretch

Compare your Construct step scores in the behavioral categories (ownership, conflict,
failure, influence) against your systems-design category scores. Most candidates score
systematically higher in one group. Identify which is weaker, add one more rep in the
weaker group, and write the verdict explaining what is structurally different about
constructing an answer in that group (what does "a concrete outcome" mean in a systems
design context versus a behavioral context?).
