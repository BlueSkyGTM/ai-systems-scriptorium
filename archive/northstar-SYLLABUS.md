# Sans Python — Course Syllabus

**Discipline:** AI Platform Engineering — infrastructure-centric: the platform that MLOps engineers and
application developers *use*. Distinct from model-centric MLOps and from general AI Engineering. The
target is the seam where indispensability lives: building, serving, operating, and governing the systems
that run models. Core hypothesis: **inference-platform engineering > model training** — the seam owns
serving, cost, observability, and governance, not model internals. Graduates carry a minimum ML-literacy
floor (read and reason about training/eval, not implement). (See SPEC.md; [[optimize-archetype-ruling]].)

**Structure: 8 modules.** Five teaching modules (Foundations → LLM Engineering → Agent Foundations →
Multi-Agent Systems → Deploy & Performance Engineering) plus three application modules (Agent Artifacts →
Multi-Agent Artifacts → Final Systems Engineering Exam). The artifacts **compound**: single agents built
in M6 are composed into teams in M7; that team builds the exam system in M8. Each artifact solves a real
business problem. ([[curriculum-module-structure]])

**Cut logic — lesson-level, not macro:** Phase-level verdicts here are directional, not final. Every
lesson gets its own keep/cut decision before Claude Code touches it. A "KEEP" phase may lose 40% of its
lessons; an Antilibrary phase may surface one worth keeping. The macro cuts (pure Optimize phases) are
the floor; lesson-by-lesson audit is the real work.

**Lean / link, don't reproduce:** Do not reproduce `ai-engineering-from-scratch`'s 500+ from-scratch
lessons. They are linked as reference/antilibrary. The curriculum spine is **business-application
artifacts**, not from-scratch reimplementation.

**Math:** No math module. Statistical literacy is embedded contextually — probability/distributions in M2
(evals, output interpretation), statistical significance in M5 (A/B testing, drift), loss functions at a
conceptual level wherever fine-tune-vs-prompt decisions arise. Students meet the math when it becomes
necessary, not as a prerequisite wall. Linear algebra for backprop, calculus for gradient descent, and
matrix operations stay in the Antilibrary. The minimum ML-literacy floor — what training, fine-tuning, and
eval metrics mean and when they matter (read, not implement) — is carried for interview and incident readiness.

**Status: structure validated, lesson-level audit not begun.** The 8-module structure passed the Step-2
flow audit against roadmap.sh (`snapshot/step2-flow-audit.md`): no backward-ordering violations, every
divergence a deliberate seam choice. Nothing here is a final curriculum decision — it is the validated
skeleton from which lesson-by-lesson review starts.

---

## How To

This spec participates in two Claude Code handoffs. Both require the sub-repo extraction outputs. Do not
hand this file to Claude Code without them.

### Handoff 1 — Lesson-level audit (after all 9 extractions complete)

**Receives:** SYLLABUS.md + all 9 `output/` folders + REFERENCE-LAYER.md
**Produces:** `output/lesson-audit.md` in each sub-repo — one row per lesson: name | keep/cut | reason

**Steps:**
1. Read SYLLABUS.md in full — understand which phases feed which modules (mapping table below).
2. For each curriculum module, open the corresponding extraction output file(s).
3. For each lesson: keep/cut test — does this build a skill an AI Platform Engineer uses in production?
4. Write verdict to `output/lesson-audit.md` per sub-repo.
5. Flag thread-tagged lessons: `[THREAD: eval]`, `[THREAD: versioning]`, `[THREAD: safety]`, `[GAP 2]`.
6. Write a one-paragraph module summary: total lessons, kept, cut, notable flags.

**Done when:** every curriculum module has a completed `output/lesson-audit.md`.

### Handoff 2 — Lesson authoring (Build phase, per module)

**Receives:** target module section + the module keep/cut dossier (`migration/_dossier/`) + REFERENCE-LAYER.md
pattern entries + the authoring contract (`migration/AUTHORING.md`) + the style contract (`migration/STYLE.md`)
**Produces:** `output/lessons/[module]/[lesson-slug].md` — one file per kept lesson

