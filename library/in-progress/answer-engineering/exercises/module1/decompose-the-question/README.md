# Exercise: Decompose the Question

**Goal:** Open your prep dossier and run the three-part decomposition on ten real interview questions, then write a calibration section naming which signal categories you read well and which you misread.

**Why:** Every step in the Algorithm depends on reading the signal correctly. A confident, wrong decomposition produces an answer that lands clean but misses the target. This exercise builds the habit before you need it under pressure.

## Steps

1. Copy `exercises/prep/decomposition-log.template.md` to `exercises/prep/decomposition-log.md`. Read the worked example entry at the top; your entries follow the same format exactly.

2. Work through all ten questions below in order. For each one, write three things:

   - **Literal parse:** strip the framing words ("tell me about," "walk me through," "describe a time"). State the noun and verb that remain, and any constraint or context the question specifies.
   - **Signal category:** choose one primary category from the four: Ownership, Judgment Under Uncertainty, Technical Depth, Communication/Influence. If you see a blend, name the primary first and note the secondary in parentheses.
   - **Primary hypothesis:** one sentence in the form "The interviewer is trying to determine whether [specific candidate claim]." Make it specific enough that you could build an answer directly from it.

   Work each question before reading the next. Do not revise your entries after the fact.

3. The ten questions:

   ```
   Q1.  Tell me about a time you strongly advocated for a technical
        decision that turned out to be wrong.

   Q2.  Walk me through the architecture of a production RAG system.

   Q3.  Describe a time you raised a concern and the team decided
        against you. What did you do?

   Q4.  When would you choose RAG over fine-tuning, and vice versa?

   Q5.  How do you explain AI limitations to non-technical colleagues?

   Q6.  Tell me about a time you led a technical initiative without
        formal authority.

   Q7.  Explain the ReAct pattern and its failure modes.

   Q8.  Design a document Q&A system for a 10,000-employee company.

   Q9.  Tell me about a difficult technical decision you made with
        incomplete information.

   Q10. Describe a situation where you had to convince others to
        adopt a new approach.
   ```

   These questions span all four signal categories. At least one is a systems-design prompt and requires an extra decomposition move: before naming the architecture, state the production constraints the design must honor (scale, latency, accuracy bar, compliance).

4. After completing all ten entries, write a calibration section at the end of the log. Cover three things in three to five sentences: which signal category you most consistently read correctly, which you misread or underweighted, and what pattern led you to assign the wrong primary signal. Be direct; this section is for you.

## Done When

Run this from the `exercises/prep/` directory:

```
python check_prep.py
```

The validator checks `decomposition-log.md` for ten entries, each with all three required fields filled in and no placeholder text left behind. It exits 0 when the log is complete.

## Stretch

Pick three questions and decompose each one twice more: once as if asked to a senior IC, and once as if asked to a staff engineer. Write how the primary hypothesis shifts with the seniority level. A question that collects Technical Depth at senior may collect Ownership or Communication/Influence at staff; state where the shift is and why.
