# Module 4 · Infrastructure & Production — Chapters 11–14 Extract

> Source: `11-infrastructure-and-mlops/`, `12-security-and-access/`, `13-reliability-and-safety/`, `14-evaluation-and-observability/`.
> Tag legend: `[THREAD: eval]` = observability/monitoring · `[THREAD: safety]` = guardrails/security/reliability · `[THREAD: versioning]` = staging/registry/promotion.

## 11 — Infrastructure and MLOps

### 01 · LLM Infrastructure
Production LLM systems require a careful choice between API providers and self-hosted deployments, driven by data privacy constraints, latency requirements, and query volume scaling thresholds. Serving architectures range from simple single-model setups to sophisticated multi-model routers that classify queries and direct them to the most cost-effective model with automated fallback support. The May 2026 hardware landscape has diversified into a multi-vendor, three-tier strategy spanning NVIDIA Blackwell Ultra, AMD MI400, AWS Trainium3, and RISC-V alternatives, demanding that architects plan around memory capacity and cost-per-token rather than single-vendor lock-in. Comprehensive infrastructure management integrates horizontal scaling, strict budget tracking with rate limiting, multi-provider disaster recovery, and rigorous monitoring of latency, resource utilization, and quality degradation.
**Key concepts:** API vs self-hosting trade-offs, serving frameworks (vLLM, TGI, TensorRT-LLM), model router pattern, horizontal GPU scaling, queue-based async processing, cost tracking and budget alerts, multi-provider failover, graceful degradation, key operational metrics (TTFT, resource utilization, quality scores), Blackwell Ultra (B300), AMD MI400 Helios, AWS Trainium3, Cerebras CS-3, Tenstorrent Galaxy, three-tier fleet strategy [THREAD: eval] [THREAD: safety]

### 02 · CI/CD for LLM Applications

Traditional CI/CD pipelines must be adapted for LLM applications to handle probabilistic evaluation, non-deterministic outputs, and multi-component changes (prompts, models, retrieval indices). The pipeline incorporates multiple testing stages—static validation, unit tests, golden set tests, and sampled LLM evaluation—followed by automated quality gates that block deployment if minimum thresholds are not met. Deployment strategies rely on canary or shadow deployments to limit blast radius, paired with continuous production monitoring and automated rollback triggers based on error rates, latency limits, and quality degradation.

**Key concepts:** Probabilistic evaluation, golden set testing, quality gates, LLM-as-judge, canary deployment, shadow deployment, automated rollback, prompt versioning, statistical testing, regression detection. [THREAD: eval] [THREAD: safety] [THREAD: versioning]

## 12 — Security and Access

### 01 · LLM Security [THREAD: safety]
LLM systems introduce unique security threats that require defense-in-depth strategies fundamentally different from traditional application security, encompassing prompt injection, data leakage, and insecure output handling. The threat landscape has evolved into an automated attacker-defender arms race, where AI-driven offensive tools (like generating zero-day exploits) and defensive agent harnesses (like multi-model security review systems) operate concurrently. Effective mitigation relies on layered architectures including input/output sanitization, strict instruction hierarchy, permission-based retrieval for multi-tenant isolation, and capability gating for untrusted external content. As agents increasingly interact with external data, implementing robust access controls, structural quoting, and continuous red-team testing is critical to prevent unauthorized data access and system manipulation.

**Key concepts:** Prompt injection, OWASP Top 10 for LLMs, Data leakage, Insecure output handling, Defense in depth, Access control, Rate limiting, Tool permission control, Multi-tenant security, Indirect Prompt Injection (IPI), Red team testing, AI-driven offense/defense, Content trust tagging, Capability gating, Model signing.

### 02 · Access Control for LLM Systems [THREAD: safety]
This section covers authentication, authorization, and data isolation patterns essential for securing multi-user and multi-tenant LLM applications. It details authentication mechanisms using API keys and JWTs, alongside authorization models like RBAC, ABAC, and model-tier access controls. Critical LLM-specific risks such as prompt injection, data leakage, and cross-tenant context pollution are mitigated through strict tenant isolation at the vector database, cache, and prompt-building levels. The section also defines API key lifecycle management (creation, validation, rotation with grace periods) and comprehensive audit logging for compliance reporting.

**Key concepts:** Authentication (API Keys, JWT, Scopes), Authorization (RBAC, ABAC, Policy Evaluation), Model-Level Permissions, Tenant Isolation (Data, Prompt, Cache), API Key Management (Hashing, Lifecycle, Rotation), Audit Logging, Compliance Reporting, Least Privilege, Defense in Depth.

## 13 — Reliability and Safety

