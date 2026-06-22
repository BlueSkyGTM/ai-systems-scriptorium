# Exercise: The Clock and the Weak-Screen Audit

**Goal:** Add a timed rep to `exercises/prep/coding-screen-log.md` and write a
weak-screen audit in the **Verdict:** field. Then confirm the full log passes the
Module 4 gate.

**Why:** Time pressure is not a distraction; it is a signal. An interviewer who
gives you forty-five minutes and watches how you allocate them is watching for
prioritization: do you clarify before you code? Do you get a working skeleton
before you polish? Do you leave time to test? The timed rep is where all four
communication habits land together under real pressure. The weak-screen audit in
the **Verdict:** field is how you turn the rep into a drill point.

## Steps

1. Set a timer for twenty-five minutes. Choose Task F (kill switch) or Task G
   (quality drift monitor) from the lesson's grounded task list. Reference patterns
   are in
   `library/completed/sans-python/exercises/module6/01-terminal-coding-agent/killswitch.py`
   and `02-production-rag-chatbot/drift.py`.

2. Spend the first three minutes only on clarifying questions. Write them into
   **Clarifying questions:** before you touch the code. If you run out of
   clarifying questions before three minutes, write "none further" and move on.

3. Code the happy path first, then the edge cases. Narrate decisions into
   **Approach narration:** as you go. If you get stuck, run the debugging motion
   from the previous exercise.

4. When the timer fires, stop. Do not finish the code. Fill **Test cases:** with
   what you would test next. Fill **Stuck and recovery:** with the debugging motion
   if you got stuck, or "none" if you did not.

5. Write the weak-screen audit in **Verdict:**. It must name one concrete weak-
   screen failure mode you noticed in your own performance. Examples:
   - "I did not clarify the boundary condition on the floor before I coded it;
     the interviewer would have had to stop me to ask."
   - "My narration dropped out for two minutes while I worked through the timeout
     handling; I went silent."
   - "I polished the happy path instead of writing the edge cases first; I ran out
     of clock before handling empty input."
   The audit is not self-criticism; it is a drill target for the next rep.

6. Confirm your log has at least three complete entries (across all four exercises)
   and run from `exercises/prep/`:

```
python check_prep.py --module 4
```

This must exit 0. Fix any incomplete or placeholder fields until it does.

## Done When

`python check_prep.py --module 4` exits 0 from `exercises/prep/`.

That means: at least three `## Screen <n>` entries, each with all six fields
(**Task:**, **Clarifying questions:**, **Approach narration:**, **Stuck and
recovery:**, **Test cases:**, **Verdict:**) filled in and free of placeholder text.

## Stretch

Run a second timed rep immediately. This time, set the timer for thirty minutes and
choose a task you have not attempted yet. After the rep, compare the two **Verdict:**
audits: did the same failure mode appear twice? If so, that is the drill target for
your next practice session outside this module. If you had a different failure mode,
you have a map of two distinct gaps. Prioritize the one that would be most visible
to an interviewer.