**Steps:**
1. Read the target module section from SYLLABUS.md.
2. Read lesson-audit keep decisions for all sub-repos feeding that module.
3. For each kept lesson: read extracted content, check REFERENCE-LAYER.md for the relevant Microsoft Learn
   pattern, draft per `migration/AUTHORING.md` (the three-source rule) and `migration/STYLE.md` (the voice).
   Author in the threaded language at its point-of-use (TS from
   M3, Rust from M5 — see `snapshot/language-tracks.md`).
4. Apply seam framing: every lesson answers "why does an AI Platform Engineer need this?"
5. Flag any lesson needing a live Microsoft Learn fetch — use the connector, do not assume from memory.

**Done when:** all kept lessons for the target module have a draft lesson file.

**Microsoft Learn — Reference Layer:** Available for cross-referencing curriculum decisions against
production-grade engineering documentation. Its role is structural, not sourcing: validating that module
sequencing maps to real LLMOps lifecycle patterns, verifying architectural concepts (inner/outer loop,
complexity ladder, eval-driven development, prompt versioning) against current industry practice, and
filling specific gaps where sub-repo material is thin. See REFERENCE-LAYER.md. ([[northstar-reference-layer]])

---

## Old → New module mapping

The snapshot files (`snapshot/module1–5.md`) were written under the old 5-module numbering. The split and
renumber, validated by the Step-2 audit:

| Old | New | Module |
|-----|-----|--------|
| M1 | **M1** | Foundations |
| M2 | **M2** | LLM Engineering |
| M3 (Tracks A–D) | **M3** | Agent Foundations |
| M3 (Tracks E–H) | **M4** | Multi-Agent Systems |
| M4 | **M5** | Deploy & Performance Engineering |
| M5 capstones (single-agent) | **M6** | Agent Artifacts |
| M5 capstones (multi-agent) | **M7** | Multi-Agent Artifacts |
| M5 finale | **M8** | Final Systems Engineering Exam |

Old M3 split cleanly at the single↔multi-agent seam — the same seam roadmap.sh's AI-Agents roadmap uses,
and the split introduced **zero backward edges** (`snapshot/step2-flow-audit.md`).

---

## Curriculum Binding Gaps (resolutions)

Five structural framing/sequencing gaps, all resolved. None require new content.

**Gap 1 — Evaluation as one continuous thread, not two topics.** Named **eval-driven development** as a
course-wide thread: the inner loop (model selection, prompt iteration, RAG tuning) runs throughout
development before the outer loop (production monitoring) takes over. Surfaces in M2 (introduce), M3/M4
(agent eval), M5 (production observability). Explicit per-module notes, no new content.

**Gap 2 — The complexity ladder as a decision framework at the M2→M3 boundary.** A named bridge section at
the end of M2 / start of M3 teaches the ladder — direct model call → single agent with tools → multi-agent
orchestration — as a *decision tool*, with explicit conditions for each rung. The governing principle:
don't add an agent between the task and the model call unless the problem requires it. This is the
anti-"agent everything" guard and the editorial spine of M3–M4.

**Gap 3 — Prompt and config versioning as a named thread.** Versioning callouts in M2 (prompt versioning
as a development-time practice — MLflow prompt registry, alias strategies) and M5 (the full lifecycle:
staging, promotion, rollback). The thread exists in the material; it is now named in the structure.

**Gap 4 — Safety distributed, not standalone.** Phase 18 (Ethics/Safety) is distributed to where it is
technically relevant: safety evals + output guardrails in M2; agent kill switches + HITL + loop budgets in
M3/M4; red-teaming + guardrail infrastructure in M5. Explicit safety callouts per module.

**Gap 5 — Data layer entry point. RESOLVED: tool-first, pre-curated data.** M2 RAG uses pre-curated
datasets — students build RAG intuition on clean data first. Data-pipeline thinking (where data comes
from, production prep) enters M5 where the deploy track gives it full context. No data primer in M1. The
declaration: *"In this course, data is given. You learn to use it. In Module 5, you learn to build it."*

---

## Module 1 — Foundations

**Source: `ai-engineering-from-scratch` (setup, NLP) + `100-exercises-to-learn-rust` + `typescript-projects`**

The environment and the transformer-forward NLP everything LLM-related assumes. Languages are **threaded
to point-of-use**, not taught as a Module-1 wall (TS enters M3, Rust enters M5 — see
`snapshot/language-tracks.md`, [[language-track-threading]]). M1 installs only the toolchains.

