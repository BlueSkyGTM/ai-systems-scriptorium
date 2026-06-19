<!-- /autoplan restore point: ~/.gstack/projects/BlueSkyGTM-sans-python/main-autoplan-restore-20260619-104217.md -->
# Module 3 — Agent Foundations — Build Plan (autoplan input)

Status: **PLAN LOCKED (2026-06-19)** via `/autoplan` (6 voices). Granularity = **Hybrid 15
lessons** (see GSTACK REVIEW REPORT → recommended table). All 15 hardening items ACCEPTED.
M2 retroactive verification runs FIRST. Next: M2 VERIFY stage → then M3 AUTHOR → VERIFY → SHIP.
The canonical build layer is `northstar/migration/`. M3 turns the six `src/module3/*`
ingredient files into 15 finished mdBook lessons + Claude Code exercises, in the locked Style
Contract voice, under the AUTHOR → VERIFY → SHIP pipeline.

## Settled decisions (locked with Ray)

1. **ICM architecture = module-as-stage.** The M3–M8 build is a sequence of bounded ICM
   stages, one per module, executed in order M3 → M8. Each stage has its own
   `build-stages/mXX/CONTEXT.md`, reads the prior stage's `output/`, and writes its own
   `output/`. The root Workspace Builder scaffold (`setup/`, `stages/`, `references/`)
   stays untouched.
2. **Each module stage runs an internal AUTHOR → VERIFY → SHIP pipeline** with hard
   handoffs:
   - AUTHOR — Sonnet drafters produce lesson drafts + exercises → `output/author/`.
   - VERIFY — hard gate: source-verify every cited number against
     `synthesis/source/module3/`; validate production/API claims via the Microsoft Learn
     connector; full-read every lesson against `STYLE.md`; run `mdbook build` for real and
     sanity-check exercises → `output/verify/` (verdict per lesson: pass / fix / cut).
   - SHIP — editor lands approved lessons into `src/module3/`, updates `src/SUMMARY.md`,
     deletes superseded ingredient files, marks the module DONE in `build-progress.md`,
     commits + pushes → `output/ship/`.
3. **The pending M2 retroactive verification runs FIRST, before any M3 authoring.** It
   proves the VERIFY pipeline on known content and fixes a shipped defect: the
   `src/module2/01-prompt-engineering.md` "assistant prefill you can seed" claim, which
   returns HTTP 400 on current Anthropic models (Opus 4.6+/Fable). M2 verify = full-read
   all 7 lessons, source-verify their numbers, validate via Microsoft Learn, fix the
   prefill claim.

## Open decision (the one to pressure-test)

**M3 lesson granularity.** Two options:

- **A — Full one-idea split (~18 lessons).** Apply the authoring brief's rule "one idea
  per lesson; a chapter ingredient → 2–4 lessons." Produces ~18 lessons (table below).
  Matches `AUTHORING.md` + `STYLE.md` §3. Diverges from how M1/M2 actually shipped.
- **B — Chapter-grain (~6 lessons).** One lesson per chapter, as M1 (5 lessons) and M2
  (7 lessons) actually shipped. Fewer files, consistent with prior modules, but each
  lesson carries multiple ideas — against the one-idea rule.

The brief mandates A; M1/M2 precedent is B. The tension is real: the brief says
"chapter → 2–4 lessons; update SUMMARY to match," yet M1/M2 used chapter = one lesson.

## Proposed M3 split (option A)

| # | Chapter (ingredient) | Lessons (one idea each) | Kind |
|---|----------------------|--------------------------|------|
| 1 | Reasoning & Loops | agent loop (ReAct) · planning (ReWOO / plan-execute) · learning from failure (Reflexion + Self-Refine/CRITIC) · reasoning-as-search (ToT/LATS) + complexity-ladder governor | concept/build |
| 2 | Tools & MCP | tool use (typed contracts — TypeScript enters) · MCP fundamentals (server/client/transports, build a pair) · MCP capabilities (resources/prompts/sampling/elicitation) · MCP security & scale (poisoning/OAuth 2.1/gateways/A2A) | build |
| 3 | Memory & State | tiers + virtual context (MemGPT) · hybrid stores (Mem0: vector/KV/graph) · memory that improves (Letta sleep-time + Voyager skills + checkpointing) | concept |
| 4 | Frameworks & Patterns | the landscape · four primitives + selection guide · design patterns & anti-patterns | concept |
| 5 | The Agent Workbench | why a workbench + instructions/state · scope/feedback/verification · review/handoff + the `agent-workbench-pack/` capstone (seeds the M6 coding agent) | build |
| 6 | TypeScript (entry) | the break-in set (read/write typed TS, define a typed tool, run `tsc`) · typing the product layer (generics for `Tool<TInput,TOutput>`, interfaces for MCP contracts, `.d.ts`) | concept/build |

