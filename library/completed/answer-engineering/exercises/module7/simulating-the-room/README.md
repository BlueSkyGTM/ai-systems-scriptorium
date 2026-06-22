# Exercise: Simulating the Room

**Goal:** Complete timed mixed-category practice in `exercises/prep/deliberate-practice.md`
until `python calibrate.py` reports READY, then confirm the full M7 dossier with
`python check_prep.py --module 7`.

**Why:** Prior exercises built the rep log in practice-mode: you chose questions, you
knew the category, you had time to think. An interview is not practice-mode. Questions
arrive in an order you did not choose, the category is not announced, and you have
ninety seconds to deliver before the interviewer cuts away from a slow start. This
exercise adds the pressure component: mixed categories, timed construction, no re-reads
between reps. The readiness verdict from `calibrate.py` is the gate -- not a feeling.

## Steps

1. Before you start, run both tools to see where you stand:

   ```
   python check_prep.py --module 7
   python calibrate.py
   ```

   Note which categories and which steps are still short of the READY threshold. That
   list determines which questions to choose in the session below.

2. Set a timer for ninety seconds per rep. Choose questions from the categories where
   your calibration scores are lowest -- not where they are highest. Mixed means: do not
   run two behavioral questions in a row; alternate between behavioral categories and at
   least one systems-design rep per session.

3. For each timed rep:

   - Read the question once. Do not re-read.
   - Decompose and identify the signal silently or aloud (thirty seconds maximum).
   - Speak or write the Construct step. The answer must contain a named decision, a
     concrete metric or outcome, and a structural lesson within ninety seconds total.
   - Stop at ninety seconds. Score the four steps honestly.
   - Write the **Verdict:** field immediately, before the next rep.

4. After each session of three or more reps, re-run `python calibrate.py`. Read the
   updated scorecard. If the verdict is still NOT READY, identify the step that is
   holding you back and run another targeted session before checking again.

5. When `python calibrate.py` exits 0 (verdict: READY), run the completeness gate:

   ```
   python check_prep.py --module 7
   ```

   Exit 0 from this command is the Done When condition. It requires that your
   `deliberate-practice.md` has at least five reps across all five signal categories,
   all step scores are valid (strong/partial/weak), all fields are filled, and all
   prior dossier artifacts (M1, M2, M3, M5, M6) are also complete.

## Done When

```
python check_prep.py --module 7
```

exits 0 from `exercises/prep/`. This requires:

- `deliberate-practice.md` has at least five ### DP<n> entries.
- All five signal categories (ownership, conflict, failure, influence, systems-design)
  appear across the entries.
- Every **Decompose:**, **Signal:**, **Construct:**, and **Stress-test:** field holds
  one of: strong, partial, weak.
- No placeholder text in any field.
- All prior dossier artifacts (M1, M2, M3, M5, M6) are also complete.

`python calibrate.py` exiting 0 (verdict: READY) is a separate and additional gate
that check_prep.py does not enforce -- it measures readiness, not completeness. You
need both to call the module done.

## Stretch

Run one final session with a question you have not seen before -- pick one from the
lesson's challenge bank or ask someone to give you one. Do not know the category in
advance. Decompose it cold, run the full rep, score it, and compare your self-score
with your calibration average. If your cold-start score matches your practiced average,
your readiness is not a function of seeing the question before. That is the target.
