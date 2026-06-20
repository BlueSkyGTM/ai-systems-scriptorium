# VERIFY verdict — Lesson 10: The Loop

**Lesson:** `build-stages/m4/output/author/10-the-loop.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch03 LOOP)
**Date:** 2026-06-19

## Markers resolved (2 of 2)

| Marker | Source checked | Result |
|---|---|---|
| `[MS-Learn: Foundry Agent Service — routines (trigger/action, run records, project-scoped governance)]` (line 65) | MS Learn connector: "Routines in Foundry Agent Service (preview)" + "Automate agents with routines (preview)" (learn.microsoft.com/azure/foundry/agents/concepts/routines, .../how-to/use-routines) | **PASS → removed.** Every claim confirmed, several verbatim. Minor wording tightened ("its configured model, tools, and identity"; arrow → "to"). |
| `[verify: loop-engineering stories — unattended CI sweeper runaway / L1-first graduation]` (line 59) | `loop-module3-loop-stories.md` — "Why We Killed Our CI Sweeper (After Day 4)" + "L1 → L2 Graduation" | **PASS → removed.** All numbers trace to source. |

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Foundry product feature is named *routines* | MS Learn "Routines in Foundry Agent Service (preview)" | PASS |
| routine = named automation rule, one trigger + one action (invoke one agent) | "A *routine* is a named automation rule that triggers an agent... the *trigger*... and what agent to invoke (the *action*)"; "one trigger and one action per routine" | PASS (verbatim framing) |
| trigger = cron schedule or one-shot timer | "two trigger types: `schedule` (cron) and `timer` (one-shot)" | PASS |
| platform queues invocation, runs agent, stores a run record to inspect later | "Foundry queues the invocation, runs the agent, and stores a run record you can inspect later" | PASS (verbatim) |
| Foundry creates run record, invokes agent w/ configured model+tools+identity, links run to trace | "Foundry creates a routine run record... invokes the configured agent endpoint... uses its configured model, instructions, tools, and identity... links the run to the agent response and trace details" | PASS |
| project-scoped governance built in | "Routines are scoped to a Foundry project... project governance model" | PASS |
| routine = one agent; many agents w/ branching + shared state = a workflow (different construct) | "When you need multiple actions, multiple agents, or conditional logic, create a workflow instead" | PASS (exact line) |
| CI-sweeper unattended, no budget caps, verifier in implementer's session, ~8M tokens, 11 bad PRs, 48h | stories: "consumed ~8M tokens in 48 hours and proposed 11 PRs... run entirely unattended with no budget caps and a verifier in the same session" | PASS |
| fix = L1 first, separate verifier, branch allowlist, daily budget | stories: "re-enabled it with strict report-only phases, separate verifiers, and a branch allowlist" | PASS |
| L1 Report / L2 Assisted / L3 Unattended ladder; climb, don't start at top | docs Readiness Levels table (L0–L3); anti-pattern #4 "L3 before L1 quality"; checklist "L1 report-only week one" | PASS |
| four-stage shape `trigger → action → verification → budget/kill-switch` | patterns source: "trigger -> action -> verification -> budget"; reference "trigger -> action -> verification -> budget/kill-switch" | PASS |
| no path from action to commit skips verify | anti-pattern #1; failure-mode "Verifier Theater" | PASS |

## STYLE result — PASS

- H1 single, present tense, second person, one confident voice throughout. ✓
- Seam lead (line 3): no throat-clearing; lands the AI-Engineer ∪ MLOps cusp. ✓
- One `## Core concepts` block, 4 testable propositions. ✓
- Handoff div present and well-formed (`data-exercise` set). ✓
- Ending (line 73): reframe + warning shape, not the banned "An AI Platform Engineer who…" template; varied vs. L11. ✓
- Acronyms (CI, PR, MCP, REJECT) standard or glossed. ✓
- Fixes applied: prose-level `→` converted to words ("L1 to L2"; "trigger to action"); shape-name arrows retained as defined notation.

## De-dup confirmation — PASS

- **Budget/kill-switch:** referenced to lessons 06–07, explicitly "referenced here, not redefined" / "you reference them, you do not rebuild them" (lines 23, 78). NOT re-taught. ✓
- **Verification gate:** referenced to M3 workbench lesson 15, "referenced, don't redefine" (lines 21, 78). NOT re-taught. ✓ ("lesson 15" = M3 workbench, matches PLAN line 72 phrasing — not M4 L15.)

## Overall verdict: **PASS** (2 markers resolved, 0 defects, 0 FLAGGED). Ship-ready.