### 00 — Setup and Tooling
Environment, toolchains, agent setup from day one. TypeScript and Rust tooling rather than Python. No IDE
dependency. The first chapter sets the philosophy. **This track is a prerequisite for every hands-on
lesson in the course.**

### 05 — NLP: Transformer-Forward Only
Cut the pre-transformer half (classical tokenization, word embeddings, RNN/LSTM, seq2seq → Antilibrary).
Keep from **attention** forward — transformer mechanics are seam knowledge for every engineer who designs
prompts and evals. The `09→10` seam (seq2seq failure → attention) is the most important cut in the phase.
The RAG-component cluster here (QA, information retrieval, embeddings, chunking) and the eval thread (NLI,
LLM-evaluation, long-context) are the **foundations half of M2** — introduced here as transformer-era NLP,
built into systems in M2.

### Language toolchains (threaded, not walled)
Rust (serving/Deploy layer) and TypeScript (product/Build layer) are installed in M1 but **taught at
point-of-use**: the break-in TS set arrives at M3 (first typed tools/MCP servers); the Rust ownership
on-ramp arrives at M5 (serving layer). Python stays read-as-literacy throughout; a narrow **write-track**
(eval scripts, pytest, packaging, FastAPI serving glue, notebook-to-service) threads in at point-of-use from
M2 and concentrates at M5. Full threading map in `snapshot/language-tracks.md`.

**Safety callout:** none at this layer.

---

## Module 2 — LLM Engineering

**Source: `ai-engineering-from-scratch` (Ph08, Ph11) + `ai-system-design-guide` (Ch05, Ch06, eval guides)**

The LLM engineering core: prompting → structured output → embeddings/RAG → eval → the agent on-ramp. The
densest, most-overlapped module — curation (dedup/merge) is the main job here, not resequencing.

### Prompting & Context (asdg Ch05 + aefs Ph11)
Prompt engineering (anatomy, instruction hierarchy, roles), few-shot/ICL, chain-of-thought, tree-of-thought,
context engineering (window budget, lost-in-the-middle, compaction), prompt caching, DSPy
[versioning thread], prompt-injection defense [safety thread]. asdg Ch05 supplies production depth over
aefs Ph11.

### Embeddings & RAG — one spine (asdg Ch06 canonical + aefs Ph11 hands-on)
**RAG dedup ruling (Step 3): merge, not cut.** M1 introduced the *components* (embeddings, IR, chunking) as
transformer-era NLP; M2 builds the *RAG system*. **`asdg` Ch06 is the canonical spine** (14 sections:
fundamentals → chunking → vector DBs → hybrid → rerank → graphRAG → agentic → eval → production);
**`aefs` Ph11 RAG is the hands-on build-track** layered onto it. The three sources collapse into one
ordered path: M1 = components, M2 = system. Agentic RAG is the seam pointer into M3.

### Evaluation (asdg eval guides + threads)
Eval-driven development originates here (Gap 1). LLM-as-judge → RAG eval (the triad) → multi-step/multi-turn
eval; observability setup → error analysis → judge design → statistical correction. Eval is a spine running
M2→M5, not a one-off lesson.

### Structured Output → Function Calling → MCP intro → LangGraph (the M2→M3 on-ramp)
Structured outputs / schema validation → function calling / tool use → MCP introduction → LangGraph
(state machines) → framework tradeoffs; function-calling + RAG + caching + guardrails → a production LLM
app. **This is the hinge into Agent Foundations.**

### Generative AI (aefs Ph08) → ANTILIBRARY
Generative *media* (GANs, diffusion, video/audio/3D) is off-seam model-building. Cut to Antilibrary
(see below). Foundation-models-as-APIs literacy and the LoRA/conditioning *concept* survive where adaptation
is discussed; FID/CLIP kept only as a generic eval reference if a lesson needs it.

**Versioning callout:** prompt versioning introduced as a development-time practice (MLflow prompt
registry, alias strategies). **Safety callout:** safety evals, guardrails on model output, prompt-injection
defense.

---

## Module 3 — Agent Foundations

**Source: `ai-engineering-from-scratch` (Ph13, Ph14) + `ai-system-design-guide` (Ch07, Ch08, Ch09, Ch15, Ch17)**

