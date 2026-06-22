# Exercise: Debugging Out Loud

**Goal:** Add a rep to `exercises/prep/coding-screen-log.md` where you hit a bug
and fill the **Stuck and recovery:** field with your out-loud debugging motion.

**Why:** Going silent when stuck is the most common screen-killer that is not about
code. Interviewers can tolerate a wrong hypothesis; they cannot tolerate a
candidate who stares at the screen and stops communicating. The debugging motion --
gather information, form hypotheses, isolate, propose a fix, verify -- is a skill
you can practice before you need it. This exercise is a forced rep on that skill:
you will pick a task designed to surface a bug, get stuck, and narrate your way out.

## Steps

1. Choose Task D (subprocess sandbox with timeout) or Task E (tool dispatch with
   path jailing) from the lesson's grounded task list. These tasks are designed to
   surface a natural debugging moment: Task D has a timeout hang; Task E has a
   path-escape bug. Reference patterns are in
   `library/completed/sans-python/exercises/module6/01-terminal-coding-agent/sandbox.py`
   and `01-terminal-coding-agent/tools/__init__.py`.

2. Add a new `## Screen <n>` entry. Fill **Task:**, **Clarifying questions:**, and
   **Approach narration:** as in prior exercises.

3. When you hit a bug (or reach the designed failure point), stop. Do not look at
   the reference yet. Write the debugging motion into **Stuck and recovery:**:
   - What behavior did you observe? (one sentence)
   - What are your two or three hypotheses for the cause? (name each hypothesis)
   - Which hypothesis did you pursue first and why? (the diagnostic decision)
   - What did you find? What was the fix?
   The field must name at least two hypotheses. A single "I found the bug" sentence
   is not enough: that narrates the outcome, not the reasoning.

4. After writing the recovery narration, fill **Test cases:** with the cases you
   would run to confirm the fix is correct and has not broken the happy path.

5. Fill **Verdict:** with one sentence: what the rep revealed about your debugging
   motion. Was your first hypothesis right? Did you isolate correctly? Did you miss
   a hypothesis?

## Done When

Your `exercises/prep/coding-screen-log.md` has at least three `## Screen <n>`
entries in total, with this entry's **Stuck and recovery:** filled in and free of
placeholder text (i.e., not containing "none" and not containing placeholder
markers like `<fill in>`).

To confirm, run from `exercises/prep/`:

```
python check_prep.py --module 3
```

The Module 4 gate (`--module 4`) requires at least three complete entries and is
the target of the final exercise.

## Stretch

After writing your hypotheses, re-read them and check whether any was unfalsifiable
as stated. A good hypothesis is one you can test with a single observation: "the
timeout fires because the child process ignores SIGTERM" can be checked; "something
is wrong with the subprocess" cannot. If you wrote an unfalsifiable hypothesis,
revise it to be testable. The discipline is the same in a screen as in production
debugging: vague hypotheses produce long debugging sessions.
