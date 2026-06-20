# Step 3 — Resolutions

The taste calls the snapshot surfaced, resolved against the thesis (SPEC.md). Cuts are **antilibrary**
(held, documented, not deleted). Resolved independently 2026-06-18; Ray can reverse any.

---

## 1. The Optimize ruling (keystone)

**Question:** model-training-from-scratch and frontier-safety research/policy — in-seam or antilibrary?

**Principle (from SPEC.md):** AI Platform Engineering is *infrastructure-centric* — it builds, serves,
operates, and governs the platform that runs models. It is **not** the Optimize archetype (training
models at scale, Python-native, the depth layer reached last). "Performance engineering > machine
learning." The platform engineer owns the *fine-tune-vs-prompt decision* and *operating models safely*,
not the *training implementation* or *frontier-safety policy*.

**Ruling — keep decisional/operational literacy; antilibrary the implementation-depth and the research survey:**

| Material | Verdict | Why |
|----------|---------|-----|
| Fine-tune vs prompt **decision** (when/why) | **KEEP** (in-seam) | a platform decision the engineer owns |
| Transformer forward-pass **literacy** (M1 attention) | **KEEP** | one conceptual lesson, enough to read what's under the hood |
| GPT-from-scratch build (M5 Part 2, 30–49) | **ANTILIBRARY** | Optimize depth — building a model, not a platform |
| Distributed training from scratch (M5 Part 2, 76–81: DDP/ZeRO/pipeline) | **ANTILIBRARY** | the sharpest cut — model-training-at-scale engineering |
| Fine-tuning pipeline artifact (07) | **ANTILIBRARY / Deploy** | executing the train, not deciding it |
| aipe training/CUDA chapters (M5 Deploy, ch01–14) | **ANTILIBRARY** (already) | consistent — perf-eng scoped to *inference* serving |
| Operational agent safety: guardrails, kill switches, circuit breakers, budgets, HITL, checkpoints/rollback, sandboxing, prompt-injection defense, the safety gate (Part 2 82–87) | **KEEP** (in-seam) | *operating* agents safely = platform engineering |
| Frontier-safety **policy/research**: RSP v3, OpenAI PF, DeepMind FSF, METR, RSI theory, self-improvement research (STaR/AlphaEvolve/DGM/AI-Scientist), CAIS/CAISI | **ANTILIBRARY** | AI-safety-researcher / policy-analyst material, not platform-build |

**Throughline:** the platform engineer builds and operates the platform; they don't train the models
or set frontier-safety policy. Keep the decisions and the operations; antilibrary the training
implementation and the research survey.

---

## 2. Generative media (M2 Track E) — CONFIRM CUT

**ANTILIBRARY.** ~90% off-seam by the source's own flags (GANs, diffusion, video, audio, 3D, VAR).
Generative *media* is model-building, off-seam and consistent with the Optimize ruling. Keep only:
the LoRA/conditioning concept (taught once where adaptation is discussed) and FID/CLIP as a generic
eval reference if a lesson needs it. Everything else → antilibrary.

## 3. RAG dedup (M1 + M2 ×2) — MERGE, not cut

Curation, not loss. One progression:
- **M1 (NLP foundations):** introduces the *components* — embeddings, information retrieval, chunking — as transformer-era NLP.
- **M2 (LLM Engineering):** builds the *RAG system*. **`asdg` Ch06 = the canonical spine** (deepest, 14 sections: fundamentals → chunking → vector DBs → hybrid → rerank → graphRAG → agentic → eval → production). **`aefs` Ph11 RAG = the hands-on build-track** layered onto it.
- No triple-teach: M1 = components, M2 = system. The three sources collapse into one ordered path.

## 4. MCP dedup (×4) — ONE SPINE

**`aefs` Ph13 (23 lessons) = the canonical MCP spine** (fundamentals → server → client → transports →
resources/prompts → sampling → roots/elicitation → async → apps → security → OAuth → gateways/registries).
`asdg` Ch17, `asdg` Ch07.03, and the `aefs` Ph14 tool lessons fold in as lighter references. One MCP
spine in **Agent Foundations**.

## 5. Track H placement (computer-use / coding / voice agents) — RESOLVED

Not a teaching track of its own. Thin *teaching* (how each works) lands in **Multi-Agent Systems** as
advanced single-agent applications; the heavy *realization* lives in the **Artifacts** they seed
(coding agent → Agent Artifact 01; voice → Agent Artifact 03). Teach light, prove in the artifact.

---

## What's left (fresh-context work)

- ✅ **Step 2 — roadmap.sh audit:** DONE 2026-06-18 (`step2-flow-audit.md`). PASS, no backward-ordering violations.
- ✅ **8-module renumber:** DONE 2026-06-18. SYLLABUS.md restructured (old M3 split → M3 Agent Foundations + M4 Multi-Agent Systems; Deploy→M5; capstones→M6/M7/M8); snapshot cross-refs renumbered; these antilibrary rulings folded into SYLLABUS.md; artifacts-plan reconciled to own-module + compounding.
- **Step 4 — `build/CONTEXT.md`:** the lesson-authoring spec, against the validated, renumbered structure. Still to write.
