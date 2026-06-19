# Module 4 — Prerequisite Snapshot

> **Renumber map (8-module, 2026-06-18). This module becomes M5** (Deploy & Performance Engineering).
> Edge list renumbered: all `m4:` nodes → `m5:`. The old `M5:` capstone targets here (inference server,
> observability dashboard, MCP governance) are **relocated into M5 itself** as Deploy artifacts, so they
> become `m5:` internal edges. `mwml:training-pipeline` resolves to **ANTILIBRARY** (model-centric MLOps).
> Prose retains original numbering. See `step2-flow-audit.md`.

Module 4 is the **Deploy + Performance Engineering core** — and the densest concentration of
the AI Platform Engineering seam (the infrastructure MLOps engineers and app devs *use*:
serving engines, GPU scheduling, gateways, observability, finops). Two complementary spines:
the deploy/ops core (aefs Ph17) and the performance-engineering depth (aipe), plus MLOps
practice (mwml) and system-design case studies (asdg).

Source files: `aefs-module4-infrastructure-production` (Ph17, 28 lessons),
`aipe-module4-inference-serving-chapters` (ch15–20), `aipe-module4-full-sweep-checklist`,
`aipe-module4-inference-reference-docs` (200+ item checklist), `asdg-module4-deploy-chapters`,
`asdg-module4-case-studies`, `mwml-module4-deploy-scripts`, `mwml-module4-madewithml-code-inventory`,
`mwml-module4-madewithml-notebook-outline`.

---

## Track A — Serving & Inference Optimization (aefs Ph17 + aipe ch15–20)

The deploy spine. aefs Ph17 is the "what/why/ops" layer; aipe ch15–20 is the "measure it at the systems/kernel level" layer. **Heavy overlap on quantization, speculative decoding, disaggregation, KV cache — a layering decision, not a resequencing one.**

```
managed-platforms / inference-economics → serving-engine-selection(vLLM/SGLang/TRT-LLM/llama.cpp)
serving-engines → vllm-internals(paged-attention, continuous-batching, chunked-prefill)
vllm-internals → speculative-decoding(EAGLE-3) → production-quantization(AWQ/GPTQ/FP8/NVFP4)
serving-engines → disaggregated-prefill-decode → kv-cache-management(LMCache, NVLink pooling)
serving-engines → prefix-caching(RadixAttention) → multi-region-kv-locality
(aipe depth) flash-attention, block-sparse, tensor-core-kernels, regional-compilation, roofline-profiling
```

Inbound: `[M1] docker/linux/terminal` (ops substrate), `[M1] rust:async` (serving layer), `[M2] production-llm-app`.

---

## Track B — Metrics, Observability & Rollout (aefs Ph17, eval thread)

The production-quality control plane — continues the eval thread from M1/M2.

```
inference-metrics(TTFT/TPOT/ITL/goodput/P99) → load-testing → observability-stack-selection
observability → shadow-traffic → canary-rollout → ab-testing
model-routing → ai-gateways(routing/fallback/secrets) → [rollback via registry+flags]
SRE-for-AI → chaos-engineering [resilience sub-thread]
```

Inbound: `[M2] llm-as-judge, rag-evaluation` (eval thread). Outbound: `→ [M5] observability-dashboard capstone`.

Audit note (from source): the eval thread here splits into (a) metrics/observability core, (b) pre-prod validation (canary/AB/load), (c) SRE/chaos resilience. The source flags (c) as detecting *infra* degradation not output quality — candidate to split into a separate resilience thread.

---

## Track C — Operations: Security, Compliance, FinOps (aefs Ph17)

The "runs in a regulated enterprise" layer. Largely standalone, depends on the serving stack existing.

```
security(secrets/vault/rotation/egress) → compliance(SOC2/HIPAA/GDPR/EU-AI-Act/ISO-42001)
finops(per-user/task/tenant attribution, spend caps, kill switches)
caching-economics + batch-apis(50% discount) → cost-optimization
```

Inbound: `[M2] guardrails/prompt-injection` (security continuity). This cluster is the clearest AI-Platform-Engineering-specific material — finops-for-tokens and AI-specific compliance don't exist in generic platform eng.

---

## Track D — Performance Engineering depth (aipe)

