# Exercise: Narrating the Screen

**Goal:** Log your first coding-screen rep in `exercises/prep/coding-screen-log.md`,
completing the Task, Clarifying questions, and Approach narration fields.

**Why:** A coding screen tests how you think, not whether you finish. The
communication layer -- clarifying before you touch a line, narrating each decision
out loud, signaling when you are pivoting -- is what separates a forgettable
performance from one that sticks. This exercise is not about getting the task
right; it is about building the habit of narrating the reasoning the interviewer
cannot see.

## Steps

1. Copy `exercises/prep/coding-screen-log.template.md` to
   `exercises/prep/coding-screen-log.md` if you have not already done so.
   Read the template's field definitions before you start.

2. Choose Task A from the lesson's grounded task list: implement a retrieval
   relevance floor that drops results below a `min_score` threshold so the
   generator only sees high-confidence context and can refuse when nothing clears
   the floor. The reference pattern is in
   `library/completed/sans-python/exercises/module6/02-production-rag-chatbot/retriever.py`.
   Read the lesson first, then the reference; do not paste from the reference.

3. Before writing any code, spend two minutes on clarifying questions. Write them
   into the **Clarifying questions:** field of your first `## Screen 1` entry.
   Good clarifying questions for this task: What type does the function return when
   no results clear the floor? What is the schema of a single result? Is `min_score`
   inclusive or exclusive? What should the caller do with an empty result?

4. Code the task in your head or on paper. As you work, narrate each decision out
   loud: "I am starting with the data shape because..." or "I am filtering before
   I truncate because..." Write the narration into **Approach narration:**. Do not
   write what you did; write what you were deciding and why.

5. Fill **Task:** with the task name and your one-sentence framing of the
   problem. Leave **Stuck and recovery:** and **Test cases:** and **Verdict:** as
   stubs for now -- the next exercises will complete them.

## Done When

Your `exercises/prep/coding-screen-log.md` has a `## Screen 1` entry with
**Task:**, **Clarifying questions:**, and **Approach narration:** filled in and
free of placeholder text.

The validator does not gate on individual fields per exercise -- it gates the full
log at the end of Module 4. You can confirm the file is present and parseable by
running from `exercises/prep/`:

```
python check_prep.py --module 3
```

Module 3 is the prerequisite; confirm it exits 0 before proceeding. The Module 4
gate (`--module 4`) requires at least three complete entries and is the target of
the final exercise.

## Stretch

After writing the narration, read it back and ask: could an interviewer follow your
reasoning without seeing the code? If any step skips the "why," revise it to add
the decision, not just the action. The test: replace every "I did X" with "I did X
because Y." If Y is obvious, you have good narration. If Y is missing, you are
narrating actions, not reasoning.
