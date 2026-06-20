# Module 5 · Capstone Projects — Phase 19 Extract

> Source: `phases/19-capstone-projects/`. Phase README is a stub; all content lives in per-project `docs/en.md`.
> This module has two parts:
> - **Part 1 — End-to-end capstone projects (01–17):** self-contained portfolio builds, each producing a deployable/demoable system and a portfolio artifact.
> - **Part 2 — Coding-agent harness build sequence (20–87):** a long, dependency-ordered component track that constructs an agent harness, tokenizer/GPT-from-scratch, research agent, multimodal/RAG/eval/distributed-training, and a safety-gate stack piece by piece. Each entry names what it **Builds** and the **Artifact** downstream lessons depend on.

## Part 1 — End-to-End Capstone Projects

### 01 · Terminal-Native Coding Agent

By 2026, coding agents share a settled architecture: a terminal harness, a permissioned tool surface, a sandbox, and a plan-act-observe loop built around a frontier model. This capstone asks the student to build one end to end — CLI in, pull request out — and measure it against mini-swe-agent and Live-SWE-agent on SWE-bench Pro. The project demonstrates that the hard part of a coding agent is not the model call but the tool loop, the sandbox, and the cost ceiling on a 50-turn run.

**Builds:** A terminal-native coding agent harness (Bun + Ink TUI) with plan/act/observe/recover loop, MCP StreamableHTTP tool surface, E2B/Daytona sandbox isolation, eight lifecycle hooks, cost controls, OpenTelemetry observability, and automated PR posting.
**Artifact:** A sandboxed coding agent skill (`outputs/skill-terminal-coding-agent.md`) that runs the full plan-act-observe loop and returns a PR URL plus a trace bundle, evaluated against a 30-task SWE-bench Pro subset.

### 02 · RAG over Codebase (Cross-Repo Semantic Search)

This project solves the problem of cross-repo code search that understands semantic meaning rather than just string matching. The student builds an end-to-end system that ingests multiple repositories, parses code with tree-sitter at AST node boundaries, embeds chunks with dual dense and sparse representations, and uses a LangGraph query agent to answer questions with file-and-line citations. The system is built to handle a 2M-line codebase fleet across 10 repos and survive incremental re-indexing triggered by git pushes.

**Builds:** An AST-aware ingestion pipeline, a hybrid (dense + BM25) search index, a symbol graph, and a LangGraph retrieval-re-rank-synthesis query agent with citation enforcement.
**Artifact:** A deliverable skill (`outputs/skill-codebase-rag.md`) that stands up the ingestion pipeline, hybrid index, and query agent to return cited answers for cross-repo questions.

### 03 · Real-Time Voice Assistant (ASR to LLM to TTS)

A voice agent must achieve sub-800ms end-to-end latency, handle barge-in interruptions, and execute tool calls without stalling audio. This capstone has the student build a full streaming pipeline—ASR, turn detection, streaming LLM, and streaming TTS—wired through WebRTC, along with cross-cutting concerns for barge-in, tool side-channels, and network backpressure. The system is evaluated against a quantitative bar measuring WER, false-cutoff rate, MOS, and sustained concurrency.

**Builds:** A streaming voice agent pipeline using LiveKit Agents with Deepgram Nova-3 ASR, Silero VAD v5, a LiveKit turn-detector, a streaming LLM, and Cartesia Sonic-2 TTS, plus an eval harness and load test.

**Artifact:** `outputs/skill-voice-agent.md` — a latency-and-quality report documenting a deployed LiveKit agent meeting the measurement bar (p50 first-audio-out under 800ms, false-cutoff under 3%, WER under 8%, MOS above 4.2, 50 concurrent calls).

### 04 · Multimodal Document QA
Enterprises struggle with PDFs that traditional OCR pipelines mangle, such as scanned financial 10-Ks with rotated tables, scientific papers dense with equations, and charts. This project solves that signal loss by implementing a 2026 vision-first late-interaction pipeline using ColQwen that treats each page as an image and embeds it with multi-vector late interaction. Students build the pipeline end-to-end on 10k pages and publish a performance comparison against an OCR-then-text baseline.
**Builds:** A vision-first multimodal document QA system featuring ColQwen multi-vector embeddings, MaxSim retrieval, DocPruner compression, and a VLM answerer with an evidence-region viewer UI.
**Artifact:** A tuned document QA system evaluated against an OCR-then-text baseline on ViDoRe v3, documented as a portfolio skill artifact.

### 05 · Autonomous Research Agent (AI-Scientist Class)
The student builds an autonomous research agent that performs best-first tree search over candidate experiments within a $30 budget per paper, following the architecture pioneered by Sakana AI's AI-Scientist. The system implements a plan-execute-verify loop, executing each experiment in a sandboxed environment with no network egress and strict resource limits, then compiles results into a LaTeX paper judged by an automated reviewer ensemble.
**Builds:** A plan-execute-verify tree-search agent featuring sandboxed code execution, a vision-feedback LaTeX writer, a five-judge NeurIPS-style reviewer ensemble, and a sandbox-escape red team defense.
**Artifact:** A reproducible research bundle (`paper.pdf`, `review.md`, and `trace.json`) shipped with a reproducibility README.

### 06 · DevOps Troubleshooting Agent for Kubernetes

An alert webhook fires, and an agent reads telemetry, walks a knowledge graph of Kubernetes objects, ranks root-cause hypotheses, and posts a Slack brief with approval buttons. The system is read-only by default, with every remediation gated by a human, and is evaluated on 20 synthetic incidents. It ingests kube-state-metrics into a graph, receives alerts via a FastAPI endpoint, uses a LangGraph agent to sample telemetry slices and hypothesize causes, and posts ranked evidence with Slack approval cards for destructive actions.

**Builds:** A LangGraph root-cause agent backed by a K8s knowledge graph, read-only MCP tool surface, hypothesis ranking with evidence scoring, Slack-gated remediation flow, and an append-only audit log.
**Artifact:** `outputs/skill-devops-agent.md` — the deliverable enabling ranked root-cause hypotheses and a Slack-gated remediation flow.

### 07 · End-to-End Fine-Tuning Pipeline (Data to SFT to DPO to Serve)

The project addresses the need for a reproducible fine-tuning pipeline that takes raw data through supervised fine-tuning (SFT), preference alignment (DPO or GRPO), quantization, and speculative-decoded serving with measurable cost per million tokens. The student runs an 8B base model (Llama 3.3, Qwen3, or Gemma 3) through five stages — data hygiene, SFT, DPO/GRPO, quantization, and vLLM serving with EAGLE-3 — then evaluates gains against lm-evaluation-harness, RewardBench-2, MT-Bench-v2, and MMLU-Pro, and publishes a model card under the 2026 Model Openness Framework.

**Builds:** A single-command pipeline (YAML in, served endpoint out) covering Datatrove dedup, Nemotron-CC quality filtering, PII scrubbing, Axolotl SFT with ZeRO-3, TRL DPO/GRPO preference tuning, GPTQ/AWQ/GGUF quantization, vLLM 0.7 with EAGLE-3 serving, ablation evals, safety eval via Llama Guard 4, and a 2026 MOF model card.

**Artifact:** A served endpoint plus a model card with eval deltas, serving metrics ($/1M tokens, tokens/s, EAGLE-3 acceptance rate), reproducibility seeds, and the YAMLs and commit SHAs for full pipeline reproducibility.

### 08 · Production RAG Chatbot for a Regulated Vertical

This capstone tackles the most-shipped production AI shape of 2026: a retrieval-augmented generation pipeline built for a regulated domain (legal, clinical, or insurance). The student builds an end-to-end system spanning high-fidelity ingestion (docling/Unstructured + ColPali), hybrid search with reranking (bge-reranker-v2-gemma), citation-enforced synthesis with prompt caching (Claude Sonnet 4.7), multi-layer guardrails (Llama Guard 4 + NeMo Guardrails), and continuous drift observability. The capstone passes upon successfully clearing a 200-question golden set, a red-team adversarial suite, and a live drift dashboard.

**Builds:** A regulated-domain chatbot with role-based access and jurisdiction-aware compliance, featuring hybrid retrieval, prompt-cached synthesis, multi-layer guardrails, and full observability.
**Artifact:** `outputs/skill-production-rag.md` — a deployed, rubric-passing chatbot deliverable featuring compliance labels, RAGAS/faithfulness evaluation, red-team clearance, and live Phoenix drift monitoring.