Total ≈ 18 lessons (4 + 4 + 3 + 3 + 3 + 2 = 19, with Reasoning & Loops collapsible to 3).

## Sources (three-source rule, non-negotiable)

1. Migration ingredient: `src/module3/<chapter>.md` (organized view) + full extraction depth
   at `synthesis/source/module3/*.md` (aefs Ph13/Ph14, asdg Ch07/08/09/15). NOTE: the
   `fleet-*` and `loop-*` files in that folder are M4's — leave them.
2. Microsoft Learn connector (`microsoft_docs_search` / `microsoft_code_sample_search` /
   `microsoft_docs_fetch`) — production-pattern validation + gap-fill. Resolve drafters'
   `[MS-Learn: …]` markers here. Zero markers in a draft is a smell, not a pass.
3. Editorial seam framing — "why does an AI Platform Engineer need this?" in every lead.

## Threads to carry

- **Complexity ladder** (Gap 2) — the M2→M3 governor; opens the module, tagged inline in
  Reasoning & Loops and Frameworks. Don't reach for an agent until the problem demands it.
- **Eval-driven development** — carried from M2.
- **Safety** — agent kill switches, human-in-the-loop (HITL), scope contracts.
- **TypeScript enters at M3**, at point-of-use (typed tools, MCP contracts). Authored in
  TypeScript, not Python, for the product-layer lessons.

## Numbering crosswalk (gotcha)

`synthesis/source/module3/` uses OLD numbering and feeds NEW M3 (single-agent) AND NEW M4
(multi-agent). For M3 pull ONLY the single-agent subset: aefs agent-engineering Ph14
(01–18, 31–42) + tools-protocols Ph13; asdg agentic-systems Ch07, memory-state Ch08,
frameworks-tools Ch09, design-patterns Ch15, tool-use-computer-agents (thin). Phases 15–16
(multi-agent) and benchmarks/computer-use/voice → M4.

## Execution model

Opus = editor-in-chief (orchestrator); Sonnet subagents draft. One drafter per
chapter-group. Every draft is reviewed against `STYLE.md` (full read) before it lands. No
worker draft ships unreviewed. The VERIFY gate runs before SUMMARY update / ingredient
deletion / DONE marking.

## Done-when (per lesson)

A file in `src/module3/`, a `src/SUMMARY.md` entry in prereq order, a `## Core concepts`
block (1–4 testable propositions), an exercise brief at
`exercises/module3/<slug>/README.md`, and `mdbook build` clean.

---

# GSTACK REVIEW REPORT

`/autoplan` (real gstack v1.58.3.0). Phases run: CEO + Eng + DX (Design skipped — no UI scope;
DX scope = 19 hits). Dual voices: Claude subagent + Codex (codex-cli 0.141.0, gpt-5.5) per phase.

## Granularity — six-voice verdicts

| Voice | Verdict | Count |
|-------|---------|-------|
| Claude CEO | B + split MCP/Workbench | ~10 |
| Codex CEO | A, capped (4/4/3/2/2/2) | 17 |
| Claude Eng | B + split MCP only | 7 |
| Codex Eng | Hybrid (split high-risk clusters) | 12 |
| Claude DX | A disciplined, TS moved early | 16 |
| Codex DX | Hybrid (~10 build + ~4 vocabulary bridges) | 14 |

**Consensus:** reject pure-B (6 overloaded survey chapters) and loose-A (18–19 over-atomized).
Median ≈ 13. Split by *buildability/density*, not mechanically. M1/M2 chapter-grain is
under-verified precedent (M2 got a 1-of-7 read), not the standard — do **not** reconcile M1/M2 now;
do it after M3 proves the lesson unit (fix only the known M2 prefill defect first).

