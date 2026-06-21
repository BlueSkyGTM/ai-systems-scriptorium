# Exercise: Construct the Answer

**Goal:** Run the full four-step Algorithm on five questions, write each answer out in full, self-score on three dimensions, and revise every partial or weak score.

**Why:** Decomposition identifies the target; construction is where you either hit it or miss it. The self-scoring step is the one most candidates skip, and it is the biggest gap between an answer that sounds good and one that holds up when the interviewer pushes back.

## Steps

1. Copy `exercises/prep/answers-log.template.md` to `exercises/prep/answers-log.md`. Read the worked example entry; your entries follow the same format.

2. Choose five questions. Your selection must include:
   - At least two behavioral questions (Ownership, Communication/Influence categories)
   - One technical-depth question
   - One systems-design question
   - One question of your choice from any category

   If you do not yet have a personal question bank, use Q1, Q3, Q5, Q7, and Q8 from the decompose-the-question exercise.

3. For each question, work all four Algorithm steps in order and record each one:

   **Step 1: Decompose.** Copy your three-part decomposition from your decomposition log if you already have it. If this question is new, write the literal parse, signal category, and primary hypothesis now.

   **Step 2: Identify the signal.** Restate the primary hypothesis in one sentence. Then list the evidence the hypothesis requires: what specific things must appear in your answer to make the claim credible? Name them before you write the answer.

   **Step 3: Construct the answer.** Write the answer in full, as you would say it. Aim for under two minutes of spoken content for behavioral questions and under three for technical and systems-design. Keep a 20/60/20 ratio: context sets the scene (20%), evidence carries the weight (60%), result closes the loop (20%).

   **Step 4: Stress-test.** Ask one question: could a weak candidate give this answer? If yes, find the sentence that a weak candidate could have written and rewrite it with one specific addition: a real number, a named decision, a failure mode you caught, a concrete outcome. If the answer already passes, state why it passes.

4. After the stress-test revision, score the answer on three dimensions using a three-point scale: strong, partial, or weak.

   - **Specificity:** does the answer contain details no weak candidate can supply? Named techniques, real numbers, actual decisions, not general claims.
   - **Structure:** can you trace the reasoning from situation to action to result? Is the ordering logical, or do context and evidence intermix?
   - **Completeness:** does the answer close the loop on the primary hypothesis? Could someone extract the evidence the signal required from this answer alone?

5. For every dimension scored partial or weak: write one sentence naming what is missing, then revise the answer to address it. The revision goes in place; note that it is a revision.

## Done When

Run this from the `exercises/prep/` directory:

```
python check_prep.py
```

The validator checks `answers-log.md` for five entries, each with all four Algorithm steps recorded and three scores (specificity, structure, completeness). It exits 0 when the log is complete.

## Stretch

Record yourself giving one of the five answers out loud, as if in a live interview. Play it back and score the spoken version on the same three dimensions. Note where the spoken and written answers diverge: those are the places where the habit is not yet automatic. The deliberate-practice sessions in Module 7 target exactly those divergence points.
