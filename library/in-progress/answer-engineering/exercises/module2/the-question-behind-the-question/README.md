# Exercise: The Question Behind the Question

**Goal:** Extend your decomposition log with a Hard Cases section that re-decomposes three real questions at two seniority levels, showing exactly how the primary hypothesis shifts from senior to staff.

**Why:** The three-part decomposition you ran in Module 1 assumes a clean, neutral framing. Real questions are not neutral: the same words collect a different signal depending on whether you are interviewing for a senior IC role or a staff role. If you miss the level dependency, you answer the right question for the wrong audience.

## Steps

1. Open `exercises/prep/decomposition-log.md`. Read your existing Q1-Q10 entries. You are continuing this file, not starting a new one.

2. Append a new `## Hard Cases` section to the bottom of `decomposition-log.md`. The exact heading is required; the validator checks for it.

3. Inside `## Hard Cases`, add three sub-entries, one for each question below. Use this format exactly:

   ```
   ### HC1

   **Question:** <the question text>

   **Senior reading:**

   **Primary hypothesis (senior):** The interviewer is trying to determine whether...

   **Staff reading:**

   **Primary hypothesis (staff):** The interviewer is trying to determine whether...

   **How the hypothesis shifts:** <one to two sentences on what changes and why>
   ```

4. Use these three questions (all from the taxonomy ingredient):

   - **HC1:** "Tell me about a time you led a technical initiative without formal authority."
   - **HC2:** "Describe a time you raised a concern and the team decided against you. What did you do?"
   - **HC3:** "Tell me about a time you strongly advocated for a technical decision that turned out to be wrong."

5. Apply the leveling principle from the lesson. The shift across levels follows three axes:
   - **Scope:** senior owns a system or feature; staff owns a platform other engineers build on.
   - **Multiplying others:** senior demonstrates high individual output; staff demonstrates what changed for the team as a result.
   - **Governance:** senior makes defensible decisions under uncertainty; staff architects for non-deterministic systems and names the organizational artifact (a process, a standard, a rubric) that came out of the work.

   A senior answer for HC1 might center on "I shipped X without formal authority." A staff answer for the same question centers on "I changed what my team could ship, and here is the organizational artifact that came out of it."

6. Write your own hypotheses before looking at your Module 1 entries for context. The exercise is in the comparison, not in reusing your prior wording.

## Done When

Open `exercises/prep/` and run:

```
python check_prep.py --module 2
```

The validator exits 0 when `decomposition-log.md` contains a `## Hard Cases` section with at least three `### HC<n>` entries, each with a `**Senior reading:**`, `**Primary hypothesis (senior):**`, `**Staff reading:**`, `**Primary hypothesis (staff):**`, and `**How the hypothesis shifts:**` field filled in and no placeholder text.

## Stretch

Add a fourth Hard Case using a question you found genuinely ambiguous during Module 1 (pick from your own Q1-Q10). Write the senior and staff readings, then add a `**Curveball framing:**` field: state one way an interviewer could re-frame the same question to force a different primary signal, and explain what the re-framing reveals.
