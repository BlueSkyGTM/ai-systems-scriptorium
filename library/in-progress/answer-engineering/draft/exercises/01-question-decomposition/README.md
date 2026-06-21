# Exercise: Question Decomposition Practice

## Goal

Run the three-part decomposition process on ten unseen interview questions, calibrate your
signal-reading against a rubric, and identify which signal categories you are consistently
reading correctly and which need more repetitions.

## Why

The decomposition step is the leverage point of the Algorithm. Every other step depends on it:
if you misidentify the primary signal, the best-constructed answer still misses the target.
This exercise builds the decomposition habit to the point where it runs automatically, before
you speak, without slowing you down.

## Steps

1. Open a new file called `decomposition-log.md` in this directory. You will record all ten
   decompositions here, one per section.

2. For each of the ten questions below, work through the three-part decomposition:

   - **Parse the literal components.** Strip the framing words. What noun and verb remain?
     What constraint or context is specified?
   - **Assign to a signal category.** Choose from: ownership, judgment under uncertainty,
     technical depth, communication/influence. If you see a blend, name the primary category
     first.
   - **Name the primary hypothesis.** Write one sentence: "The interviewer is trying to
     determine whether [candidate claim]." This sentence should be specific enough that you
     could build an answer directly from it.

3. The ten questions:

   ```
   Q1. Tell me about a technical decision you made that you would make differently today.
   Q2. How would you design a system to monitor an LLM in production for quality degradation?
   Q3. Describe a time you had to explain a model limitation to a non-technical stakeholder.
   Q4. Walk me through how you would choose between fine-tuning and RAG for a new feature.
   Q5. Tell me about a project that shipped late or not at all. What happened?
   Q6. How do you decide when an AI system is ready to replace a human in a workflow?
   Q7. Describe a time you disagreed with a technical direction but the team went ahead anyway.
   Q8. How would you build an eval pipeline for a multi-turn conversational agent?
   Q9. Tell me about a time you had to learn something quickly under production pressure.
   Q10. You are three days before a launch and your evaluation metrics show a regression.
        What do you do?
   ```

4. After completing all ten decompositions, compare each against the rubric in
   `decomposition-rubric.md` (provided in this directory). For each question, note: where your
   hypothesis matched the rubric's primary signal, where it diverged, and why.

5. In a final section of `decomposition-log.md`, write three to five lines:
   - Which signal category did you most consistently read correctly?
   - Which did you misread or underweight?
   - What pattern, if any, led you to assign the wrong primary signal?

## Done When

- All ten questions are decomposed with all three parts filled in (literal parse, category
  assignment, one-sentence hypothesis).
- Each decomposition has a rubric comparison note.
- The calibration section identifies at least one consistent strength and one consistent gap.
- The log is honest: mark any question where you were uncertain before you checked the rubric,
  not after.

## Stretch

Pick three questions from the list and run an additional decomposition step: what would change
about your hypothesis if the role level changed? Decompose each question as if it were being
asked to a senior IC, a tech lead, and a staff engineer. Write out how the primary hypothesis
shifts with the seniority level, and what that means for the answer you would construct.