### 01 · Guardrails and Safety [THREAD: safety]
Guardrails are systems that constrain LLM behavior to ensure safe, reliable outputs and prevent unsafe actions in production environments. They employ a defense-in-depth architecture, systematically chaining input guardrails (e.g., topic filtering, PII detection, injection defense), output guardrails (e.g., content safety, relevance, factuality), and action validation (e.g., scope checks, sandboxing). Failure handling relies on graceful degradation strategies such as structured output retries, fallback LLM chains, and human escalation for low-confidence responses. Production implementations are commonly orchestrated via pipelines and specialized frameworks like NeMo Guardrails and Guardrails AI.
**Key concepts:** Defense-in-depth, Input/Output Guardrails, Topic classification, PII detection and redaction, Prompt injection detection, Sandwich defense, Delimiter defense, Input/output isolation, Hallucination mitigation, Context grounding, Self-consistency, Abstention strategy, Structured output validation, Action safety, Sandbox execution, Fallback chains, Human escalation, NeMo Guardrails, Guardrails AI

### 02 · Ensemble Methods for LLM Reliability [THREAD: eval]
Ensemble methods coordinate multiple models or multiple generation passes to improve production reliability, reduce hallucinations, and mitigate single-judge bias. Key patterns include Panel of LLM Judges (PoLL) for evaluation, Self-Consistency and Best-of-N for generation, and Multi-Agent Debate or Mixture of Agents (MoA) for verification and synthesis. These techniques trade increased computational cost and latency for measurable accuracy gains (5–30%) and greater output robustness. Implementations rely heavily on parallel execution, conservative aggregation strategies (e.g., median, trimmed mean, percentile-based scoring) to prevent reward hacking, and inter-judge agreement tracking to flag low-confidence results for human review.
**Key concepts:** Panel of LLM Judges (PoLL), positional debiasing, Self-Consistency (majority voting), Best-of-N with reward models, reward hacking prevention, Multi-Agent Debate, Mixture of Agents (MoA), ensemble vs. arbitration, cost-accuracy tradeoffs.

### 03 · Reliability Patterns [THREAD: safety]
Production LLM systems require advanced reliability patterns beyond basic retry logic to handle unique failure modes such as rate limiting, context overflow, quality degradation, and provider outages. Key strategies include exponential backoff with jitter, circuit breakers to halt cascading failures during systemic outages, and bulkheads to isolate resources across different workloads. Additionally, implementing layered and adaptive timeouts, graceful degradation pipelines, multi-provider failovers, and request hedging ensures high availability and responsive behavior when dependencies fail.

**Key concepts:** Reliability targets, Retryable vs non-retryable errors, Exponential backoff with jitter, Circuit breaker (closed/open/half-open), Bulkhead pattern, Layered timeouts, Adaptive timeouts, Graceful degradation levels, Multi-provider failover, Request hedging.

## 14 — Evaluation and Observability

### 01 · LLM Evaluation [THREAD: eval]
Evaluating LLM systems requires assessing multiple independent quality dimensions—such as correctness, faithfulness, and safety—rather than relying on single objective metrics. Practitioners employ a combination of automated programmatic methods, LLM-as-judge, and human evaluation to score outputs across these dimensions. For complex workflows like RAG and autonomous agents, evaluation expands to cover specific context metrics and step-by-step trajectory analysis. Modern production stacks employ a layered architecture of distilled inline judges, frontier model calibration, and human review to track quality, catch drift, and manage costs at scale.
**Key concepts:** Evaluation dimensions, Automated evaluation methods, LLM-as-Judge (pairwise comparison, judge calibration), Human evaluation (inter-annotator agreement), RAG evaluation (RAGAS, faithfulness, context relevance), Evaluation pipelines, Production monitoring (online evaluation, drift detection), Layered judge architecture, Distilled judges (Galileo Luna-2), Agent benchmarks (tau2-bench, pass^k), Agent-as-Judge (Process Reward Models, trajectory grading), HaluMem (operation-level hallucination benchmarks).

### 02 · LLM Observability [THREAD: eval]
LLM observability extends traditional monitoring by treating output quality, non-determinism, and token economics as first-class metrics alongside standard operational concerns. Systems implement this via three pillars—logging, metrics, and traces—using tools like OpenTelemetry or Langfuse to instrument multi-component pipelines such as RAG architectures. Quality and drift detection are continuously assessed using statistical baselines and LLM-as-a-judge sampling, while real-time cost trackers attribute per-token expenses to specific users, teams, or use cases. Alerting strategies prioritize operational thresholds (error rate, latency), quality degradation, and budget limits, often routing alerts based on severity levels ranging from critical to informational.
**Key concepts:** Three pillars (logs, metrics, traces), LLM-as-a-judge, quality drift detection, time to first token (TTFT), token economics and cost attribution, OpenTelemetry tracing, RAG pipeline instrumentation, statistical drift detection.
