# Exercise: Ownership Stories

**Goal:** Write one of your own Ownership stories into `exercises/prep/behavioral-bank.md`, run the full four-step Algorithm on it, run the M2 weak-answer audit, and record the result.

**Why:** The Algorithm trains on questions; the behavioral bank trains on stories. You need one story for each category that passes both the basic bar and the staff bar before the room. This exercise builds the first one. The work compounds directly from M1 (the Algorithm) and M2 (the audit): you are not learning new tools, you are loading them into a real story.

## Steps

1. Open `exercises/prep/behavioral-bank.md`. If the file does not exist, copy `exercises/prep/behavioral-bank.template.md` to `exercises/prep/behavioral-bank.md` and delete the worked example entry, leaving only the empty stubs.

2. Find the Ownership stub in the file (headed `## Story <n>` with `**Category:** ownership`). Read the five STAR-L fields. Your task is to fill them in with your own story, not a canned one.

3. Choose your story. The Ownership category probes one question: did you drive this, or did you watch it? The real questions you may be asked include:

   - "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong."
   - "Describe a project that failed. What happened and what did you learn?"
   - "Tell me about a time you led a technical initiative without formal authority."
   - "Tell me about a time you started an AI project with unclear requirements."
   - "Describe a situation where you changed direction mid-project."

   You are not answering one of these questions yet. You are finding the story from your own experience that would best answer several of them. The strongest Ownership story has a named decision that you personally drove, a concrete result or failure signal, and a Learning step that is a named change in your practice, not a platitude.

4. Write the five STAR-L fields for your story. Keep each one tight:

   - **Situation:** one to two sentences: the context that made this a real problem, not a routine task.
   - **Task:** one sentence: what you were personally responsible for in this situation.
   - **Action:** two to four sentences: what you specifically did, in first person. Every sentence starts with "I," not "We." Name the decisions you made, the things you built, the moves you made under pressure.
   - **Result:** one to two sentences: what changed. Name a metric, a timeline, or a concrete outcome. Do not end here.
   - **Learning:** one to two sentences: what you changed in your practice after this. Name the specific habit, rule, or process that came out of it. "I learned to..." is the minimum; "I now attach kill criteria to my own proposals" is the standard.

5. Run the four-step Algorithm on your story as if you are preparing to answer the question "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong" (or whichever question your story best fits). Record the four steps in your `answers-log.md` as a new `## A<n>` entry before the next step.

6. Run the M2 weak-answer audit. In the `**Audit verdict:**` field of your story entry in `behavioral-bank.md`, record:

   - Which pitfalls from the audit checklist your story risks (vague ownership, buried result, missing failure signal, no structural lesson).
   - Whether it passes the basic bar: could a weak candidate give this exact answer?
   - Whether it passes the staff bar: does the story contain an organizational artifact that changed what others could do?
   - The one specific thing you added or changed after the audit.

## Done When

From `exercises/prep/`, run:

```
python check_prep.py --module 3
```

The validator exits 0 when `behavioral-bank.md` contains at least four story entries across all four categories (ownership, conflict, failure, influence), each with the five STAR-L fields and an `**Audit verdict:**` field filled in and no placeholder text. Complete all four category exercises before running `--module 3`. After completing only this exercise, you can verify your entry is structurally correct by opening `behavioral-bank.md` and checking that the fields under your Ownership story are filled in.

## Stretch

Write a second Ownership story covering a different question from the list above. Compare the two stories side by side: which one contains a stronger staff-bar artifact, and which one would be harder for a weak candidate to fake? Use that comparison to decide which story to rehearse first.
