# Ahab — Interview Prep (Chapter 00)

> **ROUTING NOTE:** This output feeds the **Ahab project**, NOT the Sans-Python curriculum. Source: `00-interview-prep/`.

## Question Bank (`01-question-bank.md`) — 116 questions by topic


### RAG Architecture Questions
- **Q1** — Walk me through the architecture of a production RAG system
- **Q2** — When would you choose RAG over fine-tuning, and vice versa?
- **Q3** — How do you handle the "lost in the middle" problem?
- **Q4** — Explain chunking strategies and when to use each
- **Q5** — How would you evaluate a RAG system?
- **Q6** — Describe hybrid search and when you would use it
- **Q7** — How do you handle multi-tenant RAG systems?
- **Q8** — What is reranking and when would you skip it?
- **Q9** — How would you handle documents with tables, charts, and images?
- **Q10** — Explain vector database indexing algorithms

### Agentic Systems Questions
- **Q11** — What is the difference between an agent and a workflow?
- **Q12** — Explain the ReAct pattern
- **Q13** — How do you implement tool use / function calling?
- **Q14** — How would you design a multi-agent system?
- **Q15** — Explain the Model Context Protocol (MCP)
- **Q16** — How do you handle long-running agent tasks?
- **Q17** — What is flow engineering?

### Model Selection Questions
- **Q18** — How do you choose between Claude Sonnet 4.6, GPT-5.5, and Gemini 3.1 Pro for a production workload?
- **Q19** — When would you use a small language model vs a frontier model?
- **Q20** — Explain reasoning models and controllable thinking. When are they worth the cost?
- **Q21** — How do you evaluate and compare embedding models?

### Optimization Questions
- **Q22** — Explain the KV cache and why it matters
- **Q23** — What is speculative decoding and when would you use it?
- **Q24** — Compare batching strategies for LLM serving
- **Q25** — How do you optimize LLM inference costs?
- **Q26** — Explain quantization techniques for LLM deployment

### Evaluation Questions
- **Q27** — How do you evaluate LLM outputs when there is no ground truth?
- **Q28** — Explain the RAGAS evaluation framework
- **Q29** — How do you detect and handle hallucinations?

### Production and MLOps Questions
- **Q30** — How do you implement observability for LLM applications?
- **Q31** — Describe CI/CD for LLM applications
- **Q32** — How do you handle rate limits and quotas?
- **Q33** — Describe strategies for LLM application security

### Tooling and Lifecycle Questions
- **Q34** — Explain the tradeoffs between different vector database options
- **Q35** — How do you handle model updates and deprecations from providers?
- **Q36** — What is DSPy and when would you use it?
- **Q37** — How do you design a feedback loop for continuous improvement?
- **Q38** — Explain token counting and why it matters
- **Q39** — How do you evaluate and compare RAG systems objectively?

### Ensemble Methods Questions
- **Q40** — When would you use Self-Consistency vs Best-of-N sampling?
- **Q41** — How do you prevent reward hacking when using Best-of-N?
- **Q42** — Design an evaluation system for comparing two LLMs on open-ended tasks.
- **Q43** — What is the difference between ensemble learning and model arbitration?
- **Q44** — When would you use Multi-Agent Debate vs Mixture of Agents?
- **Q45** — When should you use LangChain vs build from scratch?
- **Q46** — How do you manage context window limits with long conversations?
- **Q47** — How do you defend against prompt injection attacks?
- **Q48** — When would you choose fine-tuning over prompt engineering?
- **Q49** — How do you optimize latency for real-time LLM applications?

### System Design Scenarios

### Advanced Questions (December 2025)
- **Q50** — Explain Model Context Protocol (MCP) and why it matters for production agents
- **Q51** — Your agent takes 47 LLM calls to complete a task that should take 5. How do you debug this?
- **Q52** — When would you choose a reasoning model (o3, DeepSeek-R1) over a standard model (GPT-5.2)?
- **Q53** — How do you prevent prompt injection in a system that accepts user input?
- **Q54** — Explain the difference between Agentic RAG and traditional RAG
- **Q55** — Your RAG system works great on test data but fails in production. What do you check?
- **Q56** — How do you implement guardrails for an autonomous agent that can take real-world actions?
- **Q57** — Explain KV Cache and why it matters for inference optimization
- **Q58** — Design a system where one user's prompt cannot leak to another user
- **Q59** — Your LLM costs are 10x higher than expected. Walk through your investigation
- **Q60** — How would you evaluate whether an LLM is hallucinating?
- **Q61** — Explain the tradeoffs between different embedding models for RAG
- **Q62** — Your search results are relevant but the LLM ignores them and answers from its training data. How do you fix this?
- **Q63** — How do you handle version control for prompts in production?
- **Q64** — Design a semantic cache that actually works in production
- **Q65** — Your agent can execute arbitrary Python code. How do you make this safe?

