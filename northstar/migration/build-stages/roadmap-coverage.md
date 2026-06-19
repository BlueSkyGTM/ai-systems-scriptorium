# Roadmap coverage + scope reframe (2026-06-19)

Triggered by Ray's midway concern: does the curriculum cover the essentials of the two roadmaps the
target role straddles? Checked against the live `developer-roadmap` node lists (roadmap.sh).

## Scope reframe (important — resets the frame for M4–M8)

"AI Platform Engineer" was a **pinpointing reference**, not a hard scope wall. The real target sits on the
**cusp of the AI Engineer and MLOps roadmaps** (which overlap heavily); platform-engineering is the anchor
that named the target and validated the performance-engineering track. **Reference point, not a hardened
rule.** Coverage bar = "the essentials of both roadmaps," judged at the cusp.

**Origin of the cusp (provenance):** the cusp was born by researching the AI Engineer + MLOps roadmaps and
comparing them against the prior curriculum draft — which is exactly where the curriculum **splintered off the
Machine Learning Engineer (MLE) track** (the math-heavy, model-training Path A). That splinter is *why math
took a backseat* and why PyTorch/training depth is thin. Full rationale: `hireability-alignment.md` → Provenance.

## AI Engineer roadmap — COVERED (home turf)
Maps comprehensively: how-LLMs-work/tokens/transformers (M1); the model landscape incl. the Anthropic nodes
the roadmap itself lists — `anthropic-claude` / `claude-agent-sdk` / `claude-code` / `claude-messages-api`
(M1–M3); prompt engineering + sampling params + caching + structured output (M2); context engineering (M2);
embeddings / chunking / vector-DBs / semantic-search / RAG / dynamic-filters / rag-vs-fine-tuning (M1–M2);
agents / multi-agents / ReAct / function-calling (M3–M4); the **entire MCP sub-tree** (M3, deeply);
frameworks — LangChain/LlamaIndex/Haystack/ADK (M3); security / prompt-injection / adversarial / privacy
(M2–M4); inference/fine-tuning (M2/M5).
**Light (mostly deliberate):** broad multimodal image/video (voice IS covered M4/M6; image generation =
antilibrary cut); local-model dev tooling (Ollama/LM Studio/HF inference — partly M5 serving).

## MLOps roadmap — overlap COVERED; native half light by thesis
- **Covered (AI-eng/platform overlap):** Docker, Kubernetes/orchestration, cloud (Azure), CI/CD (GitHub
  Actions), monitoring/observability (Prometheus/Grafana/OTel) → M5 + M6–M8 artifacts.
- **Light by design (inference-platform, not data-platform / model-training bet):** data engineering /
  pipelines / streaming (Kafka/Spark/Airflow/lakes/lineage); classic ML (PyTorch/TF/sklearn/training/DL);
  IaC (Terraform/Ansible); experiment tracking (MLflow/DVC); edge AI (Jetson/TFLite); Go.

## Decision (with Ray)
**Fold in ONE:** a **Docling-anchored data-ingestion / pipeline thread** — the biggest MLOps-native gap and
the one that also serves the AI-eng document-understanding spot. **Keep deliberately light/out** (Ray's call):
IaC/Terraform, explicit experiment-tracking, a multimodal lesson, classic-ML training, edge-AI, Go,
image-generation/diffusion (antilibrary). These remain the conscious inference-platform de-emphasis.

## Docling — adopted (the ingestion stack)
[docling-project/docling](https://github.com/docling-project/docling) (LF AI & Data, MIT): document parsing
(PDF/DOCX/PPTX/XLSX/HTML/audio) with advanced PDF understanding (layout, reading order, tables, code,
formulas, charts→tables), unified `DoclingDocument` → Markdown/JSON, OCR, VLMs, LangChain/LlamaIndex/CrewAI/
Haystack integrations, a built-in **MCP server**, local/air-gapped execution. Python (`pip install docling`).

**Data-ingestion thread placements (carry through authoring):**
- **M2 RAG** — Docling is the concrete tool for the existing "structure-aware splitting / VLM-for-PDFs" step.
  (Light retro-touch when M1/M2 reconciliation runs — currently deferred; don't re-open shipped M2 now.)
- **M5 Deploy & Perf** — a data-ingestion / pipeline-architecture lesson (the MLOps data-eng concept), where
  the platform/ops layer fits. Born with the thread.
- **M6 RAG-chatbot artifact** — Docling as the ingestion layer; the concrete "one stack" under the locked
  capability + portable-seam binding (the portable seam = `DoclingDocument` → chunks).
- **M3 Tools & MCP** — Docling's MCP server is a real, runnable MCP-server example (optional; M3 ships as-is,
  fold into M6 or a later polish rather than re-opening verified M3).
