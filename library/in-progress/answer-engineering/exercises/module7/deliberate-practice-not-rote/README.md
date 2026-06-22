# Exercise: Deliberate Practice, Not Rote

**Goal:** Log your first three practice reps in `exercises/prep/deliberate-practice.md`,
spanning at least two signal categories.

**Why:** Rote repetition builds fluency with a script; deliberate practice builds the
reasoning reflex that generalizes to questions you have never seen. The difference is the
rep structure: each rep runs the full four-step Algorithm, scores each step honestly, and
writes a verdict that names exactly what to drill next -- not a general note like "be more
specific," but a named gap (e.g., "Decompose weak: I identified the wrong primary signal;
re-read the lesson on Conflict vs. Ownership"). The practice log is the instrument. If you
skip the verdict, you are just rehearsing.

## Steps

1. Copy `exercises/prep/deliberate-practice.template.md` to
   `exercises/prep/deliberate-practice.md` if you have not already done so. Read the
   template's field definitions before you start.

2. Choose a question from the lesson's warm-up bank or from any prior exercise. Write it
   verbatim (or as a close paraphrase) into the **Question:** field of your first DP entry.
   Do not use a question you have already answered fully in answers-log.md -- the point is
   to extend into territory you have not covered.

3. Run the four Algorithm steps in your head, spoken aloud, or on paper -- not in the
   **Construct:** field yet. Do the work first; log the scores second.

4. Fill in the four step fields with one of: strong, partial, weak. Be honest. If you
   hedged in your Decompose, write "partial." If your Construct had no named decision or
   no concrete metric, write "weak."

5. Write the **Verdict:** field. It must name one specific thing to drill before the next
   rep: a gap in a named step, a category that is harder than expected, or a pattern you
   noticed in how you handled the question.

6. Repeat for a second and third rep. At least two of the three reps must be in different
   signal categories (ownership, conflict, failure, influence, systems-design). The category
   is the primary signal of the question you chose -- not the category you scored best in.

## Done When

You have three ### DP<n> entries in `exercises/prep/deliberate-practice.md`, spanning at
least two signal categories, with all seven fields filled in and free of placeholder text.

To confirm your first three reps are structurally complete, run from `exercises/prep/`:

```
python check_prep.py --module 7
```

This will report incomplete until you have all five signal categories covered (that is the
goal of the next exercise). What it tells you now: whether your first reps are missing
required fields or contain placeholder text.

For a readiness score, run:

```
python calibrate.py
```

`calibrate.py` scores how many reps you have per category and which Algorithm step is
weakest. At this stage it will show you under-practiced categories and a readiness verdict
of NOT READY -- that is expected and correct.

## Stretch

Add a fourth rep in a category where your step scores were weakest. Write the verdict
before you look at the calibrate.py output, then run `python calibrate.py` and compare
your self-assessment with the scorecard. Where they disagree, the scorecard is right.
