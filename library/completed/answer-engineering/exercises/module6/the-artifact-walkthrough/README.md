# Exercise: The Artifact Walkthrough

**Goal:** Choose one artifact from your Sans Python portfolio and write the **Artifact:** and
**Overview:** fields in your `exercises/prep/portfolio-narrative.md` entry. The overview is a
sixty-second spoken narrative leading with the artifact's differentiator.

**Why:** An interviewer asking "walk me through a project" is not asking for a feature list.
They are testing whether you understand the reasoning behind your own design. The artifact
walkthrough is the entry point for every portfolio question: it has to land in sixty seconds,
it has to lead with the decision that separates a prepared candidate from one who only shipped
the code, and every field that follows in the dossier hangs off it. You cannot strong-answer
a portfolio question if you cannot name the differentiator in the opening sentence.

## Steps

1. Copy `exercises/prep/portfolio-narrative.template.md` to `exercises/prep/portfolio-narrative.md`.
   Do not fill in all fields now -- this exercise covers the first two fields only.

2. Choose one artifact from the Sans Python portfolio. Strong candidates for a sixty-second
   opening:
   - The Terminal Coding Agent (lead with the verification gate that defaults to REJECT)
   - The Production RAG Chatbot (lead with the citation-and-refusal contract)
   - Any other artifact you shipped that has a load-bearing decision you can name in one sentence

   If you are uncertain which to pick, pick the one where you can immediately name the decision
   that a weak candidate would skip. That is the differentiator.

3. Write the **Artifact:** field: the artifact name plus one sentence describing what it does.
   Keep it factual and concrete. Do not write a marketing sentence.

4. Write the **Overview:** field: your sixty-second spoken walkthrough. Structure:
   - Sentence 1: what the artifact does (functional role, not the technology)
   - Sentence 2: the differentiator -- the one decision or design property that a weak candidate
     would skip or state only generically
   - Sentence 3-4: what that decision protects against (the failure mode) and what it cost
     (the tradeoff)
   - Closing sentence: one concrete outcome or gate that proves the artifact works

   Speak it out loud before writing it. Time it. A sixty-second overview delivered at normal
   pace is roughly 120-150 words. If you run over 180 words, cut. If you run under 90 words,
   you have not earned the decision yet.

5. Read the overview back and ask: could a candidate who memorized the README give this answer?
   If yes, your differentiator is not specific enough. Name the design decision by its mechanism,
   not by its category. "The verification gate defaults to REJECT and runs the real test suite"
   is specific. "I made sure it was robust" is not.

## Done When

`exercises/prep/portfolio-narrative.md` exists and contains:
- The **Artifact:** field filled in with a name and a one-sentence description (no placeholder text)
- The **Overview:** field filled in with a sixty-second walkthrough leading with the differentiator
  (no placeholder text)

The remaining five fields may still contain placeholder text; the validator does not check this
file until `--module 6`. Move on to the next exercise once these two fields are written.

## Stretch

Write the sixty-second overview a second time without looking at the first version. Compare the
two. Which phrasing of the differentiator is crisper? Which failure mode lands harder? Keep the
stronger version. The comparison is the coaching -- your own revision instinct is the right signal.
