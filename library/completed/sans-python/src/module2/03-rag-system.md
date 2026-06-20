# The RAG System

Module 1 taught you the retrieval components — embeddings, chunking, vector search. This lesson assembles them into a working system. The leap from component to system is where most engineers fail: they bolt parts together and wonder why production explodes at scale.

You build a RAG pipeline that grounds model responses in private data without retraining the model.

## From components to system

The system has a single job: given a user query, find the most relevant context from your corpus, inject it into the prompt, and return a grounded answer. Every architectural decision — chunking strategy, index type, retrieval method — exists to make that job reliable at production load.

The spine runs in this order: document ingestion → chunking → embedding → vector storage → retrieval → generation. You don't have to run all stages every request. Ingestion is offline. Retrieval and generation are online.

## Chunking

Fixed-size chunking breaks semantic units and poisons your index. Use structure-aware splitting instead — split at logical boundaries (paragraph breaks, section headers, list items). For code, use AST parsing; for PDFs with mixed layouts, use a vision-language model to extract positional structure first.

The core tension: small chunks give high retrieval precision but strip reasoning context; large chunks provide rich context but dilute match accuracy. Hierarchical (parent-child) chunking resolves this — index small child chunks for search, return the larger parent to the model. You get precision at retrieval, context at generation.

At ingestion time, prepend each chunk with a short context sentence that anchors it to its source document before embedding. Anthropic's contextual retrieval pattern reduces top-20 retrieval failures by 35% with this one change, rising to 67% when you add a reranker.

## Vector databases

Approximate Nearest Neighbor (ANN) search is the engine under every production retrieval system. HNSW runs in-memory — lowest latency, highest RAM cost. DiskANN indexes to disk — higher latency, fraction of the memory cost.

PostgreSQL with pgvector handles corpora up to roughly one million vectors. Above that, move to a dedicated vector database: Qdrant, Weaviate, Milvus, or Pinecone scale to billions of vectors at sub-100ms P99 latency. Size the decision by your corpus and your operational capacity — a managed serverless offering is not always worse than a self-hosted cluster.

Filter before you search. Metadata pre-filtering narrows the candidate set before ANN runs, which cuts both latency and memory. Index the fields you filter on.

## Hybrid search

Dense-only retrieval misses exact matches — model names, version numbers, product codes. Sparse-only (BM25/TF-IDF) misses semantic similarity. In production, run both and merge the ranked lists with Reciprocal Rank Fusion (RRF): assign each document a score of `1 / (rank + k)` from each retrieval path and sum. RRF is rank-based, so it handles the score-scale mismatch between dense and sparse naturally.

Hybrid search is the baseline for any production RAG system. The added complexity — two retrieval paths — pays for itself on the first query that contains a named entity alongside a conceptual phrase.

## Reranking

First-stage retrieval optimizes for recall. Reranking optimizes for precision. Pull the top 50–100 candidates from hybrid search, then run a cross-encoder to jointly score the query–document pair. A cross-encoder reads both together, uses full attention, and assigns a relevance score orders of magnitude more accurate than a bi-encoder similarity metric.

The tradeoff is latency: cross-encoders run at 10–100ms per pair, not sub-millisecond. Budget accordingly. FP16 inference and ONNX export cut this by 2–3x. Cache reranker scores for repeat queries.

## Production concerns

By widely-cited industry estimates, the large majority of enterprise RAG failures — on the order of three in four — trace to retrieval, not generation. The exact figure is soft, drawn from practitioner reports rather than a controlled study, but every team that has run RAG in production recognizes the shape of it. Invest in the knowledge source — chunking quality, freshness, index maintenance — before tuning prompts or swapping models.

Route queries by complexity. Simple queries with exact-match answers go directly to sparse retrieval; semantic queries go to hybrid; multi-document synthesis queries need the full pipeline. A lightweight classifier at the router pays for itself in latency and cost.

Multi-tenant deployments need isolation. Three patterns: Silo (one index per tenant — maximum isolation, maximum cost), Pool (shared index with metadata filters — efficient, careful about filter escapes), Bridge (pool with selective silo escalation for high-value tenants).

Semantic caching sits between the router and retrieval. If an incoming query is close enough to a cached query — cosine similarity above your threshold — return the cached answer. In high-traffic systems, cache hit rates above 30% are achievable on question-answer workloads.

For small static corpora (under 50,000 tokens), skip the retrieval pipeline entirely. Load the corpus directly into the context window with prompt caching enabled. For large, dynamic corpora, use RAG. The boundary is a corpus size decision, not a pattern loyalty.

## Core concepts

- RAG grounds model responses in private data through retrieval at query time — no retraining, zero-cost data updates.
- Hierarchical (parent-child) chunking indexes small chunks for retrieval precision but returns the parent chunk to the model for reasoning context.
- Hybrid search — dense plus sparse merged via RRF — is the production baseline; dense-only retrieval misses exact matches.
- Because most production RAG failures trace to retrieval — by widely-cited industry estimates, roughly three in four — the knowledge source quality is the highest-leverage investment in any RAG system.

<div class="claude-handoff" data-exercise="exercises/module2/03-rag-system/">

**Build it in Claude Code** — assemble a working RAG pipeline: ingest a small corpus, chunk with parent-child splitting, build a hybrid search index, add a cross-encoder reranker, and verify retrieval quality with recall metrics. Open the repo and run the exercise for this lesson.

</div>
