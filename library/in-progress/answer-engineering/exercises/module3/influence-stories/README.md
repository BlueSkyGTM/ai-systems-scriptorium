# Exercise: Influence Stories

**Goal:** Write one of your own Technical Influence story into `exercises/prep/behavioral-bank.md`, run the full four-step Algorithm on it, run the M2 weak-answer audit, and record the result.

**Why:** The staff bar is not a harder version of the senior bar; it is a different bar. Senior ICs are evaluated for what they shipped. Staff ICs are evaluated for whether they changed what other engineers could ship. The Technical Influence category is where that distinction lives. If your behavioral bank contains only Ownership, Conflict, and Failure stories, you have answered the senior interview. The Influence story is what answers the staff interview.

## Steps

1. Open `exercises/prep/behavioral-bank.md`. Locate the Technical Influence stub (headed `## Story <n>` with `**Category:** influence`).

2. Choose your story. The Technical Influence category probes: did the candidate leave an organizational artifact that outlasted the project? The real questions you may be asked include:

   - "Tell me about a time you led a technical initiative without formal authority."
   - "Describe a situation where you had to convince others to adopt a new approach."
   - "Tell me about a time you raised an ethical concern."
   - "Describe a situation where you prioritized safety over speed."
   - "How do you explain AI limitations to non-technical colleagues?"
   - "Describe a time you raised a concern and the team decided against you. What did you do?"

   The organizational artifact is the discriminant: a process, a standard, a pattern, a template, a set of metrics that changed what the team could do after you. "I convinced my team" is not the artifact. "I proposed the collaboration structure, which became the template we now use for research-to-production handoffs" is the artifact.

3. Write the five STAR-L fields. Two fields need special attention in this category:

   - **Action:** name the specific mechanism of influence. Not "I persuaded them" but the concrete move: the quantified risk framing, the two alternatives with tradeoffs, the collaboration structure with co-authorship credit, the cheap mitigations asked for inside the launch window. Influence through alignment of incentives is stronger than influence through argument-winning.
   - **Learning:** this is where you name the organizational artifact explicitly. What process, standard, or practice now exists that did not exist before? Who does it apply to other than you?

4. Run the four-step Algorithm on your story against the question that best fits it from the list above. Record it as a new `## A<n>` entry in `answers-log.md`.

5. Run the M2 weak-answer audit. The failure mode most specific to this category is stopping at the decision outcome: the story ends at "they agreed" or "I was overruled but committed" without naming the constructive action and the organizational artifact that followed. Check:

   - Does your Action step name the specific mechanism of influence?
   - Does your Result or Learning step name an organizational artifact?
   - Is the artifact concrete enough to name who it applies to and what they can now do differently?

   Record your audit result in the `**Audit verdict:**` field: which pitfalls are present, basic bar verdict, staff bar verdict, and the one specific thing you added after the audit.

## Done When

From `exercises/prep/`, run:

```
python check_prep.py --module 3
```

The validator exits 0 when `behavioral-bank.md` contains at least four story entries across all four categories (ownership, conflict, failure, influence), each with the five STAR-L fields and an `**Audit verdict:**` field filled in and no placeholder text.

## Stretch

Raise an ethical concern story is the hardest version of this category. If your Influence story is not an ethical concern story, write the first three STAR-L fields of one from your own experience. Stop at Action. Then: does your Action step frame the concern as a business and legal risk with proposed alternatives, or as a moral objection? The difference is what determines whether the concern lands. Revise until the framing is the former.
