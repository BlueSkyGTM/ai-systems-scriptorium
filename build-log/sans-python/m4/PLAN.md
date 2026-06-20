# Module 4 — Multi-Agent Systems — Build Plan

Status: **PLAN LOCKED (2026-06-19)** by Opus per the midway-review decisions (`build-stages/midway-review.md`).
The midway `/autoplan` already reviewed the back-half engine and locked M4's open items (count, kill-switch/HITL
dedup, Ch03 Fleet/Loop split, positive inclusion list, `_harness/` starter). No separate autoplan gate — this
plan executes those rulings. Pipeline: **AUTHOR → VERIFY → SHIP** on the proven M3 engine. Canonical build
layer: `northstar/migration/`. M4 turns the four `src/module4/*` ingredient stubs into **15 finished lessons**
+ Claude Code exercises, in the locked Style Contract voice.

M4 is the seam's defining material — single agent → runs safely for hours → coordinates with many → governed
as a fleet. It is **denser and safety-critical**; the operational-safety load (kill switches, HITL, budgets)
is the spine, not a footnote.

## Locked lesson plan — 15 lessons (range 13–16), split by buildability/density

| # | Lesson | Chapter | Label | One idea |
|---|--------|---------|-------|----------|
| 01 | Why multi-agent — the single-agent ceiling | Multi-Agent & Swarms | Decision | Complexity ladder gates entry: more agents, not a bigger agent — and only past the single-agent ceiling. **Opens the module.** |
| 02 | Communication protocols (MCP / A2A / ACP / ANP) | Multi-Agent & Swarms | Build | The four-protocol stack + FIPA-ACL heritage; build a real wire-format agent↔agent handoff, not raw strings. |
| 03 | The four primitives & orchestration | Multi-Agent & Swarms | Build/Decision | Agent · Handoff · Shared-state · Orchestrator; supervisor-worker / swarm / hierarchical patterns. |
| 04 | Debate & multi-agent failure modes (MASFT) | Multi-Agent & Swarms | Concept | Society-of-Minds debate (sparse topology); the 14 MASFT failures — design flaws, not model limits. |
| 05 | Long-horizon agents & durable execution | Autonomous & Operational Safety | Build | The qualitative break; checkpoint/retry/replay; resume-by-`thread_id` (Temporal / LangGraph→Postgres / Durable Objects). |
| 06 | Action budgets & cost governors | Autonomous & Operational Safety | Build | Denial-of-Wallet defense; multi-timescale limits; tiered routing; kill-switch-on-breach. |
| 07 | Kill switches, circuit breakers, canary tokens | Autonomous & Operational Safety | Build | The control plane the agent reads-but-cannot-write; breaker states; honeypot credentials. |
| 08 | HITL propose-then-commit + checkpoints/rollback | Autonomous & Operational Safety | Build/Decision | Idempotency key + precondition + post-verify + rollback; rubber-stamp mitigation; EU AI Act Art. 14. |
| 09 | Guardrails: Constitutional AI & Llama Guard | Autonomous & Operational Safety | Concept/Decision | Four-tier priority; input/output classification; the honest caveat — classifiers are a *layer*, not a solution. |
| 10 | The loop — a single agent-system as governed infrastructure | Fleet & Loop (LOOP) | Build | `trigger → action → verification → budget/kill-switch`; the L1/L2/L3 autonomy ladder. |
| 11 | Loop patterns in practice | Fleet & Loop (LOOP) | Build | daily-triage / PR-babysitter / dependency-sweeper / CI-sweeper; worktrees, verifiers, registries-as-code. |
| 12 | The fleet — graduation to governed many | Fleet & Loop (FLEET) | Build/Concept | "Loops live inside fleets"; the 3-loop/5-agent threshold; `registry → identity → permissions → inbox-HITL → audit → economics → kill-switch`. |
| 13 | Fleet patterns & governance-as-code | Fleet & Loop (FLEET) | Build | team-registry / cross-agent-audit / fleet-budget-guard / hierarchical-delegation / shared-inbox-HITL; machine-readable registries+schemas. **Seeds the M7 fleet finale.** |
| 14 | Computer-use & coding agents (thin) | Computer-Use/Coding/Voice | Concept | Vision-based control + the untrusted-input contract; scaffolding matters (OpenHands CodeAct). **Seeds M6 artifact 01.** |
| 15 | Voice agents & benchmark literacy (thin) | Computer-Use/Coding/Voice | Concept | Pipecat/LiveKit latency budgets; SWE-bench/GAIA/WebArena/OSWorld — know what they don't measure. **Seeds M6 artifact 03.** |

Collapsible to 13: merge 04→03 (debate into orchestration) and 06→07 (budgets into kill-switches) if either reads
thin. Expandable to 16: split 13 (fleet economics/audit out). Drafters may merge **within a chapter** with a one-line
note in the verdict; never split beyond 16.

## Source map + POSITIVE inclusion list (the M3 exclusion rule INVERTS here)

`synthesis/source/module3/` uses OLD numbering and feeds BOTH new-M3 (single-agent, shipped) AND new-M4
(multi-agent). For M3 the fleet-*/loop-* files were **forbidden**; for M4 they are **required**. Drafters load
ONLY the files for their chapter:

| Chapter | INCLUDE (load these) | Scope note |
|---|---|---|
| 01 Multi-Agent | `aefs-module3-agent-engineering.md` (**Ph16** multi-agent §) · `asdg-module3-agentic-systems.md` (Ch07.04 multi-agent §) | multi-agent only; single-agent reasoning shipped in M3 |
| 02 Op-Safety | `aefs-module3-agent-engineering.md` (**Ph15 operational-safety half ONLY**) | research/policy half is **antilibrary** — do not pull (STaR, AlphaEvolve, DGM, RSP, FSF, METR, CAIS) |
| 03 LOOP | `loop-module3-loop-{docs,patterns,reference,skills,stories,templates}.md` (6) | the files M3 was forbidden to touch |
| 03 FLEET | `fleet-module3-fleet-{patterns,reference,schemas,stories,templates}.md` (5) | the seam core |
| 04 Thin | `asdg-module3-tool-use-computer-agents.md` (Ch17) · `aefs-module3-agent-engineering.md` (Ph14 19–22 thin) | teach light; the build is the M6 artifact |

**EXCLUDE (shipped in M3 — never load for M4):** `aefs-module3-tools-protocols.md`, `asdg-module3-design-patterns.md`,
`asdg-module3-frameworks-tools.md`, `asdg-module3-memory-state.md`, and the single-agent phases of
`aefs-module3-agent-engineering.md` (Ph13/Ph14 01–18,31–42). **Do not read any path containing `skills/` or `gstack/`.**

## Three-source rule (non-negotiable)
1. Migration ingredient: `src/module4/<chapter>.md` (organized) + the included `synthesis/source/module3/*` depth above.
2. **Claim-authority map** — primary source per claim class: MCP/A2A specs; MASFT, Reflexion, Society-of-Minds papers;
   **MS Learn connector** for Azure/Databricks/Agent-Framework production patterns (`RequestInfoEvent`, durable execution);
   **WebFetch** for non-MS platforms (Temporal, LangGraph, Cloudflare Durable Objects, Pipecat, LiveKit, OpenHands,
   Anthropic Constitutional AI, Meta Llama Guard, EU AI Act Art. 14). ≥1 logged authority check per technical lesson;
   zero markers in a draft is a smell, not a pass.
3. Editorial seam framing — "why does this sit at the AI-Engineer ∪ MLOps cusp?" in every lead (no template endings; STYLE §8).

## Kill-switch / HITL / verification de-dup (the locked threading rule)
These primitives appear in BOTH ch02 (single-agent operational safety) and ch03 (fleet governance). **Define once,
reference after:**
- **Kill switch / circuit breaker / budgets** — *defined* in L06–L07 (the primitive + how to build it). In L10/L12 they
  appear as the loop/fleet `…→ kill-switch` step: show them **at scale**, reference L06–L07, do not re-teach.
- **HITL** — *defined* in L08 (propose-then-commit, single-agent). In L13 the `shared-inbox-HITL` pattern **applies** it
  across a fleet: show the fleet inbox, reference L08, do not re-teach the commit protocol.
- **Verification gate** — carried from M3 workbench (lesson 15). In L10 it is the loop's `verification` step: reference, don't redefine.

## Throughline artifact + `_harness/` starter (DX decision)
M4's throughline is **`module4-fleet/`** — a governed multi-agent system built on top of `module3-agent/`. Each lesson
adds one governance capability (protocol → orchestration → budget → kill-switch → HITL → guardrail → loop wrapper →
fleet registry). To give the safety lessons something to govern from lesson 1, **seed `exercises/module4/_harness/`**
before authoring: two stub agents (reuse `module3-agent` as a worker; add a second role) + a Python orchestrator +
a JSON/YAML fleet-registry stub. Control plane = **Python**; registries/schemas = **JSON/YAML** (everything-as-code);
typed wire contracts reuse the M3 **TypeScript** MCP work where a format needs checking. The capstone (L13) packages a
small governed fleet that **M7** imports.

## Code gate (scope note)
M4 stays **AUTHOR → VERIFY → SHIP** (prose + exercise briefs + the `_harness/` starter). The runnable BUILD→TEST gate
(`tsc --noEmit` / `cargo check` / smoke-with-mocks) is locked for **M6–M8**, not M4. The `_harness/` starter is verified
by read for coherence, not run.

## Threads to carry
- **Complexity ladder** — gates multi-agent entry (L01) and fleet graduation (L12). Don't reach past the ceiling.
- **Safety** — the ch02 spine; threaded into ch03 at fleet scale. (M2 → M3 → **M4** → M5.)
- **Eval-driven / verification gate** — the loop's verification step (from M3 workbench).
- **Mixed-language** — Python control plane + JSON/YAML registries + TS contracts; MCP/A2A reuse M3.
- **NOT in M4:** the Docling data-ingestion thread (lands M5/M6); image/video multimodal (antilibrary).

## Execution model
Opus = editor-in-chief; Sonnet subagents draft, treating `STYLE.md` as the spec ("writing as code"). Drafter batching:
A = ch01 (L01–04), B = ch02 (L05–09, safety — review hardest), C = ch03 LOOP (L10–11), D = ch03 FLEET (L12–13),
E = ch04 (L14–15), plus the `_harness/` starter. VERIFY fleet: one verdict file per lesson in `output/verify/`,
each resolving its own authority markers via the connector + WebFetch. No draft ships unreviewed.

## Done-when (per lesson)
A file in `src/module4/`, a `src/SUMMARY.md` entry in topological (dependency) order, a `## Core concepts` block
(1–4 testable propositions), an exercise brief at `exercises/module4/<slug>/README.md` that extends `module4-fleet/`,
a per-lesson VERIFY verdict, and `mdbook build` clean at SHIP.
