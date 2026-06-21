# Exercise: Failure Stories

**Goal:** Write one of your own Failure stories into `exercises/prep/behavioral-bank.md`, run the full four-step Algorithm on it, run the M2 weak-answer audit, and record the result.

**Why:** The Learning step is the load-bearing move in a Failure story. An answer that ends at Result ("and then we rolled it back") reads as low-reflection. The interviewer is not looking for a polished success that happened to have complications; they are looking for evidence that you extracted a generalizable lesson and changed something. Every candidate has a failure story. Most of them stop at Result. This exercise forces the Learning step.

## Steps

1. Open `exercises/prep/behavioral-bank.md`. Locate the Failure stub (headed `## Story <n>` with `**Category:** failure`).

2. Choose your story. The Failure category probes three sub-signals: taking responsibility, root cause analysis, and systems thinking about prevention. The real questions you may be asked include:

   - "Tell me about an AI system that did not work as expected."
   - "Describe a time you shipped something that had issues."
   - "Describe a project that failed. What happened and what did you learn?"
   - "How do you handle a model that performs poorly in production?"
   - "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong."

   Pick the failure that is honestly yours: a decision you drove, a call you owned, a system you built that did not behave as you said it would. The interviewer's preparation checklist (from the ore) says explicitly: include at least one story where you were wrong. Not one where the project was hard. Where you were wrong.

3. Write the five STAR-L fields. The most common underwrite is Situation: candidates describe a vague context that makes it impossible to assess their individual role. Name the project, the timeline, and your specific responsibility within it.

   For the Learning step: name a specific change in your practice, process, or architecture standard that came out of this failure. "I learned to test more carefully" fails the bar. "I now require a stratified test set that matches production user distribution before any model launch" passes it. The named change is the signal.

4. Run the four-step Algorithm on your story against the question that best fits it from the list above. Record it as a new `## A<n>` entry in `answers-log.md`.

5. Run the M2 weak-answer audit. The two failure modes most specific to this category are:

   - **No Learning step:** the answer ends at Result. The Algorithm requires a Learning step; the audit confirms it is present and named, not abstract.
   - **Polished excuse instead of honest scoping:** the failure is framed as almost-a-success or as beyond your control. An honest Failure story names the moment you knew it was wrong and what you did next. The ore's positive model: "I did not hide the problem. I immediately flagged it to leadership with the data showing the gap."

   Record your audit result in the `**Audit verdict:**` field: which pitfalls are present, basic bar verdict, staff bar verdict, and the one specific thing you added after the audit.

## Done When

From `exercises/prep/`, run:

```
python check_prep.py --module 3
```

The validator exits 0 when `behavioral-bank.md` contains at least four story entries across all four categories (ownership, conflict, failure, influence), each with the five STAR-L fields and an `**Audit verdict:**` field filled in and no placeholder text. Complete all four category exercises before running `--module 3`.

## Stretch

Take your Failure story and identify the staff bar signal: did the Learning step produce an organizational artifact? A personal lesson ("I now attach kill criteria") is senior. An organizational artifact ("the postmortem produced a new team rule that any architecture pitch must include a cost model under realistic update patterns") is staff. If your story does not have the organizational artifact, write what it would have been. If it does, identify who other than you it changed and how.
