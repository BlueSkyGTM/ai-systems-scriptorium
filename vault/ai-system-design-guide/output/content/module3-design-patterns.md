# Module 3 · AI Design Patterns — Chapter 15 + PATTERNS.md

> Source: `15-ai-design-patterns/01-design-patterns.md`, `15-ai-design-patterns/02-anti-patterns.md`, root `PATTERNS.md`.

## Pattern Catalog

| Pattern | Problem it solves | When to use |
|---------|-------------------|-------------|
| **Naive RAG / Basic RAG** | Simple Q&A over documents; easy implementation pipeline | MVP and prototyping; simple question-answering; when retrieval quality is sufficient |
| **Advanced RAG** | Needs higher accuracy through query rewriting, hybrid search, reranking, and filtering | Production systems; when accuracy matters; complex document sets |
| **Hybrid Search** | Improving recall by combining semantic and BM25/keyword search | Keyword-heavy content; complex queries needing better recall |
| **Reranking** | High-precision retrieval to filter out noise | When precision matters and latency budget allows |
| **Query Expansion** | Handling ambiguous queries | Better recall, accepting more tokens |
| **HyDE (Hypothetical Document Embeddings)** | Finding matches when no direct matches are expected | Creative generation tasks, accepting hallucination risks |
| **Parent-Child Retrieval / Chunking** | Needs precision in retrieval but broader context in generation; memory overhead trade-off | Document structure is hierarchical; need both precision and surrounding context |
| **Self-RAG** | Deciding dynamically when and what to retrieve | Mixed knowledge (parametric + retrieved); research and experimentation |
| **Corrective RAG (CRAG)** | Evaluating and correcting retrieval quality with fallbacks | Unreliable document corpus; need high accuracy; can afford latency for quality checks |
| **Zero-Shot** | Simple tasks requiring fast implementation | Fast execution needed, accepting less reliability |
| **Few-Shot** | Format control and consistent outputs | Willing to spend tokens for prompt examples to guide output |
| **Chain-of-Thought** | Complex reasoning tasks | Latency acceptable; explainability of reasoning steps is required |
| **Self-Consistency** | High-stakes answers requiring verification | Accepting 3-5x cost for multiple generations to reach consensus |
| **Structured Output** | API responses requiring strict data schemas | Machine-readable responses needed; constraining model creativity |
| **ReAct** | Interleaving reasoning and acting for tool usage | General-purpose agents; explainable decision making; moderate complexity tasks |
| **Plan-and-Execute** | Complex multi-step tasks benefiting from decomposition | Tasks requiring upfront planning and visibility; complex multi-step workflows |
| **Critic/Verifier** | Quality assurance via generation and critique loops | Quality is critical; tasks have clear success criteria; can afford extra latency |
| **Hierarchical Agents** | Delegation for tasks spanning multiple domains | Complex tasks spanning domains; different tools per subtask; parallelization opportunities |
| **Multi-Agent Debate** | Verification through multiple interacting agents | High-complexity verification |
| **Human-in-the-Loop (HITL)** | Validating high-stakes actions | High-stakes actions where agent errors are unacceptable |
| **Swarm / Handoff** | Routing to specialized sub-agents | Highly specialized domain tasks requiring distinct contexts |
| **Scaffold → Implement → Verify** | Full feature development in agentic coding | Claude Code / OpenHands workflows |
| **Read-Plan-Edit** | Refactoring existing code via agents | Targeted modifications using tools like Claude Code text_editor |
| **Test-Driven Agent** | High reliability code generation | Development scenarios where agent writes tests first |
| **Shadow Review** | PR quality gate enforcement | Agent reviews diff before merge to prevent bad commits |
| **CLAUDE.md Manifest** | Project context injection for agents | Providing coding style, test commands, forbidden patterns, architecture decisions |
| **Sub-Agent Parallelism** | Large codebase changes | Executing multiple agents concurrently per module |
| **Cascading Models / Model Routing** | Cost optimization by routing to the cheapest sufficient model | High query volume; variable query complexity; cost optimization priority |
| **Speculative Execution** | Latency reduction by drafting with small model and verifying with large | Latency-critical applications; have aligned draft model; predictable generation |
| **Caching Layers (Exact Match, Semantic Cache, KV Cache, Response Cache)** | Reducing cost and latency for repeated queries | Repeated similar queries; cost reduction priority; can tolerate some staleness |
| **Retry with Backoff / Fallback** | Transient failures, rate limits, or provider unavailability | External API calls; rate limits and temporary errors are expected |
| **Circuit Breaker** | Cascading failures from a failing service | External service calls; preventing resource exhaustion when a provider goes down |
| **Bulkhead** | Resource isolation to prevent one component's failure from affecting others | Agent workloads need separate thread pools from RAG workloads; isolating components |
| **Timeout** | Slow or hanging LLM responses | Every API call level; preventing user-facing latency |
| **Token Budget** | Uncontrolled token usage blowing context limits or costs | Constraining input tokens to prevent exceeding context windows |
| **Cost Tracking Decorator** | Blindness to LLM API spend | Tracking token usage and cost metrics systematically per model |
| **Input Validation** | Prompt injection and malicious inputs | Public-facing applications; untrusted user input |
| **Output Filtering** | Data leakage and PII exposure | Systems outputting to end-users; handling sensitive data |
| **Tenant Isolation** | Cross-tenant data access | Multi-tenant architectures; enforcing access control per document/query |
| **Rate Limiting (Security)** | API abuse and denial of service | Untrusted or public users; preventing budget exhaustion by single actors |
| **Golden Set** | Regression testing for AI performance | Ensuring system quality does not degrade across updates |
| **LLM-as-Judge** | Quality scoring without manual human review | Scaling evaluation pipelines; quick quality assessment |
| **Human Eval** | Establishing ground truth | Final accuracy verification; calibrating automated evaluation |
| **A/B Testing** | Production comparison of models or prompts | Measuring user-facing metrics across different versions |
| **Prompt Compression** | Reducing token cost of long prompts | Willing to accept minor quality risks for token savings |
| **Batch Processing** | High token cost for concurrent individual requests | Latency-tolerant workloads allowing batched API calls |