The single-agent spine: a reasoning loop with tools, memory, and a framework. `Agent = Reasoning Model +
Tool Use + Persistent Memory + Environment Feedback`. **The complexity ladder (Gap 2) opens this module** as
the decision framework for when to add an agent at all.

### Agent fundamentals & reasoning loops (asdg Ch07, aefs Ph14)
ReAct (observe-think-act) → reflexion (critic + memory) → ToT/LATS (search) → self-refine; planning &
task decomposition → error handling & recovery. The complexity-ladder thread is the anti-"agent everything"
governor running through the whole module.

### Tools & Protocols / MCP — one spine (aefs Ph13 canonical)
**MCP dedup ruling (Step 3): one spine.** `aefs` Ph13 (23 lessons) is canonical: fundamentals → server →
client → transports → resources/prompts → sampling → roots/elicitation → async → apps → security
(poisoning) → OAuth 2.1 → gateways/registries. asdg Ch17 + Ch07.03 fold in as lighter references. Typed
tool/MCP contracts are where **TypeScript enters** (break-in set + generics/interfaces).

### Memory & State (asdg Ch08)
Memory architectures (L1 working / L2 episodic / L3 semantic) → short-term context (KV/paged-attention) →
long-term memory (vector + graph) → agentic memory (Mem0/Letta/MemGPT) → semantic caching → state
management (checkpointing). KV-cache/paged-attention is introduced here and deepened in M5 serving (layering).

### Frameworks (asdg Ch09)
LangChain → LangGraph → LangSmith; LlamaIndex; semantic-kernel / MS agent framework; CrewAI; Claude/OpenAI/
Google SDKs; pydantic-ai/mastra (typed) → framework-selection guide. DSPy tagged optimize-territory.

### Design patterns (asdg Ch15)
Pattern catalog + anti-patterns — the systems-thinking vocabulary for interviews and architecture.

**TypeScript entry:** break-in set (type system, JS→TS, unions, objects, functions, basic interfaces,
tsconfig) + generics, interfaces, type modifiers, declaration files, classes — all at point-of-use for
typed tools and MCP contracts. **Safety callout:** agent kill switches, human-in-the-loop. **→ Culminates
in Module 6 (Agent Artifacts).**

---

## Module 4 — Multi-Agent Systems

**Source: `ai-engineering-from-scratch` (Ph15, Ph16) + `ai-system-design-guide` (Ch07.04, Ch17) + `fleet-engineering` + `loop-engineering`**

The seam's defining material: single agent → runs safely for hours → coordinates with many → governed as a
fleet. The complexity ladder gates entry — multi-agent only past the single-agent ceiling. roadmap.sh treats
this as a few subtopics; **Northstar makes it a full module** (deliberate deviation D1 — agent infrastructure
& governance *is* AI Platform Engineering).

### Multi-agent & swarms (aefs Ph16, asdg Ch07.04)
Why multi-agent (single-agent ceiling) → communication protocols (MCP/A2A/ACP/ANP) → multi-agent primitives
(Agent/Handoff/SharedState/Orchestrator) → orchestration patterns (supervisor/swarm/hierarchical/debate) →
multi-agent debate → failure modes (MASFT 14 modes).

### Autonomous systems & operational safety (aefs Ph15 — seam half)
Long-horizon agents → durable execution → action budgets / cost governors → kill switches / circuit
breakers → HITL propose-then-commit → checkpoints/rollback → guardrails (Llama-Guard) → constitutional AI.
This is how you *operate* agents safely = platform engineering. (The frontier-safety research/policy half —
RSP, FSF, METR, RSI theory, self-improvement research — is Antilibrary; see below.)

### Fleet & Loop engineering (`fleet-engineering` + `loop-engineering`) — seam core
The production operational layer, the clearest AI Platform Engineering material in the curriculum.
**"Loops live inside fleets."** Loop (single agent-system ops): trigger → action → verification →
budget/kill-switch; patterns: daily-triage, PR-babysitter, dependency-sweeper, CI-sweeper. Fleet (3+ loops /
5+ agents governance): registry → identity → permissions → inbox-HITL → audit → economics → kill-switch.
Both carry machine-readable registries + schemas (everything-as-code platform vocabulary).

