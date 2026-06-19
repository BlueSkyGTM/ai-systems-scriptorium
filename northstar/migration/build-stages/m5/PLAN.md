# Module 5 — Deploy & Performance Engineering — Build Plan

Status: **PLAN LOCKED (2026-06-19)** by Opus. Pipeline: **AUTHOR → VERIFY → SHIP** on the proven engine.
Canonical build layer: `northstar/migration/`. M5 turns the five `src/module5/*` ingredient stubs (+ a new
lifecycle-lite chapter) into **15 finished lessons** + Claude Code exercises, in the locked Style Contract voice.

M5 is the seam's home turf — the infrastructure MLOps engineers and app devs *use*. **Built, not described.**
Core thesis: **performance engineering > machine learning** (inference-centric; model-centric MLOps stays at
literacy depth, deep versions in the antilibrary). This is the guide's **Step 4 — "the step that separates
candidates who get hired from those who get filtered"** (`hireability-alignment.md`), so it carries weight.

## MLOps-inventory pass (vs the hireability guide's Step-4 checklist)
- **Covered:** model serving (ch1 vLLM/Triton/BentoML/FastAPI), Docker/K8s (ch3 + M4 AKS), monitoring
  Prometheus/Grafana + OTel (ch2), cloud ML platform Azure-deep (ch1–3).
- **Brought back at LITERACY depth** (guide rates these 63%-screen separators; were antilibrary): experiment
  tracking (MLflow/W&B), data versioning (DVC), pipeline orchestration (Airflow/Prefect — conceptual),
  fine-tuning (PyTorch/LoRA/QLoRA) → the new **ch5 lifecycle-lite**. Deep build stays antilibrary → *Avec Python*.
- **Locked thread:** the **Docling** data-ingestion lesson lands here (ch5), the RAG production front door.
- **Stays cut (antilibrary, logged at SHIP):** aipe training/CUDA (ch01–14), mwml model-centric training
  pipelines/lifecycle deep, deep DVC/Airflow, fine-tuning *implementation*. Name **advanced Python + ML math**
  explicitly as *Avec Python* candidates in `antilibrary.md` at SHIP (maintenance rule).

## Locked lesson plan — 15 lessons, 6 chapters (split by buildability/density)

| # | Lesson | Chapter | Label | One idea |
|---|--------|---------|-------|----------|
| 01 | Serving engines & engine selection | Serving & Inference Opt | Build/Decision | Inference infra ≠ training infra; vLLM / TGI / TensorRT-LLM, wrapped by FastAPI/Triton/BentoML; pick by workload. **Opens the module on the perf>ML thesis.** |
| 02 | Inside the engine: continuous batching & paged KV-cache | Serving & Inference Opt | Concept/Build | Why an LLM server is not a REST server; continuous batching + paged attention (vLLM internals). |
| 03 | The optimization levers: quantization, speculative decoding, disaggregation | Serving & Inference Opt | Decision | The throughput/latency levers and their trade-offs; prefill/decode disaggregation. |
| 04 | Inference metrics & load testing | Metrics, Observability & Rollout | Build | TTFT / TPOT / throughput / p99; load-test before you ship. |
| 05 | Safe rollout: shadow, canary, A/B + AI gateways | Metrics, Observability & Rollout | Build/Decision | The eval thread's **outer loop**; progressive delivery through an AI gateway. |
| 06 | Observability & SRE-for-AI | Metrics, Observability & Rollout | Build | OpenTelemetry GenAI semconv, traces, quality/drift monitoring, Prometheus/Grafana dashboards. |
| 07 | Security & compliance for AI ops | Operations | Concept/Decision | Secrets, least-privilege access, SOC2 / HIPAA / EU AI Act as *operational* requirements. |
| 08 | Token FinOps & cost optimization | Operations | Build/Decision | The bill as a first-class metric; caching, routing, quotas, the cost levers (ties M4 budgets to the platform). |
| 09 | Measure before you optimize: profiling & roofline | Performance Engineering Depth | Concept/Build | The attribution discipline — profile, find the bound (roofline), then optimize. The thesis core. |
| 10 | The production performance checklist | Performance Engineering Depth | Reference/Decision | NVLink/topology awareness + the 200-item reference distilled into a usable pre-ship checklist. |
| 11 | Data ingestion at production scale (Docling) | Data, Experiments & Lifecycle [lite] | Build | PDF/DOCX/slides → structured (`DoclingDocument`) → chunks; the RAG front door; data/prompt versioning (DVC-style). |
| 12 | Experiment tracking & the LLMOps outer loop | Data, Experiments & Lifecycle [lite] | Build/Decision | MLflow (W&B alt): runs, params, metrics, model registry — eval-driven development's outer loop, made durable. |
| 13 | Fine-tuning, in practice and in proportion | Data, Experiments & Lifecycle [lite] | Concept/Decision | PyTorch/LoRA/QLoRA **literacy** (speak-to-it bar); when to fine-tune vs RAG vs prompt; deep impl → *Avec Python*. |
| 14 | Rust break-in: ownership, borrowing, the type system | Rust (entry) | Build | The ownership on-ramp at point-of-use — why the serving layer reaches for Rust. |
| 15 | Async Rust for serving | Rust (entry) | Build | tokio + an async inference proxy/gateway; where Rust earns its place in the AI platform. |