## Anti-Patterns

*   **The God Prompt**
    *   *Trap:* Using a single massive prompt to handle every scenario, causing the model to struggle with conflicting instructions and waste context.
    *   *Fix:* Route queries to specialized components/handlers, each optimized for one specific task.
*   **Single Provider Dependency**
    *   *Trap:* Building the entire system so it fails completely if one LLM provider has an outage or rate limits.
    *   *Fix:* Abstract the LLM interface and use multi-provider failover.
*   **Premature Fine-Tuning**
    *   *Trap:* Spending time and money fine-tuning a model before exhausting simpler approaches like prompting, few-shot, or RAG.
    *   *Fix:* Follow a progression: prompting → few-shot → RAG → then consider fine-tuning (with 500+ examples).
*   **Retrieve Everything**
    *   *Trap:* Stuffing the prompt with too many retrieved documents regardless of relevance, drowning the signal in noise.
    *   *Fix:* Prioritize quality over quantity using reranking and similarity score thresholds (e.g., > 0.7).
*   **No Chunking Strategy**
    *   *Trap:* Using arbitrary, fixed-size blind chunking that breaks sentences and loses semantic coherence.
    *   *Fix:* Use semantic-aware chunking that respects paragraph and section boundaries with appropriate overlap.
*   **Ignoring Metadata**
    *   *Trap:* Treating all documents as equal, unstructured text, preventing filtering or access control.
    *   *Fix:* Store rich metadata (date, source, access level) in the vector database and apply filters during retrieval.
*   **Infinite Loop Risk**
    *   *Trap:* Allowing agents to run without termination conditions, causing infinite loops and spiraling costs.
    *   *Fix:* Enforce multiple hard termination limits (e.g., max steps, max cost, max time).
*   **Unsafe Tool Access**
    *   *Trap:* Giving agents unrestricted access to critical tools (e.g., delete file, unrestricted DB queries).
    *   *Fix:* Provide scoped, validated tools (e.g., specific directories, read-only databases) with audit trails.
*   **Agent Without Memory**
    *   *Trap:* A stateless agent that restarts from scratch every turn, repeating mistakes and degrading UX.
    *   *Fix:* Implement persistent memory keyed by session ID to maintain context across turns.
*   **Vague Instructions**
    *   *Trap:* Ambiguous prompts expecting specific behavior, resulting in inconsistent outputs.
    *   *Fix:* Provide specific, structured prompts detailing exact roles, formats, and forbidden actions.
*   **No Output Format**
    *   *Trap:* Expecting structured output from a prompt without specifying the desired schema.
    *   *Fix:* Specify explicit formats (like JSON schemas) in the prompt or use native structured output APIs.
*   **Vibes-Based Evaluation**
    *   *Trap:* Using manual spot-checking or "it looks good" as the sole evaluation method.
    *   *Fix:* Establish a systematic evaluation dataset (100+ examples) with defined scoring metrics.
*   **Training on Test Set**
    *   *Trap:* Using evaluation data to make development decisions, causing overfitting to specific examples.
    *   *Fix:* Maintain proper data splits with separate dev (iteration) and untouched test (final eval) sets.
*   **No Rate Limiting**
    *   *Trap:* Leaving LLM calls entirely open per user, creating denial-of-service and budget-exhaustion risks.
    *   *Fix:* Implement strict per-user rate limits (requests per minute/day) and cost limits.
*   **No Caching**
    *   *Trap:* Sending every identical request to the LLM, wasting money and adding unnecessary latency.
    *   *Fix:* Implement semantic caching with a high similarity threshold (e.g., 0.95) for common queries.
*   **Context Stuffing**
    *   *Trap:* Wasting tokens by including irrelevant context in prompts.
    *   *Fix:* Retrieve and inject only strictly relevant information into the context window.
*   **Retry Forever**
    *   *Trap:* Retrying failed requests endlessly, leading to resource exhaustion.
    *   *Fix:* Use a circuit breaker to fail-fast after a set failure threshold.
*   **Trust All Output**
    *   *Trap:* Consuming raw LLM output as absolute truth, risking downstream errors from hallucinations.
    *   *Fix:* Always verify and ground outputs using tools, checks, or retrieval contexts.
*   **No Observability**
    *   *Trap:* Operating blind without logs, making debugging impossible.
    *   *Fix:* Trace everything—including prompts, responses, token usage, and internal states.
*   **Over-trusting Computer-Use**
    *   *Trap:* Letting agents blindly click UI elements without verification.
    *   *Fix:* Implement screenshot validation and Human-in-the-Loop (HITL) for risky actions.
*   **No CLAUDE.md / Manifest**
    *   *Trap:* Deploying agentic coders without proper project context, causing architectural drift.
    *   *Fix:* Always provide a coding manifest outlining style, test commands, and rules.
*   **Thinking Mode Always On**
    *   *Trap:* Incurring 3-10x token costs with no benefit for simple queries.
    *   *Fix:* Gate advanced reasoning/thinking modes behind a complexity classifier.
