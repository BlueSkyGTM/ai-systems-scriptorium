# Module 5 — Prerequisite Snapshot

> **Renumber map (8-module, 2026-06-18). This module becomes the artifact + exam modules.** The 17
> capstones split by archetype: single-agent → **M6 Agent Artifacts**, multi-agent → **M7 Multi-Agent
> Artifacts**, the governed-fleet finale + exam → **M8**. The Part-2 harness build (20–29) feeds M6's
> coding-agent artifact (`m6:`). **Part-2 Track B (GPT-from-scratch 30–49) and distributed training
> (76–81) resolve to ANTILIBRARY** (`antilib:` prefix) per the Optimize ruling. Relocated Deploy
> capstones (inference server, observability, MCP governance) live in **M5**. Prose retains original
> numbering. See `step2-flow-audit.md` + `step3-resolutions.md`.

Module 5 is the **capstone / integration module** — it depends on everything and produces
nothing downstream except portfolio + career. Two parts: 17 end-to-end portfolio capstones
(Part 1) and a 68-component dependency-ordered build sequence (Part 2, lessons 20–87) that
constructs an agent harness, a GPT-from-scratch, a research agent, multimodal/RAG/eval, and a
safety stack piece by piece.

Source file: `aefs-module5-capstone` (Phase 19).

---

## Part 1 — End-to-End Capstones (17 projects)

Each is a self-contained portfolio build producing a deployable system + a skill artifact. They map cleanly onto the three archetypes and the seam:

- **Build-leaning:** terminal coding agent (01), RAG-over-codebase (02), voice assistant (03), multimodal doc QA (04), code migration (09), AI tutor (17).
- **Deploy-leaning (seam-dense):** production RAG for regulated vertical (08), observability+eval dashboard (11), speculative-decoding inference server (14), MCP server with registry+governance (13), issue-to-PR cloud agent (16).
- **Optimize-leaning:** end-to-end fine-tuning pipeline data→SFT→DPO→serve (07), constitutional safety harness + red-team (15).
- **Multi-agent / orchestration:** research agent (05), devops K8s agent (06), multi-agent SWE team (10).

These have **no internal prerequisite chain** — each is an independent integration. Their prerequisites point *backward* into every prior module.

---

## Part 2 — Coding-Agent Harness Build Sequence (lessons 20–87)

**The most explicit internal DAG in the entire library** — each lesson names the artifact downstream lessons depend on. Low internal audit risk; it's pre-sequenced.

### Track A — Agent harness (20–29)
```
harness-loop-contract(20) → tool-registry(21) → json-rpc-stdio(22) → dispatcher(23)
→ plan-execute-control(24) → verification-gates(25) → sandbox-runner(26)
→ eval-harness(27) → observability-otel(28) → end-to-end-coding-agent(29)
```

### Track B — GPT from scratch + training (30–49) — SEAM CHECK
```
bpe-tokenizer(30) → tokenized-dataset(31) → embeddings(32) → multi-head-attention(33)
→ transformer-block(34) → gpt-assembly(35) → training-loop(36) → load-pretrained(37)
→ classifier-finetune(38) → sft(39) → dpo(40) → eval-pipeline(41)
→ corpus-downloader(42) → hdf5-corpus(43) → lr-schedule(44) → grad-clip-mixed-precision(45)
→ grad-accumulation(46) → checkpoint-resume(47) → ddp-fsdp(48) → lm-eval-harness(49)
```
**Audit flag (major):** this track is model *training* — the **Optimize** archetype. It sits in tension with the thesis ("performance engineering > machine learning") and M4's deliberate cut of training/CUDA chapters to antilibrary. Two readings: (a) in-seam as "understand the transformer from the inside" (one-time literacy, like Python literacy), or (b) Optimize-archetype depth that belongs in antilibrary for an AI *Platform* Engineering track. **This is the single biggest seam question Module 5 raises** — surface at Step 3.

### Track C — Research agent (50–57), Multimodal (58–63), RAG (64–69+), Safety
Dependency-ordered sub-DAGs, each composing into an end-to-end demo. RAG track (64–69) re-implements chunking/hybrid/rerank/eval from scratch — overlaps M2 RAG (capstone-level rebuild, not new concept).

---

## Module 5 — flow observations (feed Step 2)

1. **Correctly terminal.** Depends on all prior modules; nothing depends on it. No backward-edge risk.
2. **Part 2 is self-sequenced** — the cleanest internal DAG in the library; trust its ordering.
3. **The GPT-from-scratch training track (30–48) is the Optimize archetype resurfacing** — and it's the mirror of M4's antilibrary'd training chapters. Northstar must decide once, consistently: is from-scratch model training in-seam literacy or out-of-seam Optimize depth? Whatever's decided in M4 (aipe ch01–14 cut) should apply here too, or the curriculum contradicts itself.
4. **RAG/eval/multimodal capstones re-build M2 concepts from scratch** — intentional capstone reinforcement, not duplication to cut.
5. Part 1 capstones are the **portfolio proof of the seam** — the Deploy-dense ones (08/11/13/14) are the strongest AI Platform Engineering signals.

## Edge list (machine-readable)
```
# Part 2 Track A (harness) — feeds M6 Agent Artifact 01 (terminal coding agent)
m6:harness-loop -> m6:tool-registry
m6:tool-registry -> m6:json-rpc-stdio
m6:json-rpc-stdio -> m6:dispatcher
m6:dispatcher -> m6:plan-execute
m6:plan-execute -> m6:verification-gates
m6:verification-gates -> m6:sandbox-runner
m6:sandbox-runner -> m6:eval-harness
m6:eval-harness -> m6:observability-otel
m6:observability-otel -> m6:e2e-coding-agent
# Part 2 Track B (GPT from scratch) — ANTILIBRARY (Optimize ruling, Step 3)
antilib:bpe-tokenizer -> antilib:tokenized-dataset
antilib:tokenized-dataset -> antilib:embeddings
antilib:embeddings -> antilib:multi-head-attention
antilib:multi-head-attention -> antilib:transformer-block
antilib:transformer-block -> antilib:gpt-assembly
antilib:gpt-assembly -> antilib:training-loop
antilib:training-loop -> antilib:sft
antilib:sft -> antilib:dpo
antilib:training-loop -> antilib:checkpoint-resume
antilib:checkpoint-resume -> antilib:ddp-fsdp   # distributed training 76-81, sharpest cut
# cross-module inbound (artifacts depend on all prior)
M1:attention -> antilib:multi-head-attention     # M1 keeps attention literacy; the build is antilibrary
M1:rust -> m6:harness-loop
M2:function-calling -> m6:e2e-coding-agent
M2:mcp -> M5:mcp-governance-artifact             # relocated Deploy capstone 13
M2:rag-fundamentals -> m6:production-rag-artifact # Agent Artifact 08
M4:orchestration-patterns -> m7:multi-agent-swe-team  # M7 finale (was M3:orchestration)
M4:multi-agent-primitives -> m7:research-agent        # M7 artifact 05 (was M3:multi-agent)
M5:serving-engines -> M5:inference-server-artifact    # relocated Deploy capstone 14 (internal M5)
M5:observability-stack -> M5:observability-artifact   # relocated Deploy capstone 11 (internal M5)
M5:finops -> m6:production-rag-artifact
```
