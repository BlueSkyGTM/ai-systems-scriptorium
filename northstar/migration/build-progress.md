# Authoring Progress

Live status of the lesson-authoring run (Handoff-2). Editor-in-chief = Opus; drafters = Sonnet subagents.
Resume from the first PENDING module. Each module: read `_dossier/moduleN.md` (keep/cut), the `src/moduleN/`
ingredients + `synthesis/source/moduleN/` depth, author finished lessons one-idea-each, self-Zinsser,
editor reviews against `STYLE.md`, update `src/SUMMARY.md`, remove superseded ingredient files.

## Status

| Module | Status | Lessons |
|--------|--------|---------|
| M1 Foundations | ✅ DONE | 01-dev-environment, 02-your-first-llm-call, 03-attention, 04-transformer-era-nlp, 05-retrieval-and-eval-foundations |
| M2 LLM Engineering | ✅ DONE | 01-prompt-engineering, 02-context-engineering, 03-rag-system, 04-advanced-rag, 05-evaluation, 06-structured-output-and-tools, 07-the-complexity-ladder |
| M3 Agent Foundations | ⬜ PENDING | reasoning-loops, tools-mcp, memory-state, frameworks-patterns, agent-workbench, typescript-entry |
| M4 Multi-Agent Systems | ⬜ PENDING | multi-agent-swarms, autonomous-safety, fleet-loop, computer-use-coding-voice |
| M5 Deploy & Perf | ⬜ PENDING | serving-inference, metrics-observability, ops-security-finops, perf-eng-depth, rust-entry |
| M6 Agent Artifacts | ⬜ PENDING | 4 artifacts (coding agent, RAG chatbot, voice, issue-to-PR) — apply M3, ship skill-*.md |
| M7 Multi-Agent Artifacts | ⬜ PENDING | 3 artifacts (research, K8s, governed fleet) — compose M6 agents |
| M8 Final Exam | ⬜ PENDING | M7 fleet builds the exam system; asdg Ch16 case studies as reference |

## Gotchas learned (save the next drafter time)

- **Model IDs:** the current Anthropic model is `claude-opus-4-8` (NOT 4-5). Verify any model ID / API shape
  via the `claude-api` skill, never from memory. First-call curl uses `anthropic-version: 2023-06-01`.
- **Numbering crosswalk:** `synthesis/source/moduleN/` uses OLD 5-module numbering; `src/moduleN/` + SUMMARY use
  NEW 8-module numbering. M3 source feeds new M3+M4; M5 source (capstone) feeds new M6+M7+M8. See `build/`... (now `MANIFEST` folded; the crosswalk lives in the dossiers + this note).
- **Voice anchors:** every drafter must read `STYLE.md` + `src/preface.md` + `src/README.md`. Em dashes are house style.
- **Granularity:** one idea per lesson; a chapter ingredient → 2–4 lessons (not 1 mega, not 12 atomic). Update SUMMARY to match; delete the ingredient file once its lessons are authored.
- **Threads to carry:** eval-driven development (M2→M5), versioning (M2/M5), safety distributed (M2/M3/M4/M5), complexity ladder (M2→M3).
- **mdbook** is not installed here; verify by checking SUMMARY links resolve to real files.
- **MS-Learn markers:** drafters insert `[MS-Learn: ...]` where a production pattern needs validation; the editor resolves them before the lesson ships (don't leave them in student-facing text).

## Follow-up polish (non-blocking)

- ✅ **RESOLVED (2026-06-19) — M2 retroactive VERIFY ran** (`build-stages/m2/output/verify/SUMMARY.md`). All 7
  lessons full-read against STYLE; ~94 cited claims source-verified against `synthesis/source/module2` (7
  NOT-FOUND, 0 contradictions); MLflow + API claims validated via MS Learn / `claude-api`; `mdbook build` clean.
- ✅ **RESOLVED (2026-06-19) — the assistant-prefill defect is fixed** in `02/01-prompt-engineering.md`. The
  hierarchy now describes the assistant tier as conversation history (lowest-trust), not a "prefill you can
  seed" (which 400s on Opus 4.6+/Fable). Also fixed: MLflow `shadow`→`staging` alias, the stale "Anthropic
  requires explicit cache_control" caching claim, and an unsourced Spearman ρ≥0.7 hard gate (reframed). See the
  verify report.
- **Module READMEs (Overview pages)** for M1/M2 were not re-read; confirm they don't still describe the old chapter structure.
- The top-level `northstar/CONTEXT.md` "AI Systems Engineering" / "LearnHouse" strings remain (flagged earlier; CONTEXT.md is archival).

## Directives (Ray) — honor in the build

- **Keep the ICM staged architecture. Do NOT remove the root scaffold (`setup/`, `stages/`, `references/`).**
  The staged / sequential / context-handoff pattern IS the intended agentic architecture for finishing the
  build. Sequence: intake (done) → quality check (current: autoplan + M1/M2 authoring sanity) → use ICM to
  define stages for the remaining work and execute them sequentially with clean per-stage `output/` handoffs.
  The M1/M2 authoring was a proto-stage to prove the loop; formalize the rest as ICM stages.
- **Projects must use the tools real AI engineers use.** M6/M7/M8 artifacts must be grounded in real
  platforms — Azure (AI Search, Azure OpenAI, AKS), Databricks (Vector Search, MLflow, agent framework),
  GitHub/CI, Pipecat/LiveKit, etc. — NOT generic toy abstractions. Bind each inherited artifact to a concrete
  platform at authoring time. The Microsoft Learn connector is the grounding source (Azure/Databricks are
  first-party there). Tool bindings are an open decision for the artifacts stage (see inherited list below).
- **Microsoft Learn connector is the designated gap-filler (verified working).** Tools:
  `microsoft_docs_search` / `microsoft_code_sample_search` / `microsoft_docs_fetch`. The editor resolves
  drafters' `[MS-Learn: …]` markers with it, and it grounds the Azure/Databricks artifact bindings (directive
  above). Per `REFERENCE-LAYER.md` its role in TEACHING lessons is structural validation + gap-fill, **not**
  vendor sourcing; the PROJECTS may use the real vendor platforms directly.
