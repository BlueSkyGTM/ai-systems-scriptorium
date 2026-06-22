# Exercise: Foreground the Decisions

**Goal:** Write the **Key decisions:**, **Tradeoffs:**, and **Failure modes handled:** fields
in your `exercises/prep/portfolio-narrative.md` entry. Each decision gets a four-part defense:
the decision, the alternative rejected, the tradeoff accepted, and the failure mode guarded.

**Why:** An interviewer probing a portfolio artifact is not satisfied by a description of what
it does. They push until they find a decision that could have gone the other way. A candidate
who can only say "I chose X" gets a weak signal. A candidate who says "I chose X over Y because
Z, and that choice accepts the cost of W but structurally blocks failure mode F" is
demonstrating the reasoning that separates a senior engineer from a junior one. This exercise
trains that four-part defense until it is automatic.

## Steps

1. Open `exercises/prep/portfolio-narrative.md` and read your **Artifact:** and **Overview:**
   fields from the prior exercise. You are continuing that entry; do not start over.

2. List at least two load-bearing decisions from your chosen artifact. A decision is
   load-bearing if:
   - A different choice would have changed the architecture, not just the implementation
   - You can name a concrete alternative you rejected
   - The choice defends against a failure mode you can name

   If you cannot satisfy all three conditions for a decision, it is not load-bearing enough.
   Drop it and find one that is.

3. For each decision, write a four-part defense in your **Key decisions:** field:
   - **Decision:** what you chose (the mechanism, not the category)
   - **Rejected:** the specific alternative you did not choose
   - **Tradeoff:** what the decision costs -- what you gave up or what gets harder
   - **Failure mode:** what concrete failure the decision structurally prevents

   Write the four parts in the order above. Do not summarize -- name the mechanism each time.
   "Schema-validated tool dispatch refusing path-traversal" is a mechanism. "Better security"
   is a category.

4. Write the **Tradeoffs:** field as a summary of the costs across all your decisions. At least
   two sentences: what you gave up and why that cost was worth it given your constraints. This
   is not a repeat of step 3 -- it is the synthesis: which tradeoffs compound, which are
   independent, and which you would revisit if the constraints changed.

5. Write the **Failure modes handled:** field. Name at least two concrete failure modes your
   design guards against, each in one sentence. A failure mode is concrete when a weak candidate
   running the same code would encounter it in production. "It could be slow" is not concrete.
   "The agent loops without a budget cap, billing until the account is empty (Denial of Wallet)"
   is concrete.

6. Stress-test your three fields: read each decision aloud and ask "could a weak candidate give
   this answer?" If the answer is yes, the decision is stated at the category level, not the
   mechanism level. Find the specific name.

## Done When

`exercises/prep/portfolio-narrative.md` contains:
- The **Key decisions:** field with at least two four-part defenses (no placeholder text)
- The **Tradeoffs:** field with a synthesis of costs and why they were worth accepting
  (no placeholder text)
- The **Failure modes handled:** field with at least two concretely named failure modes
  (no placeholder text)

The remaining fields (**Role tailoring:** and **Audit verdict:**) may still contain placeholder
text. Move on to the next exercise.

## Stretch

Add a third load-bearing decision to your **Key decisions:** field -- one from a different layer
of the architecture than your first two (e.g. if your first two are about the model seam and the
budget, the third could be about the evaluation gate or the data contract). Breadth across
architectural layers shows the candidate understands the system, not just the component they
spent the most time on.
