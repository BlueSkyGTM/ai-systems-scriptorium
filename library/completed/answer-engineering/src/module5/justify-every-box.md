# Justify Every Box

The whiteboard fills with boxes everyone draws. Embedding model, vector DB, reranker, API
gateway: the vocabulary is the same from candidate to candidate. The score is in the why.

Every component in a systems-design answer is a choice. Naming it is the entry ticket; defending
it is the work. The interviewer already knows that a retrieval system needs a vector store. What
they cannot learn from your diagram is whether you chose that store because it is the correct tool
at your stated scale, or because it is the component you memorized. That distinction is the
signal they are listening for across the entire construct step.

## What the Interviewer Hears

There is a specific failure mode that looks, from the outside, like strong preparation. The
candidate draws a clean architecture. The components are correct. The terminology is fluent. Then
the interviewer asks: "Why hybrid search instead of pure vector?" The answer comes back: "Because
hybrid is generally better for enterprise corpora." That answer fails. Not because it is wrong,
but because it is untethered from the design at hand. "Generally better" is a reference
architecture talking. A production design is specific.

The failure modes have names. Shallow RAG understanding: you can list the pipeline stages but
cannot explain the tradeoff within any single stage. Treating prompts as magic: "we prompt the
model to return structured JSON" with no mention of output format enforcement, format slipping
over long sessions, or what happens when the model defies the schema. One-size-fits-all model
selection: a single frontier model handles everything, with no routing, no cost reasoning, and no
acknowledgment that the document classifier and the generative step have different latency and
accuracy profiles. Each of these is a naming failure dressed as a knowledge failure. The candidate
named the box; they just cannot tell you why it belongs in this design, at this scale, instead of
the cheaper or simpler thing.

The defense of a component has a shape. Name what you chose, name the simpler alternative you
considered, and then name the scale-dependent reason the simpler choice loses. That reason has to
be specific to the constraints on the board: not "vector search scales better" but "at 50 million
products with 100 million queries per day and a P99 under 100ms, pure dense retrieval without
HNSW tuning and an edge cache does not close the latency budget." The specificity is the proof
that you reasoned from this design, not from a template.

## Worked Example One: Semantic Search at Scale

The prompt arrives with these constraints: 50 million products, 100 million queries per day, P99
latency under 100ms, real-time inventory updates, and personalization based on user history.

Before you draw anything, the numbers tell you what kind of problem this is. 100 million queries
per day is about 1,160 per second at uniform load, with real peaks well above that. P99 under
100ms is aggressive: you have no slack. And real-time inventory means the index is a moving
target. These constraints are not decoration. Each one disqualifies design choices that would
work fine at smaller scale.

**The edge cache as a first-class component.** The obvious design puts embedding, ANN search,
filtering, and generation in a pipeline and tries to make each step fast. The right design
recognizes that the latency budget does not close without a cache hit. The math is unforgiving:
edge cache check adds 5ms, embedding lookup (cache hit) adds 10ms, vector search adds 30ms,
filtering 10ms, personalization 10ms, serialization 10ms, network 25ms. That lands at 100ms with
a cache hit. Without the edge cache, the path runs long. A 30% edge cache hit rate on popular
queries is not an optimization detail you mention at the end. It is load-bearing infrastructure
the budget depends on. Draw it first, justify it first: "30% of queries at this volume are
navigational repeats. Without a cache in front of the embedding step, the P99 target does not
close."

The weaker candidate draws the same pipeline without the cache and then asserts the latency
target is met. The interviewer probes: "Walk me through the latency budget." There is no answer,
because there is no budget. Naming a P99 requirement you have not grounded in arithmetic is the
same as not naming it.

**Dynamic hybrid weighting by query type.** The design includes hybrid search, which is correct.
But there is a choice inside that component that most candidates skip. A query like "nike air max
90 size 10" is a keyword query. The model name, the size, and the product code are exact-match
tokens. Dense vectors built from embedding that phrase will find semantically similar products,
which is not what the user wants. Sparse retrieval (BM25 or equivalent) handles the exact-match
case well. A query like "comfortable running shoes for flat feet" is a natural language query.
Sparse retrieval cannot handle the semantic intent; dense retrieval can. The fixed-weight hybrid
fails both: it underperforms on keyword queries relative to sparse-only, and it underperforms on
natural language queries relative to dense-only.

The defense of dynamic weighting is scale-dependent: at 50 million products and this query
volume, a fixed weight is measurable underperformance on a large fraction of your traffic. The
justification is: "keyword-heavy queries use sparse 0.7 / dense 0.3; natural language queries
flip to sparse 0.3 / dense 0.7. The classifier to determine query type adds under 5ms and
recovers recall on both ends of the distribution." If you draw "hybrid search" without this
reasoning, you have named the box. If you justify the weighting strategy, you have earned it.

**Inventory update versus description update.** The real-time update requirement hides a choice
that separates engineers who have shipped search systems from engineers who have read about them.
A price change or an inventory status change is a metadata update: you write to the vector DB's
metadata store, and the change propagates in seconds via the message queue. No re-embedding. A
product description change is different: the embedding is derived from the description, so a
description change requires re-embedding the product and swapping the index entry. If you treat
these as the same operation, you either miss the latency requirement for inventory updates
(re-embedding takes too long) or you trigger unnecessary re-embeds on every price change (which,
at 50 million products, is not tractable). The justification for splitting them: "inventory
changes update metadata only, propagating in seconds; description changes queue an async
re-embed job with an index swap so the old entry stays live until the new one is ready." That is
a real architectural choice, and the candidate who draws a single "update" arrow and calls it
real-time has not made it.

