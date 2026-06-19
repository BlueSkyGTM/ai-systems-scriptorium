# Phase Inventory — ai-engineering-from-scratch

<!-- Generated per CONTEXT.md Target 1. Directory listing only — lesson contents extracted in Targets 2–9. -->

**Source:** `phases/`  
**Result:** All 20 phases (00–19) present. Required prerequisite (Target 1) passes — extraction proceeds.

**Curriculum phases** = 00, 05, 08, 11, 13, 14, 15, 16, 17, 19 (sub-lessons listed).  
**Antilibrary phases** = 01, 02, 03, 04, 06, 07, 09, 10, 12, 18 (folder names only).

---

## Curriculum Phases

### Module 1 — Setup and Tooling

#### `00-setup-and-tooling/` (12 lessons)
- 01-dev-environment
- 02-git-and-collaboration
- 03-gpu-setup-and-cloud
- 04-apis-and-keys
- 05-jupyter-notebooks
- 06-python-environments
- 07-docker-for-ai
- 08-editor-setup
- 09-data-management
- 10-terminal-and-shell
- 11-linux-for-ai
- 12-debugging-and-profiling

### Module 1 — NLP: Transformer-Forward (partial)

#### `05-nlp-foundations-to-advanced/` (29 lessons)
- 01-text-processing
- 02-bag-of-words-tfidf
- 03-word-embeddings-word2vec
- 04-glove-fasttext-subword
- 05-sentiment-analysis
- 06-named-entity-recognition
- 07-pos-tagging-parsing
- 08-cnns-rnns-for-text
- 09-sequence-to-sequence
- 10-attention-mechanism  ← transformer-forward
- 11-machine-translation
- 12-text-summarization
- 13-question-answering
- 14-information-retrieval-search
- 15-topic-modeling
- 16-text-generation-pre-transformer
- 17-chatbots-rule-to-neural
- 18-multilingual-nlp
- 19-subword-tokenization
- 20-structured-outputs-constrained-decoding
- 21-nli-textual-entailment
- 22-embedding-models-deep-dive
- 23-chunking-strategies-rag
- 24-coreference-resolution
- 25-entity-linking
- 26-relation-extraction-kg
- 27-llm-evaluation-frameworks
- 28-long-context-evaluation
- 29-dialogue-state-tracking

### Module 2 — Generative AI

#### `08-generative-ai/` (14 lessons)
- 01-generative-models-taxonomy-history
- 02-autoencoders-vae
- 03-gans-generator-discriminator
- 04-conditional-gans-pix2pix
- 05-stylegan
- 06-diffusion-ddpm-from-scratch
- 07-latent-diffusion-stable-diffusion
- 08-controlnet-lora-conditioning
- 09-inpainting-outpainting-editing
- 10-video-generation
- 11-audio-generation
- 12-3d-generation
- 13-flow-matching-rectified-flows
- 14-evaluation-fid-clip-score
- 19-visual-autoregressive-var

### Module 2 — LLM Engineering

#### `11-llm-engineering/` (17 lessons)
- 01-prompt-engineering
- 02-few-shot-cot
- 03-structured-outputs
- 04-embeddings
- 05-context-engineering
- 06-rag
- 07-advanced-rag
- 08-fine-tuning-lora
- 09-function-calling
- 10-evaluation
- 11-caching-cost
- 12-guardrails
- 13-production-app
- 14-model-context-protocol
- 15-prompt-caching
- 16-langgraph-state-machines
- 17-agent-framework-tradeoffs

### Module 3 — Tools and Protocols

#### `13-tools-and-protocols/` (23 lessons)
- 01-the-tool-interface
- 02-function-calling-deep-dive
- 03-parallel-and-streaming-tool-calls
- 04-structured-output
- 05-tool-schema-design
- 06-mcp-fundamentals
- 07-building-an-mcp-server
- 08-building-an-mcp-client
- 09-mcp-transports
- 10-mcp-resources-and-prompts
- 11-mcp-sampling
- 12-mcp-roots-and-elicitation
- 13-mcp-async-tasks
- 14-mcp-apps
- 15-mcp-security-tool-poisoning
- 16-mcp-security-oauth-2-1
- 17-mcp-gateways-and-registries
- 18-mcp-auth-production
- 19-a2a-protocol
- 20-opentelemetry-genai
- 21-llm-routing-layer
- 22-skills-and-agent-sdks
- 23-capstone-tool-ecosystem

### Module 3 — Agent Engineering