### Computer-use, coding & voice agents (asdg Ch17, aefs Ph14/16) — thin teaching
**Track-H ruling (Step 3): teach light, prove in the artifact.** How each works (computer-use:
screenshot-reason-act; coding agents; voice: Pipecat/LiveKit) is taught thinly here; the heavy realization
lives in the Artifacts they seed (coding → Agent Artifact 01; voice → Agent Artifact 03).

**Safety callout:** action budgets, circuit breakers, fleet kill-switches, shared-inbox HITL. **→ Culminates
in Module 7 (Multi-Agent Artifacts).**

---

## Module 5 — Deploy & Performance Engineering

**Source: `ai-engineering-from-scratch` (Ph17) + `ai-performance-engineering` (inference subset) + `made-with-ml` (deploy subset) + `ai-system-design-guide` (Ch11–14, Ch16)**

The densest concentration of the seam: the infrastructure MLOps engineers and app devs *use* — serving
engines, GPU scheduling, gateways, observability, finops. **Built, not described** — every concept has a
hands-on counterpart. roadmap.sh MLOps front-loads data engineering + model training; **Northstar is
inference-centric and defers ops to here** (deliberate deviation D2). **Rust enters** at this layer
(ownership on-ramp + async serving).

### Serving & Inference Optimization (aefs Ph17 + aipe ch15–20)
Managed platforms / inference economics → serving-engine selection (vLLM/SGLang/TRT-LLM/llama.cpp) →
vLLM internals (paged-attention, continuous batching, chunked prefill) → speculative decoding (EAGLE-3) →
production quantization (AWQ/GPTQ/FP8/NVFP4); disaggregated prefill/decode → KV-cache management
(LMCache, NVLink pooling); prefix caching (RadixAttention). aefs = operate; aipe = measure/profile/attribute
(layer them, don't dedup).

### Metrics, Observability & Rollout (aefs Ph17, eval thread outer loop)
Inference metrics (TTFT/TPOT/ITL/goodput/P99) → load testing → observability-stack selection → shadow
traffic → canary rollout → A/B testing; model routing → AI gateways (routing/fallback/secrets) → rollback
via registry+flags. SRE-for-AI → chaos engineering [resilience sub-thread]. The eval thread's outer loop.

### Operations: Security, Compliance, FinOps (aefs Ph17, asdg Ch12)
Security (secrets/vault/rotation/egress) → compliance (SOC2/HIPAA/GDPR/EU-AI-Act/ISO-42001); finops
(per-user/task/tenant attribution, spend caps, kill switches); caching economics + batch APIs (50% discount)
→ cost optimization. The clearest AI-Platform-Engineering-specific material — finops-for-tokens and
AI-specific compliance don't exist in generic platform eng.

### Performance Engineering depth (aipe inference subset)
The thesis core: **inference-platform engineering > model training.** Scoped to *inference serving*
(aipe ch15–20) + the 200+ item production checklist. Profiling (Nsight), roofline analysis, NVLink/NVSwitch
topology, NUMA/OS tuning, I/O pipeline. Measured deltas (continuous batching 4.16×, NVLink KV pool 6.11×,
tensor-core decode 15.65×). **aipe training/CUDA chapters (ch01–14) are Antilibrary** — perf-eng is
inference-scoped.

### MLOps subset (made-with-ml, deploy half)
The **deploy/serving/CI** material stays (versioning, experiment tracking, serving pipelines as portfolio
pieces). The **model-centric training-pipeline / model-lifecycle** material is Antilibrary — AI Platform
Engineering is infrastructure-centric, distinct from model-centric MLOps (deviation D2).

### Relocated artifacts (ride the Deploy/Optimize ruling)
From the old capstone set, these belong here, not in the agent-artifact modules: **11** LLM observability &
eval dashboard (Deploy); **13** MCP server with registry & governance (Deploy/platform — its governance also
feeds the M7 finale fleet layer); **14** speculative-decoding inference server (Deploy/Optimize); **07**
end-to-end fine-tuning pipeline (Optimize — executing the train, not deciding it).

**Versioning callout:** full lifecycle — staging, promotion, rollback. **Safety callout:** red-teaming,
responsible deployment, guardrail infrastructure.

---

## Module 6 — Agent Artifacts

**Applies Module 3. Source: `ai-engineering-from-scratch` (Ph19 capstones, single-agent subset)**

Single-agent portfolio builds, each solving a real business problem and shipping a skill artifact
(`outputs/skill-*.md`). Picked for distinct, non-overlapping competencies. **These agents are reused and
composed into teams in M7** (the compounding design).

| # | Artifact | Competency |
|---|----------|------------|
| 01 | Terminal coding agent | the canonical agent harness — plan/act/observe, tools, sandbox, cost ceiling |
| 08 | Production RAG chatbot (regulated vertical) | RAG + guardrails + citations + drift observability |
| 03 | Real-time voice assistant | streaming under hard latency budgets (ASR→LLM→TTS, barge-in) |
| 16 | Issue-to-PR autonomous agent | autonomous cloud worker, scoped credentials, in-sandbox CI verification |

> **Reconciled (2026-06-18):** `snapshot/artifacts-plan.md` has been updated to this own-module +
> compounding structure (M6 single agents → M7 governed teams → M8 the team builds the exam). The plan and
> this section agree. Only open item: the minor 4/3-vs-4/4 multi-agent split.

---

## Module 7 — Multi-Agent Artifacts

**Applies Module 4. Source: `ai-engineering-from-scratch` (Ph19 capstones, multi-agent subset) + `fleet-engineering`**

Single agents from M6 composed into governed teams. The structural last boss of the teaching arc.

| # | Artifact | Competency |
|---|----------|------------|
| 05 | Autonomous research agent | plan-execute-verify tree search with sub-agents + sandbox |
| 06 | DevOps K8s troubleshooting agent | supervisor + specialist agents, read-only, HITL Slack gates |
| 10★ | Governed multi-agent fleet | the SWE team (architect/coders/reviewer/tester via A2A) wrapped in the fleet layer: registry, budgets, HITL inbox, audit, kill-switches |

**Finale principle — elevate, don't author:** the fleet artifact reuses an existing multi-agent project and
layers fleet governance onto it (DRY), rather than a from-scratch fleet build. A fleet of agents run as
governed infrastructure = AI Platform Engineering, thesis full circle.

> **Open (Ray):** 4/3 vs 4/4 artifact split — a 4th multi-agent artifact could elevate **13** (MCP
> governance) separately. Minor; superseded somewhat by the own-module structure.

---

## Module 8 — Final Systems Engineering Exam

**Integration capstone. Source: the M7 fleet + `ai-system-design-guide` (Ch16 case studies) as reference architectures**

The M7 team builds the exam system end to end — the compounding arc's terminal node. Not an academic demo:
a production-grade system designed against the seam job description (eval-gated pipeline, multi-tenant RAG,
agentic MLOps system). The 20 asdg case studies serve as reference architectures to build *a version of*,
not invent from scratch. Distributed-systems vocabulary (load balancing, caching, sharding, async/queues,
CAP for distributed agent state) is assumed/applied here — used as structural benchmark, not taught as a
standalone module (deviation D6).

**Delivery platform (pivoted 2026-06-18):** **mdBook** for course content (markdown, builds straight from
the repo) + **Claude Code via VS Code** for exercises/quizzes/projects + a per-lesson **copy button** that
hands a context payload to Claude Code (repo open) to run the task and resume where you left off. Progress =
git + a small progress file. **LearnHouse dropped entirely** (full DB reviewed = multi-tenant LMS plumbing;
its RAG + progress patterns are coupled and trivially replaced — RAG is already an M2/M6 artifact). See
[[delivery-platform-pivot]]. Albatross (was the LearnHouse instance) and Mariner (was the LearnHouse
migration pipeline) need reconceiving.

---

## Phase Verdicts

**07 — Transformers Deep Dive → ANTILIBRARY.** Transformer implementation is Optimize territory. M1's
transformer-forward subset (attention mechanics) covers what the seam needs. Building transformers from
scratch is not an AI Platform Engineer skill.

**12 — Multimodal AI → ANTILIBRARY.** Foundation-models-as-APIs is sufficient; VLM API usage surfaces
naturally in artifacts. Training multimodal models is Optimize territory.

**18 — Ethics, Safety, Alignment → DISTRIBUTED (Gap 4).** Not standalone. Safety evals + output guardrails
(M2); agent kill switches + HITL + loop budgets (M3/M4); red-teaming + guardrail infrastructure (M5). The
frontier-safety *research/policy* layer is Antilibrary (below).

---

## Antilibrary

Material we chose not to prioritize. Not discarded — held. Use it when a specific problem surfaces, as a
reminder that depth is infinite, or as a jumping-off point when curiosity pulls.

> *We don't need to read all of it. We just need to know it exists and roughly where to find it.*

### Locked by the Optimize ruling (Step 3 — [[optimize-archetype-ruling]])

The throughline: **the platform engineer builds and operates the platform; they don't train the models or
set frontier-safety policy.** Keep the decisions and the operations; antilibrary the training implementation
and the research survey.

**Generative media (M2 Track E).** GANs, diffusion (DDPM/latent), video/audio/3D generation, VAR — ~90%
off-seam by the source's own flags. Model-building, not platform. Keep only the LoRA/conditioning concept
and FID/CLIP as a generic eval reference.

**GPT-from-scratch build (old M5 Part 2, lessons 30–49).** BPE tokenizer → embeddings → multi-head attention
→ transformer block → GPT assembly → training loop → SFT → DPO. Optimize depth — building a model, not a
platform. (M1 attention literacy is the kept conceptual minimum.)

**Distributed training from scratch (old M5 Part 2, lessons 76–81).** DDP/FSDP/ZeRO/pipeline/tensor
parallelism. The sharpest cut — model-training-at-scale engineering.

**Fine-tuning pipeline implementation (artifact 07).** Relocated to M5 as Optimize/Deploy reference, not an
agent artifact — executing the train, not deciding it. (The fine-tune-vs-prompt *decision* stays in-seam, M2.)

**`ai-performance-engineering` training & CUDA subset (ch01–14).** Distributed training (FSDP/TP/PP), CUDA
kernel writing, Triton, GPU architecture deep dive. The inference-serving subset (ch15–20) is in M5; this is
what's left. Perf-eng correctly scoped to inference.

**Made-with-ML model-centric MLOps.** Training-pipeline / model-lifecycle material — model-centric, off the
infrastructure-centric seam. The deploy/serving/CI subset stays in M5.

**Frontier-safety research & policy.** RSP v3, OpenAI Preparedness Framework, DeepMind FSF, METR
time-horizons, RSI/alignment theory, self-improvement research (STaR/AlphaEvolve/DGM/AI-Scientist),
CAIS/CAISI societal-risk. AI-safety-researcher / policy-analyst material, not platform-build. (Operational
agent safety — guardrails, kill switches, HITL — stays in-seam, M4.)

**`ai-engineering-from-scratch` 500+ from-scratch lessons — link, don't reproduce.** The curriculum spine is
business-application artifacts; the from-scratch lesson corpus is linked as reference/antilibrary, not
rebuilt. ([[antilibrary-principle]])

### Pre-existing antilibrary (foundations depth)

**01 — Math Foundations (partial).** Linear algebra, calculus for backprop, matrix operations → Antilibrary.
Probability, distributions, statistical significance, loss-function concepts are embedded contextually in
M2/M5, not cut.

**02 — ML Fundamentals.** Supervised/unsupervised learning, training basics. Optimize. Knowing they exist is
seam literacy; implementing from scratch is not.

**03 — Deep Learning Core.** Backprop, activations, gradient descent. The applied form in M2 is sufficient.

**04 — Computer Vision.** CNNs, object detection, image classification. Pure Optimize, off-seam.

**06 — Speech and Audio.** ASR, TTS, audio feature engineering. Optimize unless targeting voice as a product
niche.

**09 — Reinforcement Learning.** RL from first principles, reward modeling. RLHF matters conceptually (a
paragraph in M2); the chapter-length version is held here.

**10 — LLMs from Scratch.** Karpathy territory. The deepest reference — understanding how LMs are constructed
makes you a better engineer even if you never implement it.

**ai-system-design-guide — Antilibrary subset.** Ch01 (LLM internals at implementation depth), Ch03
(training/adaptation: fine-tuning/LoRA/DPO/distillation — Optimize-heavy, though the fine-tune-vs-prompt
*decision* is embedded in M2), Ch04 (inference optimization — overlaps `ai-performance-engineering`, handled
in M5).

**05 — NLP Foundations (pre-transformer half).** Classical tokenization, word embeddings, RNN/LSTM, seq2seq.
The historical arc to transformers. Worth reading when curiosity pulls; not curriculum.