Collapsible to 13 (merge 02→03, 09→10); expandable to 16 (split ch5). Drafters may merge within a chapter with a verdict note.

## Source map + POSITIVE inclusion list (synthesis uses OLD numbering: M5 ← `synthesis/source/module4/`)
| Chapter | INCLUDE | Note |
|---|---|---|
| ch1 Serving (01-03) | `aefs-module4-infrastructure-production.md` (Ph17 operate) · `aipe-module4-inference-serving-chapters.md` (ch15–20 measure) | **layer, don't dedup** (two depths) |
| ch2 Observability (04-06) | `aefs…` (Ph17 metrics/rollout) · `asdg-module4-deploy-chapters.md` (Ch14 eval/observability) | outer loop of eval-driven dev |
| ch3 Ops (07-08) | `aefs…` (Ph17 ops) · `asdg…` (Ch12 security, Ch13 reliability) · `mwml-module4-deploy-scripts.md` (CI/serving) | |
| ch4 Perf (09-10) | `aipe-module4-inference-serving-chapters.md` · `aipe-module4-inference-reference-docs.md` (200+ checklist) · `aipe-module4-full-sweep-checklist.md` | inference-only |
| ch5 Lifecycle-lite (11-13) | **Docling** docs via WebFetch (github.com/docling-project/docling) · `mwml-module4-deploy-scripts.md` (deploy subset) · fine-tuning at *decision* depth only · `asdg-module4-case-studies.md` (architectures) | literacy depth; deep build → antilibrary |
| ch6 Rust (14-15) | `synthesis/source/module1/rust-module1-*` (rust-book-structure, rust-exercises-by-topic) | threaded from M1, taught here |

**EXCLUDE (antilibrary):** `aipe` training/CUDA ch01–14; `mwml-module4-madewithml-code-inventory.md` / `-notebook-outline.md` (model-centric training/lifecycle) except the deploy subset; fine-tuning *implementation*. **Do not read any path containing `skills/` or `gstack/`.**

## Three-source rule + claim-authority map
1. Migration ingredient (the included `synthesis/source/module4/*` + Docling docs).
2. **MS Learn connector** for Azure (Azure ML, AKS, Azure AI gateway/APIM, Azure Monitor/App Insights, Azure OpenAI serving). **WebFetch** for non-MS (vLLM, TGI, TensorRT-LLM, Triton, BentoML, Docling, MLflow, W&B, DVC, OpenTelemetry GenAI semconv, HuggingFace PEFT/LoRA/QLoRA, Rust/tokio). **Perf/vendor numbers are high-risk — mark every one** (M4-ch04 discipline).
3. Editorial seam framing — "why at the AI-Engineer ∪ MLOps cusp?" in every lead; no template endings (STYLE §8).

## Threads to carry
- **performance engineering > ML** (the M5 thesis; opens ch1).
- **eval-driven development** — M2 inner loop → M5 outer loop (ch2 rollout + ch12 experiment tracking).
- **safety/ops** — M4 budgets/kill-switch → M5 FinOps/quotas/gateways (ch08).
- **data-ingestion (Docling)** — M2 RAG → **M5 ch11** (deep) → M6 RAG artifact.
- **mixed-language** — Python control/glue; **Rust** at the serving layer (ch6); TS where a typed gateway contract earns it.
- **antilibrary maintenance** — log every cut at SHIP; name advanced Python + ML math as *Avec Python* candidates.

## Throughline artifact + code-gate note
Throughline: **`module5-serving/`** — a production serving + observability + ops stack the M6 artifacts later deploy onto. Each lesson adds a layer (serve → metrics → rollout → finops → ingest → a Rust proxy). M5 stays **AUTHOR → VERIFY → SHIP** (prose + exercise briefs); the runnable **BUILD→TEST gate begins at M6**. Rust/serving snippets are illustrative, verified by read.

## Execution model
Opus = editor-in-chief; Sonnet drafters by chapter (A ch1, B ch2, C ch3, D ch4, E ch5 lifecycle-lite, F ch6 Rust). VERIFY fleet: one verdict per lesson, connector + WebFetch, perf-number discipline. No draft ships unreviewed.

## Done-when (per lesson)
A file in `src/module5/`, a `src/SUMMARY.md` entry in dependency order, a `## Core concepts` block (1–4 props), an exercise brief at `exercises/module5/<slug>/README.md` extending `module5-serving/`, a per-lesson VERIFY verdict, and `mdbook build` clean at SHIP.
