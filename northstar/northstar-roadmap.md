# Sans Python — AI Platform Engineering

## Module 1 — Foundations

### Setup & Tooling
- Dev environment (no IDE dependency)
- TypeScript & Rust toolchains
- Git, GPU setup, Docker
- APIs & keys (first LLM call)
- Debugging & profiling

### NLP — Transformer-Forward
- Attention (the pivot)
- Tokenization → embeddings → chunking
- QA & information retrieval (RAG components)
- Eval thread origin (NLI, LLM-eval, long-context)

### Language Toolchains (threaded, not walled)
- TypeScript installed (taught at M3)
- Rust installed (taught at M5)

## Module 2 — LLM Engineering

### Prompting & Context
- Prompt engineering (anatomy, roles, instruction hierarchy)
- Few-shot, chain-of-thought, tree-of-thought
- Context engineering (window budget, compaction)
- Prompt caching
- Prompt-injection defense

### Embeddings & RAG (one spine)
- Embeddings → RAG fundamentals
- Chunking strategies → vector databases
- Hybrid search → reranking
- Advanced RAG (HyDE, GraphRAG, agentic, ColBERT)
- RAG evaluation

### Evaluation (eval-driven development)
- LLM-as-judge
- RAG triad eval
- Observability → error analysis → judge design
- Statistical correction

### Agent On-Ramp (M2 → M3 seam)
- Structured outputs & schema validation
- Function calling / tool use
- MCP introduction
- LangGraph → framework tradeoffs
- Complexity ladder (decision framework)

## Module 3 — Agent Foundations

### Agent Fundamentals & Reasoning Loops
- ReAct (observe-think-act)
- Reflexion (critic + memory)
- Tree-of-Thought / LATS (search)
- Planning & task decomposition
- Error handling & recovery

### Tools & Protocols / MCP (one spine)
- Tool interface
- MCP server → client → transports
- Resources/prompts → sampling → async
- MCP security → OAuth 2.1 → gateways/registries

### Memory & State
- Memory architectures (L1/L2/L3)
- Short-term context (KV / paged-attention)
- Long-term memory (vector + graph)
- Agentic memory (Mem0/Letta/MemGPT)
- State management & checkpointing

### Frameworks & Design Patterns
- LangChain / LangGraph / LangSmith
- LlamaIndex / CrewAI / typed (pydantic-ai)
- Framework selection
- Design patterns & anti-patterns

### TypeScript (entry — point-of-use)
- Break-in set (types, unions, interfaces, functions)
- Generics → typed tool wrappers
- Declaration files for JS-first packages

## Module 4 — Multi-Agent Systems

### Multi-Agent & Swarms
- Why multi-agent (single-agent ceiling)
- Communication protocols (A2A/ACP/ANP)
- Multi-agent primitives (Handoff/SharedState/Orchestrator)
- Orchestration patterns (supervisor/swarm/hierarchical/debate)
- Failure modes (MASFT)

### Autonomous Systems & Operational Safety
- Long-horizon agents → durable execution
- Action budgets / cost governors
- Kill switches / circuit breakers
- HITL propose-then-commit
- Checkpoints/rollback → guardrails

### Fleet & Loop Engineering (seam core)
- Loop: trigger → action → verification → budget
- Loop patterns (daily-triage, PR-babysitter, CI-sweeper)
- Fleet: registry → identity → permissions
- Fleet governance (inbox-HITL, audit, economics, kill-switch)

### Computer-Use, Coding & Voice (thin teaching)
- Computer-use agents
- Coding agents
- Voice agents (Pipecat/LiveKit)

## Module 5 — Deploy & Performance Engineering

### Serving & Inference Optimization
- Serving engine selection (vLLM/SGLang/TRT-LLM)
- vLLM internals (paged-attention, continuous batching)
- Speculative decoding → production quantization
- Disaggregated prefill/decode → KV-cache management
- Prefix caching (RadixAttention)

### Metrics, Observability & Rollout
- Inference metrics (TTFT/TPOT/goodput/P99)
- Load testing → observability stack
- Shadow traffic → canary → A/B testing
- AI gateways (routing/fallback/secrets)
- SRE-for-AI → chaos engineering

### Operations: Security, Compliance, FinOps
- Secrets / vault / rotation / egress
- Compliance (SOC2/HIPAA/GDPR/EU-AI-Act)
- FinOps (token attribution, spend caps)
- Caching economics + batch APIs

### Performance Engineering Depth
- Profiling (Nsight) & roofline analysis
- NVLink/NVSwitch topology, NUMA tuning
- 200-item production checklist

### Rust (entry — serving layer)
- Ownership on-ramp
- Async serving (tokio), typed errors

## Module 6 — Agent Artifacts

### Single-Agent Builds (real business problems)
- Terminal coding agent (the harness)
- Production RAG chatbot (regulated vertical)
- Real-time voice assistant
- Issue-to-PR autonomous agent

## Module 7 — Multi-Agent Artifacts

### Composed Teams (compounding from M6)
- Autonomous research agent
- DevOps K8s troubleshooting agent
- Governed multi-agent fleet (SWE team + fleet layer)

## Module 8 — Final Systems Engineering Exam

### The Team Builds the System
- M7 fleet builds a production system end to end
- Reference architectures (asdg case studies)
- Eval-gated pipeline / multi-tenant RAG / agentic MLOps
