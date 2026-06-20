# Curriculum Map — Lesson → Module

> Generated from the phase extractions. Maps each source phase and its lessons onto the five course modules. Antilibrary phases are listed separately in `output/antilibrary.md`.

## Overview

| Module | Section | Source Phase | # Lessons | Output File |
|---|---|---|---|---|
| Module 1 | Setup & Tooling | phase 00 | 12 | `output/content/module1-setup-tooling.md` |
| Module 1 | NLP Transformer-Forward | phase 05 (subset) | 19 | `output/content/module1-nlp-transformer-forward.md` |
| Module 2 | Generative AI | phase 08 | 15 | `output/content/module2-generative-ai.md` |
| Module 2 | LLM Engineering | phase 11 | 17 | `output/content/module2-llm-engineering.md` |
| Module 3 | Tools & Protocols | phase 13 | 23 | `output/content/module3-tools-protocols.md` |
| Module 3 | Agent Engineering | phases 14, 15, 16 | 89 | `output/content/module3-agent-engineering.md` |
| Module 4 | Infrastructure & Production | phase 17 | 28 | `output/content/module4-infrastructure-production.md` |
| Module 5 | Capstone Projects | phase 19 | 85 | `output/content/module5-capstone.md` |

## Lesson Rosters

### Module 1 · Setup & Tooling (phase 00)

1. 01-dev-environment
2. 02-git-and-collaboration
3. 03-gpu-setup-and-cloud
4. 04-apis-and-keys
5. 05-jupyter-notebooks
6. 06-python-environments
7. 07-docker-for-ai
8. 08-editor-setup
9. 09-data-management
10. 10-terminal-and-shell
11. 11-linux-for-ai
12. 12-debugging-and-profiling

### Module 1 · NLP Transformer-Forward (phase 05 subset)

*Note: Pre-transformer lessons (tokenization classical, bag-of-words, word2vec/glove, RNN/LSTM, seq2seq) are antilibrary.*

1. 10 Attention Mechanism — The Breakthrough
2. 11 Machine Translation
3. 12 Text Summarization
4. 13 Question Answering Systems
5. 14 Information Retrieval and Search
6. 15 Topic Modeling — LDA and BERTopic
7. 18 Multilingual NLP
8. 19 Subword Tokenization — BPE, WordPiece, Unigram, SentencePiece
9. 20 Structured Outputs & Constrained Decoding
10. 21 NLI — Textual Entailment
11. 22 Embedding Models — The 2026 Deep Dive
12. 23 Chunking Strategies for RAG
13. 24 Coreference Resolution
14. 25 Entity Linking & Disambiguation
15. 26 Relation Extraction & Knowledge Graph Construction
16. 27 LLM Evaluation — RAGAS, DeepEval, G-Eval
17. 28 Long-Context Evaluation — NIAH, RULER, LongBench, MRCR
18. 29 Dialogue State Tracking

### Module 2 · Generative AI (phase 08)

1. 01-generative-models-taxonomy-history
2. 02-autoencoders-vae
3. 03-gans-generator-discriminator
4. 04-conditional-gans-pix2pix
5. 05-stylegan
6. 06-diffusion-ddpm-from-scratch
7. 07-latent-diffusion-stable-diffusion
8. 08-controlnet-lora-conditioning
9. 09-inpainting-outpainting-editing
10. 10-video-generation
11. 11-audio-generation
12. 12-3d-generation
13. 13-flow-matching-rectified-flows
14. 14-evaluation-fid-clip-score
15. 19-visual-autoregressive-var

### Module 2 · LLM Engineering (phase 11)

1. 01-prompt-engineering
2. 02-few-shot-cot
3. 03-structured-outputs
4. 04-embeddings
5. 05-context-engineering
6. 06-rag
7. 07-advanced-rag
8. 08-fine-tuning-lora
9. 09-function-calling
10. 10-evaluation
11. 11-caching-cost
12. 12-guardrails
13. 13-production-app
14. 14-model-context-protocol
15. 15-prompt-caching
16. 16-langgraph-state-machines
17. 17-agent-framework-tradeoffs

### Module 3 · Tools & Protocols (phase 13)

1. 01-the-tool-interface
2. 02-function-calling-deep-dive
3. 03-parallel-and-streaming-tool-calls
4. 04-structured-output
5. 05-tool-schema-design
6. 06-mcp-fundamentals
7. 07-building-an-mcp-server
8. 08-building-an-mcp-client
9. 09-mcp-transports
10. 10-mcp-resources-and-prompts
11. 11-mcp-sampling
12. 12-mcp-roots-and-elicitation
13. 13-mcp-async-tasks
14. 14-mcp-apps
15. 15-mcp-security-tool-poisoning
16. 16-mcp-security-oauth-2-1
17. 17-mcp-gateways-and-registries
18. 18-mcp-auth-production
19. 19-a2a-protocol
20. 20-opentelemetry-genai
21. 21-llm-routing-layer
22. 22-skills-and-agent-sdks
23. 23-capstone-tool-ecosystem