- **Verification is its own ICM stage (author → verify → ship).** The risk on this project is not slop; it is
  confident, well-written, subtly-WRONG content (proof: the M2 assistant-prefill claim that 400s on current
  Anthropic models — it shipped because MS-Learn validation was skipped and review was 1-of-7). Do not fold
  verification into authoring. Each module's verify stage gates "ship" and MUST: (a) **source-verify** every
  cited number/claim against `synthesis/source/` — it traces or it gets cut/flagged; (b) **validate**
  production/technical/API claims against Microsoft Learn via the connector (the three-source rule's source #2,
  skipped in M2 — confidence is not validation; zero `[MS-Learn]` markers is a smell, not a pass); (c)
  **full-read** every lesson against `STYLE.md` (no structural-sweep-only passes like M2 got); (d) **build it
  for real** — install + run `mdbook build` and sanity-check exercises ("links resolve" is not "renders and
  works").

## M3 stage — plan locked (2026-06-19, via `/autoplan`)

Stage breakdown decided with Ray (directive #1). The reviewable plan + full audit trail live in
`build-stages/m3/PLAN.md → GSTACK REVIEW REPORT`. Six voices (CEO/Eng/DX × Claude subagent + Codex gpt-5.5).

- **Granularity: Hybrid 15 lessons** (locked). Split by buildability, NOT mechanically: Reasoning & Loops 3 ·
  TypeScript 2 (moved BEFORE Tools & MCP — fixes an order inversion) · Tools & MCP 4 · Memory & State 2 ·
  Frameworks & Patterns 2 · Agent Workbench 2. Every lesson gets one checkable exercise. Lessons labelled
  Build / Decision / Vocabulary.
- **M1/M2 are NOT reconciled now.** Their chapter-grain (5 and 7 lessons) is under-verified precedent, not the
  standard. Reconcile after M3 proves the lesson unit; fix only the known M2 prefill defect first.
- **15 hardening items ACCEPTED** (audit trail in PLAN.md). Highlights: VERIFY becomes artifact-enforced
  (`output/verify/<lesson>-verdict.md` claim ledger required before SHIP); claim ledger covers ALL non-obvious
  claims, not just numbers; claim-authority map (primary specs/papers for MCP/ReAct/Letta/etc., MS Learn for
  Azure/Databricks); ≥1 logged MS-Learn validation per technical lesson; drafter file-exclusion rule (never
  glob `synthesis/source/module3/` — fleet-*/loop-* are M4); catalog `asdg-module3-tool-use-computer-agents.md`
  in the dossier; install mdbook; complexity ladder opens lesson 1; throughline artifact `module3-agent/` +
  named `agent-workbench-pack/` that M6 imports; workbench scripts stay Python while new tool/MCP examples are
  TypeScript; `build-stages/m3/dependencies.md` (SUMMARY must be a topological sort); deferred-topic audit.
- **ICM = verification boundary + audit trail**, not management ceremony (cut excess per-subagent scaffolding).
- **Sequence:** M2 VERIFY (first) → M3 AUTHOR → M3 VERIFY → M3 SHIP → continue M4→M8.