## CEO consensus table

| Dimension | Claude | Codex | Consensus |
|---|---|---|---|
| Premises valid? | partial | partial | DISAGREE-on-framing — granularity premise (A vs B) is false binary |
| Right problem? | yes | yes | CONFIRMED |
| Scope calibration | B/~10 | A/17 | DISAGREE → taste (hybrid) |
| Alternatives explored? | no | no | CONFIRMED gap — hybrid never considered in plan |
| ICM worth it? | as audit trail | as verification boundary | CONFIRMED — keep gates, cut ceremony |
| M2-verify-first sound? | yes | yes (tightly scoped) | CONFIRMED |

## Eng consensus table

| Dimension | Claude | Codex | Consensus |
|---|---|---|---|
| Architecture sound? | mostly | inconsistent stage boundary | DISAGREE → fix artifact flow |
| "Test"/VERIFY sufficient? | no | no | CONFIRMED — gate is process- not artifact-enforced |
| mdbook gate runnable? | no (not installed) | n/a | CONFIRMED blocker |
| Source isolation? | no (M4 bleed) | no | CONFIRMED — need drafter exclusion list |
| Dossier complete? | no (1 uncatalogued file) | n/a | CONFIRMED |
| Dependency ordering? | linear-ok | needs DAG | DISAGREE → add dependencies.md |

## DX consensus table

| Dimension | Claude | Codex | Consensus |
|---|---|---|---|
| Granularity for learner? | A/16 | hybrid/14 | CONFIRMED finer-than-B |
| TS on-ramp position? | inverted | inverted | CONFIRMED — move TS before MCP |
| read→build loop holds? | only if 1 build/lesson | only with throughline artifact | CONFIRMED |
| MCP exercise buildable? | no (scope collapse) | no | CONFIRMED — split MCP |
| Workbench buildable? | no (7 surfaces) | no | CONFIRMED — split Workbench |
| Pacing labels? | concept/build too coarse | add Build/Decision/Vocabulary | CONFIRMED |

## Decision Audit Trail (auto-decided via the 6 principles)

| # | Phase | Decision | Class | Principle | Rationale |
|---|-------|----------|-------|-----------|-----------|
| 1 | DX | Move TypeScript break-in set to **before** the first Tools & MCP lesson | Mechanical | P5 explicit | TS is first needed in ch2; shipping it in ch6 is a dependency inversion. One right answer. |
| 2 | Eng | VERIFY becomes **artifact-enforced**: require `output/verify/<lesson>-verdict.md` (a claim ledger) before SHIP can run | Mechanical | P1 complete | Process-only gates failed in M2; the gate must be a file the SHIP step reads. |
| 3 | Eng | Claim ledger covers **all non-obvious technical/source/API claims**, not just cited numbers | Mechanical | P1 complete | A polished uncited assertion (the prefill class) bypasses a numbers-only check. |
| 4 | Eng | Add a **claim-authority map**: primary specs/papers/vendor docs for MCP/ReAct/Reflexion/MemGPT/Letta/BFCL/LangGraph; MS Learn where it is the production-platform source (Azure/Databricks) | Mechanical | P1 complete | MS Learn cannot validate every M3 claim; refines directives #3/#4b. |
| 5 | Eng | Require **≥1 logged MS-Learn validation per technical/build lesson** in `output/verify/`; zero = verify fail pending explanation | Mechanical | P1 complete | Operationalizes "zero markers is a smell." |
| 6 | Eng | Add an explicit **drafter file-exclusion rule**: load ONLY the single-agent subset; never glob `synthesis/source/module3/` (fleet-*/loop-* are M4) | Mechanical | P2 boil-lake | M4 contamination vector is live; 18 M4 files share the folder. |
| 7 | Eng | Catalog `asdg-module3-tool-use-computer-agents.md` in the dossier with a verdict (thin tool-use → M3, computer-use → M4 forward-pointer) | Mechanical | P4 DRY | Dossier's "nothing uncatalogued" is false. |
| 8 | Eng | Install **mdbook** as a VERIFY prerequisite (the real "renders and works" gate), not the SUMMARY-link fallback | Mechanical | P1 complete | Directive #4d calls the link-check insufficient. |
| 9 | CEO | Complexity ladder **opens lesson 1 as the framing**, not an inline tag | Mechanical | P5 explicit | M2/07 ends promising "M3 builds the single-agent rung"; needs a structural anchor. |
| 10 | DX | Name a **throughline artifact** `module3-agent/`; every lesson adds one capability; the `agent-workbench-pack/` is the named output M6 imports | Mechanical | P2/compounding | Prevents exercises fragmenting into unrelated mini-builds; makes M6 reuse real. |
| 11 | DX | Label each lesson **Build / Decision / Vocabulary**; every Vocabulary lesson keeps a small artifact-inspection task | Mechanical | P5 explicit | Pacing; protects the read→build loop. |
| 12 | Eng | Workbench surface scripts stay **Python** (pre-existing pack); new tool/MCP contract examples are **TypeScript** | Mechanical | P5 explicit | Resolves the TS-vs-Python ambiguity the "TS from M3" rule creates. |
| 13 | Eng | Add `build-stages/m3/dependencies.md`; SUMMARY order must be a **topological sort** of it before SHIP | Mechanical | P3 pragmatic | Thematic order ≠ dependency order (MCP-security depends on tool-use, etc.). |
| 14 | Eng | Add a **deferred-topic audit** (benchmarks/computer-use/voice/OTel/DSPy = mention/forward-pointer/cut, never taught deep) to VERIFY | Mechanical | P2 boil-lake | Prevents M4/M5 material leaking into M3. |
| 15 | CEO | Keep ICM as a **verification boundary + audit trail**; cut excess per-subagent handoff scaffolding and process docs longer than the decision they govern | Taste→action | P3 pragmatic | Models agree ICM earns its place as audit, not management theater. |