### 09 · Code Migration Agent
The project tackles repo-level language and runtime upgrades (e.g., Java 8 to 17, Python 2 to 3) by combining a deterministic AST rewrite substrate with an LLM agent loop to handle ambiguous cases that mechanical recipes cannot. The student builds an end-to-end migration pipeline that executes deterministic recipes, spins up per-branch sandboxes for agent-driven build/test iterations, and generates a taxonomy of migration failures across 50 real repositories.
**Builds:** A two-layer code migration system combining deterministic recipes (OpenRewrite/libcst) with an agent loop (LangGraph/OpenAI Agents SDK) operating in Daytona sandboxes to produce green-CI branches or file failures under a tagged taxonomy.
**Artifact:** A failure-taxonomy dashboard and migration skill document (`outputs/skill-migration-agent.md`) reporting the pass rate, cost-per-repo, and coverage preservation across a 50-repo MigrationBench subset run.

### 10 · Multi-Agent Software Engineering Team
Single-agent coding harnesses hit a ceiling on large tasks because a single context window cannot hold an architecture plan, parallel codebase slices, reviewer commentary, and test output simultaneously. Students build a multi-agent software factory where an architect plans, N coders work in parallel git worktrees, a reviewer gates, and a tester verifies, communicating via typed A2A-protocol messages on a shared task board. The system is evaluated on 50 SWE-bench Pro issues to identify which handoffs break and how multi-agent performance compares per dollar against a single-agent baseline.
**Builds:** A multi-agent team of typed roles (Architect, Coders, Reviewer, Tester) orchestrated via LangGraph with isolated git worktrees, a merge coordinator, and a file-backed task board.
**Artifact:** A portfolio post-mortem documenting SWE-bench Pro results, per-role token accounting, and a handoff-failure histogram.

### 11 · LLM Observability & Eval Dashboard

Every AI team running production traffic needs an observability plane for cost attribution, hallucination detection, drift monitoring, and alerting. Students build a self-hosted dashboard that ingests OpenTelemetry GenAI-semconv spans from at least four SDK families, runs batch eval jobs (DeepEval, RAGAS, custom LLM-judge) over sampled traces, detects distribution drift, and alerts via Prometheus Alertmanager. The success bar is catching a deliberately injected regression — a prompt that starts leaking PII — and firing an alert in under five minutes.

**Builds:** A self-hosted observability system with an OTLP HTTP collector, ClickHouse span store, Postgres metadata store, batch eval jobs, embedding-space drift detector, and a Next.js 15 dashboard.

**Artifact:** `outputs/skill-llm-observability.md` documenting a dashboard that ingests LLM application traces, runs evals, alerts on drift, and surfaces cost-per-user breakdowns.

### 12 · Video Understanding Pipeline (Scene, QA, Search)
Long-form video QA at scale requires a scene-level index because natively processing hundreds of hours of video is infeasible. The capstone is ingesting 100 hours of video, segmenting it into scenes, aligning transcripts, and building a multi-vector index that supports queries with timestamped citations and frame previews. Students evaluate the system against public benchmarks and explicitly measure hallucination rates on counting and action-type questions.
**Builds:** An end-to-end video understanding pipeline combining scene segmentation (TransNetV2/PySceneDetect), VLM captioning, Whisper ASR alignment, a multi-vector Qdrant index, and temporal grounding with a VLM synthesizer.
**Artifact:** `outputs/skill-video-qa.md` — a deliverable pipeline that indexes scenes from a URL or uploaded video and answers natural-language questions with timestamped citations and frame previews.

### 13 · MCP Server With Registry and Governance

This project solves the enterprise challenge of deploying Model Context Protocol (MCP) servers at scale by building a production-grade tool-use system with per-tenant OAuth scopes, OPA policy gating, stateless horizontal scaling, and per-call audit logs. Students build an MCP server exposing internal tools (Postgres, S3, Jira, etc.), a registry UI for platform discovery, and a human-approval gate via Slack for destructive tools.

**Builds:** A production-grade MCP server exposing 10 internal tools via StreamableHTTP transport with OAuth 2.1 scopes and OPA gating, alongside a separate registry service for tool discovery and a destructive-tool server requiring human approval.

**Artifact:** A production-grade MCP server, registry, and audit layer for internal tools with OAuth 2.1 scopes and OPA gating, documented as a portfolio-ready skill deliverable.

### 14 · Speculative-Decoding Inference Server

This capstone addresses the production serving problem of achieving high LLM throughput using speculative decoding techniques like EAGLE-3 and P-EAGLE. The student builds an end-to-end Kubernetes-deployed inference server using vLLM 0.7 or SGLang, configuring draft heads and target models to serve two open models at 2.5x+ baseline throughput while generating a comprehensive tail-latency and cost report.

**Builds:** A production inference server with EAGLE-3/P-EAGLE speculative decoding, FP8/INT4 quantization, and Kubernetes HPA autoscaling on queue-wait metrics.
**Artifact:** `outputs/skill-inference-server.md` — a measured serving stack deliverable containing speedup benchmarks, acceptance rates across traffic distributions, p99 tail-latency reports at varying batch sizes, and a $/1M tokens cost comparison.

### 15 · Constitutional Safety Harness + Red-Team Range
This capstone addresses the problem of composing multiple safety classifiers correctly around a production LLM without over-refusing benign prompts or leaving exploitable holes. The student hardens a target application by wiring together a five-layer safety pipeline (input sanitization, policy rails, classifier gate, output filter, and human-in-the-loop tier) and then runs an autonomous red-team range executing six or more attack families against it. A constitutional self-critique training run produces a measurable before/after harmlessness delta.
**Builds:** A five-layer production safety harness (NeMo Guardrails, Llama Guard 4, X-Guard, ShieldGemma-2, Presidio) wrapping a target LLM, plus a scheduled red-team range running PAIR, TAP, GCG, encoding, multi-turn, and multilingual attacks.
**Artifact:** A reproducible CVSS-scored red-team findings report with disclosure timelines and a before/after harmlessness delta measurement, delivered as a portfolio safety harness specification.

### 16 · GitHub Issue-to-PR Autonomous Agent

This capstone addresses the async cloud coding agent product category, where labeling a GitHub issue triggers a cloud worker to resolve the problem and open a review-ready pull request. The student builds a self-hosted GitHub App and async cloud worker that reproduces the repo's build environment, runs an autonomous agent loop to edit files, verifies full CI passes in-sandbox, and opens a PR with the agent's rationale while enforcing strict credential scoping, per-repo budgets, and no-force-push policies.

**Builds:** A GitHub App with a webhook receiver, an ECS Fargate task dispatcher, environment inference for generating Dockerfiles, a mini-swe-agent/SWE-agent v2 loop, in-sandbox CI verification with coverage delta gating, and scoped PR posting via fine-grained installation tokens.

**Artifact:** A `skill-issue-to-pr.md` deliverable documenting the GitHub App and async cloud worker that turns labeled issues into review-ready PRs with bounded cost and scoped credentials.

### 17 · Personal AI Tutor (Adaptive, Multimodal, with Memory)
Students build a subject-specific adaptive tutor (K-12 algebra or intro Python) that uses a Socratic pedagogy policy, multimodal input (text, voice, photo-math), and a Bayesian knowledge-tracing learner model. The system walks a Neo4j curriculum graph to select concepts, maintains privacy-respecting memory, and enforces strict age-appropriate safety filters. The project culminates in a measured efficacy study comparing the adaptive tutor against a non-adaptive baseline.
**Builds:** A multimodal adaptive tutor comprising a LangGraph Socratic policy, a Bayesian knowledge-tracing learner model, a Neo4j curriculum graph, an agentmemory-style store, a LiveKit voice loop, photo-math recognition, and Llama Guard 4 safety filters.
**Artifact:** A subject-specific adaptive tutor with multimodal input, learner model, memory, safety, and measured learning efficacy (`outputs/skill-ai-tutor.md`).


## Part 2 — Coding-Agent Harness Build Sequence (20–87)

> Dependency-ordered component track. Each entry names what it **Builds** and the **Artifact** downstream lessons depend on.

### 20 · Agent Harness Loop Contract
Freezes the agent loop as a deterministic state machine — six states, ten lifecycle hook topics, two pull points, eleven event types, and a per-session budget envelope — so that swapping models, tools, or policies becomes a registration call instead of a refactor. The model is treated as a coprocessor the harness wires in; everything else (registry, transport, dispatcher, planner) plugs into this shape.
**Builds:** A typed harness loop in Python with interceptable hooks, budgets on turns/tool-calls/wall-clock, and a typed event stream downstream UIs and tracers can subscribe to without inspecting the loop.
**Artifact:** The harness core contract that lessons 21–29 build on.

