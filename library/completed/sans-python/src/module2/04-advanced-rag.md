# Advanced RAG

Basic RAG breaks in a predictable pattern — not randomly, but on the exact queries that matter most: multi-document synthesis, entity-relationship chains, and questions that require the model to reason over retrieved evidence rather than recite it. Knowing where the system breaks tells you what to replace.

## Where Basic RAG Breaks

Three failure modes account for most production escapes.

**Semantic mismatch.** The user query and the relevant document don't share vocabulary. A query about "cost reduction" misses a document titled "budget optimization strategies." Dense embeddings partially solve this, but they fail on domain-specific terminology and cross-lingual mismatches. The fix is query transformation — decompose the query into sub-queries, generate a hypothetical answer document (HyDE) and embed *that*, or expand with synonyms before retrieval.

**Missing context.** The relevant information spans multiple chunks. The chunk containing the answer references entities or tables defined three sections earlier. Parent-child chunking recovers some of this, but when the reasoning chain requires crossing document boundaries, single-stage retrieval can't assemble the evidence.

**Multi-hop questions.** "Which of the products launched after the acquisition outperformed Q3 targets?" requires the model to resolve the acquisition date, identify post-acquisition products, and compare to a revenue threshold — three retrieval steps, each conditioned on the last. Linear pipelines don't do this.

## GraphRAG

GraphRAG replaces the vector index with a knowledge graph. Entities become nodes; relationships become edges. Multi-hop traversal then answers questions a flat vector index can't — "all contracts signed by subsidiaries of Company X" requires following edges, not ranking cosine distances.

Use GraphRAG only when empirical analysis shows 30% or more of your retrieval failures are graph-shaped — questions requiring entity-relationship chains across documents. Don't use it as a default upgrade; the cost is substantial: LLM-based entity extraction, quarterly graph maintenance as the corpus drifts, and scalability limits in the millions of entities rather than the billions of vectors a standard index handles.

The 2026 production sweet spot is graph-as-reranker: run standard hybrid retrieval first, then expand the top-k results via one or two hops in a lightweight graph before the cross-encoder. You capture 70–80% of full GraphRAG quality at roughly 20% of the infrastructure cost.

## Agentic RAG

Agentic RAG replaces the linear retrieve-once pipeline with a reasoning loop. The agent decides when to retrieve, what to retrieve, and whether the evidence gathered is sufficient before generating an answer.

Three dominant patterns:

**Self-RAG** — the model emits special critic tokens evaluating whether retrieval is needed, whether the retrieved context is relevant, and whether the generated response is grounded. Retrieval is conditional, not mandatory per query.

**Corrective RAG (CRAG)** — a lightweight evaluator grades initial retrieval confidence. Below the threshold, the system routes to a fallback — web search, a secondary index, or an explicit "I don't know" path. Above the threshold, generation proceeds. This eliminates the failure mode where the model confidently fabricates from low-relevance context.

**Adaptive RAG** — a query classifier upstream of retrieval selects pipeline depth: skip retrieval for factual-recall questions the model answers reliably, use single-stage for standard semantic queries, use multi-hop for complex synthesis queries. The classifier runs at near-zero cost and cuts median latency significantly on mixed-complexity workloads.

Budget 8–12 seconds per loop for a 3–4 iteration agentic retrieval cycle. Route simple queries to the standard pipeline to protect P50 latency. Constrain the agent with an explicit state machine — LangGraph or LlamaIndex Workflows — so the loop graph is defined and testable rather than emergent and fragile.

Agentic RAG is an agent pattern. The reasoning loop it adds is the same loop Module 3 builds as Agent Foundations. This is the seam — when retrieval needs to decide, plan, and verify, it has become an agent.

## RAG Evaluation

You can't improve what you don't measure. The RAG triad measures end-to-end correctness: context relevance (did retrieval return what the query needed?), groundedness (does the answer cite the retrieved context?), and answer relevance (does the answer address the question?). These are the three levers. Component metrics — Recall@K, NDCG, MRR — isolate which stage to fix. The evaluation chapter covers the full measurement stack; name the triad here, go deep there.

## Core Concepts

- Basic RAG fails on three predictable failure modes: semantic mismatch, missing context, and multi-hop questions — each requires a targeted fix, not a prompt change.
- GraphRAG answers entity-relationship questions a flat vector index cannot, but it costs far more; the graph-as-reranker pattern captures most of the quality at a fraction of the cost.
- Agentic RAG — Self-RAG, CRAG, Adaptive RAG — replaces linear retrieval with a reasoning loop that decides when and what to retrieve; this is the point where RAG becomes an agent.
- The RAG triad (context relevance, groundedness, answer relevance) measures end-to-end correctness; component metrics isolate the broken stage.

<div class="claude-handoff" data-exercise="exercises/module2/04-advanced-rag/">

**Try It in Claude Code** — Extend the RAG pipeline from the previous lesson: add a HyDE query transformation, implement a simple CRAG reliability gate that routes low-confidence retrievals to a fallback, and measure the change in retrieval recall. Open the repo and pick up from this lesson.

</div>
