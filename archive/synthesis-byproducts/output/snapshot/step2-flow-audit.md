# Step 2 — Flow Audit vs roadmap.sh

**Run:** 2026-06-18, fresh context. Live-fetched the benchmark DAGs; assembled our cross-module
edge graph from `module1–5.md`. This is the one Step-2 piece that needed live fetching.

**Verdict:** **PASS.** No backward-ordering violations anywhere — including after the 8-module
renumber. Every place Northstar diverges from the benchmarks is a *deliberate seam choice*, listed
below. The Sans Python sequencing thesis holds against the current (2026) roadmaps.

---

## Benchmarks fetched (roadmap.sh, live 2026-06-18)

Node graphs pulled from the `.json` endpoints (pages are client-rendered; HTML shell has no nodes).

**AI-Engineer** — concept order:
intro/terminology → pre-trained models & providers → prompt engineering (tokens, context, how-LLMs-work,
ReAct, CoT, shots, sampling) → AI safety & ethics → open-source / running models → **embeddings →
vector DBs → RAG → AI agents → MCP → multimodal AI**.

**AI-Agents** — concept order:
prereqs (backend, git, REST) → LLM fundamentals (transformers, tokenization, context, pricing,
generation controls, open/closed weights, reasoning-vs-standard, fine-tune-vs-prompt, embeddings, RAG
basics) → **AI agents 101 (agent loop: perceive→reason→act→observe) → prompt engineering → tools/actions
→ agent memory (short/long, episodic/semantic, summarization, forgetting) → agent architectures (ReAct,
MCP, CoT, planner-executor, DAG, ToT) → building agents (manual→native→frameworks) → evaluation → debug/
observability → security & ethics**.

**MLOps** — concept order (model-centric):
programming fundamentals + git → ML fundamentals → **data engineering (pipelines, lakes/warehouses,
Airflow/Spark/Kafka)** → MLOps principles → MLOps components (version control, CI/CD, orchestration,
experiment tracking, data lineage, **model training & serving**, monitoring, IaC) → tools (DVC, MLflow,
Terraform, KubeFlow, Prometheus/Grafana, Jenkins/GitLab) → containerization + cloud → deep learning,
model evaluation → edge AI, explainable AI.

**System-Design** — concept order (structural/vocab only):
fundamentals (perf-vs-scalability, latency-vs-throughput, CAP, consistency/availability patterns,
replication) → DNS/CDN/load-balancers → app layer/microservices/service-discovery → databases
(SQL/NoSQL, sharding/federation) → caching → asynchronism/queues → communication (HTTP/REST/gRPC) →
monitoring → cloud design patterns.

---

## Northstar ordering (8-module, post-split)

M1 Foundations · M2 LLM Engineering · M3 Agent Foundations · M4 Multi-Agent Systems ·
M5 Deploy & Performance Engineering · M6 Agent Artifacts · M7 Multi-Agent Artifacts ·
M8 Final Systems Engineering Exam.

---

## Where the benchmarks AGREE with us (no deviation)

1. **M1→M2 spine is benchmark-identical.** AI-Engineer's order — prompt eng → embeddings → vector DBs →
   RAG → agents/MCP — is exactly M1 (transformer-forward NLP) → M2 (prompting → embeddings → RAG → agent
   on-ramp). Same concept sequence, same prerequisite direction.
2. **The M3↔M4 split sits on the benchmark's own seam.** AI-Agents keeps single-agent foundations (loop →
   tools → memory → architectures) *before* orchestration/building. Northstar's M3 (Agent Foundations:
   loop, tools/MCP, memory, frameworks) → M4 (Multi-Agent Systems) splits at precisely that single↔multi
   boundary. The split is benchmark-validated, not a deviation.
3. **Build-before-eval, eval-as-thread.** Both AI-Agents and our snapshot run eval as a late/continuous
   thread after the build concepts exist. Matches our eval-driven-development thread (M2→M5).

## Deliberate deviations (the seam — expected, marked)

| # | Deviation | Benchmark says | Northstar does | Why (thesis) |
|---|-----------|----------------|----------------|--------------|
| D1 | **Multi-agent + fleet/loop = a full module (M4)** | a few subtopics under "Agent Architectures" | whole module incl. fleet/loop governance, registries, kill-switches | AI Platform Engineering = agent *infrastructure & governance*. platformengineering.org backs the multi-agent emphasis. The single biggest, most intentional deviation. |
| D2 | **Deploy & Performance Engineering deferred to M5, inference-centric** | MLOps front-loads data engineering + model training/serving; AI-Engineer barely covers serving | defers ops to M5; serving-engines/KV-cache/finops kept, **model-centric MLOps (training pipelines, data eng, experiment tracking) → antilibrary** | "performance engineering > machine learning." Infra-centric, distinct from model-centric MLOps. |
| D3 | **Safety distributed, not a block** | AI-Engineer = early standalone "AI Safety & Ethics"; AI-Agents = terminal "Security & Ethics" | woven per module (safety evals M2; kill-switch/HITL M3–M4; guardrails/red-team M5) | Gap-4 resolution: safety is a thread at point-of-use, not a chapter. |
| D4 | **Multimodal / generative media cut** | AI-Engineer has a full late Multimodal stage | antilibrary; only VLM-API-as-tool surfaces inside artifacts | Off-seam (media *training*). Thesis-aligned cut. |
| D5 | **Compounding-artifact capstones (M6→M7→M8)** | no analog — benchmarks are skill DAGs, not portfolio programs | single-agent artifacts → composed into teams → team builds the exam system | Pedagogical structure; terminal (depends on all prior). No benchmark conflict. |
| D6 | **No standalone distributed-systems module** | System-Design teaches CAP/sharding/LB as a curriculum | assumed / embedded at point-of-use (M5, M8) | One-jump-from-Platform-Engineer scoping; SD used as vocab benchmark, not content. |

## Backward-ordering check across the renumber

The renumber that the audit had to stress-test: old M3 splits into M3+M4; old M4 Deploy → M5; old M5
capstones → M6/M7/M8. Re-ran every cross-module edge:

- `agent-loop (M3) → why-multi-agent / multi-agent-primitives (M4)` — forward (3→4). ✔
- `otel-genai (M3) → observability-stack`, `M4 multi-agent → fleet (M4)`, all Deploy edges → M5 — forward. ✔
- `M5 serving/observability/finops → M6/M7/M8 artifacts & exam` — forward. ✔
- **Split integrity:** nothing in M3 (Agent Foundations, Tracks A–D) *requires* anything in M4 (Tracks
  E–H). The complexity-ladder reference to multi-agent is a forward *governor*, not a prerequisite edge.
  Memory/frameworks don't depend on multi-agent. The cut at the single↔multi seam introduces **zero new
  backward edges.** ✔

**Conclusion:** ordering is sound pre- and post-renumber. The work that remains is curation + the
mechanical renumber, never resequencing. Deviations D1–D6 are the seam doing its job.

---

## Feeds the next steps

- Renumber (Step 2b): the split is validated — proceed with old M3→M3+M4, old M4→M5, old M5→M6–M8.
- SYLLABUS antilibrary fold-in: D2 (model-centric MLOps), D4 (multimodal) are confirmed cuts to record.
- `build/CONTEXT.md`: cite D1 (fleet/loop module) and D2 (inference-centric deploy) as the explicit,
  benchmark-contrasted differentiators of the curriculum.
