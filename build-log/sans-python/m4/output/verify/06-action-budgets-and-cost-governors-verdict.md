# VERIFY verdict — Lesson 06: Action Budgets & Cost Governors

**Lesson:** `build-stages/m4/output/author/06-action-budgets-and-cost-governors.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch02 Op-Safety, safety-critical)
**Date:** 2026-06-19

## Markers resolved (2 of 2)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: Claude Code — max_turns / max_budget_usd run controls]` | WebSearch Claude Code docs + budget-control guides | **PASS → removed.** `--max-turns` caps agentic steps; `--max-budget-usd` is a hard spend ceiling; both are non-interactive/print-mode run controls; on breach the agent stops and returns a partial result. Reworded to use the CLI flag names and the stop-with-partial-result behavior. |
| `[MS-Learn: Azure AI / Agent governance — token quotas and budget controls]` | MS Learn connector: "Enforce token limits for models" (Foundry Control Plane), "Manage Azure OpenAI quota", "Model router for Azure AI Foundry" | **PASS → removed.** Foundry Control Plane enforces per-project TPM rate limits + total token quotas to "prevent runaway token consumption" / "cost control by capping aggregate usage"; model-router routes per prompt. Corrected overstated "per-agent budgets" → accurate "per-project token-per-minute rate limits and total token quotas" + model router. |

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Denial of Wallet: agent keeps reasoning/calling/billing because nothing was designed to stop it | Ph15 L13 verbatim ("an agent keeps reasoning/calling/billing because nothing was designed to stop it") | PASS |
| Pairs with durability (L05): durability keeps a run alive, budgets keep an alive run from bankrupting you | Ph15 L12+L13 thread; PLAN safety spine | PASS |
| One monthly cap catches a runaway only after the wallet is gone | Ph15 L13 verbatim ("a single monthly cap catches a runaway only after the wallet is gone") | PASS |
| Limit stack: `max_tokens`, iteration caps (`max_turns`), per-task token/$ budgets, per-tool caps, velocity limits, calendar caps | Ph15 L13 (full enumeration matches) | PASS |
| Velocity limit: >$50 in 10 min → cut | Ph15 L13 verbatim ("financial velocity limits (>$50 in 10 min → cut)") | PASS |
| Governor is deterministic code, not model judgment | Ph15 L13/L14 spine ("hard constitutional limits that do not bend") | PASS |
| Tiered model routing / prompt caching / context windowing are cost governance | Ph15 L13 verbatim ("tiered model routing, prompt caching, context windowing") | PASS |
| On breach, trip the kill switch / next action does not run (→ L07) | Ph15 L13 ("kill switch on breach"); de-dup rule defers mechanism to L07 | PASS |
| Same governor runs at fleet scale; fleet references, does not rebuild | PLAN de-dup rule (budgets defined L06–07, referenced at fleet scale) | PASS |
| `budget.py` code (per-task $, turns, velocity-window ledger) | Self-consistent illustrative control-plane code; matches narrative; no false API claims | PASS |

## STYLE result — PASS

- Single H1, present tense, 2nd person, one voice. ✓
- Seam lead: bug-that-keeps-billing problem + explicit cusp ("squarely the MLOps half of the seam… the platform engineer answers for the bill"). ✓
- One `## Core concepts` block, 4 testable propositions. ✓
- Handoff div well-formed. ✓
- Ending ("that gap, between comfortable and catastrophic, is the budget's entire job"): reframe shape, not the banned template; varied vs. siblings. ✓
- Acronyms: USD/$ standard; no unexpanded jargon introduced. ✓
- De-dup: kill-switch mechanism explicitly deferred to L07 ("that mechanism is the next lesson"); fleet-scale deferred with "define the governor once, here." ✓

## Antilibrary fence — PASS
No frontier-safety/policy material. ✓

## Overall verdict: **PASS** (2 markers resolved, 1 defect FIXED [overstated "per-agent budgets" corrected to per-project quotas], 0 FLAGGED). Ship-ready.
