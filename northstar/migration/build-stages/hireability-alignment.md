# Hireability alignment (2026-06-19)

Source: Ray's forked field guide *"How to Pivot into an AI/ML Engineering Role in 2026"* (Desktop PDF).
Goal: land an **AI Engineer** role (~$100k+ floor, give or take). Strategy: **front-load the on-the-job
production skills**, leaning on existing AI programming intuition; the **GitHub portfolio is the resume**
("skill fork"). This file maps the Sans Python curriculum to the guide's hireability bar so M5–M8 author
against it.

## The guide's bar (what it says actually gets you hired)
- **Path B — AI Engineer (Applied/GenAI):** system integrator turning foundation models into apps — RAG,
  agents, fine-tuning, user-facing AI. Largest volume of 2026 openings. Skills: LangChain/LlamaIndex,
  OpenAI/Anthropic APIs, vector DBs, RAG, agents.
- **Hiring screens (% of postings):** Python 94% · ML frameworks PyTorch/TF 78% · Cloud 71% · MLOps tools
  63% · LLMs/GenAI 58% · SQL+data-eng 52% · ML system design 48% · Docker/K8s 44%.
- **Step 4 (MLOps/production) = "the step that separates candidates who get hired from those who get
  filtered."** Step 5: **portfolio of 3 deployed end-to-end projects** (real API/app, README framing the
  problem, evaluation/metrics, tests, versioned) = mid-level interviews. Step 6: **ML system design is the #1
  interview skill (35%)**; project deep-dive 20%.
- **Insider:** certs don't matter, portfolios do; the math wall is real but *conceptual fluency* is the
  applied bar (no from-scratch derivation); junior ML market is brutal — position as a mid SWE who does ML;
  specialists earn 30–50% more, **agents/autonomous-systems specialists $175–250k**.

## Where Sans Python is ON the path (strong)
- **Agents / tool use / MCP / multi-agent / fleet** (M3–M4) — the curriculum's spine, and the guide's
  highest-premium specialization ($175–250k). This is the fork's bet, validated.
- **RAG + eval** (M2, + Docling ingestion) — core AI-Engineer-path skill. ✓
- **Production/ops skills front-loaded** (M4 operational safety: durable execution, budgets, kill switches,
  HITL, guardrails; M5 serving/observability) — this IS the guide's Step-4 "hired vs filtered" separator,
  taught early exactly per Ray's strategy. ✓✓
- **Portfolio artifacts** (M6 single-agent, M7 multi-agent) map directly to the guide's recommended AI-Engineer
  projects (production RAG system, AI agent with tool use). The portfolio-as-resume bet = the guide's #1 factor.
- **System design** (M4 fleet/loop governance, M5 serving architecture, M7 multi-agent, M8 exam) feeds the
  35%-weight interview skill.
- **SWE-credibility positioning** — TypeScript/Rust + production discipline = the "premium production hire"
  the guide describes.

## Conscious divergences (the fork's trade-offs — name them, don't drift into them)
1. **"Sans Python" + "platform not model"** narrows away from PyTorch/TF model-training depth (78% screen) and
   deep fine-tuning (a listed AI-Engineer-path skill). Mitigation: a **thin PyTorch + fine-tuning (LoRA)
   literacy** touch so a candidate can *speak to it* (guide: conceptual fluency is the applied bar) — same
   "thin teaching" pattern as M4 ch04. Decide at M5.
2. **Classic ML fundamentals** (regression/trees/boosting, AUC-ROC, feature engineering — guide Step 3A) are
   skipped. Fine for the GenAI sub-path, but a classic-ML system-design prompt could surface it. Conscious
   GenAI-specialization trade.
3. **Math foundation** (guide Step 2) is lighter — M1 covers conceptual attention/transformers; acceptable for
   the applied bar.
4. **No explicit interview-prep / job-search module** (guide Steps 6–7). Mitigation: frame **M8 as the ML
   system-design + portfolio-deep-dive rehearsal** (defend design decisions, discuss failures).
5. **M6/M7 artifacts must hit the guide's "strong project" bar explicitly**: deployed (not a notebook) + README
   framing the problem + evaluation + tests + versioned. Bake this into the M6 PLAN's done-when.

## Salary note
Ray's ~$100k floor is **conservative** vs the guide's US figures (AI Engineer ~$206k avg; "below $160k for a
career-switcher with portfolio is below market"). The agents/platform specialization aims above the floor.
Figures are the guide's; geography/market vary — treat as direction, not a guarantee.

## Feeds M5
The guide's **Step 4 MLOps checklist** (MLflow/W&B experiment tracking, DVC data versioning, model serving
FastAPI/Triton/BentoML, Docker/K8s, Airflow/Prefect/Kubeflow, Evidently/Prometheus/Grafana monitoring, one
cloud ML platform deep) is the yardstick for the **M5 MLOps-inventory pass** — re-weigh the earlier "keep
MLOps-native light" call against "Step 4 is the hireability separator." The Docling ingestion thread already
added covers the data-eng front door.