#### `14-agent-engineering/` (42 lessons)
- 01-the-agent-loop
- 02-rewoo-plan-and-execute
- 03-reflexion-verbal-rl
- 04-tree-of-thoughts-lats
- 05-self-refine-and-critic
- 06-tool-use-and-function-calling
- 07-memory-virtual-context-memgpt
- 08-memory-blocks-sleep-time-compute
- 09-hybrid-memory-mem0
- 10-skill-libraries-voyager
- 11-planning-htn-and-evolutionary
- 12-anthropic-workflow-patterns
- 13-langgraph-stateful-graphs
- 14-autogen-actor-model
- 15-crewai-role-based-crews
- 16-openai-agents-sdk
- 17-claude-agent-sdk
- 18-agno-and-mastra-runtimes
- 19-benchmarks-swebench-gaia
- 20-benchmarks-webarena-osworld
- 21-computer-use-agents
- 22-voice-agents-pipecat-livekit
- 23-otel-genai-conventions
- 24-agent-observability-platforms
- 25-multi-agent-debate
- 26-failure-modes-agentic
- 27-prompt-injection-defense
- 28-orchestration-patterns
- 29-production-runtimes
- 30-eval-driven-agent-development
- 31-agent-workbench-why-models-fail
- 32-minimal-agent-workbench
- 33-instructions-as-executable-constraints
- 34-repo-memory-and-state
- 35-initialization-scripts
- 36-scope-contracts
- 37-runtime-feedback-loops
- 38-verification-gates
- 39-reviewer-agent
- 40-multi-session-handoff
- 41-workbench-for-real-repos
- 42-agent-workbench-capstone

#### `15-autonomous-systems/` (22 lessons)
- 01-long-horizon-agents
- 02-star-family-reasoning
- 03-alphaevolve-evolutionary-coding
- 04-darwin-godel-machine
- 05-ai-scientist-v2
- 06-automated-alignment-research
- 07-recursive-self-improvement
- 08-bounded-self-improvement
- 09-coding-agent-landscape
- 10-claude-code-permission-modes
- 11-browser-agents
- 12-durable-execution
- 13-cost-governors
- 14-kill-switches-canaries
- 15-propose-then-commit
- 16-checkpoints-rollback
- 17-constitutional-ai
- 18-llama-guard
- 19-anthropic-rsp
- 20-openai-preparedness-deepmind-fsf
- 21-metr-external-evaluation
- 22-cais-caisi-societal-risk

#### `16-multi-agent-and-swarms/` (25 lessons)
- 01-why-multi-agent
- 02-fipa-acl-heritage
- 03-communication-protocols
- 04-primitive-model
- 05-supervisor-orchestrator-pattern
- 06-hierarchical-architecture
- 07-society-of-mind-debate
- 08-role-specialization
- 09-parallel-swarm-networks
- 10-group-chat-speaker-selection
- 11-handoffs-and-routines
- 12-a2a-protocol
- 13-shared-memory-blackboard
- 14-consensus-and-bft
- 15-voting-debate-topology
- 16-negotiation-bargaining
- 17-generative-agents-simulation
- 18-theory-of-mind-coordination
- 19-swarm-optimization-pso-aco
- 20-marl-maddpg-qmix-mappo
- 21-agent-economies
- 22-production-scaling-queues-checkpoints
- 23-failure-modes-mast-groupthink
- 24-evaluation-coordination-benchmarks
- 25-case-studies-2026-sota

### Module 4 — Infrastructure and Production

#### `17-infrastructure-and-production/` (28 lessons)
- 01-managed-llm-platforms
- 02-inference-platform-economics
- 03-gpu-autoscaling-kubernetes
- 04-vllm-serving-internals
- 05-eagle3-speculative-decoding
- 06-sglang-radixattention
- 07-tensorrt-llm-blackwell
- 08-inference-metrics-goodput
- 09-production-quantization
- 10-cold-start-mitigation
- 11-multi-region-kv-locality
- 12-edge-inference
- 13-llm-observability
- 14-prompt-semantic-caching
- 15-batch-apis
- 16-model-routing
- 17-disaggregated-prefill-decode
- 18-vllm-production-stack-lmcache
- 19-ai-gateways
- 20-shadow-canary-progressive
- 21-ab-testing-llm-features
- 22-load-testing-llm-apis
- 23-sre-for-ai
- 24-chaos-engineering-llm
- 25-security-secrets-audit
- 26-compliance-frameworks
- 27-finops-llms
- 28-self-hosted-serving-selection

### Module 5 — Capstone Projects