The thesis core: **"performance engineering > machine learning."** aipe's training/CUDA chapters (ch01–14) are **already cut to antilibrary** — performance engineering is scoped to *inference serving* (ch15–20) + the 200+ item production checklist. Profiling (Nsight Systems/Compute), roofline analysis, NVLink/NVSwitch topology, NUMA/OS tuning, I/O pipeline. Measured deltas throughout (continuous batching 4.16x, NVLink KV pool 6.11x, tensor-core decode 15.65x).

Audit note: aipe ch15–20 overlaps aefs Ph17 on the *topics* (disaggregation, quant, spec decode, KV) but at a different *depth* — aipe = measure/profile/attribute, aefs = deploy/operate. Layer them; don't dedup to one.

---

## Track E — MLOps & Case Studies (mwml + asdg) — PARTIAL SEAM

`mwml` (Made With ML) is model-centric **MLOps**: data pipelines, training, CI/CD, model registry, deploy scripts, notebooks. Per the thesis, AI Platform Engineering is *infrastructure*-centric and **distinct from MLOps** (model-centric). So mwml is partly off-seam — the training-pipeline-centric material is a **CHECK / partial-antilibrary candidate** (same pattern as generative-media in M2); the deploy/CI/serving material stays. `asdg-module4` (deploy chapters + production case studies) reinforces the deploy spine.

Audit flag: confirm at Step 3 which mwml content is seam (deploy/serving/CI) vs antilibrary (training-pipeline/model-lifecycle).

---

## Module 4 — flow observations (feed Step 2)

1. **M4 is the seam's home turf.** Tracks A–D are squarely AI Platform Engineering. Highest-confidence module for the discipline.
2. **aefs Ph17 ↔ aipe overlap is a layering job, not a conflict.** Same topics, two depths (operate vs measure). Step 3 decides how to interleave.
3. **aipe training chapters already antilibrary** — performance engineering correctly scoped to inference. Aligns with thesis; no action.
4. **mwml MLOps is the M4 analog of M2's generative-media** — partly off-seam (model-centric training). Flag for cut/keep at Step 3.
5. **Inbound edges all point backward correctly** (M1 ops/rust, M2 app/eval/guardrails). No backward violations. Outbound → M5 capstones (serving, observability, MCP-governance, fine-tuning pipeline).

## Edge list (machine-readable)
```
M1:docker -> m5:serving-engines
M1:linux -> m5:serving-engines
M1:rust-async -> m5:serving-layer
M2:production-llm-app -> m5:serving-engines
m5:serving-engines -> m5:vllm-internals
m5:vllm-internals -> m5:speculative-decoding
m5:speculative-decoding -> m5:production-quantization
m5:serving-engines -> m5:disaggregated-prefill-decode
m5:disaggregated-prefill-decode -> m5:kv-cache-management
m5:serving-engines -> m5:prefix-caching
m5:inference-metrics -> m5:load-testing
m5:inference-metrics -> m5:observability-stack
m5:observability-stack -> m5:shadow-traffic
m5:shadow-traffic -> m5:canary-rollout
m5:canary-rollout -> m5:ab-testing
m5:model-routing -> m5:ai-gateways
m5:observability-stack -> m5:sre-for-ai
m5:sre-for-ai -> m5:chaos-engineering
m5:security -> m5:compliance
m5:security -> m5:finops
m5:caching-economics -> m5:cost-optimization
m5:batch-apis -> m5:cost-optimization
M2:rag-evaluation -> m5:observability-stack
M2:guardrails -> m5:security
m5:vllm-internals -> m5:inference-server-artifact   # relocated capstone 14
m5:observability-stack -> m5:observability-artifact # relocated capstone 11
m5:ai-gateways -> m5:mcp-governance-artifact        # relocated capstone 13
# aipe performance depth (parallel layer)
m5:vllm-internals -> aipe:continuous-batching-profiling
m5:production-quantization -> aipe:awq-gptq-smoothquant-bench
m5:disaggregated-prefill-decode -> aipe:nvlink-kv-pool-bench
aipe:roofline-profiling -> aipe:tensor-core-kernels
# mwml (partial seam)
mwml:deploy-scripts -> m5:serving-engines
mwml:training-pipeline -> ANTILIBRARY:model-centric-mlops
```
