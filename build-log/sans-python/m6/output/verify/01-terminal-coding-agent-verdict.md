# VERIFY verdict — 01 Terminal Coding Agent (build-guide chapter)

Artifact: `build-stages/m6/output/author/01-terminal-coding-agent.md`
Scaffold: `build-stages/m6/output/author/exercises/module6/01-terminal-coding-agent/`
Gate: AUTHOR → **VERIFY** (prose: claims + STYLE + guide-matches-scaffold). CODE already passed BUILD→TEST.
Verifier: Sonnet VERIFY subagent. Date: 2026-06-19.

## Markers resolved (all removed from student-facing prose)

| # | Marker (original) | Resolution | Source |
|---|---|---|---|
| 1 | `[verify: "settled architecture" framing — terminal harness + permissioned tool surface + sandbox + plan/act/observe loop]` | Confirmed against capstone §01 (`aefs-module5-capstone.md` Part 2, components 20–29). Reads as current. Marker deleted; prose unchanged in substance. | capstone source |
| 2 | `[verify: Claude Agent SDK — Messages API tool-use loop, `tool_use` block → `tool_result` until `stop_reason` end_turn]` | Confirmed. `claude-api` skill: Messages API tool-use loop — model emits `tool_use`, harness returns `tool_result`, loop ends when the model stops calling tools. Rewrote marker into clean prose. Scaffold `client_llm.py` implements exactly this. | claude-api skill |
| 3 | `[MS-Learn: Azure AI Foundry Agent Service exposes the same loop as Runs and Run Steps]` | Confirmed via MS Learn (Foundry Agent Service Transparency Note + function-calling docs): **Run** = activation that calls models/tools and appends messages; **Run Steps** = detailed list of steps (tool calls / messages). Loop polls `requires_action` → submit tool outputs → `in_progress` → `completed`. Folded into prose accurately. | MS Learn connector |
| 4 | `[verify: model IDs and per-MTok pricing]` | Confirmed. Current model `claude-opus-4-8` (matches build-progress gotcha; NOT hardcoded by me — verified via `claude-api`). Cheaper pass `claude-haiku-4-5`. Opus 4.8 pricing **$5 in / $25 out per MTok** — matches scaffold `client_llm.py` `_PRICE_IN_PER_MTOK=5.00`, `_PRICE_OUT_PER_MTOK=25.00`. Marker deleted. | claude-api skill |
| 5 | `[verify: 20–29 component list + each Builds/Artifact]` | Confirmed against capstone source lines 125–173. Components 20–29: Loop Contract / Tool Registry / JSON-RPC-over-stdio / Dispatcher / Plan-Execute / Verification Gates+Observation Budget / Sandbox Runner (denylist+path jail) / Eval Harness / Observability (OTel+Prometheus) / End-to-End agent. Marker deleted. | capstone source |
| 6 | `[verify: sandbox-as-dev-guardrail caveat — capstone §26]` | Confirmed. §26 = "Sandbox Runner with Denylist and Path Jail" returning structured `SandboxResult`. Rewrote into clean prose ("pairing the timeout with a denylist and a path jail"). | capstone source |

## Defects fixed

- **Component-range mislabel (build step 3).** Original "The dispatcher (22–23)" implied 22 was the dispatcher. Source: 22 = JSON-RPC-over-stdio wire format, 23 = dispatcher. Reworded to "The transport and dispatcher (22–23)" and added one sentence noting the scaffold collapses the wire format into an in-process registry — now both accurate and honest about the scaffold's simplification.
- All 6 markers removed; no markers remain in student-facing text (grep clean).

## Guide-matches-scaffold (confirmed)

- Build spine 20→29 maps to scaffold files: loop (`agent.py`), registry+dispatch (`tools/__init__.py`), plan/execute (mock plan in `mock_llm.py` advancing the loop), verify gate (`verify_gate.py`), sandbox (`sandbox.py`, subprocess + wall-clock timeout, no Docker), eval/trace (smoke trace + `tests/`).
- Three operator surfaces (cost ceiling / kill switch / verify gate) — `budget.py` (`Budget(max_usd, max_turns)`, breach stops before next action), `killswitch.py` (`KillSwitch.tripped()` read-only; `OperatorKillSwitch` holds write path), `verify_gate.py` (default REJECT, ACCEPT only on clean pass). Match exact.
- `## What you build` + handoff brief name `read_file`/`write_file`/`run_tests`, `smoke.py`, `.env` opt-in Anthropic, four operator-surface tests — all present in scaffold.
- claude-handoff div → `exercises/module6/01-terminal-coding-agent/` (correct exercise).
- BUILD→TEST claims re-run live: `python smoke.py` exit 0 (verified ACCEPT); `python -m pytest tests/` = **6 passed**. Guide's prose ("smoke run fixes the fixture, budget breach stops, kill switch halts, verify gate REJECTs a bad patch") accurately describes the suite.

## STYLE (full-read)

- H1 ✓ ("The Terminal Coding Agent"). Seam-framed lead ✓ (chatbot-vs-agent gap, first sentence pulls into second).
- Unity: 2nd person, present tense, confident voice — held start to end, including inserted prose. ✓
- `## What you build` ✓ · `## Core concepts` ✓ (4 propositions, in-voice).
- claude-handoff div present, correct exercise path. ✓
- Ending: "What M7 reuses" closes on a reframe ("the single agent you make verifiable today is the team member you can govern tomorrow") — not the banned "An AI Platform Engineer who…" template. ✓
- Acronyms: SDK / API used as house-standard unexpanded terms (consistent with shipped M3–M5). No new stacking issue.

## FLAGGED (non-blocking)

- None blocking. Note: the guide describes a "subprocess sandbox" as a dev-time guardrail; the scaffold's `sandbox.py` implements the timeout but the path-jail lives in `tools/_resolve` (not in `sandbox.py`). The guide's prose attributes the denylist/path-jail to "the capstone §26"; in this condensed scaffold the jail is in the tool dispatch layer, which is correct architecturally. Reader-accurate; no change needed.

## Verdict

**PASS.** All 6 markers resolved against authoritative sources and removed from student-facing prose; one component-label defect fixed; guide matches the scaffold (build spine, operator surfaces, file names, test count); STYLE holds. Claims are source-true (model id, pricing, Azure Run/Run-Steps mapping, capstone arc). Ready for SHIP.