#### `19-capstone-projects/` (85 entries; numbering skips 18, 19)
- 01-terminal-native-coding-agent
- 02-rag-over-codebase
- 03-realtime-voice-assistant
- 04-multimodal-document-qa
- 05-autonomous-research-agent
- 06-devops-troubleshooting-agent
- 07-end-to-end-fine-tuning-pipeline
- 08-production-rag-chatbot
- 09-code-migration-agent
- 10-multi-agent-software-team
- 11-llm-observability-dashboard
- 12-video-understanding-pipeline
- 13-mcp-server-with-registry
- 14-speculative-decoding-server
- 15-constitutional-safety-harness
- 16-github-issue-to-pr-agent
- 17-personal-ai-tutor
- 20-agent-harness-loop-contract
- 21-tool-registry-schema-validation
- 22-jsonrpc-stdio-transport
- 23-function-call-dispatcher
- 24-plan-execute-control-flow
- 25-verification-gates-observation-budget
- 26-sandbox-runner-denylist
- 27-eval-harness-fixture-tasks
- 28-observability-otel-traces
- 29-end-to-end-coding-task-demo
- 30-bpe-tokenizer-from-scratch
- 31-tokenized-dataset-sliding-window
- 32-token-positional-embeddings
- 33-multihead-self-attention
- 34-transformer-block
- 35-gpt-model-assembly
- 36-training-loop-eval
- 37-loading-pretrained-weights
- 38-classifier-finetuning
- 39-instruction-tuning-sft
- 40-dpo-from-scratch
- 41-eval-pipeline
- 42-large-corpus-downloader
- 43-hdf5-tokenized-corpus
- 44-cosine-lr-warmup
- 45-gradient-clipping-amp
- 46-gradient-accumulation
- 47-checkpoint-save-resume
- 48-distributed-fsdp-ddp
- 49-lm-eval-harness
- 50-hypothesis-generator
- 51-literature-retrieval
- 52-experiment-runner
- 53-result-evaluator
- 54-paper-writer
- 55-critic-loop
- 56-iteration-scheduler
- 57-end-to-end-research-demo
- 58-vision-encoder-patches
- 59-vit-transformer
- 60-projection-layer-modality-align
- 61-cross-attention-fusion
- 62-vision-language-pretraining
- 63-multimodal-eval
- 64-chunking-strategies-advanced
- 65-hybrid-retrieval-bm25-dense
- 66-reranker-cross-encoder
- 67-query-rewriting-hyde
- 68-rag-eval-precision-recall
- 69-end-to-end-rag-system
- 70-task-spec-format
- 71-classical-metrics
- 72-code-exec-metric
- 73-perplexity-calibration
- 74-leaderboard-aggregation
- 75-end-to-end-eval-runner
- 76-collective-ops-from-scratch
- 77-data-parallel-ddp
- 78-zero-parameter-sharding
- 79-pipeline-parallel
- 80-checkpoint-sharded-resume
- 81-end-to-end-distributed-train
- 82-jailbreak-taxonomy
- 83-prompt-injection-detector
- 84-refusal-evaluation
- 85-content-classifier-integration
- 86-constitutional-rules-engine
- 87-end-to-end-safety-gate

---

## Antilibrary Phases (folder names only)

- `01-math-foundations/`
- `02-ml-fundamentals/`
- `03-deep-learning-core/`
- `04-computer-vision/`
- `06-speech-and-audio/`
- `07-transformers-deep-dive/`
- `09-reinforcement-learning/`
- `10-llms-from-scratch/`
- `12-multimodal-ai/`
- `18-ethics-safety-alignment/`

---

## Notes for Downstream Targets

- **Phase 05 cut (Target 3):** Transformer-forward subset starts at `10-attention-mechanism`. Pre-attention lessons (01–09, plus 16-text-generation-pre-transformer, 17-chatbots-rule-to-neural) are antilibrary. The seam lessons that *use* attention but are not pre-transformer (e.g. embedding models, chunking-for-RAG, eval frameworks, structured outputs) likely belong on the seam side — flagged for the lesson-level audit.
- **Phase 08 (Target 4):** Seam-relevant lessons are `08-controlnet-lora-conditioning` and `14-evaluation-fid-clip-score`. All others flagged `[CHECK: possibly antilibrary]`.
- **Phase 19 (Target 9):** 87 numbered folders. Note the gap in numbering (18, 19 missing) — 67–87 are fine-grained "from-scratch" build tasks grouped by sub-domain (RAG internals, distributed training, safety gate, eval runner). Capstone extraction should treat each as a project.
- **`projects/` directory:** Empty (only `.gitkeep`). No capstone content lives outside `phases/19-capstone-projects/`.
- **No missing phases.** Extraction proceeds to Target 2.
