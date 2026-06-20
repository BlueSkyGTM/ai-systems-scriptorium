# Module 2 — Migration Dossier

Source: `../sub-repos/synthesis/source/module2/`. The densest, most-overlapped module — curation here is
**dedup/merge**, not resequencing.

## Source files in

| Source file | Verdict | Destination / note |
|-------------|---------|--------------------|
| `aefs-module2-llm-engineering.md` (Ph11, 17 lessons) | **KEEP** (most) | The Build-track core → split across all 4 M2 chapters. Exceptions below. |
| `asdg-module2-prompting-context.md` (Ch05, 8 sections) | **KEEP** | Production depth over Ph11 prompting → `src/module2/01`. |
| `asdg-module2-retrieval-systems.md` (Ch06, 14 sections) | **KEEP — canonical RAG spine** | → `src/module2/02`. The deepest RAG treatment in the stack. |
| `asdg-module2-eval-guides.md` (2 guides ×16 ch) | **KEEP — eval reference** | → `src/module2/03`. The eval deep-dive (LangWatch/Phoenix + Langfuse). |
| `aefs-module2-generative-ai.md` (Ph08) | **CUT → antilibrary** | Generative media (GANs/diffusion/video/audio/3D). Off-seam model-building. Keep only the LoRA/conditioning *concept* where adaptation is discussed. |

## Merges (the big dedup job — collapse to one spine each)

- **RAG (triple coverage → one spine):** M1 NLP taught the *components* (QA/IR/embeddings/chunking); M2 builds
  the *system*. **`asdg` Ch06 = canonical spine** (14 sections: fundamentals → chunking → vector DBs →
  hybrid → rerank → graphRAG → agentic → eval → production); **`aefs` Ph11 lessons 04/06/07 = the hands-on
  build-track** layered on. No triple-teach.
- **Prompting:** `aefs` Ph11 (01 prompt-eng, 02 CoT/ToT, 05 context-eng) + `asdg` Ch05 (8 sections) →
  dedup; asdg supplies production depth (instruction hierarchy, context rot, RAD).
- **Eval:** `aefs` Ph11 (10) + the two `asdg` eval guides + M1 (21 NLI, 27 RAGAS, 28 long-context) → one
  eval-driven-development thread; the guides are the reference depth.
- **Structured output:** `aefs` Ph11 (03) + `asdg` Ch05 (06) → one treatment; backbone of M3 tool calls.

## Threaded / forward-pointers

- **MCP intro only.** `aefs` Ph11 (14) introduces MCP; the **deep MCP spine is M3** (`aefs` Ph13). M2 = the
  on-ramp lesson, not the protocol deep-dive.
- **Fine-tune-vs-prompt:** `aefs` Ph11 (08, LoRA/QLoRA) — keep the **decision** (when/why to fine-tune) in
  M2; the LoRA/QLoRA **implementation depth** → antilibrary (Optimize ruling, [[optimize-archetype-ruling]]).
- **Function calling / LangGraph / framework tradeoffs** (09/16/17) → the M2→M3 seam (agent on-ramp).

## Threads named (binding gaps)

- `[THREAD: eval]` (Gap 1) — originates M1, concentrated here, runs to M5.
- `[THREAD: versioning]` (Gap 3) — prompt versioning introduced here (DSPy, MLflow prompt registry).
- `[THREAD: safety]` (Gap 4) — guardrails/injection defense (Ph11 12, Ch05 08) → safety evals.
- **Complexity ladder (Gap 2)** — the bridge section closing M2 / opening M3.

## Accounted-for check

5 source files: 4 kept (1 as the RAG spine), 1 cut. MCP deep-dive deferred to M3; LoRA impl → antilibrary;
generative media → antilibrary. Nothing uncatalogued.
