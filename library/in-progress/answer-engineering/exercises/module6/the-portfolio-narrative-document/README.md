# Exercise: The Portfolio Narrative Document

**Goal:** Finish the `exercises/prep/portfolio-narrative.md` document, run the weak-walkthrough
audit against your completed entry, write the **Audit verdict:** field, and run the validator to
confirm the entry is complete.

**Why:** All prior exercises in this module built your walkthrough in layers. This exercise
closes the loop: you audit your own entry against the weak-walkthrough red flags before an
interviewer does, then run the validator as a structural gate. The audit is what distinguishes a
prepared candidate from one who practiced without feedback. The validator exit confirms the entry
is complete and the full M6 dossier is clear.

## Steps

1. Open `exercises/prep/portfolio-narrative.md` and read the entire entry. All six prior fields
   should be filled in from the preceding exercises. Do not re-write them here. Read them as a
   unit and note which fields feel thin.

2. Run the weak-walkthrough audit. The named red flags from the lesson are:

   - **Generic lead:** the overview opens with what the artifact is (a chatbot, an agent) rather
     than what it decides
   - **No rejected alternative:** decisions are stated without naming what was not chosen
   - **Tradeoffs as positives:** the tradeoff field only says what the decision gives you, not
     what it costs
   - **Failure modes as categories:** failure modes are named at the level of "it could fail" or
     "it could be slow" rather than the concrete failure mechanism
   - **Role tailoring is repetition:** the two role framings open with the same sentence or the
     same decision
   - **Underpowered Overview:** the sixty-second overview could be given by a candidate who only
     read the README, not one who built and operated the artifact

   For each red flag, decide: does your entry pass or risk it? Be specific. "I risk Generic lead
   because my Overview opens with 'I built a RAG chatbot' rather than the citation-and-refusal
   contract" is a diagnosis. "I could be more specific" is not.

3. Fix any field that fails the audit before writing the verdict. The audit is not a
   retrospective report; it is a gate. Do not write the verdict over a field that you know is thin.

4. Write the **Audit verdict:** field. It must include:
   - Which red flags your entry passes (name them from the list above)
   - Which red flags your entry risks or fails (name them and why)
   - The one specific change you would make if you had two more minutes (name the field, the
     sentence, or the mechanism; not a general improvement)

5. From `exercises/prep/`, run:

   ```
   python check_prep.py --module 6
   ```

   The validator checks that all seven fields in your `portfolio-narrative.md` entry are filled
   in and free of placeholder text, and that all prior dossier artifacts (M1, M2, M3, M5) are
   also complete. Exit 0 means the full Module 6 gate is cleared.

## Done When

```
python check_prep.py --module 6
```

exits 0 from `exercises/prep/`. This requires that your `portfolio-narrative.md` entry is
complete (all seven fields filled, no placeholder text) and that all prior dossier artifacts
(M1, M2, M3, M5) are also complete.

## Stretch

Write a second entry in `portfolio-narrative.md` for a different artifact from the portfolio
bank. The second entry is a `## Artifact 2` block with the same seven fields. Compare the two
**Overview:** fields: which differentiator is stronger? Which decision set has more depth?
The comparison exposes which artifact you understand more deeply -- that is usually the one you
should lead with in an interview. Add a note after the second entry naming which artifact you
would lead with and why.