### 21 · Tool Registry with Schema Validation
A typed registry of tool name → schema → handler that the dispatcher can query once and trust afterwards. Ships a JSON Schema 2020-12 subset (eight keywords covering ~90% of real tool calls) and json-pointer-shaped error paths so the model can self-correct in one round trip. Rejects silent re-registration and keeps the validator pure (no I/O, no time, no globals) so it replays cleanly.
**Builds:** `ToolRecord` + a pure schema validator returning precise error paths, with explicit-override re-registration.
**Artifact:** A registry module the dispatcher (lesson 23) and transport (lesson 22) treat as the single source of truth for what tools exist.

### 22 · JSON-RPC 2.0 Over Newline-Delimited Stdio
The transport between a model client and a tool server, hand-rolled once so every framing layer's cost is visible. Speaks JSON-RPC 2.0 as newline-delimited JSON over stdin/stdout, maps the five standard error codes (-32700/-32600/-32601/-32602/-32603), distinguishes requests/responses/notifications/batches, and isolates per-line parse errors without poisoning the stream.
**Builds:** A stdio JSON-RPC client/server pair plus a self-terminating `io.BytesIO` demo that runs without spawning a child process.
**Artifact:** The wire format every tool server in the harness speaks.

### 23 · Function Call Dispatcher
The seam where the harness pays for every promise the schema made: per-call timeouts, exponential-backoff retry with jitter, idempotency-key dedupe, exception-to-error-envelope mapping, and bounded parallel dispatch. The dispatcher is the only layer that knows about timers, retries, and idempotency — the loop, registry, and handler stay ignorant of all three.
**Builds:** An async dispatcher wrapping tool handlers in `asyncio.wait_for`, honoring the registry's `idempotent`/`timeout_ms` flags, and returning a JSON-RPC-shaped result or `DispatchError`.
**Artifact:** The single retry/timeout policy the loop hands tool calls to.

### 24 · Plan-Execute Control Flow
Turns a script into an agent by building the replanner first. A plan is an ordered list of typed `Step`s (tool, args, expected_outcome); the executor runs each through the dispatcher and, on failure, chooses abort/skip/replan. Replan hands the error back to the planner at the current cursor and emits a plan diff so a tracer can show why the plan changed. Two hard ceilings: step budget and replan budget.
**Builds:** A pure `planner(goal, history, last_error)` function plus a small executor state machine with replan-from-cursor and structured plan diffs.
**Artifact:** The control-flow layer that makes the harness goal-directed rather than chat-driven.

### 25 · Verification Gates and the Observation Budget
The deterministic gate chain that decides whether a tool call may fire, how much of its output the model may see, and when the loop must stop for reading too much. Composes four gates — Whitelist, Regex, Recency, Budget — with short-circuit semantics, backed by an `ObservationLedger` that tracks every token the model has been shown per tool and per turn.
**Builds:** A `VerificationGate` protocol, a `GateChain` with short-circuit DENY, an `ObservationLedger`, and a structured `GateDecision` record for observability.
**Artifact:** The first of two layers between the model and the OS; kills unbounded observation, stale recency, and privilege creep.

### 26 · Sandbox Runner with Denylist and Path Jail
What happens when a gated tool call actually runs. A `subprocess`-based sandbox with four refusal axes — executable denylist (rm/sudo/mkfs/dd), argv inspection (interpreter `-c`/`-e` and shell metacharacters), path jail via `realpath` against a project root, and wall-clock timeout with output truncation. Explicitly framed as a dev-time guardrail, not an OS security boundary.
**Builds:** A `Sandbox` class returning a structured `SandboxResult` (exit_code, stdout/stderr, truncated, timed_out, denied, reason) with sentinel codes for denied (-100) and timed_out (-101).
**Artifact:** The execution layer the eval harness and observability read structured results from.

### 27 · Eval Harness with Fixture Tasks
The source of truth that separates a regression from a refactor. Each fixture is a `(goal, setup, verifier)` triple; the harness runs each through a candidate agent k times and scores pass/fail via deterministic verifiers (`file_equals`, `regex_match`, `shell_exit_zero`). Aggregates pass@1, pass@k, mean and p95 latency, and mean cost into a structured JSON report.
**Builds:** `FixtureTask` loader, a verifier registry, multi-sample scoring with the pass@k formula, and an `EvalReport` a regression-tracking script can ingest.
**Artifact:** A reproducible eval suite that runs every fixture, every time, in fixed order.

