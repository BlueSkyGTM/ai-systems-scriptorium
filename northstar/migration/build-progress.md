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
| M3 Agent Foundations | ✅ SHIPPED (15-lesson hybrid; first real `mdbook build` PASS 2026-06-19) | 01 agent-loop · 02 planning · 03 learning-from-failure · 04-05 typescript · 06-09 tools&mcp · 10-11 memory · 12-13 frameworks · 14-15 workbench — live in src/module3/; ship manifest in build-stages/m3/output/ship/ |
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

## Build pipeline — proven on M3 (the engine for M4–M8)

Module-as-stage ICM, run **AUTHOR → VERIFY → SHIP**. Opus = editor-in-chief / orchestrator / review gate;
Sonnet subagents do the work. Writing is treated as engineering: `STYLE.md` is the spec, lessons are compiled
against it, Opus is the type-checker (see memory `writing-is-engineering-delegate-to-sonnet`).

- **AUTHOR.** One Sonnet drafter per chapter-group. Each reads `STYLE.md` + voice anchors (`preface`/`README` +
  approved prior lessons) + the `_dossier/moduleN` ruling + its `src/moduleN` ingredient + the **single-agent
  source subset** (exclusion rule: open only the named source files, never glob the dir — keeps M4 `fleet-*` /
  `loop-*` out of M3, etc.). Drafts finished lessons + exercises to `output/author/`; inserts `[MS-Learn: …]`
  markers where a production pattern needs validation. Opus reviews each draft against STYLE (full-read the
  pilot chapter to lock the exemplar, then diff-review the fleet).
- **VERIFY (directive #4 hard gate) — run as code.** A Sonnet fleet (one subagent per chapter-group) runs
  `STYLE.md` as spec against the drafts: (a) **resolve every `[MS-Learn]` marker via the Microsoft Learn
  connector — the connector IS available inside subagents**, so marker-resolution scales to a fleet instead of
  bottlenecking on Opus (the key M3 unlock, "connector per agent"); (b) source-verify cited numbers/claims
  against `synthesis/source/moduleN`; (c) apply STYLE §8 (vary endings/rhythm, kill the template ending);
  (d) write a per-lesson `output/verify/<slug>-verdict.md`. Opus reviews via `git diff`, resolves anything the
  connector can't reach (non-Microsoft products → primary docs), and owns judgment calls. M3 caught real
  defects this way (wrong SDK shapes, a renamed package, an unverifiable GA date, an unsupported vendor claim).
- **SHIP.** Relocate `output/author/` → `src/moduleN/` and `output/author/exercises/` → `exercises/moduleN/`;
  rewrite `src/SUMMARY.md` + the module `README.md` to the real lesson list; delete superseded ingredient
  files; run `mdbook build` (the real "renders and works" gate); mark the module DONE; commit → `output/ship/`.

Throughput on M3: 15 lessons authored + verified via ~11 Sonnet subagent runs; Opus orchestrated + reviewed.
Commit each stage to GitHub as it lands. **Reuse this engine for M4–M8 — unchanged for prose (M4/M5),
extended with a code gate for the build-artifact modules (M6–M8); see the midway decisions below.**

## Midway review — locked (2026-06-19, via `/autoplan`)

Full report: `build-stages/midway-review.md → GSTACK REVIEW REPORT`. Six-voice review (CEO/Eng/DX × Claude +
Codex) at the M3→M4 line. Decisions with Ray:

- **Build order: module-sequential (M4 next).** Keep strict M4 → M5 → M6–M8; the "pull/artifact-first" reorder
  was considered and declined.
- **Artifact→platform binding altitude (directive #2 resolved): capability + one concrete stack + portable
  seam.** Bind each M6–M8 artifact to a production *capability* (retrieval index, model gateway, eval store,
  deploy target, tracing, secrets, CI, human gate), implement on ONE real stack (Azure/Databricks/Pipecat/
  LiveKit/GitHub), and name the portable interface so a swap is config. Not toy abstractions; not vendor lock.
- **VERIFY extends for code (M6–M8): AUTHOR → VERIFY → BUILD → TEST → SHIP.** `mdbook build` proves *renders*,
  not *runs*. Add a runnable gate before M6: `tsc --noEmit` / `cargo check` / mocked smoke tests; exercises
  ship runnable. (M4/M5 prose keep the existing gate.)
- **Claim-authority map for non-Microsoft platforms.** The MS Learn connector doesn't cover Pipecat/LiveKit/
  OpenHands/Databricks primary docs — VERIFY subagents resolve those via **WebFetch** (works inside subagents)
  against named primary-doc URLs; tag each platform claim `mslearn / vendor-doc / spec / repo-example /
  local-smoke / unverified-cut`.
- **Cloud-cred strategy for M6–M8 exercises:** dry-run-first (mocks/emulators/fake creds/`.env.example`/
  `plan`-only) + a local `done-when` fallback per artifact; live cloud is opt-in BYO-account + budget caps +
  teardown. Add `exercises/module6/_prereqs/CLOUD-SETUP.md`.
- **M4 gets its own `build-stages/m4/PLAN.md` before authoring:** lock a lesson count; dedupe the kill-switch/
  HITL threading (it lands in both the safety and fleet chapters); **split Ch03 Fleet & Loop** (11 source
  files) into Fleet + Loop drafter turns; write a POSITIVE inclusion list — the M3 exclusion rule INVERTS, M4
  needs all `synthesis/source/module3/fleet-*` + `loop-*` files. Seed `exercises/module4/_harness/` (2 stub
  agents + orchestrator) so safety lessons have a substrate to govern.
- **M5: one Rust bridge lesson** (rustup + hello + cargo) before the serving-layer Rust lessons.
- **M8: define the student's active role before M6** ("M7 fleet builds the exam" is an agentic run, not prose
  authoring — design what the learner specifies/reviews/gates, or it's a demo not an exam).
- **Sequence now:** M3 SHIP (unanimous — `src/module3/` still holds old stubs; run `mdbook build`, the first
  real build, which also validates M1/M2) → then M4 (author its PLAN first).

## Scope reframe + roadmap coverage (2026-06-19) — `build-stages/roadmap-coverage.md`

- **Reframe (Ray):** "AI Platform Engineer" is a *pinpointing reference*, not a hard scope wall. The real
  target is the **cusp of the AI Engineer ∪ MLOps roadmaps**; platform-engineering is the anchor (and what
  validated the perf-eng track). Judge coverage against *both* roadmaps' essentials, at the cusp.
- **Verdict (checked vs the live roadmap.sh node lists):** AI Engineer roadmap = **covered** (home turf).
  MLOps = the platform/deploy overlap (Docker/K8s/cloud/CI/observability) **covered** via M5 + artifacts; the
  data-platform + model-training halves stay the **conscious inference-platform de-emphasis**.
- **Decision:** fold in ONE MLOps-native gap — a **Docling-anchored data-ingestion / pipeline thread**. Keep
  deliberately light/out: IaC/Terraform, explicit experiment-tracking, a multimodal lesson, classic-ML
  training, edge-AI, Go, image-generation (antilibrary). 
- **New carried thread — data ingestion (Docling-anchored):** M2 RAG (light, on M1/M2 reconciliation) → M5
  (data-ingestion/pipeline lesson) → M6 RAG-chatbot artifact (deep: Docling ingestion layer; portable seam =
  `DoclingDocument`→chunks). **Docling** ([docling-project/docling], LF AI & Data, MIT) is the adopted
  ingestion stack and a real MCP-server example. Do NOT re-open shipped M2 / verified M3 for it now — it lands
  in the unwritten modules (M5/M6) and a later M2 reconciliation.
