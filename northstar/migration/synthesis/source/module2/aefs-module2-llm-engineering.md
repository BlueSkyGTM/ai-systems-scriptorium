# Module 2 · LLM Engineering — Phase 11 Extract

> Source: `phases/11-llm-engineering/` (17 lessons, 01–17). Phase README is a stub; all content lives in per-lesson `docs/en.md`.
> This is the **Build-track core**: prompt engineering, structured outputs, embeddings, RAG (basic → advanced), fine-tuning/LoRA, function calling, evaluation, caching/cost, guardrails, MCP, prompt caching, LangGraph, and agent-framework tradeoffs.
> Tag legend: `[THREAD: eval]` = evaluation / quality measurement (Gap 1) · `[THREAD: versioning]` = prompt/config versioning & registries (Gap 3) · `[THREAD: safety]` = guardrails / moderation / safety (Gap 4).

## Lessons

### 01 · Prompt Engineering: Techniques & Patterns — **Build** · Python · ~90 minutes
This lesson teaches the anatomy of LLM API calls (system, user, assistant prefill) and how to engineer them using structural patterns like persona, few-shot, chain-of-thought, and guardrails to constrain output reliably across different models. Students build a multi-model testing harness in Python that evaluates prompt variations against expected criteria (length, format, keywords) using simulated API responses.
**Tools/APIs:** OpenAI API, Anthropic API, Google Gemini API, LangChain, GPT-5, Claude Opus 4.7, Gemini 3 Pro, Llama 4, DeepSeek-V3.1, Qwen3

### 02 · Few-Shot, Chain-of-Thought, Tree-of-Thought — **Build** · Python · ~45 minutes [THREAD: eval]
This lesson teaches advanced reasoning strategies—few-shot, chain-of-thought (CoT), self-consistency, tree-of-thought (ToT), and ReAct—for optimizing LLM accuracy on complex tasks without changing the underlying model. Students build a math problem solver pipeline in Python that escalates from simple few-shot CoT to self-consistency voting (N samples) and ToT, measuring accuracy improvements against the GSM8K benchmark. The final implementation outputs a production-ready reasoning chain prompt template and a decision framework for selecting the appropriate prompting pattern based on cost, latency, and accuracy constraints.
**Tools/APIs:** Python, OpenAI API, GSM8K benchmark, LangChain (FewShotPromptTemplate, SemanticSimilarityExampleSelector), DSPy (ChainOfThought, dspy.majority)

### 03 · Structured Outputs: JSON, Schema Validation, Constrained Decoding — **Build** · Python · ~90 minutes
This lesson teaches the spectrum of structured output control—from prompt-based JSON instructions to schema-constrained decoding—and how to bridge the gap between natural language model outputs and typed application data. Students build a complete extraction pipeline from scratch, including a custom JSON Schema validator, a Pydantic-style schema generator, a constrained token filter simulating decoding-level enforcement, and a retry mechanism that feeds validation errors back to the model. The final artifacts are a reusable extraction prompt template and a decision framework for choosing the right structured output strategy based on provider capabilities and reliability requirements.
**Tools/APIs:** OpenAI API (`response_format`, Structured Outputs, function calling), Anthropic API (tool use, `input_schema`), Pydantic, Instructor, JSON Schema, Outlines, XGrammar, Microsoft Guidance, LMQL

### 04 · Embeddings & Vector Representations — **Build** · Python · ~75 minutes
This lesson teaches the fundamentals of converting text into dense vector representations to solve the vocabulary mismatch problem in keyword search. Students build a complete semantic search engine from scratch using Python and numpy, implementing text chunking, a TF-IDF based embedder, brute-force vector indexing, and multiple similarity metrics (cosine, dot product, Euclidean). It also covers production concepts including HNSW, bi-encoder/cross-encoder pipelines, Matryoshka truncation, and binary quantization.
**Tools/APIs:** Python, numpy, OpenAI API (text-embedding-3-small, text-embedding-3-large), Cohere API (rerank-v3.5), Sentence Transformers (BAAI/bge-small-en-v1.5), LangChain (RecursiveCharacterTextSplitter), Pinecone, Weaviate, Qdrant, ChromaDB, pgvector, FAISS.

### 05 · Context Engineering: Windows, Budgets, Memory, and Retrieval — **Build** · Python · ~90 minutes
This lesson teaches context engineering as the discipline of managing the LLM context window (system prompts, tool definitions, retrieved documents, and conversation history) as a scarce resource to mitigate the "lost-in-the-middle" attention degradation effect. Students build a dynamic context assembly pipeline in Python that includes a token budget manager, a lost-in-the-middle reordering function, a conversation history compressor, and a dynamic intent-based tool selector. The final artifacts are a prompt auditing the context strategy and a skill defining a decision framework for context pipelines.
**Tools/APIs:** Python, NumPy, OrderedDict, CLAUDE.md, ChatGPT Memory, LangChain

### 06 · RAG (Retrieval-Augmented Generation) — **Build** · Python · ~90 minutes