## Worked Example Two: Document Processing Pipeline

The prompt: a document processing pipeline for financial services, handling 100,000 documents per
day across invoices, contracts, and forms, with a 99% accuracy requirement, HIPAA and SOC2
compliance, and human review for low-confidence extractions.

The 99% accuracy target on financial documents is not a number you can reason about in the
abstract. Invoices have line items that must sum to a total. Contracts require at least two
parties and a valid date. Forms carry tax IDs with a specific format. The accuracy bar is not a
model metric; it is a business constraint expressed as field-level correctness, with real dollar
consequences when it fails.

**Tiered extraction as a cost and accuracy lever.** The obvious move is to route every document
through the highest-quality vision model. A frontier vision LLM on every invoice at 100,000
documents per day is a cost structure most financial services teams will not approve. But the
plain Document AI tier (Textract, Azure Form Recognizer) handles structured forms with known
layouts fast and cheaply, and returns per-field confidence scores. The design uses Document AI as
the first tier, with a vision LLM as the fallback for the documents that fail Document AI's
confidence threshold.

The justification has two parts. First, cost: standard forms, which make up the majority of the
volume, run cheaply through Document AI. The vision LLM sees only the subset that Document AI
cannot handle. Second, accuracy: cross-validating both outputs on the fallback documents catches
errors neither tier surfaces alone. The 99% bar requires combining both; neither alone hits it
across the full document distribution. "We use a vision LLM for all documents" fails on cost and
does not even reach the bar; "we use Document AI for everything" fails on the complex layouts.
Stating those two failure modes and then drawing the tiered architecture is what justifying the
box looks like.

**Cross-field validation as named business logic.** Schema validation tells you whether a field
was extracted. It does not tell you whether the extraction is correct. Line items must sum to the
invoice total. A tax ID must match the expected regex for the jurisdiction. A contract must have
at least two named parties and a valid date. These are not generic output-validation concerns;
they are the specific rules that distinguish a financial document processing system from a generic
extraction pipeline.

The weaker candidate draws a "validate" step and moves on. The stronger candidate names the
validation rules for each document type and explains why they exist: "Cross-field consistency
checks are where extraction errors surface as business failures. A line item total that does not
match the invoice total is not a schema violation; it is a downstream accounting error. That rule
has to live in the validation layer, not in a human's head." That is the difference between
naming a box and making a case for it.

The human review interface follows from the same logic. If the reviewer sees only the extracted
fields and not the original document image, they are reviewing an abstraction. Normalizing
extraction errors against an abstraction you cannot verify is how the 99% bar slips. The design
explicitly surfaces the original document image beside the extracted fields, with per-field
confidence scores and validation failures highlighted. That is not a UX nicety; it is the
mechanism that makes human review useful.

## How To Justify a Box You Are Drawing for the First Time

The two worked examples share a structure you can apply to any component in any design:

Name the alternative. Every component you draw had a simpler or cheaper version you did not draw.
Naming the alternative proves you made a choice rather than reaching for a default. "I chose a
tiered extraction approach rather than routing all documents through a vision LLM." "I chose
dynamic hybrid weighting rather than a fixed-weight hybrid."

Name the scale-dependent reason the alternative loses. The reason has to be grounded in the
constraints on the board. "At 100,000 documents per day, routing everything through a frontier
vision LLM is a cost structure that cannot survive a finance review; Document AI handles
structured forms at a fraction of the cost with comparable accuracy on that subset." "At 50
million products with a P99 under 100ms, the latency budget does not close without a cache hit
design."

The scale-dependent reason is what makes the justification stick. "Hybrid search is better than
pure vector" is not a justification; it could apply to any retrieval system at any scale. "At
this document volume and this exact-match query fraction, a fixed-weight hybrid measurably
underperforms on a large portion of traffic" is a justification, because it cannot be recycled
from a template.

One more move: state the failure mode the simpler choice creates. The cache-miss path that blows
the P99. The re-embed on every price change that cannot keep up at 50 million products. The
Document AI tier alone that misses the complex layouts in the tail of the distribution. The
candidate who names what goes wrong with the rejected option has thought through the design from
both directions, and that is rare enough to register.

## Core Concepts

- Naming a component is the entry ticket; defending it with a scale-dependent reason is the work.
- The defense of any component has a shape: name what you chose, name the simpler alternative
  you rejected, and name the reason the simpler choice loses at this scale and these constraints.
- Cross-field validation is named business logic, not generic output checking; the candidate who
  names the rules earns the validation step.
- The failure modes to audit against are shallow RAG understanding (pipeline fluency without
  tradeoff depth), treating prompts as magic, and one-size-fits-all model selection.

<div class="claude-handoff" data-exercise="exercises/module5/justify-every-box/">

**Try It in Claude Code:** take the prompt you scoped in the last lesson and draw the initial architecture into your systems-design log, writing one defensible justification for every component: what you chose, the alternative you rejected, and the scale-dependent reason.

</div>
