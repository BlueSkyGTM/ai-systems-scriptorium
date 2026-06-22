# Exercise: The Happy Path and the Edges

**Goal:** Add one or two more reps to `exercises/prep/coding-screen-log.md`,
filling the **Test cases:** field with the edge cases you identified and handled.

**Why:** A candidate who codes only the happy path has shown they can write code.
A candidate who names the edges before being prompted has shown they think about
correctness. Interviewers watch for this: they want to see you consider what
happens when input is empty, at the boundary, or adversarially constructed,
without being asked. The test cases you write -- and how you sequence them -- are
a signal independent of whether your code compiles.

## Steps

1. Choose Task B (token-budget guard) or Task C (content guardrail) from the
   lesson's grounded task list, or both if time allows. Reference patterns live in
   `library/completed/sans-python/exercises/module6/01-terminal-coding-agent/budget.py`
   and `02-production-rag-chatbot/guardrail.py`. Read the lesson section for the
   task before looking at the reference.

2. Add a new `## Screen <n>` entry (increment the number from your last entry).
   Fill **Task:** and **Clarifying questions:** as in the previous exercise.

3. Code the happy path first. Then stop, and before writing defensive cases, write
   the edge cases into **Test cases:**. Format: one case per line, naming the
   category and the expected behavior. Examples:
   - "empty input list -> return empty result, do not raise"
   - "cost exactly at dollar ceiling -> raise immediately (inclusive)"
   - "prohibition pattern in input with benign framing -> still blocked"

4. Now code the edge cases. If your happy-path code had to change to handle an
   edge, note that in **Approach narration:**.

5. Fill **Stuck and recovery:** with "none" if you were not stuck. Leave
   **Verdict:** as a stub.

6. Repeat for a second task if you have time. Aim for at least two `## Screen`
   entries total across this exercise and the previous one.

## Done When

Your `exercises/prep/coding-screen-log.md` has at least two `## Screen <n>`
entries, each with **Task:**, **Clarifying questions:**, **Approach narration:**,
and **Test cases:** filled in and free of placeholder text.

To confirm the file is present and parseable, run from `exercises/prep/`:

```
python check_prep.py --module 3
```

The Module 4 gate (`--module 4`) requires at least three complete entries and is
the target of the final exercise.

## Stretch

After writing your test cases, group them by category: boundary cases, empty/null
cases, adversarial cases, and error-path cases. If any category is missing, ask
what a failure there would look like in production and add one case for it. The
discipline of naming the category before you write the case is the same discipline
that produces reliable software: you are writing a threat model before the tests,
not tests at random.
