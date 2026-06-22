# Exercise: Conflict Stories

**Goal:** Write one of your own Conflict stories into `exercises/prep/behavioral-bank.md`, run the full four-step Algorithm on it, run the M2 weak-answer audit, and record the result.

**Why:** Conflict questions are not about winning arguments. They probe whether you can operate constructively after an argument's outcome, whether you disagreed and committed, or disagreed and converted. A candidate who cannot name the specific move they made after the disagreement has told a grievance story, not a collaboration story. This exercise builds the one Conflict story you need before the room.

## Steps

1. Open `exercises/prep/behavioral-bank.md`. Locate the Conflict stub (headed `## Story <n>` with `**Category:** conflict`).

2. Choose your story. The Conflict category probes: did you find the shared frame, or did you just survive the friction? The real questions you may be asked include:

   - "Tell me about a disagreement with a colleague about a technical approach."
   - "Describe working with a team that had different priorities."
   - "Tell me about a conflict with a product manager over AI capabilities."
   - "Describe a time you raised a concern and the team decided against you. What did you do?"
   - "Describe working with someone who had a very different working style."
   - "Tell me about a time you had to say no to a stakeholder request."

   You are not answering one of these yet. You are finding the story from your own experience that best fits the category. The strongest Conflict story names the concrete mechanism you used to reach alignment or convert a lost argument, not just that alignment happened.

3. Write the five STAR-L fields. The field most candidates underwrite is Action: the interviewer wants to know the specific move, not that you "had a conversation" or "aligned on priorities." Name the mechanism: the collaboration structure you proposed, the evidence you brought, the mitigations you asked for inside the launch window, the thing you documented.

   The Learning step for a Conflict story should name what you now carry forward about working across disagreement, not just what you learned about the specific project.

4. Run the four-step Algorithm on your story against the question that fits it best from the list above. Record it as a new `## A<n>` entry in `answers-log.md`.

5. Run the M2 weak-answer audit. Pay particular attention to two failure modes that are common in Conflict stories:

   - **No relationship outcome:** a story that ends at the decision without addressing what happened to the working relationship. Ask yourself: what was the relationship like after?
   - **Vague "we aligned":** an Action step that names the outcome of alignment but not the move that produced it. If your Action step could be summarized as "we talked it through and agreed," it needs a concrete mechanism.

   Record your audit result in the `**Audit verdict:**` field: which pitfalls are present, basic bar verdict, staff bar verdict, and the one specific thing you added after the audit.

## Done When

From `exercises/prep/`, run:

```
python check_prep.py --module 3
```

The validator exits 0 when `behavioral-bank.md` contains at least four story entries across all four categories (ownership, conflict, failure, influence), each with the five STAR-L fields and an `**Audit verdict:**` field filled in and no placeholder text. Complete all four category exercises before running `--module 3`.

## Stretch

Take your Conflict story and reframe it as a Technical Influence story. What would you need to change in the Action or Learning step to move the emphasis from "we reached agreement" to "I changed what the team could do afterward"? Write the reframed Learning step and compare it to your original. This is the move that separates a senior answer from a staff answer.