### Module 3 · Agent Engineering (phase 14)

1. 01-the-agent-loop
2. 02-rewoo-plan-and-execute
3. 03-reflexion-verbal-rl
4. 04-tree-of-thoughts-lats
5. 05-self-refine-and-critic
6. 06-tool-use-and-function-calling
7. 07-memory-virtual-context-memgpt
8. 08-memory-blocks-sleep-time-compute
9. 09-hybrid-memory-mem0
10. 10-skill-libraries-voyager
11. 11-planning-htn-and-evolutionary
12. 12-anthropic-workflow-patterns
13. 13-langgraph-stateful-graphs
14. 14-autogen-actor-model
15. 15-crewai-role-based-crews
16. 16-openai-agents-sdk
17. 17-claude-agent-sdk
18. 18-agno-and-mastra-runtimes
19. 19-benchmarks-swebench-gaia
20. 20-benchmarks-webarena-osworld
21. 21-computer-use-agents
22. 22-voice-agents-pipecat-livekit
23. 23-otel-genai-conventions
24. 24-agent-observability-platforms
25. 25-multi-agent-debate
26. 26-failure-modes-agentic
27. 27-prompt-injection-defense
28. 28-orchestration-patterns
29. 29-production-runtimes
30. 30-eval-driven-agent-development
31. 31-agent-workbench-why-models-fail
32. 32-minimal-agent-workbench
33. 33-instructions-as-executable-constraints
34. 34-repo-memory-and-state
35. 35-initialization-scripts
36. 36-scope-contracts
37. 37-runtime-feedback-loops
38. 38-verification-gates
39. 39-reviewer-agent
40. 40-multi-session-handoff
41. 41-workbench-for-real-repos
42. 42-agent-workbench-capstone

### Module 3 · Agent Engineering (phase 15)

1. 01-long-horizon-agents
2. 02-star-family-reasoning
3. 03-alphaevolve-evolutionary-coding
4. 04-darwin-godel-machine
5. 05-ai-scientist-v2
6. 06-automated-alignment-research
7. 07-recursive-self-improvement
8. 08-bounded-self-improvement
9. 09-coding-agent-landscape
10. 10-claude-code-permission-modes
11. 11-browser-agents
12. 12-durable-execution
13. 13-cost-governors
14. 14-kill-switches-canaries
15. 15-propose-then-commit
16. 16-checkpoints-rollback
17. 17-constitutional-ai
18. 18-llama-guard
19. 19-anthropic-rsp
20. 20-openai-preparedness-deepmind-fsf
21. 21-metr-external-evaluation
22. 22-cais-caisi-societal-risk

### Module 3 · Agent Engineering (phase 16)

1. 01-why-multi-agent
2. 02-fipa-acl-heritage
3. 03-communication-protocols
4. 04-primitive-model
5. 05-supervisor-orchestrator-pattern
6. 06-hierarchical-architecture
7. 07-society-of-mind-debate
8. 08-role-specialization
9. 09-parallel-swarm-networks
10. 10-group-chat-speaker-selection
11. 11-handoffs-and-routines
12. 12-a2a-protocol
13. 13-shared-memory-blackboard
14. 14-consensus-and-bft
15. 15-voting-debate-topology
16. 16-negotiation-bargaining
17. 17-generative-agents-simulation
18. 18-theory-of-mind-coordination
19. 19-swarm-optimization-pso-aco
20. 20-marl-maddpg-qmix-mappo
21. 21-agent-economies
22. 22-production-scaling-queues-checkpoints
23. 23-failure-modes-mast-groupthink
24. 24-evaluation-coordination-benchmarks
25. 25-case-studies-2026-sota

### Module 4 · Infrastructure & Production (phase 17)

