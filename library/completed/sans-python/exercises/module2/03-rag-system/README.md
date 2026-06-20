# Exercise: The RAG System

## Goal

Build a working RAG pipeline that ingests a small document corpus, chunks it with parent-child splitting, indexes it with a hybrid search setup, reranks retrieved candidates, and measures retrieval quality with recall metrics.

## Why

RAG is the default way an Production AI Engineer grounds a model in private data — this exercise proves you can assemble the components into a system that actually works, not just a demo that passes one query.

## Steps

1. Ingest a small corpus (10–20 documents of your choice — markdown files, text files, or a public dataset).
2. Implement structure-aware chunking: split at paragraph boundaries, not fixed character counts. Add a short context sentence to each chunk before embedding (contextual retrieval pattern).
3. Build a parent-child chunk structure: index child chunks (small) for search, store parent chunks (large) to return at generation time.
4. Embed the child chunks using a sentence-transformer model of your choice.
5. Build a hybrid search function: dense (cosine similarity over embeddings) plus sparse (BM25). Merge results with Reciprocal Rank Fusion (RRF).
6. Add a cross-encoder reranker over the top-20 hybrid results. Return the top-5 parent chunks to the model.
7. Write 10 test queries with known relevant documents. Measure Recall@5 (fraction of queries where the relevant document appears in the top-5 results) before and after adding the reranker.
8. Call a model with the retrieved context to generate grounded answers for 3 of your queries.

## Done when

- Recall@5 prints to the console for both the baseline (hybrid-only) and the reranked pipeline.
- The reranked pipeline shows equal or higher Recall@5 than hybrid-only.
- A model answer for each of the 3 generation queries prints, citing context from the retrieved documents.
- No hardcoded chunk sizes — chunking respects structural boundaries.

## Stretch

Add semantic caching: hash each incoming query's embedding, check cosine similarity against a cache of prior queries, and return the cached answer when similarity exceeds 0.92. Measure the cache hit rate on a repeated query set.
