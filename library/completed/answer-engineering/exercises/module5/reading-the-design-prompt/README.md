# Exercise: Reading the Design Prompt

**Goal:** Choose one open-ended AI system design question and write the **Prompt:** and **Scope:**
fields of your first entry in `exercises/prep/systems-design-log.md`.

**Why:** Systems design interviews fail before the first component is drawn. The interviewer
gives a one-sentence prompt; the candidate who jumps straight into architecture has already lost
the S and P phases of SPIDER. The S phase (Scope and Clarify) and P phase (Prioritize
Requirements) are what turn a vague prompt into a tractable design. This exercise builds the
habit of reading the prompt, narrowing the problem space, and naming your priorities out loud
before drawing anything. Everything downstream -- your component choices, your latency budget,
your eval strategy -- is only coherent if Scope and Prioritize are solid.

## Steps

1. Open `exercises/prep/systems-design-log.md`. If it does not exist, copy
   `exercises/prep/systems-design-log.template.md` to `exercises/prep/systems-design-log.md`.
   You will fill this entry in across all four Module 5 exercises. Do not delete the stub fields
   for the other exercises yet.

2. Choose your design question. Pick one of the following (or propose your own to your coach):

   - "Walk me through the architecture of a production RAG system."
   - "Design a customer support chatbot for an e-commerce company handling 10,000
     conversations per day."
   - "Design an evaluation pipeline for a production LLM product used by 50,000 daily users."
   - "Design a content moderation system for a social platform handling 1 million posts per day."
   - "Design the memory and state system for a personal AI assistant that works with a user over
     months."

   The question you choose is the one you will take all the way through the four exercises. Pick
   one that exposes real tradeoffs across cost, latency, reliability, and evaluation -- not one
   you can answer comfortably from memory.

3. Write the **Prompt:** field: copy the question verbatim into the field. One sentence. Do not
   paraphrase -- you will reference the exact words during the scope phase.

4. Run the SPIDER S phase. Ask the six clarifying questions out loud (or write them down) as if
   you were in the room:
   - What is the scale? (users, requests per day, data volume)
   - What are the latency requirements?
   - What accuracy or quality bar must the system meet?
   - Are there compliance or security requirements?
   - What existing infrastructure can be assumed?
   - What is the budget constraint?

   Invent reasonable answers for a mid-size production company if the question does not specify.
   State them as assumptions. Write them down.

5. Run the SPIDER P phase. From your scoping answers, name your priorities explicitly:
   - Which two or three requirements are load-bearing? (latency, cost, accuracy, isolation,
     compliance -- pick the ones that constrain the most design decisions)
   - Which requirements are second-order? (you will address them but they do not drive the
     high-level architecture)

6. Write the **Scope:** field: three to six bullet points summarizing requirements, scale,
   constraints, and your stated priorities. Each bullet is one concrete fact or decision, not a
   vague description. Include at least one number (a scale figure or latency target) and at
   least one explicit priority statement ("I will prioritize X over Y because...").

## Done When

The **Prompt:** field and **Scope:** field in `exercises/prep/systems-design-log.md` are filled
in, free of placeholder text, and contain at least one number and one explicit priority
statement. You can verify by opening the file and reading the two fields; the validator will
check them when you run `--module 5` after the fourth exercise.

## Stretch

Before moving to the next exercise, read your Scope field aloud as if presenting to an
interviewer. Does it produce numbers the rest of the design can reference? Could a weak
candidate have produced the same scope by restating the prompt? If yes to either, tighten it.