1. 01-managed-llm-platforms
2. 02-inference-platform-economics
3. 03-gpu-autoscaling-kubernetes
4. 04-vllm-serving-internals
5. 05-eagle3-speculative-decoding
6. 06-sglang-radixattention
7. 07-tensorrt-llm-blackwell
8. 08-inference-metrics-goodput
9. 09-production-quantization
10. 10-cold-start-mitigation
11. 11-multi-region-kv-locality
12. 12-edge-inference
13. 13-llm-observability
14. 14-prompt-semantic-caching
15. 15-batch-apis
16. 16-model-routing
17. 17-disaggregated-prefill-decode
18. 18-vllm-production-stack-lmcache
19. 19-ai-gateways
20. 20-shadow-canary-progressive
21. 21-ab-testing-llm-features
22. 22-load-testing-llm-apis
23. 23-sre-for-ai
24. 24-chaos-engineering-llm
25. 25-security-secrets-audit
26. 26-compliance-frameworks
27. 27-finops-llms
28. 28-self-hosted-serving-selection

### Module 5 · Capstone Projects (phase 19)

1. 01-terminal-native-coding-agent
2. 02-rag-over-codebase
3. 03-realtime-voice-assistant
4. 04-multimodal-document-qa
5. 05-autonomous-research-agent
6. 06-devops-troubleshooting-agent
7. 07-end-to-end-fine-tuning-pipeline
8. 08-production-rag-chatbot
9. 09-code-migration-agent
10. 10-multi-agent-software-team
11. 11-llm-observability-dashboard
12. 12-video-understanding-pipeline
13. 13-mcp-server-with-registry
14. 14-speculative-decoding-server
15. 15-constitutional-safety-harness
16. 16-github-issue-to-pr-agent
17. 17-personal-ai-tutor
18. 20-agent-harness-loop-contract
19. 21-tool-registry-schema-validation
20. 22-jsonrpc-stdio-transport
21. 23-function-call-dispatcher
22. 24-plan-execute-control-flow
23. 25-verification-gates-observation-budget
24. 26-sandbox-runner-denylist
25. 27-observability-otel-traces
26. 28-end-to-end-coding-task-demo
27. 29-end-to-end-coding-task-demo (Note: Duplicate slug in source data)
28. 30-bpe-tokenizer-from-scratch
29. 31-tokenized-dataset-sliding-window
30. 32-token-positional-embeddings
31. 33-multihead-self-attention
32. 34-transformer-block
33. 35-gpt-model-assembly
34. 36-training-loop-eval
35. 37-loading-pretrained-weights
36. 38-classifier-finetuning
37. 39-instruction-tuning-sft
38. 40-dpo-from-scratch
39. 41-eval-pipeline
40. 42-large-corpus-downloader
41. 43-hdf5-tokenized-corpus
42. 44-cosine-lr-warmup
43. 45-gradient-clipping-amp
44. 46-gradient-accumulation
45. 47-checkpoint-save-resume
46. 48-distributed-fsdp-ddp
47. 49-lm-eval-harness
48. 50-hypothesis-generator
49. 51-literature-retrieval
50. 52-experiment-runner
51. 53-result-evaluator
52. 54-paper-writer
53. 55-critic-loop
54. 56-iteration-scheduler
55. 57-end-to-end-research-demo
56. 58-vision-encoder-patches
57. 59-vit-transformer
58. 60-projection-layer-modality-align
59. 61-cross-attention-fusion
60. 62-vision-language-pretraining
61. 63-multimodal-eval
62. 64-chunking-strategies-advanced
63. 65-hybrid-retrieval-bm25-dense
64. 66-reranker-cross-encoder
65. 67-query-rewriting-hyde
66. 68-rag-eval-precision-recall
67. 69-end-to-end-rag-system
68. 70-task-spec-format
69. 71-classical-metrics
70. 72-code-exec-metric
71. 73-perplexity-calibration
72. 74-leaderboard-aggregation
73. 75-end-to-end-eval-runner
74. 76-collective-ops-from-scratch
75. 77-data-parallel-ddp
76. 78-zero-parameter-sharding
77. 79-pipeline-parallel
78. 80-checkpoint-sharded-resume
79. 81-end-to-end-distributed-train
80. 82-jailbreak-taxonomy
81. 83-prompt-injection-detector
82. 84-refusal-evaluation
83. 85-content-classifier-integration
84. 86-constitutional-rules-engine
85. 87-end-to-end-safety-gate

## Cross-Cutting Threads

*   `[THREAD: eval]` — Tracks frameworks, methodologies, and metrics for evaluating model and system performance across NLP, generative AI, LLMs, and agents.
*   `[GAP 2: complexity ladder]` — Tracks the progression from basic primitive concepts to complex multi-component production architectures.
*   `[THREAD: versioning]` — Tracks system state management, dataset versioning, prompt iterations, and checkpointing.
*   `[THREAD: safety]` — Tracks guardrails, compliance, jailbreak defense, alignment, and human safety intervention mechanisms across agent and infrastructure layers.
