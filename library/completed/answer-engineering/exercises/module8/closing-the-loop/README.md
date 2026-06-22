# Exercise: Closing the Loop

**Goal:** Drive your dossier to a READY verdict on every stage. Done When:
`python check_prep.py --module 8` exits 0 AND `python grade_dossier.py` exits 0
(VERDICT: READY). This is the capstone gate for the book.

**Why:** The prior exercises built the dossier piece by piece: decompositions,
answers, signal maps, behavioral stories, a system design, a portfolio narrative,
deliberate-practice reps, and a per-stage plan. This exercise asks a different
question: are you actually ready to walk into each stage and perform? The two-gate
close answers it without ambiguity. `check_prep.py --module 8` confirms that the
dossier is complete and structurally valid. `grade_dossier.py` confirms that the
material inside the dossier is ready: validators pass, categories meet the calibration
threshold, and every stage has a concrete plan. Both gates must exit 0. A candidate
who passes only one is not done.

## Steps

1. Start by running both gates to see where you stand:

   ```
   python check_prep.py --module 8
   python grade_dossier.py
   ```

   If both exit 0, you are done. Read the Done When section and confirm the
   artifacts are in the state described.

2. If `check_prep.py --module 8` exits 1, fix the completeness failures first.
   The output names the exact file and field. Do not move to the grader until
   `check_prep.py --module 8` exits 0.

3. If `grade_dossier.py` exits 1 (check_prep passed but grader did not), read the
   grader report. Each GAP line names the reason. Work the gaps in priority order:
   close the gap that blocks the most stages first.

4. For each remaining gap:

   **Validator failed:**
   Open the named artifact. The validator messages tell you which field is missing,
   empty, or contains placeholder text. Fix it. Re-run `python check_prep.py --module 8`
   to confirm.

   **Category not ready:**
   Run `python calibrate.py`. Read the per-category scorecard. The category is not
   ready because either you have too few reps or your latest rep in that category
   was not clean. Add reps in `deliberate-practice.md` in the weak category. Score
   each rep honestly. Re-run `python calibrate.py` until the category status flips
   to ready.

   **Loop-plan entry missing or empty:**
   Open `loop-plan.md`. The Plan field for that stage is a stub or placeholder.
   Write a specific, artifact-referencing plan. Re-run `python check_prep.py --module 8`.

5. After each gap-closing action, re-run both gates:

   ```
   python check_prep.py --module 8
   python grade_dossier.py
   ```

   Continue until both exit 0.

## Done When

```
python check_prep.py --module 8
```

exits 0 AND

```
python grade_dossier.py
```

exits 0 (VERDICT: READY), both from `exercises/prep/`.

When both gates are green:

- `loop-plan.md` has all five stage entries with filled Dossier pieces, valid
  Readiness values, and non-placeholder Plan fields.
- `deliberate-practice.md` has at least five reps covering all five signal categories
  with valid step scores.
- All prior dossier artifacts (M1 through M7) are complete.
- Every interview-loop stage shows READY in the grader report.

This is the end of the book's exercise track. The dossier is your artifact:
a complete, graded record of preparation that was tested against the same rubric
the evaluators use.

## Stretch

Schedule a mock loop with someone who has run the actual hiring process at an AI
company. Walk them through your dossier the way you would walk an interviewer
through it: the portfolio narrative for the recruiter screen, two behavioral stories
for the hiring manager, one full system design for the systems-design round, the
artifact walkthrough for the portfolio deep-dive, and two more stories for the panel.
After the mock, score each stage the way `grade_dossier.py` would: validator pass,
category ready, plan executed. If the mock reveals a gap the grader did not, add
a DP rep to `deliberate-practice.md` targeting that gap and re-run `python calibrate.py`.
The loop closes when the mock score and the grader score agree.