### Advanced Questions - March 2026
- **Q66** — When would you use Claude's extended or adaptive thinking vs. standard mode, and how do you control costs?
- **Q67** — How does reasoning effort work on GPT-5.5, and when would you choose it over Claude Opus 4.8?
- **Q68** — Explain how you would design a system that uses Claude Code (or OpenHands) as a CI/CD component for automated bug fixing.
- **Q69** — DeepSeek released frontier-quality open-weight models at dramatically lower cost. How does this change your production architecture decisions?
- **Q70** — Explain provider-level prompt caching and how you would architect a system to maximize cache hit rate.
- **Q71** — How do you build a production LLM evaluation pipeline using LLM-as-a-Judge? What are the failure modes?
- **Q72** — Explain MCP (Model Context Protocol) 2.0 and the security risks of running MCP servers in production.
- **Q73** — How would you design a semantic routing system that dynamically selects the cheapest model that can handle a query with acceptable quality?
- **Q74** — A candidate claims their AI system achieves 95% accuracy. What questions do you ask to assess whether this is meaningful?
- **Q75** — How do SWE-bench Verified and LiveCodeBench differ, and which matters more for evaluating a coding agent?
- **Q76** — Your production LLM application suddenly shows a 30% increase in hallucination rate after a model provider silently updated their model. How do you detect and respond?
- **Q77** — How would you design a multi-provider LLM architecture for 99.9% availability?
- **Q78** — Someone on your team suggests replacing your entire RAG pipeline with a 1M-token context window and just loading all documents every request. How do you evaluate this idea?
- **Q79** — How do you approach prompt injection defense in a multi-tenant agentic system where the agent reads external web pages or documents?
- **Q80** — What is the difference between error analysis and automated evals, and when should you prioritize each?

