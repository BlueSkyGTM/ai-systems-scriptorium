# Sans Python — Course Criteria

**What does "usable" mean?**
Content is usable when Opus can hand it to lesson authoring and the lesson writes itself.
If the source material needs translation, explanation, or cleanup before it teaches the seam — it is not yet usable.

---

## The AI Platform Engineering Seam

Every piece of usable content must serve this job: **building, deploying, and operating the infrastructure that MLOps engineers and application developers use.**

This is not:
- Training models
- Writing CUDA kernels
- General data science
- Python-first thinking

This is:
- Orchestration (how work gets routed, scheduled, and controlled)
- Inference serving (vLLM, SGLang, TensorRT-LLM — cost/token, throughput, latency)
- Agent infrastructure (loops, fleets, memory, tool registries, observability)
- API gateways, cost governors, kill switches, safety harnesses
- TypeScript/Rust as the building material; Python as a runtime artifact you interact with, not author

---

## Content Classification

Every extracted content block is assigned one of four labels:

| Label | Meaning |
|-------|---------|
| **LESSON** | Can become a LearnHouse lesson. Has concept, context, and at least one exercise angle. |
| **EXERCISE** | Concrete enough to become an exercise but not a full lesson on its own. Attach to a parent lesson. |
| **REFERENCE** | Background material, reading, or reference implementation. Does not teach directly. |
| **CUT** | Antilibrary or out of seam. Log reason, discard. |
| **HOLD** | Seam alignment is unclear or a taste judgment is required. Flag for Ray with a one-sentence question. Do not cut. Do not include. Wait. |

---

## Usability Criteria (all six must pass)

### 1. Seam-aligned
Content addresses AI Platform Engineering concerns. Test: could a platform engineer use this in production? If the answer requires model training context, it's cut.

Pass: vLLM serving configuration, agent loop budget, MCP server design, RAG pipeline architecture
Fail: PyTorch training loop, CUDA kernel optimization, dataset preprocessing

### 2. Language-appropriate
TypeScript or Rust are the teaching languages. Python appears only as:
- A deploy artifact (Dockerfile, serve.py, config.py)
- A system you call (MLflow API, Ray Serve endpoint)
- A seam explanation ("this is what the platform sees")

Python is never the vehicle for teaching the concept. If the only example is Python, the content is a rewrite candidate — flag it.

### 3. English-first
Orchestration patterns are explainable in clear English prose + TypeScript/Rust. If a concept requires Python pseudocode to make sense, it fails the seam test. The thesis: English IS the programming language for orchestration. The content should demonstrate this, not undermine it.

### 4. Exercise-viable
Every LESSON candidate has at least one exercise angle:
- Build it (implement a tool, configure a server, write an agent loop)
- Benchmark it (measure latency, cost/token, throughput)
- Observe it (add OpenTelemetry, read traces, respond to a canary)

If the content is pure theory with no hands-on anchor, classify as REFERENCE.

### 5. Module-mapped
Every content block is assigned to one module and one section per SYLLABUS.md. No orphaned content. If it doesn't fit, it's cut.

| Module | What belongs here |
|--------|------------------|
| Module 1 | Rust foundation, TypeScript foundation, NLP transformer-forward, tooling setup |
| Module 2 | Foundation models as APIs, LLM engineering, prompt/context engineering, RAG, evals |
| Module 3 | MCP/A2A protocols, agent engineering, orchestration patterns, multi-agent systems |
| Module 4 | Inference serving, MLOps, infrastructure, production operations |
| Module 5 | Capstone projects (10–15 selected, AI Platform Engineering system-level work) |

### 6. Non-redundant
If the same concept appears in two or more source repos, keep the best version. "Best" means:
- Most concrete (code over prose)
- Most TypeScript/Rust-native
- Closest alignment to Microsoft Learn orchestration patterns (REFERENCE-LAYER.md)
- Most recent (2025/2026 vintage beats 2022/2023)

---

## Gap Definition

A gap is flagged when SYLLABUS.md requires a lesson but the synthesis finds no usable content for it.

Gap severity:
- **CRITICAL**: Core seam concept with no source material. Must find content before Build phase begins.
- **HIGH**: Important lesson with partial coverage. Microsoft Learn is the fallback source.
- **LOW**: Nice-to-have lesson with no source material. Mark antilibrary, move on.

---

## Module 5 Capstone Selection Criteria

From the 85 Phase 19 items, select 10–15 that meet ALL of:
1. Demonstrates system-level AI Platform Engineering (not a single component in isolation)
2. TypeScript or Rust primary — or infrastructure-level Python (deploy, serve, observe)
3. Integrates two or more concepts from Modules 2–4
4. Could plausibly be a portfolio artifact for an AI Platform Engineer job application
5. Has a real operational artifact (running server, agent system, observability dashboard, cost report)

Candidates to prioritize: terminal-native-coding-agent, multi-agent-software-team, llm-observability-dashboard, speculative-decoding-server, github-issue-to-pr-agent, constitutional-safety-harness, mcp-server-with-registry.

---

## Microsoft Learn Thread

Every module synthesis must cross-reference REFERENCE-LAYER.md. The orchestration patterns in that document are the spine the content hangs on. If a content block maps to a REFERENCE-LAYER.md pattern, tag it. These mappings survive into lesson authoring.

Pattern reference: `specs/northstar/REFERENCE-LAYER.md`