This lesson teaches the complete Retrieval-Augmented Generation (RAG) pipeline—document loading, chunking, embedding, vector storage, retrieval, and generation—by building it from scratch using TF-IDF embeddings and brute-force cosine similarity search. Students construct a functional Python `RAGPipeline` class that indexes documents, retrieves the top-k most relevant chunks for a given query, constructs a grounded LLM prompt, and simulates generation. The lesson also details the transition to production tools (e.g., OpenAI/Anthropic models, ChromaDB) and covers chunking strategies, vector similarity metrics, and RAG evaluation concepts.

**Tools/APIs:** TF-IDF, Cosine Similarity, OpenAI API, text-embedding-3-small, gpt-4o-mini, Anthropic API, claude-sonnet-4-20250514, ChromaDB, FAISS, Pinecone, Weaviate, pgvector, Qdrant, LangChain (RecursiveCharacterTextSplitter), LlamaIndex, all-MiniLM-L6-v2, Sentence Transformers

### 07 · Advanced RAG (Chunking, Reranking, Hybrid Search) — **Build** · Python · ~90 minutes [THREAD: eval]
This lesson teaches advanced retrieval techniques to solve common RAG failures on ambiguous queries, multi-hop questions, and large corpora. Students implement a from-scratch BM25 algorithm, merge results with semantic search via Reciprocal Rank Fusion (RRF), and apply a custom reranker, HyDE (Hypothetical Document Embeddings), and parent-child chunking. The final artifact is a complete hybrid search and evaluation pipeline (`code/main.py`) that measures retrieval recall, faithfulness, and answer correctness.
**Tools/APIs:** Python, BM25, Reciprocal Rank Fusion (RRF), HyDE, Cross-encoders, Bi-encoders, Sentence Transformers, Cohere Rerank API, Anthropic API (Claude Sonnet), Weaviate, ColBERTv2, DSPy, GraphRAG, Self-RAG.

### 08 · Fine-Tuning with LoRA & QLoRA — **Build** · Python · ~75 minutes
This lesson teaches parameter-efficient fine-tuning (PEFT) by explaining the memory and cost constraints of full fine-tuning before introducing Low-Rank Adaptation (LoRA) and 4-bit quantized QLoRA. Students implement a low-rank adapter injection mechanism in pure PyTorch (freezing base weights, training matrices A and B, and merging them back into the model) alongside simulated NF4 quantization. The resulting artifact is a complete `lora.py` script that demonstrates parameter counting, adapter injection, weight merging, and quantization utilities, alongside usage examples for the Hugging Face `peft` and `bitsandbytes` ecosystems.
**Tools/APIs:** PyTorch, Hugging Face PEFT, Hugging Face Transformers, Hugging Face TRL, bitsandbytes, Unsloth, Axolotl, LLaMA-Factory, torchtune, Llama 3 8B.

### 09 · Function Calling & Tool Use — **Build** · Python · ~75 minutes

This lesson teaches the architecture of LLM function calling, detailing the 5-step loop from defining JSON Schema tool contracts to handling tool execution, argument validation, and error propagation. The student builds a complete function calling engine in Python that includes a tool registry, five simulated tools (calculator, weather, search, file reader, code runner), an argument validator, and a multi-turn agent loop capable of parallel function calls and security enforcement. **Tools/APIs:** Python, JSON Schema, OpenAI API, Anthropic API, Google Gemini, Llama 4, Model Context Protocol (MCP).

### 10 · Evaluation & Testing LLM Applications — **Build** · Python · ~45 minutes  [THREAD: eval]
This lesson teaches the engineering discipline of LLM application evaluation, covering the taxonomy of automated metrics, LLM-as-judge scoring, and statistical regression testing. Students build a complete evaluation framework from scratch that defines test cases with rubrics, executes runs, computes confidence intervals (Wilson and bootstrap), and outputs a pass/block decision report for comparing prompt or model versions. The final artifact (`code/eval_framework.py`) orchestrates the full eval pipeline, simulating LLM outputs and judge scores to detect silent quality degradation.
**Tools/APIs:** Python, promptfoo, DeepEval, Braintrust, LangSmith, Arize Phoenix, ROUGE-L, BERTScore, RAGAS, G-Eval, GitHub Actions, GPT-4o, Claude Opus 4.7, GPT-5-mini, Gemini 3 Flash

### 11 · Caching, Rate Limiting & Cost Optimization — **Build** · Python · ~45 minutes

This lesson teaches the financial and architectural strategies required to scale LLM applications sustainably by mitigating redundant API spending. Students build a comprehensive cost optimization layer in Python that implements exact hash-based caching, embedding-based semantic caching, token-bucket rate limiting with tiered quotas, complexity-based model routing, and a cost tracker with automated budget circuit breakers. The final runnable script simulates a production traffic pipeline, comparing costs before and after optimization to demonstrate measurable savings.
**Tools/APIs:** OpenAI API, Anthropic API, OpenAI Batch API, Redis, Pinecone, pgvector, GPTCache, text-embedding-3-small, NumPy, Martian Model Router, Not Diamond, Helicone