### 28 · Observability with OTel GenAI Spans and Prometheus Metrics
Hand-rolled telemetry that makes the harness a white box. A span builder emits records compliant with the OpenTelemetry GenAI semantic conventions (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.*`, `gen_ai.tool.*`), writes them one-per-line to a JSONL file, and exposes counters and histograms in Prometheus text format — all stdlib Python, all offline.
**Builds:** A `GenAISpan` data class, a JSONL exporter, a `MetricsRegistry` with labeled counters/histograms, and a span context manager wrapping any callable.
**Artifact:** `traces.jsonl` plus a `/metrics` exposition consumable by Grafana, Honeycomb, or Jaeger without custom parsing.

### 29 · End-to-End Coding Agent on the Harness
Track A's payoff: stitches the gate chain, sandbox, eval harness, and OTel spans into one working coding agent that fixes a real (fixture-scale) off-by-one bug in a multi-file Python project. The policy is a deterministic five-state machine (SURVEY → RUN_TESTS → INSPECT → FIX → VERIFY), not an LLM — which makes the lesson reproducible and proves the harness was the interesting part; a real model plugs in at the policy seam with no contract change.
**Builds:** An integrated agent loop enforcing a global step budget and observation budget, emitting complete OTel traces and Prometheus metrics, scored by the eval harness.
**Artifact:** A runnable end-to-end coding agent plus its eval report, trace log, and metrics exposition.

### 30 · BPE Tokenizer From Scratch
Bytes in, ids out, ids back to the same bytes. Trains a byte-level Byte-Pair Encoding vocabulary from a raw corpus by repeatedly merging the most frequent adjacent symbol pair, then applies the deterministic merge table to fresh text. The 256-byte alphabet guarantees any UTF-8 input round-trips without an unknown token; special tokens (`<|endoftext|>`, `<|pad|>`) are reserved and protected.
**Builds:** A BPE trainer (pair counting, greedy merge, vocab growth) plus an encode/decode pair sharing one merge table, with a whitespace/punctuation pretokenizer.
**Artifact:** A tokenizer that every following LLM lesson (31–46) feeds through.

### 31 · Tokenized Dataset with Sliding Window
The conveyor that feeds ids into a pretraining run. Tokenizes the corpus once into a flat id stream, slices it into fixed-length windows with a configurable stride, and exposes them through a PyTorch `Dataset`/`DataLoader` as `(B, T)` input and `(B, T)` target tensors (target = input shifted left by one) with a seeded per-epoch shuffle.
**Builds:** A sliding-window slicer with stride/overlap tradeoff reasoning and a memory-cheap Dataset that computes window starts on the fly from one copy of the id stream.
**Artifact:** The `(B, T+1)` batch contract the training loop consumes.

### 32 · Token and Positional Embeddings
Two lookup tables between integer ids and dense vectors: a token embedding (`V × D`) and a positional embedding added (not concatenated) to it. Builds both a learned positional table and a parameter-free sinusoidal table, and contrasts them on length generalization and parameter count — the learned table is bounded by training context length; the sinusoidal table extends by formula.
**Builds:** `nn.Embedding` token table, a learned positional table, a precomputed `SinusoidalPositionalEmbedding`, and their elementwise-sum composition into `(B, T, D)` attention input.
**Artifact:** The embedding stage that feeds the first transformer block.

### 33 · Multi-Head Self-Attention
The attention block as the model actually uses it: one `D → 3D` linear projection split into Q/K/V, reshaped into H parallel heads of size `D // H`, scaled dot-product attention with a causal mask, then concatenate and project back. Two linear layers are the only parameters; the mask, softmax, matmuls, and reshapes are parameter-free.
**Builds:** A batched multi-head causal attention module with correct dtype handling, plus per-head weight inspection and a toy training task that shows heads specializing as loss falls.
**Artifact:** The attention sublayer dropped into the transformer block (lesson 34).

### 34 · Transformer Block from Scratch
One block is the unit of every modern decoder LLM: LayerNorm, multi-head causal attention, residual, position-wise MLP (D → 4D → D), residual. Builds both the pre-LN and post-LN variants side by side and shows which one survives a 12-layer stack at common learning rates without warmup — making the LayerNorm-placement choice mechanical instead of superstitious.
**Builds:** A reusable transformer block in two normalization configurations, with causal masking inside attention and gradient-flow tracking through a 12-layer stack.
**Artifact:** The drop-in block unit the GPT assembly (lesson 35) stacks.

### 35 · GPT Model Assembly
Assembles the block from lesson 34 into the full 124M-parameter GPT-2 small: token embedding (50257×768), learned position embedding (1024×768), twelve blocks, final LayerNorm, and a language-model head tied to the token embedding (saving ~38M params). Counts parameters piece by piece to confirm the model matches the reference shape, then generates text with multinomial sampling, temperature, and top-k.
**Builds:** A `GPTModel` class at the exact 124M configuration (vocab 50257, ctx 1024, d 768, 12 heads, 12 layers) with weight tying and autoregressive sampling.
**Artifact:** A from-scratch 124M-parameter GPT that generates text and is ready to train.

### 36 · Training Loop and Evaluation
The loop that drives the GPT model and trains every decoder LLM afterwards: cross-entropy with correct input/target shift alignment, AdamW with the weight-decay split (decay on matrices, not on LayerNorm/bias), linear-warmup-plus-cosine LR schedule, `evaluate_model` on held-out data, `generate_and_print_sample` as a qualitative probe every K steps, and a JSONL loss log you can plot.
**Builds:** A `train_model` loop with loss-alignment correctness, the decay split, the warmup-cosine schedule, periodic eval, and a qualitative sample probe.
**Artifact:** A `losses.jsonl` training log that is the loop's testimony and a shippable training skeleton.

### 37 · Loading Pretrained Weights
Training 124M params from scratch is a budget decision; loading a checkpoint is a Tuesday. Reads a safetensors file, maps each published GPT-2 parameter name (`wte`, `h.N.attn.c_attn`, `mlp.c_fc` …) onto the lesson-35 architecture, refuses shape mismatches before any assignment, and sanity-generates a continuation to prove the load worked. No network, no third-party loaders.
**Builds:** A safetensors reader, an explicit name mapper, a pre-assignment shape check under `torch.no_grad()`, and a `LoadReport` of hits, misses, and mismatches.
**Artifact:** A populated 124M GPT whose generations come from the loaded distribution, ready for fine-tuning.

### 38 · Classifier Fine-Tuning by Head Swap
Track B's first capstone. A pretrained LM body ends in a token-prediction head; for spam-vs-ham the head is wrong but the body is mostly right. Rips off the LM head, glues on a two-class linear layer over the pooled representation, and trains it two ways — frozen-body (head-only) and full fine-tuning — sharing one loop, then compares precision, recall, F1, and a confusion matrix.
**Builds:** A head-swap classifier with mean/CLS pooling, attention-mask-aware padding, two training regimes behind one loop, and metrics computed from raw logits.
**Artifact:** A binary SMS spam classifier plus a head-only-vs-full-finetune comparison report.

### 39 · Instruction Tuning by Supervised Fine-Tuning
The smallest change that makes a base model follow instructions. Formats paired instruction-response examples into a single causal sequence with `<INST>`/`<RESP>` boundary tokens, and builds a collate function that masks instruction tokens with `ignore_index=-100` so cross-entropy only counts response tokens. Trains on 200 Alpaca-style pairs across six task types and evaluates held-out exact-match.
**Builds:** An SFT template, a masking collate function, a tiny transformer trained under the SFT objective, and greedy/temperature generation that respects the response-start boundary.
**Artifact:** An instruction-following model plus its held-out exact-match score.

### 40 · Direct Preference Optimization from Scratch
Collapses the reward-model-plus-PPO RLHF stack into a single supervised loss fit directly against preference pairs. Derives the DPO loss from the Bradley-Terry reward-difference identity, ships a frozen reference model plus a trainable policy, computes per-token log-probs with prompt masking, and trains on `(prompt, chosen, rejected)` triples. Tests pin the loss math, the gradient sign, and reference invariance.
**Builds:** A reference+policy model pair, sequence-level masked log-prob computation, the DPO loss, and a test suite proving the implementation matches the paper.
**Artifact:** A preference-tuned policy whose chosen log-prob rises relative to rejected, with a passing math-correctness test suite.

### 41 · Full Evaluation Pipeline
Evaluation is the part you have to design. Builds a unified pipeline that runs four heterogeneous evals on any trained LM — perplexity (masked-token accounting), exact-match (normalized short-form), token F1 (open-ended similarity), and a local mock LLM-as-judge (1–5 scoring) — and aggregates them into a weighted per-task report. Runs fully offline with no network.
**Builds:** Four `(model, dataset) -> EvalResult` eval functions with correct perplexity token counting and normalization, a mock judge, and a weighted aggregation report.
**Artifact:** A single-file eval pipeline and an aggregate model report showing the trade-offs each dimension catches.

### 42 · Large Corpus Downloader
Training begins long before the first forward pass. A streaming downloader that pulls compressed shards with `urllib`, decompresses on the fly via `zstandard`, resumes partial downloads with verified-offset HTTP `Range` requests, fingerprints near-duplicates with MinHash + LSH, and writes a shard manifest (content hash, byte size, doc count, dedup verdict) the rest of the pipeline trusts.
**Builds:** A streaming GET + zstd reader, a `.partial.json` checkpoint with sha256-verified resume, a MinHash/LSH deduper, and a shard manifest emitter.
**Artifact:** A deduplicated, resumable corpus on disk plus its manifest.

### 43 · HDF5 Tokenized Corpus
The layout the trainer can stream from at line speed — JSONL dies at the first cold-cache page fault. Streams tokenization into a resizable, chunked HDF5 integer dataset using buffer-then-extend discipline, shards the write across multiple files so a crash loses at most one shard, and reads back through HDF5's page-cache-backed chunk layout via a sliding-window dataloader.
**Builds:** A chunk-aligned resizable HDF5 writer, sharded output with a `shards.json` index (path, token count, doc count, sha256), SWMR memory-mapped read, and a packing-aware sliding-window dataloader.
**Artifact:** A sharded HDF5 token corpus the trainer reads at hundreds of thousands of samples per second.

### 44 · Cosine LR with Linear Warmup
The second most important decision after the loss function. Implements AdamW wired to a cosine schedule with linear warmup: linear ramp 0 → `lr_max` over `warmup_steps`, cosine decay `lr_max` → `lr_min` over the rest, pinned at `lr_min` past `total_steps`. Computes the exact value at any step without float drift, logs gradient L2 norm alongside the rate, and renders to a text plot plus CSV.
**Builds:** A drift-free single-function schedule with proven endpoint continuity, gradient-norm logging, and text/CSV rendering.
**Artifact:** A schedule module with boundary tests proving warmup, peak, and decay endpoints hold.

### 45 · Gradient Clipping and Mixed Precision
The two safety belts production training cannot ship without. Global L2 gradient clipping to a configured norm, and a mixed-precision loop with `autocast` + `GradScaler` that detects NaN/Inf in loss or gradients, skips the step cleanly, and logs the scaling factor. Nails the operation order — `scale → backward → unscale_ → clip → step → update` — because any other order is silently broken.
**Builds:** A clipped, mixed-precision training step with finite-loss and finite-gradient checks, skip-on-overflow logging, and scaler-factor forensics.
**Artifact:** A robust step function that survives the gradient spike at step 8,217 that would otherwise reset the run.

### 46 · Gradient Accumulation
Train at an effective batch you cannot afford, one micro-batch at a time. Derives the `effective_batch = micro_batch × accum_steps` identity, scales each micro-batch loss by `1/accum_steps` so the accumulated gradient matches a single full-batch backward, and defers optimizer synchronization to the last micro-batch (`no_sync` on non-final steps for multi-rank).
**Builds:** A loss-scaled accumulation loop with sync-on-last-step and an in-code equivalence proof against a single full-batch backward.
**Artifact:** An accumulation-aware training step plus a throughput-vs-effective-batch curve showing the diminishing return.


### 47 · Checkpoint Save and Resume
Training runs die from interrupts, wallclock caps, and cluster reboots, and without checkpoints all progress is lost — including optimizer state that took hours to build. Students build a checkpoint system that captures the full training state (model, optimizer, scheduler, train counters, and RNG) into a payload that can be reloaded into a fresh process, using atomic writes so a crash never leaves a half-written file. The system also includes a sharded checkpoint layout with hash-verified shards and a JSON index for models that no longer fit in a single file.
**Builds:** A complete checkpoint save/resume system with atomic single-file and sharded variants, full state capture (model, optimizer, scheduler, counters, RNG), and a mid-epoch resume demo that asserts the post-resume loss trajectory matches the uninterrupted baseline within 1e-4.
**Artifact:** `outputs/skill-checkpoint-save-resume.md` — the recipe (payload shape, atomic write, RNG capture, sharded index) droppable into any new training script.

### 48 · Distributed Data Parallel and FSDP from Scratch
Multi-rank training requires precise bookkeeping: parameters must be broadcast to all ranks at startup so they start identical, gradients must be averaged across ranks after backward so optimizer steps stay synchronized, and large models must be sharded across devices with all-gather reconstructing full tensors layer by layer during the forward pass. The student implements a minimal DDP wrapper by hand, proves that per-rank gradient all-reduction produces gradients identical to single-process training on the concatenated batch, and sketches the FSDP parameter-sharding round trip. The entire system runs on CPU using the `gloo` backend and `torch.multiprocessing`, with the same code paths mapping directly to `nccl` on multi-GPU nodes.
**Builds:** A minimal DDP wrapper that broadcasts parameters at construction and all-reduces gradients after backward, plus an FSDP sketch that flattens, shards, all-gathers, and reconstructs parameters with bit-equal round-trip verification.
**Artifact:** A skill recipe (`outputs/skill-distributed-fsdp-ddp.md`) and a demo output (`outputs/ddp-demo.json`) capturing per-rank parameter sums, post-all-reduce gradient norms, FSDP round-trip results, and the manual-vs-reference gradient diff.

### 49 · Language Model Evaluation Harness

A new language model lands every week, and without an evaluation harness in your repo, you compare models by vibes rather than by score on a fixed task set. The student builds a complete evaluation harness from scratch: a JSONL task spec format, five metrics implemented from scratch (exact match, rouge-l F1, executable code check, multiple choice, and substring contains), a batched runner that dispatches to a swappable model adapter, and a leaderboard JSON output with per-task scores, latency, and an overall average that is reproducible and diffable across runs.

**Builds:** A swappable-adapter evaluation harness with JSONL task definitions, five from-scratch metrics, a batched runner, and a leaderboard JSON emitter with a schema string.

**Artifact:** A recipe skill file (`outputs/skill-lm-eval-harness.md`) plus the runnable `code/main.py` and fixture task JSONLs that together produce a reproducible `outputs/leaderboard.json`.

### 50 · Hypothesis Generator
A research agent that generates multiple candidate hypotheses from a single seed prompt, then filters and ranks them to produce a depth queue — so when the first hypothesis fails, the next one is already ready without another full sampling pass. The student builds the full pipeline end to end: temperature-ramped sampling from a mock language model, parsing of typed Hypothesis records from tagged responses, novelty filtering via hashed bag-of-tokens embeddings with cosine distance, and ranking by a weighted blend of novelty, specificity, and testability scores. The entire pipeline is deterministic: the same seed prompt and seed always produce the same ranked queue.
**Builds:** A `HypothesisGenerator` system that drives a mock LLM through a temperature ramp, parses typed Hypothesis records, rejects near-duplicates via cosine distance, and ranks survivors into a sorted queue.
**Artifact:** A deterministic, tested hypothesis-generation pipeline (`code/main.py` with `code/tests`) that accepts a seed prompt and returns a ranked queue of typed, novelty-filtered hypotheses.

### 51 · Literature Retrieval

Students build a retrieval layer that answers whether a hypothesis is already settled in the existing literature before any experiment runs. The system uses a two-pass approach: a BM25 keyword index over paper abstracts to catch lexical matches, and a citation graph traversal that expands seed papers forward and backward by one to two hops to surface relevant work that uses different vocabulary. Results from both passes are merged, deduplicated by stable paper id, and ranked by a combined score spanning BM25 relevance, graph distance, and recency.

**Builds:** A retrieval client that combines a from-scratch BM25 index over abstracts with a citation graph BFS traversal, backed by two mock API clients (arxiv and semantic scholar) returning a hundred-paper corpus across five ML topics.

**Artifact:** A tested `RetrievalClient` module (`code/main.py` with `code/tests/test_retrieval.py`) that returns a ranked, deduplicated paper list with per-paper score fields (`bm25_score`, `graph_distance`, `recency_score`, `final_score`) for downstream experiment runners and evaluators to consume.

### 52 · Experiment Runner

The project builds a research loop experiment runner that takes a typed ExperimentSpec, serialises its configuration to a temp file, and launches the experiment script in an isolated subprocess with a hard wall clock timeout and a soft memory cap polled via RSS. The runner captures stdout, stderr, and a structured JSON metrics blob into a single ExperimentResult record the evaluator can trust, treating any non-zero exit or limit breach as a terminal failure. It also ships an ablation helper that sweeps one configuration knob at a time over a fixed base spec, and enforces seed-based determinism so results are reproducible across runs.

**Builds:** A subprocess-isolated experiment runner with wall-clock timeout, memory polling, JSON metrics capture, and single-knob ablation table generation over deterministic ExperimentSpecs.

**Artifact:** A tested ExperimentRunner, AblationRunner, and mock experiment script that together produce deterministic ExperimentResult records for the evaluator pipeline.

### 53 · Result Evaluator

The runner produces metrics, but raw numbers alone cannot determine whether a change is a real improvement, a regression, or just seed noise. This project builds a verdict path that compares a candidate run against a baseline using direction-aware improvement thresholds and a paired t-test implemented from scratch over per-seed metrics, turning the results into a one-line conclusion an orchestrator can attach to a hypothesis queue.

**Builds:** A pure-function evaluator that normalizes log-scaled metrics, computes signed direction-aware improvement, runs a stdlib-only paired t-test, and emits a per-hypothesis verdict record.
**Artifact:** A tested `Evaluator` module with `MetricSpec` and `Verdict` dataclasses, plus a decision-table verdict path covering improved, regressed, noise, and failed cases.

### 54 · Paper Writer
The project addresses the problem of structural debt in research papers — where prose-first drafting leads to misplaced sections, undefined figure references, and duplicate bibliography entries. The student builds a paper writer that treats a research paper as a structured artifact: sections, figures, and bibliography keys are declared up front as data, a LaTeX skeleton is generated from that declaration, and prose is injected into slots deterministically. The system reads experiment output manifests to produce figure records, validates the paper against four structural gates before writing, and emits three files as output.
**Builds:** A `PaperWriter` with a `Paper` data model (`Section`, `Figure`, `BibEntry`), a `render_latex` function, a `MockProseGenerator`, four validation gates, and a `read_experiment_manifest` helper that converts experiment JSON into `Figure` records.
**Artifact:** A `paper.tex` file, a `references.bib` file, and a `manifest.json` listing every figure referenced, every citation used, and every section rendered.

### 55 · Critic Loop

This project addresses the problem of unstructured, non-converging feedback loops in iterative refinement workflows. The student builds a critic loop harness that scores a paper draft across five fixed dimensions (clarity, novelty, evidence, methodology, related-work), applies structured revision suggestions each round, and terminates based on convergence rules: target met, plateau detected over two consecutive rounds, or budget exhausted. The system ships with a deterministic critic and reviser so the convergence mechanics are fully testable without a live model call.

**Builds:** A critic loop harness with a `Critique` data contract, deterministic critic and reviser pair, multi-round convergence detection (target, plateau, budget), and a per-round trace output.

**Artifact:** A tested critic loop module with a score trajectory trace and convergence verdicts, suitable for integration into an iteration scheduler or dashboard.

### 56 · Iteration Scheduler

This project tackles the problem that a flat worklist cannot adapt to research findings — when experiment three's result should reorder experiments four and five. The student builds an asyncio-based iteration scheduler that models a research workflow as a hypothesis queue feeding parallel experiment slots, with results fanning back through a UCB1 scorer that re-prioritizes the queue, prunes low-yield branches, and triggers paper-write events when branches cross a reward threshold.

**Builds:** A `IterationScheduler` system with concurrent async experiment slots, UCB1 branch scoring, pruning gates, paper-trigger fan-out, follow-up hypothesis expansion, and budget limits — surfaced through a per-iteration trace of every scheduling decision.

**Artifact:** A tested iteration scheduler (`code/main.py` with `code/tests`) that produces a final trace report of branch scores, slot occupancy, pruning decisions, and paper triggers — serving as the orchestration layer for the subsequent end-to-end demo.

### 57 · End-to-End Research Demo
This project wires the auto-research loop end to end — from seed hypotheses through an iteration scheduler, experiment runner, critic loop, and paper writer — composing primitives from four earlier Track D lessons via plain Python imports rather than a framework. The demo runs deterministically to a self-terminating end and emits a single report listing every stage's output, with typed errors surfaced immediately when any stage's contract breaks.
**Builds:** The full five-stage research pipeline (seed, scheduler, experiment runner, critic loop, paper writer) composed through Python imports of upstream lesson modules, plus a best-result picker and the `mini_to_full_paper` upgrade bridging the critic output to the paper writer.
**Artifact:** A deterministic `DemoReport` containing the scheduler report, best branch and reward, critic result, paper manifest (LaTeX, BibTeX, and figure), and stop reason — validated by a test suite asserting end-to-end correctness, cross-run determinism, and typed failure modes.

### 58 · Vision Encoder Patches
A vision transformer cannot process raw pixels efficiently because treating every pixel as a token explodes the sequence length and attention compute. This project solves the image tokenization problem by cutting an image into a grid of square patches, flattening each patch, and projecting it through a linear layer to create a manageable sequence of vectors. The student builds a `VisionFrontEnd` pipeline that combines a `Conv2d`-based patch projection, a deterministic 2D sinusoidal position embedding, and a learned CLS token to produce the exact input sequence a transformer requires.
**Builds:** A patch embedding front end (`PatchEmbed`, `sinusoidal_2d`, and `VisionFrontEnd`) that converts a raw 224x224x3 image into a sequence of 197 tokens of dimension 768.
**Artifact:** Tested `nn.Module` components for vision encoder patch tokenization, verified by unit tests confirming `Conv2d`/unfold equivalence and correct output shapes.

### 59 · Vision Transformer Encoder

The patch embedding from the prior lesson produces a sequence of 197 token vectors, each with no awareness of any other patch. This project implements the pre-LN transformer encoder that turns that isolated sequence into contextual tokens, where the CLS token aggregates whole-image features across 12 stacked blocks of multi-head self-attention and 4x feed-forward expansion. The result is a complete ViT-Base encoder that forms the architectural substrate of every modern vision-language model.

**Builds:** A 12-layer, 12-head pre-LN ViT-Base encoder wiring the patch front end into a stack of transformer blocks with multi-head self-attention and GELU feed-forward sub-layers, exposing the full contextual sequence and the pooled CLS vector.

**Artifact:** A runnable ViT-Base encoder (~86M parameters) that processes a 224×224 fixture image into a `(1, 197, 768)` contextual token tensor with a CLS pooled output, validated by shape, softmax, and gradient-flow tests.

### 60 · Projection Layer for Modality Alignment

A vision encoder produces image tokens and a text decoder consumes text tokens, but the two live in different vector spaces with no relationship to each other. This project builds a two-layer MLP projection that maps image features into the text embedding space, using a cosine alignment loss against paired caption embeddings to pull the two spaces into agreement. The vision encoder and text embedding table remain frozen while only the projection layer trains, mirroring the recipe used by LLaVA, BLIP-2, and other open-weight vision-language models.

**Builds:** A two-layer GELU MLP projector, a frozen mock text embedding table, synthetic paired samples, a cosine alignment loss, and a training loop that trains the projection alone with frozen encoder and text table.

**Artifact:** A trained projection layer that reduces cosine alignment loss over 200 steps on synthetic image-caption pairs, along with unit tests verifying output shape, frozen parameters, loss behavior, gradient flow, and training dynamics.

### 61 · Cross-Attention Fusion
This project solves the problem of fusing vision and language streams in a multimodal decoder using late-fusion cross-attention, where text queries attend to image keys and values at every decoder layer. The student builds a complete vision-language decoder block that combines causal text self-attention, unmasked cross-attention into a fixed image memory, and a feed-forward network with pre-LN residuals. The implementation includes correct mask discipline (causal for self-attention, none for cross-attention) and a KV-cache that computes image keys and values once for efficient autoregressive generation.
**Builds:** A four-layer `VisionLanguageDecoder` with `CrossAttention`, `CausalSelfAttention`, `DecoderBlock`, and `causal_mask` components, including a cached and uncached inference path.
**Artifact:** A tested cross-attention fusion module that produces `(batch, seq_len, vocab)` logits and passes shape, mask, and cache-consistency unit tests.

### 62 · Vision-Language Pretraining
The project tackles the problem of pretraining a vision-language model to master two skills simultaneously: ranking (finding the right image for a caption) and generation (captioning an image). The student builds an end-to-end multi-objective pretraining system that combines a bidirectional InfoNCE contrastive loss with an autoregressive language modeling loss, training both objectives in a single pass over a synthetic image-caption corpus. The 50-step demo training loop confirms the gradient plumbing works and that adding the LM loss does not destabilize the contrastive objective.
**Builds:** A multimodal model (ViT encoder, MLP projector, text encoder, cross-attention decoder) with InfoNCE loss, LM loss, a mock corpus generator, and a combined training loop.
**Artifact:** A runnable vision-language pretraining demo that demonstrates both contrastive and captioning losses decreasing together, backed by a test suite covering loss correctness and training dynamics.

### 63 · Multimodal Evaluation

This project addresses the gap between training loss and actual multimodal model performance by building three evaluation surfaces from scratch: image-caption retrieval (R@1, R@5, R@10), visual question answering (exact match accuracy), and image captioning (BLEU-4). Each metric is implemented as a thin function over model outputs, run against a deterministic, held-out 50-sample synthetic eval suite. The system loads a trained multimodal model, evaluates it before and after a short training run, and prints a comparison table.

**Builds:** Three metric functions (`recall_at_k`, `vqa_exact_match`, `bleu4`), a synthetic eval suite builder, and a unified `evaluate` runner that tests a multimodal model end to end.
**Artifact:** A before/after evaluation script with a passing test suite, producing a metrics table suitable for a multimodal evaluation portfolio piece.

### 64 · Chunking Strategies, Compared

Chunking determines what a RAG retriever can surface, and boundary errors can cause up to a 35% swing in retrieval recall. This project builds five chunking strategies side by side — fixed-window, sentence, recursive-split, semantic clustering, and structural markdown headers — and evaluates them against a fixture corpus with gold-labeled answer spans to measure recall@k. The student reads chunk-length distributions, recognizes failure modes each strategy injects, and selects a default chunker for a new corpus based on document type, paragraph length, and structural cues.

**Builds:** Five chunking strategies (fixed-window, sentence, recursive-split, semantic clustering, structural markdown) with a dense embedding index and a recall@k evaluation loop that compares all strategies against a gold-labeled fixture corpus.

**Artifact:** A recall@k comparison table showing which boundary policy wins on prose versus technical documents, plus the selected chunking strategy that feeds forward into the end-to-end RAG system.

### 65 · Hybrid Retrieval With BM25 and Dense Embeddings

Lexical and semantic retrieval each fail on opposite query distributions — BM25 misses paraphrased queries, while dense embeddings miss literal identifiers. This project implements a hybrid retrieval system that runs both modalities in parallel and merges their results using reciprocal rank fusion (RRF), which votes on ranked lists rather than interpolating scores. The student builds the full pipeline end to end, from a from-scratch BM25 index with field weighting to a deterministic dense retriever to the published RRF merge step.

**Builds:** A hybrid retriever combining a field-weighted BM25 index, a dense embedding index, and reciprocal rank fusion with tunable per-modality weights.

**Artifact:** A runnable system that loads a fixture corpus, executes queries across both retrieval modalities, and prints the fused ranking demonstrating wins across all query classes.

### 66 · Cross-Encoder Reranker

A bi-encoder retriever embeds query and document independently, which is fast but cannot distinguish between documents with similar overall embeddings where only one truly answers the query. A cross-encoder solves this by reading the query and document together as a single packed sequence with full attention, producing one relevance scalar per pair. Because running a cross-encoder over a full corpus is prohibitively slow, students build a two-stage retrieve-then-rerank pipeline that uses a cheap bi-encoder to retrieve top-N candidates, then applies a cross-encoder to rerank down to a top-K within a request latency budget.

**Builds:** A small `CrossEncoder` PyTorch module (embedding, one transformer block with multi-head attention, mean-pooled regression head) plus a two-stage `pipeline(query, retriever, top_n, top_k)` that retrieves top-N and reranks to top-K.

**Artifact:** A runnable reranker system (`code/main.py`) with tests that demonstrates the bi-encoder top-N, cross-encoder top-K reranked output side by side, and a latency summary for each stage.

### 67 · Query Rewriting: HyDE, Multi-Query, and Decomposition

Users type queries whose phrasing does not match the corpus vocabulary, causing BM25 to miss and bi-encoders to rank the correct document outside top-N. This project implements three query rewriting strategies — HyDE (generate a hypothetical answer document and embed that), multi-query expansion (rewrite into N paraphrases and merge via reciprocal rank fusion), and decomposition (split multi-faceted questions into sub-questions) — then runs all three against a fixture corpus using a deterministic mock LLM so the rewriter loop executes offline.

**Builds:** A query rewriting pipeline with `MockLLM`, three rewriter classes (`HyDERewriter`, `MultiQueryRewriter`, `DecomposeRewriter`), a `retrieve_with_rewriter` fusion function, and a demo that compares strategies on a fixture corpus.

**Artifact:** A runnable script that takes mismatched, multi-faceted queries and prints per-strategy rankings showing which rewriter surfaces the gold answer document first.

### 68 · RAG Evaluation: Precision, Recall, MRR, nDCG, Faithfulness, Answer Relevance
A RAG pipeline has at least four moving parts (chunker, retriever, reranker, generator), and a wrong answer could originate at any stage. This project builds an offline, deterministic evaluation harness that computes four retrieval metrics (precision@k, recall@k, MRR, nDCG@k) and two answer-grade metrics (faithfulness, answer relevance) from a hand-built fixture qrels file, enabling a developer to diagnose exactly where a pipeline is failing.
**Builds:** A metrics evaluation orchestrator that runs six RAG evaluation metrics (four retrieval, two answer-grade) against a fixture qrels file using a deterministic mock judge, comparing multiple pipeline variants in a single metrics table.
**Artifact:** A portfolio-ready RAG evaluation suite (`main.py` with accompanying tests) that grades retrieval and generation quality, runnable out-of-the-box in CI or locally.

### 69 · End-to-End RAG System

This project solves the problem that six RAG components in isolation prove nothing — a chunker, retriever, reranker, rewriter, and generator must be composed into a single pipeline and evaluated end to end against fixture qrels to demonstrate that the integrated system beats each stage's isolated demo on every metric. The student builds a complete end-to-end RAG pipeline that ingests a corpus, runs queries through all five stages (chunking, hybrid retrieval, query rewriting, cross-encoder reranking, and cited answer generation), and includes a self-terminating CLI demo that exits zero only when all evaluation thresholds pass.

**Builds:** A `Pipeline` class composing five swappable stages — Chunker, HybridIndex, Rewriter, Reranker, and Generator — wired into a `run_demo()` orchestrator that ingests a fixture corpus, runs a fixed query set with per-stage latency tracing, executes the eval loop, and exits with a pass/fail status.

**Artifact:** A self-terminating CLI demo (`code/main.py` with tests) that runs the full pipeline offline against fixture qrels, prints a per-query trace and metrics table, and returns exit code 0 on pass — the shape a CI smoke test takes.

### 70 · Task Spec Format

This project tackles the problem of contract drift in research eval codebases by freezing a JSONL task record schema and closed metric vocabulary before any scoring functions are written. The student builds a strict validator that enforces required fields, field types, category-metric pair legality, and task ID uniqueness, plus a 10-task fixture set covering arithmetic, MCQ, code execution, classification, and summarisation. A separate bad-fixture file trips every rule so the validator's error reporting is tested against every branch.

**Builds:** A JSONL task spec validator (`TaskSpec`, `validate_task`, `validate_file`, CLI entry point) with post-process and few-shot rendering helpers, plus a 10-task valid fixture and a bad-fixture that trips every validation rule.

**Artifact:** A validated task spec module and fixture set that downstream eval lessons import as a single dependency, ensuring every task record honours the same contract.

### 71 · Classical Metrics

The project addresses the confusion that arises when comparing evaluation numbers across papers and libraries — differences in tokenization, smoothing, and normalization cause BLEU and ROUGE-L scores to vary by points or orders of magnitude. The student implements five canonical metrics (BLEU-4, ROUGE-L, F1, exact-match, accuracy) entirely from first principles using only stdlib plus numpy, pinning a single fixed tokenizer and a metric-agnostic dispatch contract. The result is an auditable, reproducible metric stack where every design choice is visible in the code.

**Builds:** A from-scratch metric library implementing exact-match, token-level F1, BLEU-4 (with brevity penalty and additive-one smoothing), ROUGE-L (via LCS dynamic programming), and accuracy, unified behind a single `score(metric_name, prediction, targets)` dispatcher.

**Artifact:** A tested `main.py` with pinned reference vectors and a test suite covering edge cases (empty prediction, empty reference, no shared tokens, repeated-phrase clipping), producing a reproducible classical-metrics package suitable for integration into an eval runner.

### 72 · Code Exec Metric

This project builds the eval harness surface for scoring generated code: extracting a code block from a free-form generation, running it in an isolated subprocess with a wall-clock timeout, output cap, and import denylist, and tallying pass-rates honestly. The student constructs a runner that spawns a fresh Python interpreter per candidate, scores tasks as the fraction of supplied assertion strings that pass, and computes pass-at-k for multi-sample generations. Sandbox crashes, syntax errors, and timeouts are treated as first-class fail modes with distinct exit codes the runner logs.

**Builds:** An isolated subprocess code-execution eval harness with code extraction, assertion scoring, a denylist, wall-clock timeout, output cap, normalised exit codes, and pass-at-k computation.
**Artifact:** A `main.py` defining `extract_code`, `run_candidate`, `score_code_exec`, and `pass_at_k` with a test suite exercising the four exit codes plus pass-at-k against HumanEval-style worked examples.

### 73 · Perplexity and Calibration

This project addresses the problem of measuring whether a language model's confidence is trustworthy — a model that claims 90% confidence but is right only 60% of the time is poorly calibrated and unsafe for production. Students build the three core trust metrics end to end: token-level perplexity over a held-out corpus, expected calibration error (ECE) from binned confidence-accuracy gaps, and Brier score with its decomposition, plus the reliability diagram data structure used to plot confidence-versus-accuracy curves. All four are wired into the eval harness so the runner can attach `perplexity`, `ece`, and `brier` numbers to a model report.

**Builds:** A set of calibration and perplexity functions (`perplexity`, `expected_calibration_error`, `brier_score`, `reliability_diagram`) with `CalibrationReport` and `PerplexityResult` dataclasses that handle edge cases and dispatch as per-model report aggregates.

**Artifact:** A tested calibration module with a demo run on three synthetic predictors (well-calibrated, overconfident, underconfident) and pinned edge-case tests that make perplexity, ECE, and Brier numbers trustworthy and reproducible.

### 74 · Leaderboard Aggregation

Per-task evaluation scores are straightforward, but producing defensible per-model rankings across heterogeneous tasks with proper statistical significance is the step most leaderboards skip. This project builds an aggregation system that consumes per-model, per-task evaluation runs and produces a complete leaderboard with bootstrap confidence intervals on both mean scores and pairwise model differences.

**Builds:** A leaderboard aggregator that takes `EvalRun` records, computes per-model mean scores and win-rates, derives bootstrap confidence intervals on means and pairwise differences, and renders the results as both a JSON report and a markdown table.

**Artifact:** A tested Python module (`main.py` with `aggregate`, `bootstrap_mean_ci`, `bootstrap_pairwise_diff`, and `render_markdown`) plus a test suite pinning the bootstrap, markdown rendering, win-rate edge cases, and empty-input behavior.

### 75 · End-to-End Eval Runner

This project integrates five preceding modules (task specs, model adapters, metric scoring, calibration reports, and leaderboard aggregation) into a single eval pipeline. The student builds a runner that reads a fixture JSONL file, executes tasks in parallel across a worker pool, scores with metric and calibration layers in one pass, and emits both a JSON report and markdown leaderboard. Three mock adapters exercise the system end to end over the lesson 70 fixture and the demo self-terminates with exit zero on a clean run.

**Builds:** A complete eval runner that composes task specs, a `ModelAdapter` interface, parallel task execution, metric dispatch, calibration aggregation, and leaderboard emission into one integration module.

**Artifact:** A self-terminating eval pipeline that produces a JSON envelope (leaderboard, pairwise diffs, calibration reports, summary) plus a markdown leaderboard table, with a passing test suite pinning the adapter interface, single-pass loop, parallel-vs-sequential equivalence, calibration buffer, and output shape.

### 76 · Collective Ops From Scratch

Distributed training frameworks like PyTorch DDP, DeepSpeed ZeRO, and FSDP all depend on four core collective operations: allreduce, broadcast, allgather, and reduce_scatter. Students build these four primitives from scratch over a `multiprocessing.Queue` mesh wired as a ring, then verify each one against a `torch.distributed` gloo reference implementation for byte-equal correctness.

**Builds:** A `Mesh` class wiring N `multiprocessing.Queue` instances into a ring plus `ring_allreduce`, `broadcast`, `allgather`, and `reduce_scatter` implementations verified against a gloo reference.

**Artifact:** A per-primitive verification table comparing queue-mesh and gloo outputs alongside a per-rank byte counter proving the 2T(N-1)/N scaling.

### 77 · Data Parallel DDP From Scratch
A 1-billion-parameter model with 12 GB of activations does not fit on one consumer GPU, and training large models sequentially takes weeks. Data parallel solves this by splitting the batch across N ranks, each computing forward and backward on its shard, with gradient allreduce ensuring all N copies stay identical after every step. Students build a `DistributedDataParallel`-shaped wrapper from scratch over the gloo backend, broadcasting initial parameters from rank 0 and installing post-backward allreduce hooks, then proving correctness by matching per-step parameter equivalence against a single-process baseline.
**Builds:** A `DistributedDataParallel` wrapper that broadcasts params at construct time and allreduces gradients after backward, run across 4 CPU ranks via `torch.multiprocessing.spawn`.
**Artifact:** A per-step training table comparing single-process loss and parameter checksums to the 4-rank DDP run, demonstrating identical loss curves to float epsilon.

### 78 · ZeRO Optimizer State Sharding
Vanilla DDP replicates parameters, gradients, and optimizer state in full on every rank, making optimizer state the largest single memory allocation in the training stack. This project implements ZeRO Stage 1, which shards optimizer state (fp32 master copy and Adam moments) across N ranks so each rank owns 1/N of the optimizer. The system uses reduce_scatter to deliver each rank only its shard's summed gradient, applies the Adam step locally, then allgathers the updated parameter shards so every rank reconstructs the full model for the next forward.
**Builds:** A flat-parameter packing utility and a `ZeroOptimizer` that owns the rank's shard of master parameters and Adam moments, with a step function running reduce_scatter, local Adam, and allgather.
**Artifact:** A per-step loss and memory table demo showing ZeRO-1 holding 1/N of the optimizer state per rank versus a vanilla DDP baseline.

### 79 · Pipeline Parallel and Bubble Analysis
A 70B-parameter model in fp16 needs 140 GB of parameters alone — no single GPU holds it. Pipeline parallelism solves this by cutting the model into N sequential stages, placing one stage per rank, and streaming M microbatches through the pipeline. The student builds a simulated multi-stage pipeline that implements the GPipe schedule, measures the bubble fraction against the closed-form prediction (N-1)/(M+N-1), and analyzes why equal compute per stage matters more than equal parameter count.
**Builds:** A 4-stage simulated pipeline with `PipelineStage` modules, a `Pipeline` orchestrator implementing the GPipe schedule, and a `bubble_fraction` function validated against measured results.
**Artifact:** A stage-by-microbatch Gantt chart trace and bubble percentage report comparing measured idle time against the theoretical prediction.

### 80 · Sharded Checkpoint and Atomic Resume

A 70B-parameter training job paused by node failure can lose hours depending on its checkpoint format. This project implements a sharded checkpoint system where every rank writes its own shard file in parallel and records ownership in a JSON manifest, replacing the slow single-rank gather-and-write pattern. The system uses the atomic write pattern (write to temp path then rename) so a crash mid-write never produces a half-finished checkpoint, and the loader verifies byte-equal state on resume while defending against world-size changes, shard count mismatches, and partial writes.

**Builds:** A `ShardManifest` dataclass plus `save_sharded` and `load_sharded` functions that write per-rank binary state shards using atomic temp-then-rename, record shard paths/offsets/hashes in a manifest, and verify sha256 checksums on reload.

**Artifact:** A round-trip test demonstrating four shard files plus a manifest written and reloaded with byte-equal verification of fp16 parameters and ZeRO optimiser state.

### 81 · End-to-End Distributed Training
This capstone assembles the distributed-training primitives built in prior lessons — DDP for gradient sync, ZeRO-1 for optimiser-state sharding, and sharded checkpoints — into a single end-to-end training loop. The student trains a tiny GPT (2-layer transformer) across 4 simulated CPU ranks for 20 self-terminating steps on a synthetic corpus, verifying that loss decreases monotonically, per-rank memory matches the ZeRO-1 formula, and the step-10 checkpoint reloads byte-equal on restart.
**Builds:** A composed distributed training system that integrates DDP broadcasts, ZeRO-1 optimiser steps, and sharded checkpointing into one training loop for a mini GPT.
**Artifact:** A self-terminating demo run that outputs a 20-row loss table, a per-rank memory profile, a checkpoint manifest, and a resume-verification result.

### 82 · Jailbreak Taxonomy

Before any detector, classifier, or rule engine can do useful work, a safety team needs a shared way to label and categorize prompt attacks. This capstone defines a six-category taxonomy that partitions attacks by which trust boundary they abuse — role-play, instruction-override, context-smuggling, multi-turn-ramp, encoding-trick, and prefix-injection — with at least seven hand-built fixtures per category. The student builds the full corpus, a taxonomy class that validates it, and a character-trigram cosine matcher that assigns categories to new prompts.

**Builds:** A six-category jailbreak taxonomy with a validated fixture corpus, a taxonomy class exposing `by_category`, `match`, and `stats` methods, and a trigram-cosine matcher implemented from scratch.

**Artifact:** `outputs/skill-jailbreak-taxonomy.md` documenting the six categories and severity rubric, plus `taxonomy.json` as a stable corpus artifact consumed by downstream lessons.

### 83 · Prompt Injection Detector

The project addresses the problem of teams shipping naive regex-based prompt injection defenses that are never measured against a labeled corpus, resulting in security theater that misses simple variations of known attacks. Students build a layered detector — deterministic substring rules, token-level regexes, and a normalization pass that decodes encodings like base64, rot13, leet, and zero-width characters — then evaluate it with a metrics runner that computes per-category precision, recall, F1, and confusion matrices against a taxonomy of fixtures plus a benign-prompt corpus.

**Builds:** A layered prompt injection detector with normalize/substring/regex stages and a metrics runner that evaluates the detector against a labeled corpus.
**Artifact:** A per-category metrics report (`outputs/detector_report.json`) and a skill document (`outputs/skill-prompt-injection-detector.md`) consumed by the downstream safety gate.

### 84 · Refusal Evaluation

A safety evaluation must measure two opposing failure modes simultaneously: under-refusal (the model answers harmful prompts) and over-refusal (the model refuses benign prompts). Students build a fixture-based evaluator with a deterministic mock LLM that scripts three policy bugs — strict, over-cautious, and leaky — so metric movements are auditable. The framework produces four numbers per policy: under-refusal rate, over-refusal rate, calibration (ECE), and a per-category breakdown using the lesson 82 taxonomy.

**Builds:** A refusal evaluation harness comprising a labeled prompt corpus, three mock LLM policies, a regex-based refusal classifier, and a metrics aggregator computing under-refusal, over-refusal, accuracy, ECE, and per-category under-refusal.

**Artifact:** `outputs/refusal_eval_report.json` comparison report across three policies plus `outputs/skill-refusal-evaluation.md` documenting the metric definitions.

### 85 · Content Classifier Integration
A model that passes every input check can still produce unsafe output — leaking PII, repeating slurs, or echoing the system prompt. This capstone wires three independent output-side classifiers (toxicity, PII, and instruction leakage) behind a single policy router that collects verdicts, picks a severity, and applies an action policy of block, redact, warn, or log. The system gives students an end-to-end output-safety pipeline that addresses attack vectors input-side classification alone cannot cover.
**Builds:** Three output-side classifiers (toxicity, PII, instruction leakage) and a policy router that aggregates verdicts by maximum severity and applies the corresponding action.
**Artifact:** A skill document (`outputs/skill-content-classifier-integration.md`) documenting the verdict and action structures so a downstream safety gate can consume them.

### 86 · Constitutional Rules Engine

Teams need to enforce contractual constraints on LLM outputs — such as "every response containing code must end in a runnable block" or "every refusal must offer a next step" — that are not natural classifier targets but declarative predicates over the response. Students build a rules engine that loads a YAML constitution file, evaluates each rule's predicate against candidate outputs, returns structured violations, applies a deterministic fixer to propose revisions, and produces a line-by-line diff between draft and revised responses.

**Builds:** A constitutional rules engine with an `Engine` class that evaluates composed predicates (`all_of`, `any_of`, `not_`), a `Fixer` class that applies declarative per-rule transforms, and a `diff` function — all driven by a YAML rule file.

**Artifact:** `outputs/skill-constitutional-rules-engine.md` documenting the rule grammar and fixer operations, plus `outputs/rules_report.json` showing violations, fixes, and diffs for demo drafts.

### 87 · End-to-End Safety Gate

This capstone addresses the problem of composing individual safety components — input detectors, streaming filters, output classifiers, and rules engines — into a single, coherent safety gate that runs at three checkpoints in the request lifecycle: pre-gen, during-gen, and post-gen. The student builds a `SafetyGate` class that orchestrates all prior lesson components, aggregates their severity signals through a deterministic decision table, and emits a structured per-request trace capturing every checkpoint's verdict, the final action, and latency.

**Builds:** A three-checkpoint safety gate that composes a detector, a streaming token filter, a classifier router, and a rules engine behind a deterministic aggregation table, exercised against a 50-fixture attack taxonomy plus benign prompts.

**Artifact:** A portfolio skill document (`outputs/skill-end-to-end-safety-gate.md`) describing the request lifecycle, aggregation table, and trace format, alongside a per-request JSON trace (`outputs/gate_trace.json`) that demonstrates the gate's layered defense end to end.
