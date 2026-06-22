# Exercise: The Self-Review Rubric

**Goal:** Re-score your existing reps strictly using the lesson's rubric, then add reps
until all five signal categories appear in `exercises/prep/deliberate-practice.md`.

**Why:** Self-scoring drifts charitable over time. The first-pass verdict is the hardest
to write honestly because the easiest move is to score your weakest step "partial" when
it was actually "weak." This exercise applies the rubric as a second pass: go back to
each rep and re-read the scored step against the lesson's bar for that step, not against
your memory of how hard the question felt. The rubric is the question, not your effort.
The category gap requirement forces you into territory that feels harder -- the categories
you avoided in the first exercise are the ones the interviewer will not avoid.

## Steps

1. Open `exercises/prep/deliberate-practice.md` and read your existing reps as a
   reviewer, not as the author. For each rep, apply the rubric for each step:

   - **Decompose:** Did you name the primary signal correctly? Did you name one latent
     signal? Could a candidate who had not read the lesson give the same decomposition?
     If yes to the last question, it is "partial" at best.
   - **Signal:** Did you state the exact hypothesis the interviewer is testing, in the
     form "The interviewer is trying to determine whether..."? If you wrote the signal as
     a category label ("ownership") rather than a hypothesis, it is "partial."
   - **Construct:** Does the answer contain a named decision, a concrete metric or
     outcome, and a structural lesson? If any one of these is missing, it is "partial."
     If two or more are missing, it is "weak."
   - **Stress-test:** Did you name a specific thing a weak candidate could not replicate?
     "I was specific" is not a stress test. Name the sentence or the number.

2. Update any step score where your first-pass score was too generous. Do not lower a
   score that was already accurate. The **Verdict:** field should reflect the re-scored
   step, not the original score.

3. Identify which of the five signal categories are missing from your log so far:
   ownership, conflict, failure, influence, systems-design. Add reps -- each a complete
   ### DP<n> entry with all seven fields -- until all five categories appear.

4. For each new rep, apply the rubric as you go (do not score first and audit second;
   score each step as you complete it, then write the verdict immediately).

## Done When

All five signal categories appear in `exercises/prep/deliberate-practice.md` across your
reps, and every step score in every entry is honest against the rubric above.

To check field completeness, run from `exercises/prep/`:

```
python check_prep.py --module 7
```

The completeness gate requires all five categories to appear and all step scores to be
one of strong, partial, or weak. It exits 1 until the category requirement is met.

For calibration, run:

```
python calibrate.py
```

`calibrate.py` will show which step is weakest across all reps and which categories are
under-practiced. At least one category will likely still be under-practiced (calibrate.py
requires a minimum of three reps per category for READY). That is the target for the next
exercise.

## Stretch

Write a second rep in your weakest category using a question from the opposite end of the
seniority range -- if your first rep was a junior-framed question ("Tell me about a time
you disagreed"), try a staff-framed version ("How do you build alignment across a large
engineering organization when you have no authority over the teams involved?"). Write the
verdict for both and compare: what shifts in the Construct step when the seniority level
rises?