### Advanced Questions - May 2026
- **Q81** — Pick a frontier model for a production agentic workload in June 2026 and defend the choice against Claude Fable 5, Claude Opus 4.8, GPT-5.5, Gemini 3.1 Pro, and DeepSeek V4 Pro.
- **Q82** — DeepSeek V3.2 and V4 publish $0.28/$0.42 per 1M tokens with a 98% cache-hit discount and 50% off-peak pricing. Refactor a production LLM architecture to fully exploit these.
- **Q83** — Llama 4 Scout claims a 10M-token context window, but Fiction.LiveBench scores it at 15.6% at 128K tokens. How would you advise a team that wants to "just dump everything into Scout's context"?
- **Q84** — Latent / continuous-space reasoning (recurrent-depth, Latent Thinking Optimization, ETD) reportedly beats token-space chain-of-thought on math benchmarks. When would you actually deploy a latent-reasoning model in production?
- **Q85** — Memory architectures (Mem0, A-MEM, multi-layered memory frameworks) are getting hyped at ICLR 2026 as the "new bottleneck beyond context window." When does your agent actually need a memory layer beyond a long context window?
- **Q86** — The standalone "Prompt Engineer" job title has effectively disappeared from major job boards in 2026. What replaced it, and what does that tell us about the field?
- **Q87** — Your production agent enters a runaway loop, calling a broken tool 400 times in five minutes. Walk through the architectural patterns that prevent this - at the orchestrator, the tool layer, and the cost-guard layer.
- **Q88** — Agent-as-judge vs LLM-as-judge - when does the upgrade pay off, and what new failure modes does it introduce?
- **Q89** — Design a Process Reward Model (PRM) for a customer-support agent. What signals do you score, and how do you avoid degenerate reward?
- **Q90** — Google announced A2A protocol v1.0 GA at Cloud Next 2026 with 150+ org adoption. When do you use A2A vs MCP, and how do they compose?
- **Q91** — A CVSS 9.8 STDIO transport vulnerability was disclosed in MCP in May 2026. Walk through the architectural fix for a production MCP deployment.
- **Q92** — On May 11, 2026, Google's threat intelligence team disclosed the first AI-built zero-day used in the wild - a 2FA-bypass exploit targeting an open-source sysadmin tool. What changes about your threat model?
- **Q93** — EU AI Act enforcement powers begin August 2, 2026. You're building a multi-tenant AI product sold into Germany and France. Walk through your FRIA/DPIA dual-assessment workflow.
- **Q94** — You're building a computer-use agent (Claude Cowork, OpenAI Operator-class) that can fill forms, click buttons, and read screen content. Design the sandbox, network policy, and human-confirmation pattern.
- **Q95** — You're integrating a third-party fine-tuned model into your production stack. The vendor publishes weights but not training data. Walk through your supply-chain trust process - what does Sigstore / OpenSSF Model Signing buy you, and what gaps remain?
- **Q96** — Indirect prompt injection (IPI) attacks rose 32% from Nov 2025 to Feb 2026 per Google. Your RAG agent reads web pages and documents from untrusted sources. Design a layered defense.
- **Q97** — Llama 4 Maverick (sparse MoE, 17B active / 128 experts) and DeepSeek V4 Pro (1.6T total / 49B active) require MoE-aware system design. Walk through what changes in your inference serving.
- **Q98** — A customer wants to reduce their $50K/month frontier-model spend by distilling a custom model for their workload. Quote a distillation project as a budgeted line item - costs, payback, re-distillation cadence.
- **Q99** — You're deploying a high-throughput inference service for an open-weight model. Pick between vLLM, SGLang, and TensorRT-LLM for a specific workload and defend the choice.
- **Q100** — It's May 2026. You're sizing a fleet for a 6-month-horizon inference workload. Walk through the AI accelerator landscape - NVIDIA Blackwell Ultra (B300), AMD MI400, AWS Trainium3, Google TPU v6, Cerebras WSE-3 - and pick a strategy.
- **Q101** — Multi-tenant RAG isolation - you're choosing between Pinecone namespaces, Weaviate per-tenant shards, and pgvector with Row-Level Security. Which fails first under noisy-neighbor pressure, and which fails first under an audit?
- **Q102** — Forward Deployed Engineer (FDE) is the breakout role of 2026 - OpenAI, Anthropic, and Google are all hiring hundreds. When does your company need to hire FDEs vs growing your customer-success or solutions-engineering function?
- **Q103** — In April 2026 Anthropic temporarily blocked Claude Pro/Max subscriptions from powering third-party agents (the OpenClaw incident). They reversed it shortly after with an "Agent SDK credit" system. What does this tell you about vendor lock-in risk in your AI architecture?
- **Q104** — Anthropic's Project Vend Phase 2 ran Claude as an autonomous shop manager for an extended period. What does the experiment teach about LLM agency limits, and how does it shape your production agent design?
- **Q105** — Meta launched the closed-weight Muse Spark model in April 2026 - its first proprietary model since the original Llama. Meanwhile Llama 4 Behemoth's release was paused amid 'capability concerns.' What does this mean for your open-source strategy?
- **Q106** — You're an Engineering Manager standing up the AI eval culture on a team. How do you set up evals so they actually drive better decisions, without engineers gaming the metrics?
- **Q107** — You're an AI Product Manager. Write the structure of a PRD for a generative AI feature that includes hallucination policy, fallback behavior, and an eval methodology section.
- **Q108** — Design a real-time fraud detection system with a hard p99 < 500ms latency requirement, using both ML rules and an LLM-RAG layer. Walk through the latency budget breakdown.
- **Q109** — Cursor 3 launched in April 2026 with an "Agent-First" interface, and Cursor's CEO has stated that >50% of internal PRs at Anysphere come from cloud agents. How do you design code review processes for a world where a majority of PRs are agent-generated?
- **Q110** — A regulator asks why your AI legal-research tool fabricated a citation in a brief. The actual incident: Sullivan & Cromwell apologized in Q1 2026 for a similar issue, and $145K in court sanctions have been levied across cases. Walk through your incident-response and disclosure policy.

### Advanced Questions - June 2026
- **Q111** — Claude Fable 5 routes sensitive queries to Claude Opus 4.8 via classifier-gated fallback. Critique this as a system design pattern and describe where you would apply tier routing in your own stack.
- **Q112** — Your agent performs well on short tasks but degrades badly past 30 minutes of autonomous work. Diagnose and fix it using context engineering.
- **Q113** — Your computer-use agent passes demos but fails 30% of real workflows in production. Walk through your reliability engineering plan.
- **Q114** — Design a skill system for a fleet of internal agents using Agent Skills. How do skills differ from MCP tools and from fine-tuning?
- **Q115** — Your team's eval scores keep improving but production complaints are flat. Diagnose the eval gaming problem and redesign the eval system.
- **Q116** — Design cost-aware multi-provider routing for June 2026 prices: Fable 5 at $10/$50, Opus 4.8 at $5/$25, GPT-5.5 at $5/$30, Sonnet 4.6 at $3/$15, DeepSeek V4 Flash at $0.14/$0.28.

## Companion Files (`00-interview-prep/`)

- `02-answer-frameworks.md` — Answer Frameworks for AI System Design Interviews
- `03-common-pitfalls.md` — Common Pitfalls in AI System Design Interviews
- `04-whiteboard-exercises.md` — Whiteboard Exercises for AI System Design
- `05-behavioral-for-ai-roles.md` — Behavioral Questions for AI/ML Roles
- `06-job-market-trends-2026.md` — AI Job Market Trends - June 2026
- `07-faq.md` — Frequently Asked Questions: AI Engineering, RAG, and Agents
- `README.md` — AI System Design Interview Preparation