## Surfaced to the gate (NOT auto-decided)

**User challenge — granularity.** Ray framed A (~18) vs B (~6). All six voices reject both as framed
and recommend a **disciplined hybrid (~13–16)**, split by buildability. This is Ray's call.

**Recommended hybrid — 15 lessons (range 13–16), labelled:**

| # | Lesson | Chapter | Label |
|---|--------|---------|-------|
| 01 | The agent loop (ReAct) — opens with the complexity-ladder governor; ends in a running loop | Reasoning & Loops | Build |
| 02 | Planning: decouple plan from execution (ReWOO / Plan-and-Execute) | Reasoning & Loops | Decision |
| 03 | Learning from failure (Reflexion + Self-Refine/CRITIC; ToT/LATS as cost-gated coda) | Reasoning & Loops | Concept/Build |
| 04 | TypeScript break-in set (typed tool, `tsc`) | TypeScript | Build |
| 05 | Typing the product layer (generics, interfaces, `.d.ts`) | TypeScript | Build |
| 06 | Tool use (typed contracts, local tool first) | Tools & MCP | Build |
| 07 | MCP fundamentals (server/client/transports; build a pair) | Tools & MCP | Build |
| 08 | MCP capabilities (resources/prompts/sampling/elicitation) | Tools & MCP | Build/Decision |
| 09 | MCP security & scale (poisoning, OAuth 2.1, gateways, A2A) | Tools & MCP | Decision |
| 10 | Memory tiers & stores (L1–L3, MemGPT, Mem0 vector/KV/graph) | Memory & State | Concept/Build |
| 11 | Memory that improves (Letta sleep-time, Voyager skills, checkpoint/resume) | Memory & State | Vocabulary/Build |
| 12 | The four primitives & selection (one minimal LangGraph, reuse M2/07 task) | Frameworks & Patterns | Decision |
| 13 | Design patterns & anti-patterns | Frameworks & Patterns | Vocabulary |
| 14 | Agent Workbench I — instructions/state/scope/feedback | The Agent Workbench | Build |
| 15 | Agent Workbench II + capstone — verification/review/handoff, package `agent-workbench-pack/` | The Agent Workbench | Build |

Trim to 13 by merging 02+03 and 10+11; expand to 16 by splitting memory's hybrid stores out.

**Taste — ICM ceremony level** (audit-trail-only vs richer per-stage scaffolding). Recommendation:
audit-trail-only (decision #15).

