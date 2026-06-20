# Module 2 — Prerequisite Snapshot

> **Renumber map (8-module, 2026-06-18).** Edge list renumbered to 8-module; prose retains original
> 5-module tags. Module 2 numbering unchanged. Its outbound `M3:` agent refs (agent-engineering,
> agent-memory, agent-security, agentic-systems, agent-eval, orchestration) all land in **M3 Agent
> Foundations** and stay M3; only `M4:production-monitoring` (old Deploy) renumbers to **M5**. See
> `step2-flow-audit.md`.

Module 2 is the **LLM engineering core**: prompting → structured output → embeddings/RAG → eval →
the agent on-ramp (function calling, MCP, LangGraph). It's the densest and most-overlapped module —
three sources cover RAG, and the eval thread runs through all of them.

Source files: `aefs-module2-generative-ai`, `aefs-module2-llm-engineering`,
`asdg-module2-prompting-context`, `asdg-module2-retrieval-systems`, `asdg-module2-eval-guides`.

---

## Track A — Prompting & Context (aefs Ph11 + asdg Ch05)

The reasoning + context ladder. Two sources, heavily overlapping; curation must dedupe.

```
prompt-engineering(anatomy, instruction-hierarchy, roles) → few-shot/ICL → chain-of-thought → tree-of-thought
prompt-engineering → context-engineering(window budget, lost-in-the-middle, compaction)
context-engineering → prompt-caching
structured-generation → (Track C function-calling)
prompt-optimization(DSPy) [versioning thread]
prompt-injection-defense [safety thread]
```

Inbound: `[M1] structured-outputs/constrained-decoding`, `[M1] attention` (window/attention concepts).
Outbound: `prompt-injection-defense → [M3] agent-security/HITL`; `context-engineering → [M3] agent-memory`.

---

## Track B — Embeddings & RAG (aefs Ph11 + asdg Ch06 + M1 NLP cluster)

**The most overlapped material in the library.** asdg Ch06 is the deepest (14 sections); aefs Ph11 builds it from scratch; M1 NLP track already introduced QA/IR/embeddings/chunking. Curation will collapse three copies into one spine.

```
embeddings → rag-fundamentals → chunking-strategies → vector-databases
rag-fundamentals → hybrid-search → reranking
rag-fundamentals → advanced-rag(HyDE, parent-child, contextual-retrieval)
advanced-rag → graphrag, agentic-rag, multimodal-rag, late-interaction-colbert
rag-fundamentals → rag-evaluation [eval thread]
```

Inbound (strong, confirms M1 finding): `[M1] qa, information-retrieval, embedding-models, chunking-for-rag` are the foundations half of this track.
Outbound: `agentic-rag → [M3] agentic-systems` (agentic RAG IS an agent pattern — seam to Module 3).

---

## Track C — Structured Output → Tools → Agents (aefs Ph11)

The on-ramp from "LLM call" to "agent." This track is the **hinge into Module 3.**

```
structured-outputs/schema-validation → function-calling/tool-use → MCP(model-context-protocol)
function-calling → langgraph(state-machines for agents) → agent-framework-tradeoffs
function-calling + rag + caching + guardrails → production-llm-app(Ph11 capstone)
```

Inbound: `[M1] ts:generics/interfaces` (tool/MCP contracts are typed), `[M1] structured-outputs`.
Outbound (strong): `function-calling, MCP, langgraph → [M3] agent-engineering/orchestration`. **This is the M2→M3 seam.**

---

## Track D — Evaluation (asdg eval-guides + threads across Ph11/Ch05/Ch06)

Eval is not a lesson, it's a thread — concentrated in two full study guides (16 chapters each) plus per-lesson `[THREAD: eval]` tags.

```
[M1] nli → llm-as-judge → rag-evaluation(RAG triad) → multi-step/multi-turn eval → production-monitoring
observability-setup → error-analysis → judge-design → statistical-correction(judgy)
```

Inbound: `[M1] nli, llm-evaluation, long-context-eval` (eval thread originates in M1).
Outbound: `eval → [M3] agent-eval`, `→ [M4] production-monitoring/observability`. Eval is a spine that runs M1→M4.

---

## Track E — Generative AI (aefs Ph08) — MOSTLY ANTILIBRARY

