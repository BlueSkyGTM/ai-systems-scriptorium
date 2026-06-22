# Foreground the Decisions

The code is where the decisions left marks. The interview is about the decisions themselves.

An interviewer can read your repository. They can follow the retrieval chain, count the classes, and
trace the guardrail logic in five minutes. What they cannot read from your code is your judgment: why
this design instead of a simpler one, which alternative you considered and set aside, what would go
wrong if you had chosen differently. That judgment is what the walkthrough has to surface, because the
code alone does not carry it.

## Why Decisions Are the Signal

When an interviewer says "walk me through how the RAG system works," they are not asking for a class
diagram. They are testing whether you can tell the difference between a component you reached for by
habit and one you chose by reasoning. The candidate who explains every component as an obvious part of
a standard RAG pipeline scores the same as the candidate who reads the docstrings aloud. The candidate
who names a choice, the alternative it beat, and the failure mode it prevents scores higher, because
that narration cannot be faked from a tutorial.

The discipline here is identical to justifying every box in a systems-design round. In that context you
defend a component you just drew. In a portfolio walkthrough you defend a component you actually
shipped, which is easier: the decisions are already made, the failure modes already handled. The work is
foregrounding them, making the reasoning visible to someone who was not in the room when you made the
calls.

## The Shape of a Defended Decision

Every load-bearing component in your walkthrough earns its place through four moves.

First, name the decision: what you built and what it does. Second, name the alternative you rejected:
the simpler or more obvious path that you did not take. Third, name the tradeoff you accepted: what the
chosen design costs. Fourth, name the failure mode it guards against: the specific thing that goes wrong
if you had made the other choice.

That four-part shape is not a formula to recite. It is a test of whether you understand the component
you shipped. If you cannot name the alternative, you may have reached for a default. If you cannot name
the failure mode, you may not know what the design is protecting. Both gaps surface immediately under
follow-up, which is exactly when a portfolio walkthrough becomes an interview.

## Worked Example: The Production RAG Chatbot

The production RAG chatbot you built in Sans Python is a citation-enforced, guardrailed retrieval
system for regulated verticals. It retrieves from a corpus, grounds every answer in retrieved chunks
with explicit citations, screens inputs and outputs against a prohibition floor, and gates a build on
retrieval precision and answer faithfulness. Here is what the decision layer looks like.

### The Chunk Citation Contract

**Decision:** every piece of text in the pipeline binds to a `Chunk`: a struct carrying document ID,
section, and text. Nothing downstream ever handles a raw document object.

**Alternative rejected:** passing raw document or file objects through the pipeline and deriving
citations when needed.

**Tradeoff accepted:** ingest is responsible for mapping every input format onto the one `Chunk`
shape. A new format means a new parser, not a new pipeline branch.

**Failure mode guarded:** a format change (swapping a scanned contract for a native PDF, adding a new
document source) rippling through retrieval, generation, and citation rendering. When the contract is
the `Chunk` shape, a format change is a one-layer problem: the parser adapts, and the rest of the
pipeline sees no change.

A follow-up an interviewer will ask: "What happens when you add a new document type?" You have the
answer: you write a parser that produces `Chunk` objects. The retriever, the guardrail, and the citation
renderer do not know a new type exists.

### The Relevance Floor

**Decision:** the retriever returns an empty set when all retrieved candidates fall below a
minimum-score threshold, which forces the chatbot to refuse rather than answer from low-relevance
context.

**Alternative rejected:** always returning the top-k results regardless of their scores, as most
off-the-shelf retrieval implementations do.

**Tradeoff accepted:** some valid questions get a "I don't have a source for that" response. The
system trades recall on low-relevance queries for honesty about its knowledge boundary.

**Failure mode guarded:** hallucinated citations. A model asked to answer from low-relevance chunks
has to fill the gap somehow. In regulated verticals, a confident wrong answer grounded in a
tangentially relevant chunk is worse than an explicit refusal. The relevance floor makes refusal
the structural default when the corpus does not support an answer.

A follow-up: "Isn't that too conservative? You're dropping valid questions." You have the tradeoff
ready: yes, and that is the deliberate choice for a regulated vertical where a fabricated citation has
compliance consequences. Adjusting the threshold is a tunable dial; setting the dial to zero recreates
the failure mode.

### The Guardrail with a Hardcoded-Prohibitions Floor

**Decision:** the guardrail splits rules into two tiers. Hardcoded prohibitions covering prompt
injection and PII exfiltration sit beneath all operator configuration, unchangeable by runtime settings.
Operator-tunable rules covering topical scope and style sit above them, adjustable per deployment.

**Alternative rejected:** making all guardrail rules operator-configurable, which is the simpler
architecture: one config surface, no hidden floor.

