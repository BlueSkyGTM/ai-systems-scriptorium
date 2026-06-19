# Exercise: Advanced RAG

## Goal

Extend the RAG pipeline from the previous exercise with HyDE query transformation and a CRAG-style reliability gate, then measure whether retrieval recall improves.

## Why

Knowing where basic RAG breaks — and how to fix each failure mode — is what separates a RAG system that handles production queries from one that works on the demo set.

## Steps

1. Start from the pipeline you built in `exercises/module2/03-rag-system/`.
2. Implement HyDE: before embedding the user query, call a model to generate a short hypothetical document that would answer the query, then embed *that* document instead of the raw query. Retrieve against it.
3. Add a CRAG reliability gate: after retrieval, score the top chunk's similarity against the query. If the score falls below a threshold you set (start at 0.6), route to a fallback response — either "I don't have enough information" or a second retrieval pass with a reformulated query.
4. Re-run your 10 test queries from exercise 03 against the HyDE pipeline. Measure Recall@5.
5. Simulate 3 queries where no relevant document exists in the corpus. Confirm the CRAG gate triggers the fallback path for at least 2 of them.
6. Log which queries triggered HyDE, which triggered the CRAG fallback, and the Recall@5 delta vs the baseline.

## Done when

- Recall@5 prints for both the HyDE pipeline and the baseline, with a delta.
- At least 2 of the 3 no-answer queries trigger the CRAG fallback instead of returning a hallucinated answer.
- The pipeline logs the routing decision (HyDE / standard / CRAG-fallback) for each query.

## Stretch

Implement Adaptive RAG: add a one-sentence query classifier (prompt the model to classify as "factual", "semantic", or "multi-hop") and route each class to a different retrieval depth — sparse-only, hybrid, and HyDE+reranker respectively. Measure latency for each class.
