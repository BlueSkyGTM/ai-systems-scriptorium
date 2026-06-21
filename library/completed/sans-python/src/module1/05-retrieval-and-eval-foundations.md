# Foundations of Retrieval and Evaluation

A RAG system that fails is not a mystery; it is a combination of components, and at least one of them is misbehaving. Knowing the components lets you debug the system instead of blaming the model.

## Retrieval Components

**Question answering** is the root architecture: a retriever finds candidate passages, a reader extracts or generates an answer from them. That retriever→reader split is the bedrock of every RAG system. The question isn't whether your system uses it; it's whether you've built each half to match the query type.

**The information retrieval pipeline** has four complementary layers. BM25 sparse retrieval is exact-match: fast (sub-10ms via an inverted index), precise on keyword queries, but blind to synonyms. Dense retrieval is semantic: it embeds queries and documents into the same vector space and retrieves by similarity, catching meaning BM25 misses at the cost of higher latency (50–200ms via FAISS or a vector database). Reciprocal Rank Fusion merges ranked lists from both systems by rank position rather than raw score; no score normalization required. A cross-encoder reranker then takes the top 20–30 candidates and scores each query-document pair together, trading speed for precision. The 2026 production pattern is dense first-pass plus sparse recall boost plus cross-encoder rerank on the shortlist.

**Embedding models** sit under dense retrieval. The key fact you must internalize: effective context length is roughly 60–70% of the advertised number. A model that claims a 512-token context window starts degrading retrieval quality well before 512 tokens. Matryoshka embeddings let you truncate the dimension vector for storage with about 1% accuracy loss per halving, which makes the storage math tractable at scale. BGE-M3 is notable because it supports dense, sparse, and multi-vector retrieval from a single model. MTEB is a necessary leaderboard, not a sufficient one; benchmark on your domain before committing to a model.

**Chunking** influences retrieval quality as much as the embedding model does. The rule that beats defaults: match chunk size to query type. Factoid questions retrieve better with 256–512 token chunks; multi-hop questions need 512–1024; whole-section questions need 1024–2048. Overlap between chunks gives roughly zero benefit under sparse retrieval. Contextual retrieval (Anthropic, 2024) prepends a summary of each chunk's document context before embedding, which reduces retrieval failures by 35–50%.

## Evaluation Components

**NLI, Natural Language Inference**, is the mechanism under RAG faithfulness. The task is three-way classification: given a premise and a hypothesis, does the premise entail, contradict, or stay neutral toward the hypothesis? Every faithfulness metric in RAGAS and DeepEval runs NLI under the hood: it checks whether the retrieved passage entails the generated answer. Understanding NLI means you can read a faithfulness score and know exactly what it measures.

**LLM-as-judge** is the production answer to the scaling problem: exact-match metrics miss semantic equivalence, and human review doesn't scale. The trust protocol is non-negotiable; freeze the judge model and version (a judge upgrade changes your historical scores), calibrate against roughly 100 human labels, require Spearman ρ ≥ 0.7 before using the judge in CI. G-Eval produces a 0–1 score with a custom rubric; RAGAS produces four named metrics; DeepEval runs in pytest so the eval loop becomes a test suite. Silent failure modes: length bias (longer answers score higher regardless of quality), same-family bias (a model prefers its own outputs), JSON parse failures that silently drop cases from the average.

**Long-context evaluation** closes the gap between what a model advertises and what you can rely on. Advertised context length and usable context length are not the same number. Gemini 2.5 Pro advertises 1M tokens; at 1M tokens, its 8-needle MRCR score drops to 26.3%. The rule is to report two numbers for any model you operate: retrieval-effective length (where single-fact recall holds) and reasoning-effective length (where multi-hop accuracy holds, typically 25–50% of advertised). NIAH (needle-in-haystack) is the baseline; RULER adds 13 task types and reveals multi-hop failures; MRCR scales the needle count to stress multi-round coreference. This feeds the eval-driven development thread that runs through the course.

Module 2 takes these components and builds them into a RAG system and an eval loop. The components are the same; what changes is the system design around them.

A Production AI Engineer who knows these components can look at a failing RAG pipeline and name which layer broke, retrieval recall, reranker precision, chunk size mismatch, or judge calibration, instead of treating the whole system as a black box.

## Core Concepts

- The retriever→reader split is the structural foundation of RAG; the IR pipeline under the retriever has four layers (BM25 sparse, dense, RRF fusion, cross-encoder rerank) that catch different failure modes.
- Effective embedding context length is roughly 60–70% of the advertised number; building a RAG system to the stated limit causes silent retrieval degradation.
- NLI (entail/contradict/neutral) is the mechanism under RAG faithfulness metrics; knowing this lets you interpret a RAGAS faithfulness score rather than treating it as a black box.
- Long-context models require two usable-length numbers, retrieval-effective and reasoning-effective, because multi-hop accuracy degrades faster than single-fact recall, often to 25–50% of the advertised context window.

<div class="claude-handoff" data-exercise="exercises/module1/05-retrieval-and-eval-foundations/">

**Try It in Claude Code**: Measure embedding context-length truncation: embed the same fact at positions 10%, 50%, and 90% of an embedding model's advertised context window, then run a similarity search to see where retrieval quality degrades.

Open the repo and pick up from this lesson.

</div>
