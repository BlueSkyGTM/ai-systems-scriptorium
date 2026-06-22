# Exercise: Justify Every Box

**Goal:** Draw the high-level architecture for your chosen design and write the **Design:**
field of your entry in `exercises/prep/systems-design-log.md`. Every component you draw must
have a one-sentence justification.

**Why:** The SPIDER I phase (Initial Architecture) is where most candidates lose points without
knowing it. They draw boxes connected by arrows and name the components correctly -- but they
cannot explain why each component is there, what problem it solves, and what the alternative
was. An interviewer probing "why this component?" after the I phase is not being difficult; they
are checking whether you designed the system or just recalled a diagram. This exercise trains
the justification habit: every box earns its place before you move to the deep dive.

## Steps

1. Open `exercises/prep/systems-design-log.md`. Read the **Prompt:** and **Scope:** fields you
   wrote in the previous exercise. Your architecture must be a direct response to those fields.
   If your Scope says latency is load-bearing, your architecture must address latency. If it
   says compliance is a constraint, your architecture must address compliance.

2. Sketch the high-level architecture. Use pencil-and-paper, a whiteboard, or any diagramming
   tool. Draw from input to output: what does the system receive, what components process it,
   and what does the system return? A standard AI system has at minimum: a client-facing entry
   point, an AI layer (model calls, prompt assembly, tool use), and a data layer (retrieval,
   storage, indexing). Your design may have more.

   Name every box. Name every arrow. Keep the sketch at the level of named components, not code
   or API calls. You will deep-dive specific paths in later exercises.

3. For each component, write one sentence that states:
   - What it does in this system (not a generic description of the technology)
   - Why it is needed here (what problem it solves for this specific prompt and scope)
   - What the alternative was and why you did not use it

   This is harder than it looks. "Vector database to store embeddings" is not a justification.
   "Pinecone for vector storage because the 2M-document corpus requires ANN search at sub-100ms
   query latency, which a relational database cannot provide" is a justification.

4. Watch for the named architectural failure modes from the lesson. Before finalizing your
   component list, check:
   - Does your design skip the data pipeline? (Pitfall 1: embeddings do not appear magically;
     name your ingestion, chunking, and indexing components)
   - Does your design use a single model for everything? (Pitfall 2: name your model tier or
     routing strategy)
   - Does your design ignore evaluation? (Pitfall 3: include at least a placeholder for how
     you will know the system works)

5. Write the **Design:** field in `exercises/prep/systems-design-log.md`. Format it as a list
   of components, each followed by its one-sentence justification. At minimum, name every
   component you drew. Do not write prose paragraphs -- write the list.

## Done When

The **Design:** field in `exercises/prep/systems-design-log.md` is filled in, free of
placeholder text, and contains at least three named components each with a one-sentence
justification that includes both what the component does and why it was chosen over an
alternative. The **Prompt:** and **Scope:** fields from the previous exercise remain unchanged.

## Stretch

After writing your component list, pick the component whose justification is the weakest -- the
one where you wrote "because it is standard" or "because it is commonly used." Rewrite that
justification to name the specific constraint from your **Scope:** field that the component
addresses. If you cannot name the constraint, the component may not be load-bearing. Consider
removing it or replacing it with something that is.
