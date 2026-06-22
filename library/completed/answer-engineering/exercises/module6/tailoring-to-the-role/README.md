# Exercise: Tailoring to the Role

**Goal:** Write the **Role tailoring:** field in your `exercises/prep/portfolio-narrative.md`
entry. The field contains two framings of the same artifact for two different roles: the same
decisions, different emphasis and lead.

**Why:** The same artifact does not tell the same story to every interviewer. An applied-AI
engineer wants to know whether the system stays reliable in production for users. An ML-platform
engineer wants to know whether the seams are clean and the system is operable. A research-adjacent
engineer wants to know whether the evaluation is rigorous. None of them is wrong. You are not
changing your decisions to match the interviewer; you are leading with the decision they most
care about. This exercise trains the skill of reading the room and opening in the right register
without inventing a different project.

## Steps

1. Open `exercises/prep/portfolio-narrative.md` and read your full entry so far: **Artifact:**,
   **Overview:**, **Key decisions:**, **Tradeoffs:**, and **Failure modes handled:**. You are
   adding to this entry; do not start over.

2. Identify two roles this artifact speaks to. Use the distinctions below as a starting point,
   but match to roles you are actually applying to:
   - **Applied-AI / product engineer:** cares about user-facing reliability, hallucination
     prevention, the citation or refusal contract, quality drift detection, the eval story
   - **ML-platform / infra engineer:** cares about the model seam, the data contract, the
     backend swap story, the budget/kill-switch governance, the deterministic gates that run in CI
   - **Research-adjacent / applied-science:** cares about the eval rigor, the precision and
     faithfulness metrics, the deterministic gate design, refusal behavior, drift detection

3. For each role, write a tailored opening: a two-to-three sentence version of the walkthrough
   that leads with the decision most relevant to that role. The decision set does not change.
   The emphasis and the lead change.

   Write your **Role tailoring:** field in this format:

   **[Role name]:** [Two-to-three sentences leading with the decision this role most cares
   about. Name the mechanism and the failure mode, not the category. End with one concrete
   outcome or gate.]

   Then a blank line, then:

   **[Role name]:** [Same structure for the second role.]

4. Read each tailored opening aloud and ask: does this lead with a decision the other role
   framing would not lead with? If both openings are nearly identical, you have not tailored --
   you have repeated. Identify the one sentence that differs and make it differ more.

5. Ask a second question: if the interviewer pressed with "why did you choose that approach over
   the alternative?" can you answer immediately from your **Key decisions:** field? If yes, the
   tailored opening is grounded. If you cannot answer without re-reading your notes, the tailored
   opening is floating above your actual work.

## Done When

`exercises/prep/portfolio-narrative.md` contains:
- The **Role tailoring:** field with two tailored framings in the format above (no placeholder text)
- Each framing is three sentences or fewer and leads with a different decision than the other

The remaining field (**Audit verdict:**) may still contain placeholder text. Move on to the
final exercise.

## Stretch

Write a third tailored framing for a role you are less certain about (e.g. an ML/AI safety
engineer, a TPM, an engineering manager). The exercise is in noticing where your current
**Key decisions:** coverage is thin: the role you struggle to frame is pointing at a gap in
the decisions you foregrounded. Add that gap to a note in your **Tradeoffs:** or **Failure
modes handled:** field.
