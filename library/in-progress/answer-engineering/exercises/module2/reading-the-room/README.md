# Exercise: Reading the Room

**Goal:** Create `exercises/prep/signal-map.md` by mapping three real interview questions across two company contexts, writing the stated signal, the latent signal, and how the interviewer's emphasis shifts depending on where you are interviewing.

**Why:** The same question collects a different real signal at a frontier lab and at an enterprise. An answer calibrated to the stated signal alone lands clean in one context and wide of the mark in the other. Mapping the latent signal before you answer protects you from giving the right answer to the wrong question.

## Steps

1. Copy `exercises/prep/signal-map.template.md` to `exercises/prep/signal-map.md`. Read the worked example entry; your entries follow the same format.

2. Complete three entries (SM1, SM2, SM3) using these questions from the taxonomy ingredient:

   - **SM1:** "Tell me about a time you raised an ethical concern."
   - **SM2:** "Describe a time you raised a concern and the team decided against you. What did you do?"
   - **SM3:** "How do you work with researchers who have different priorities?"

3. For each entry, write four things:

   - **Stated signal:** the signal category the question appears to collect on first parse. One phrase: "Ownership" or "Communication/Influence (primary), Judgment (secondary)."
   - **Latent signal:** what the question actually probes beneath the surface. One to two sentences. Think about what a weak answer exposes that the stated signal alone does not.
   - **Frontier lab context:** how the emphasis shifts when you are interviewing at a company like Anthropic, OpenAI, or xAI. What does the interviewer weight differently at this tier, and why?
   - **Enterprise context:** how the emphasis shifts at a company like Deloitte, Citi, or Caterpillar AI. What does the interviewer need to hear that a frontier-lab frame would miss?

4. Use the context signals from the lesson: frontier labs weight mission alignment, responsible AI judgment, and safety reasoning; enterprises weight governance fluency, compliance awareness (SOC 2, HIPAA, EU AI Act), and customer-facing communication. The context does not change which primary signal is collected; it changes what a strong answer must demonstrate to pass.

5. After writing all three entries, run the validator to check your work before you call it done.

## Done When

Open `exercises/prep/` and run:

```
python check_prep.py --module 2
```

The validator exits 0 when `signal-map.md` contains at least three `### SM<n>` entries, each with a `**Stated signal:**`, `**Latent signal:**`, `**Frontier lab context:**`, and `**Enterprise context:**` field filled in and no placeholder text. It exits 1 if any field is empty, missing, or contains a placeholder.

## Stretch

Add a fourth entry using a systems-design question from the taxonomy ingredient (for example: "Design a document Q&A system for a 10,000-employee company."). The stated/latent signal split is different for design prompts: state the clarifying questions you would ask in the `S` phase of SPIDER, then explain how the interviewer's response to each clarifying question is itself a signal about what the company is actually probing.