```
generative-models-taxonomy → VAE → GAN → diffusion(DDPM) → latent-diffusion → [video/audio/3D/flow]
                                                          → controlnet-lora-conditioning [seam-relevant]
                                                          → evaluation-fid-clip [seam-relevant, generative-media]
```

**Audit flag (major):** the source itself marks 13 of 15 lessons `[CHECK: possibly antilibrary]`. Generative *media* (GANs, diffusion, video, audio, 3D) is **off-seam** for AI Platform Engineering. Only LoRA/conditioning(08) connects (and it reappears as a first-class technique in Track C fine-tuning). **This whole track is a strong CUT candidate** — recommend Step 3 confirm cut to antilibrary, keeping only the LoRA concept where it's already taught in Ph11-08.

---

## Module 2 — flow observations (feed Step 2)

1. **Triple RAG coverage** (M1 NLP cluster + aefs Ph11 + asdg Ch06) is the biggest dedup job in the curriculum. Not a sequencing *error* — a curation/merge task. Flag for Step 3, not a violation.
2. **The M1→M2 RAG/eval edge is now confirmed from both sides.** M1's NLP RAG/eval lessons are consumed here. Resolves toward: M1 holds transformer-level foundations, M2 holds the RAG *system*. Defensible as-is.
3. **Track E (generative media) is the clearest off-seam block in the library.** Strong antilibrary candidate. The thesis (AI Platform Engineering, not model/media training) backs the cut.
4. **Track C is the clean M2→M3 seam** — function-calling → MCP → LangGraph hands directly to agent engineering. Correctly ordered.
5. No backward edges (nothing in M2 depends on M3+). Clean ordering; the work here is *curation* (dedup + cut), not *resequencing*.

## Edge list (machine-readable)
```
# Track A
m2:prompt-engineering -> m2:few-shot-icl
m2:few-shot-icl -> m2:chain-of-thought
m2:chain-of-thought -> m2:tree-of-thought
m2:prompt-engineering -> m2:context-engineering
m2:context-engineering -> m2:prompt-caching
M1:structured-outputs -> m2:structured-generation
m2:prompt-injection-defense -> M3:agent-security
m2:context-engineering -> M3:agent-memory
# Track B
m2:embeddings -> m2:rag-fundamentals
m2:rag-fundamentals -> m2:chunking-strategies
m2:rag-fundamentals -> m2:vector-databases
m2:rag-fundamentals -> m2:hybrid-search
m2:hybrid-search -> m2:reranking
m2:rag-fundamentals -> m2:advanced-rag
m2:advanced-rag -> m2:graphrag
m2:advanced-rag -> m2:agentic-rag
m2:advanced-rag -> m2:multimodal-rag
m2:rag-fundamentals -> m2:rag-evaluation
M1:embedding-models -> m2:embeddings
M1:chunking-for-rag -> m2:chunking-strategies
M1:qa -> m2:rag-fundamentals
m2:agentic-rag -> M3:agentic-systems
# Track C
m2:structured-outputs -> m2:function-calling
m2:function-calling -> m2:mcp
m2:function-calling -> m2:langgraph
m2:langgraph -> m2:agent-framework-tradeoffs
m2:function-calling -> m2:production-llm-app
m2:rag-fundamentals -> m2:production-llm-app
m2:guardrails -> m2:production-llm-app
M1:ts-generics -> m2:function-calling
m2:function-calling -> M3:agent-engineering
m2:mcp -> M3:agent-engineering
m2:langgraph -> M3:orchestration
# Track D
M1:nli -> m2:llm-as-judge
m2:llm-as-judge -> m2:rag-evaluation
m2:rag-evaluation -> m2:multi-step-eval
m2:observability-setup -> m2:error-analysis
m2:error-analysis -> m2:judge-design
m2:judge-design -> m2:statistical-correction
m2:rag-evaluation -> M3:agent-eval
m2:llm-as-judge -> M5:production-monitoring
# Track E (antilibrary candidate)
m2:gen-taxonomy -> m2:vae
m2:vae -> m2:gan
m2:gan -> m2:diffusion
m2:diffusion -> m2:latent-diffusion
m2:latent-diffusion -> m2:controlnet-lora
```
