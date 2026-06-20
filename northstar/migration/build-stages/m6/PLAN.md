# Module 6 — Agent Artifacts — Build Plan

Status: **PLAN LOCKED (2026-06-19)** by Opus. M6–M8 **apply** the teaching modules (M3/M4) — they build, they
don't introduce concepts. Pipeline extends to **AUTHOR → VERIFY → BUILD→TEST → SHIP** (the runnable code gate
begins here). Canonical build layer: `northstar/migration/`.

M6 ships **4 single-agent portfolio artifacts**, each: a build-guide chapter in `src/module6/` + a runnable
starter scaffold in `exercises/module6/`. Each solves a real business problem, hits the hireability **"strong
project" bar**, ships an `outputs/skill-*.md`, and becomes a node reused in M7. Built on the M3 **agent-workbench
pack** + the M5 **`module5-serving/`** platform.

## The 4 artifacts (capability + ONE stack + portable seam; dry-run-first)

| # / file | Artifact | Capability | Stack (one) | Portable seam | Dry-run (local) | Reused in M7 as |
|---|---|---|---|---|---|---|
| 01 `01-terminal-coding-agent.md` | Terminal coding agent | plan/act/observe + tools + sandbox + cost ceiling + verification gate | Claude Agent SDK (Python) + subprocess sandbox; Part-2 harness seq 20–29 on the M3 workbench pack | the tool/loop + verification interface (model-agnostic) | subprocess sandbox (no Docker), mock-LLM smoke, real Anthropic via `.env` | the **coder node** of the SWE team (10★) |
| 02 `02-production-rag-chatbot.md` | Production RAG chatbot (regulated vertical) | RAG + guardrails + citations + drift observability | Docling (M5) → Azure AI Search → Azure OpenAI/Anthropic + M4 guardrail + M5 OTel | retriever interface + `DoclingDocument`→chunks (swap Azure AI Search ↔ local FAISS/Chroma) | local vector store + sample corpus, mock-LLM smoke | the **knowledge/retrieval service** |
| 03 `03-realtime-voice-assistant.md` | Real-time voice assistant | streaming under a hard latency budget (VAD→STT→LLM→TTS, barge-in) | Pipecat (Python) | the pipeline stages (swap STT/TTS) | text-driven pipeline sim + mock STT/TTS, measure latency vs ~450–600 ms | the **human-interface channel** |
| 04 `04-issue-to-pr-agent.md` | Issue-to-PR autonomous agent | autonomous worker: issue→branch→fix→PR, scoped creds, in-sandbox CI verify | GitHub + GitHub Actions; the M4 loop (trigger→action→verify→budget/kill-switch) wrapping artifact 01 | the issue→PR loop + CI verification gate (git host swappable) | local git repo + mock CI (run tests as "CI"), real GitHub fork opt-in via scoped token; **never auto-merge** | the **autonomous-execution pattern** |

## M8 student-role — DEFINED NOW (locked before M6 design; per midway)
In M8 the M7 governed fleet builds the system; the **student is the operator + judge + architect-of-record**:
(1) frames the problem and picks the reference architecture (from the 20 `asdg` Ch16 case studies); (2)
configures and operates the fleet — **sets budgets, approves HITL gates, reviews the audit trail, holds the
kill-switch**; (3) judges output against an acceptance rubric (eval gates + the strong-project bar); (4)
intervenes on failure. **Consequence for M6/M7:** every artifact must expose the **operator surfaces** the
student will drive in M8 — budget config, an HITL gate, an audit log, a kill-switch, and an eval/acceptance
gate. Design the artifacts so those surfaces are real, not decorative. (Seeds `build-stages/m8/PLAN.md`.)

## The BUILD→TEST gate (new this module)
Each scaffold must pass, locally and offline, before SHIP:
- **Python:** imports clean + a `smoke` entry runs the artifact end-to-end on a fixture with a **mock LLM**
  (deterministic), exercising the operator surfaces (budget breach stops it; kill-switch halts; verify gate rejects a bad output).
- **TypeScript (if any tool/contract is TS):** `npx tsc --noEmit` clean.
- **No Docker / no cloud / no GPU** in the gate (subprocess sandbox; mocks; `.env.example` for opt-in real services).
- `cargo`/Rust not used in M6. The gate is run by the BUILD/TEST subagents and re-checked by Opus; `mdbook build` still runs at SHIP for the guides.

## "Strong project" bar (hireability — every artifact's done-when)
Deployed-or-locally-runnable (a real entry point, **not a notebook**) · README that frames the **business
problem** (not just code) · **evaluation** (metrics + ≥2 approaches compared where it fits) · **tests** (smoke +
operator-surface tests) · **versioned** (clean repo layout) · ships `outputs/skill-<artifact>.md`.

## Sources + claim-authority
1. `synthesis/source/module5/aefs-module5-capstone.md` (17 Part-1 capstones + Part-2 harness seq 20–29) — the
   build sequences. Artifact 01 also reuses the M3 workbench pack (`exercises/module3/15-…`, and
   `synthesis/raw/ai-engineering-from-scratch/phases/14-agent-engineering/42-agent-workbench-capstone/outputs/agent-workbench-pack`).
2. **MS Learn connector** for Azure (AI Search, Azure OpenAI, AKS, Key Vault) · **WebFetch** for non-MS
   (Claude Agent SDK, Pipecat, Docling, GitHub Actions, FAISS/Chroma). Mark every platform/API claim; resolve at VERIFY.
3. Reuse, don't reinvent: artifact 01 builds on M3 workbench pack; 02 on M5 Docling/serving; 03 on M4 ch15 voice; 04 on M4 loop + artifact 01.
4. **Do not read any path containing `skills/` or `gstack/`.**

## Cuts (antilibrary — log at SHIP)
GPT-from-scratch (capstone Part-2 30–49) + distributed-training (76–81) stay cut; application-internals
(research/multimodal/RAG internals 50–69) fold into the relevant artifact, not separate builds. (Already in `antilibrary.md` M6–M8 line — confirm at SHIP.)

## Execution model
Opus = editor-in-chief. One Sonnet drafter per artifact (writes the guide + the runnable scaffold + the
exercise README + `outputs/skill-*.md`). Then VERIFY fleet (claim/STYLE), then BUILD/TEST fleet (run each
scaffold's smoke + tsc), then SHIP. Also seed `exercises/module6/_prereqs/CLOUD-SETUP.md` (dry-run-first:
mocks/emulators/`.env.example`/plan-only + a local done-when per artifact).

## Done-when (per artifact)
A guide in `src/module6/`, a `src/SUMMARY.md` entry, a `## Core concepts`/`## What you build` block, a runnable
scaffold + exercise brief in `exercises/module6/<artifact>/` passing the BUILD→TEST gate, an `outputs/skill-*.md`,
a per-artifact VERIFY verdict + BUILD/TEST verdict, and `mdbook build` clean at SHIP.
