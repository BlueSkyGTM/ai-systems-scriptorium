# Exercise: Production Reasoning as the Differentiator

**Goal:** Write the **Cost:**, **Latency:**, **Reliability:**, and **Evaluation:** fields of
your entry in `exercises/prep/systems-design-log.md`, and name at least one tradeoff between
any two of the four pillars.

**Why:** A merely-senior candidate optimizes one dimension -- usually latency or cost -- and
treats the others as background assumptions. A staff candidate threads all four pillars together
and names the tradeoff when they conflict. This exercise is where your design becomes an
argument, not a diagram. The SPIDER E and R phases (Evaluation and Reliability) are the phases
most candidates reach last and execute thinnest. This exercise makes you build those phases with
the same rigor as the architecture.

## Steps

1. Open `exercises/prep/systems-design-log.md`. Read the **Prompt:**, **Scope:**, and
   **Design:** fields. The four fields you write now must be grounded in the constraints and
   components you already wrote. Do not introduce new components here; connect the production
   reasoning to what is already in the design.

2. Write the **Cost:** field. Your reasoning must include:
   - Which model tier or routing strategy you are using, and why (name the models; say what
     queries they handle and approximately what they cost per request)
   - What your dominant cost driver is (input tokens, output tokens, retrieval calls, compute)
   - What caching strategy you are using (semantic cache, prefix cache, or none) and why
   - One named tradeoff: where does optimizing for cost conflict with another pillar? Name the
     specific tension and state which side you chose and why.

3. Write the **Latency:** field. Your reasoning must include:
   - Your p95 latency target (from your Scope, or stated as an assumption)
   - A latency budget: the sum of each component's estimated contribution. The budget must add
     up to at most your p95 target. Use real numbers; do not write "fast" or "low latency."
   - One named tradeoff: where does hitting the latency target conflict with another pillar?
     Name the specific tension.

4. Write the **Reliability:** field. Your reasoning must include:
   - The two or three failure modes most likely in your specific design (LLM provider outage,
     retrieval returning nothing, data pipeline lag -- name the ones that apply to your system)
   - Your graceful degradation strategy: what does the system do in each failure mode? A ladder
     from full capability to minimal capability to offline is a strong pattern.
   - One named tradeoff: where does a reliability measure conflict with another pillar?

5. Write the **Evaluation:** field. Your reasoning must include:
   - Your offline eval strategy: what dataset, what metrics, and how you gate deploys
   - Your online monitoring approach: what you sample, what metrics you trend, and what triggers
     a human review
   - How you would know the system was silently degrading without a user complaint

6. Verify that you have named at least one tradeoff across pillars. A tradeoff must name both
   sides: "Reranking adds 150ms to p95 latency (hurts Latency) but raises retrieval hit rate
   from 70% to 90% (improves quality and reduces downstream generation cost)" is a tradeoff.
   "Reranking is expensive" is not.

## Done When

The **Cost:**, **Latency:**, **Reliability:**, and **Evaluation:** fields in
`exercises/prep/systems-design-log.md` are filled in, free of placeholder text, each field
contains at least one number, and at least one cross-pillar tradeoff is named anywhere across
the four fields. The **Prompt:**, **Scope:**, and **Design:** fields remain unchanged.

## Stretch

After writing the four fields, identify the weakest pillar -- the one where your reasoning is
the most generic and could apply to any system. Rewrite that field's tradeoff statement so it
references a specific component from your **Design:** field and a specific number from your
**Scope:** field. If you cannot ground the tradeoff in your specific design, it is not a
production reasoning move -- it is a template.