### 12 · Guardrails, Safety & Content Filtering — **Build** · Python · ~45 minutes [THREAD: safety]
This lesson teaches the architecture of a defense-in-depth "guardrail sandwich" to protect LLM applications from prompt injection, jailbreaks, PII leakage, and toxicity. Students build a complete Python pipeline implementing input validation (length, injection detection, PII, topic classification), output validation (toxicity filtering, relevance checking, system prompt leak detection), automated red-team simulations, and a latency/block-rate monitoring dashboard.
**Tools/APIs:** OpenAI Moderation API, LlamaGuard 3 (1B/8B), NeMo Guardrails, Guardrails AI, LLM Guard, Rebuff AI, Microsoft Presidio, Perspective API, MLCommons AI Safety taxonomy, garak, Python `re`, Python `hashlib`

### 13 · Building a Production LLM Application — **Build (Capstone)** · Python · ~120 minutes
This capstone lesson teaches students how to integrate all previously learned Phase 11 components—prompts, RAG, function calling, caching, and guardrails—into a single production-grade LLM service. Students build a complete Python application that implements streaming token delivery via Server-Sent Events (SSE), graceful error handling with exponential backoff and fallback model chains, structured observability, and per-request cost tracking.
**Tools/APIs:** Python, FastAPI, Uvicorn, Jinja2, Server-Sent Events (SSE), asyncio, OpenAI API, Anthropic API, OpenTelemetry, Redis, Docker, Kubernetes, OpenAI GPT-4o, Anthropic Claude Sonnet 4, vLLM, Hugging Face TGI, NVIDIA TensorRT-LLM

### 14 · Model Context Protocol (MCP) — **Build** · Python · ~75 minutes
This lesson introduces the Model Context Protocol (MCP), the JSON-RPC 2.0 wire format that standardizes how LLM hosts connect to external tools, data sources, and agent frameworks. Students build a runnable MCP server and client pair exposing tools, resources, and prompts via stdio and streamable HTTP transports, while implementing capability scoping, mutation allowlists, and tool poisoning defenses.

**Tools/APIs:** Model Context Protocol (MCP), `mcp` Python SDK, `FastMCP`, JSON-RPC 2.0, Anthropic SDK, stdio transport, streamable HTTP transport, Claude Desktop, Claude Code, `modelcontextprotocol/servers`, `@modelcontextprotocol/sdk`, Rust SDK, OAuth 2.1

### 15 · Prompt Caching and Context Caching — **Build** · Python · ~60 minutes

This lesson teaches the mechanics of provider-side prompt caching—reusing a warm KV-cache for token-identical prefixes to cut input cost by 50–90% and first-token latency by 40–85%. Students implement and compare caching APIs across Anthropic (explicit `cache_control`), OpenAI (automatic prefix detection), and Google Gemini (explicit `CachedContent`), analyzing write premiums, TTLs, and read discounts for each. The concrete artifact is a simulated three-provider accountant (`code/main.py`) that tracks cache hit/miss counts and computes blended cost, alongside a prompt-layout planner skill that enforces cache-friendly ordering.

**Tools/APIs:** Anthropic API, OpenAI API, Google Gemini API (`google.genai`), `cache_control`, `CachedContent`, KV-cache

### 16 · LangGraph — State Machines for Agents — **Build** · Python · ~75 minutes

This lesson teaches how to model function-calling AI agents as explicit state machines using LangGraph's `StateGraph` abstraction, replacing fragile `while True:` loops with a defined graph of nodes, edges, and typed state. Students learn how to leverage graph compilation to gain access to four production-grade superpowers for free: checkpointing (state persistence), interrupts (human-in-the-loop pauses), streaming (event/token deltas), and time-travel (forking from prior execution steps). The concrete artifact built is a four-node ReAct agent loop, complete with a human-in-the-loop tool approval gate and debuggable time-travel replay.

**Tools/APIs:** Python, LangGraph (`StateGraph`, `END`, `ToolNode`, `MemorySaver`, `PostgresSaver`, `Send`, `Command`), LangChain (`AnyMessage`, `HumanMessage`, `AIMessage`, `add_messages`), TypedDict, SQLite, Redis, PostgreSQL

### 17 · Agent Framework Tradeoffs — LangGraph vs CrewAI vs AutoGen vs Agno — **Learn** · Python · ~45 minutes

This lesson maps the core abstractions of four dominant agent frameworks (LangGraph, CrewAI, AutoGen, Agno) to the shapes of agent problems they fit best, comparing their approaches to state management, branching, observability, interoperability, and cost. Students learn a decision matrix for matching problem requirements (e.g., typed state, role-playing, multi-agent dialogue, parallel fanout) to the correct framework, and practice the skill of refusing a framework until the architecture can be drawn as a graph, org chart, chat, or single agent. The concrete artifact is a decision-tree script (`pick_framework.py`) that takes a JSON problem description and returns a framework recommendation.

**Tools/APIs:** LangGraph, CrewAI, AutoGen, Agno, LangChain, LlamaIndex, LangSmith, OpenTelemetry, Langfuse, Phoenix, Opik, AgentOps, SQLite, Postgres, MongoDB, Redis, DynamoDB, Model Context Protocol (MCP), Pydantic