**Tradeoff accepted:** the operator cannot disable security-critical prohibitions. For a
multi-tenant deployment this may feel limiting; for a regulated vertical it is the point.

**Failure mode guarded:** a misconfigured or pressured operator lowering the security floor. If every
rule is configurable, a deployment with a misconfigured scope check silently removes the
prompt-injection check at the same time. Splitting the tiers means the operator's scope changes cannot
reach the security controls, by construction.

A follow-up: "How do you handle a tenant that needs a custom prohibition?" The answer is: they add to
the operator-tunable layer. The hardcoded floor is not negotiable, and that is precisely its value.

### The Deterministic Eval Gate

**Decision:** the acceptance gate scores retrieval precision and answer faithfulness offline, without
an LLM judge, and defaults to FAIL. A degraded build cannot ship; the test suite includes a case where
a bad answerer is injected and the gate must reject it.

**Alternative rejected:** an LLM-as-judge setup or manual post-deployment evaluation.

**Tradeoff accepted:** the metrics are simpler than an LLM judge would provide. They will miss
sophisticated hallucinations that a model evaluator might catch.

**Failure mode guarded:** a degraded build shipping because the eval is expensive to run, requires a
live model, or is only done manually after deployment. When the gate runs offline in CI, it is
mandatory, not optional. Defaulting to FAIL means a broken eval configuration does not become a green
pass.

A follow-up: "Doesn't a simple precision and faithfulness metric miss too much?" You have the tradeoff
ready: yes, and you chose it deliberately so the gate runs in CI on every build without a model call.
Sophisticated hallucination detection belongs in a separate, slower eval loop, not in the gate the
build depends on.

## What Foregrounding Looks Like Under Probing

The four-part shape is also what saves you when the interviewer digs.

Suppose they ask: "Why not just return top-k results? Isn't that simpler?" You do not need to think of
an answer on the spot. You made the decision; you know the alternative you rejected; you know what goes
wrong without the floor. The answer is immediate: "The alternative is always returning top-k. The
failure mode is a model answering from low-relevance context with a confident citation, which in a
regulated vertical has compliance consequences. The tradeoff is a stricter refusal rate; we set the
threshold deliberately."

That answer is not rehearsed. It is reconstructed from the four parts you already know. This is the
difference between memorizing a monologue and owning a design: a memorized walkthrough breaks under the
first novel question; a decision-layer walkthrough holds because every component has a reason behind it
that you can reconstruct from first principles.

The follow-up is where candidates separate. A strong interviewer will follow every major component with
"why not the simpler thing?" or "what breaks if you had done it differently?" If you foregrounded the
decisions, you already answered those questions in your head when you built the artifact. The interview
is just making that reasoning audible.

## Extracting the Decision Set From Any Artifact

Before a portfolio round, do this for every artifact you plan to walk through.

List the load-bearing components: the pieces where a different choice would have produced a different
system. Not every class or method; the three or four places where you made a real architectural call.

For each component, write out the four parts: what you chose, what you rejected, what the choice cost,
what it guards. If you cannot fill in all four, you have found a gap in your own understanding of your
system. That gap will surface under follow-up. Fill it now, by reading the code and asking why each
piece exists, before you are across a table from someone asking the same question.

Then sort by importance. Lead with the component that shows the most judgment, the decision that
distinguishes your design from a naive version of the same system. For the production RAG chatbot, that
is the citation and refusal contract: the combination of the `Chunk` shape, the relevance floor, and the
eval gate is what makes this a regulated-vertical system rather than a chatbot with a search bar.

The artifacts you built in Sans Python are already strong. The decision layer is already there. The work
before a portfolio round is not inventing reasoning; it is writing down the reasoning you did when you
shipped the system, in four parts, so it comes out clean when an interviewer asks.

## Core Concepts

- A defended decision has four parts: what you chose, what you rejected, the tradeoff you accepted,
  and the failure mode it guards against; a walkthrough that runs this shape for every load-bearing
  component cannot be faked from a tutorial.
- The relevance floor is a structural refusal mechanism: returning an empty set when no candidate
  clears the minimum score trades recall on marginal queries for honesty about the corpus boundary.
- Splitting guardrail rules into a hardcoded-prohibitions floor and an operator-tunable layer above
  it makes the security controls unreachable from misconfigured operator settings, by construction.
- Defaulting an eval gate to FAIL means a broken eval configuration does not become a silent pass;
  running it offline without an LLM judge makes it mandatory rather than expensive.

<div class="claude-handoff" data-exercise="exercises/module6/foreground-the-decisions/">

**Try It in Claude Code:** for the artifact in your portfolio-narrative document, write its key decisions, the tradeoffs each accepted, and the failure modes each guards against, in the four-part shape.

</div>
