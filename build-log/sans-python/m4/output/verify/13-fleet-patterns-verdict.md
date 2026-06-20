# VERIFY verdict — L13 "Fleet Patterns & Governance-as-Code"

Lesson: `build-stages/m4/output/author/13-fleet-patterns.md` · Chapter: ch03 FLEET · Verifier: Sonnet VERIFY subagent

## Markers resolved (all removed → clean student-facing prose)

| Marker | Resolution |
|---|---|
| `[verify: … runaway delegation tree under a manager-only cap]` | CONFIRMED. `fleet-stories.md` L4-7: "12 sub-agent retries … 8× normal by 6am … sub-agents had no individual caps." Marker removed. |
| `[verify: … inbox bypass, the "just this once" DM approval]` | CONFIRMED. `fleet-stories.md` L9-12: on-call engineer approved a deploy by DM; review could not answer "evidenced by what?"; compliance flagged bypass; ban on DM approvals. Marker removed. |
| `[MS-Learn: Azure AI Foundry Agent Service — catalog, RBAC, budgets, approval gates as declared governance]` | CONFIRMED via connector. Rewritten to clean prose; RBAC expanded to "role-based access control (RBAC)"; redundant double-listing collapsed. |
| `[verify: PLAN.md — L13 capstone is the governed fleet M7 imports]` | CONFIRMED. PLAN.md L81: "The capstone (L13) packages a small governed fleet that M7 imports"; lesson-plan row 13: "Seeds the M7 fleet finale." Marker removed; M7 section kept. |

## Claim ledger (claim → source → verdict)

| Claim | Source | Verdict |
|---|---|---|
| Six patterns: team-registry, cross-agent-audit, fleet-budget-guard, hierarchical-delegation, shared-inbox-HITL, agent-clone-fork | patterns L4-32 (all six present) | PASS |
| Team-registry = registry index + per-agent manifest; carries 4 accountability clauses; human gate on prod-data/credential change | patterns L29-32 | PASS |
| Cross-agent-audit = single correlation ID across chain; read-only playbook querying time range / agent ID / principal / tool class | patterns L9-12 | PASS |
| Fleet-budget-guard = team total + per-agent attribution; admission control pauses scheduler; inbox approval to raise | patterns L14-17 | PASS |
| Runaway: 12 retries, 8× spend by morning, manager-only cap missed it | stories L4-7 | PASS |
| Hierarchical-delegation = typed JSON handoff packets (authority/constraints/evidence), report-only workers, human gate for promotion, conflict resolved at gate | patterns L19-22; templates `handoff-schema.json` L24-26 | PASS |
| Shared-inbox-HITL = one central inbox, `inbox_id` on every approval, no auto-execute of destructive tools, no off-channel approval | patterns L24-27 | PASS |
| Inbox bypass "just this once" DM; could not answer "evidenced by what?"; compliance flagged bypass | stories L9-12 | PASS |
| "An inbox nobody uses is worse than no inbox … false confidence" | stories L12 (verbatim sense) | PASS |
| Agent-clone-fork = tiered perms (can run / can clone / can edit); lineage `forked_from`/`owner`; human gate experimental→production | patterns L4-7; templates `fork-policy.md` L20-22 | PASS |
| Each pattern backed by a schema (JSON Schema registry+manifest, JSON handoff contract, structured audit record) | schemas L4-101; templates `handoff-schema.json`, `audit-runbook.md` | PASS |
| Governance-as-code: machine-readable artifacts validated in CI, diffed, versioned in git | reference L22-32 (Active Fleet Posture: registry.yaml + fleet-audit CI); PLAN throughline | PASS |
| Registry addressable — control plane reads contract (Claude Code now, local model later) | PLAN L79-81; reference (registry is what guards read against) | PASS |
| FleetBudgetGuard imports lesson-06 `TaskBudget`/`BudgetBreach` unchanged | PLAN dedup L68-69; code L31 | PASS — de-dup real |
| shared_inbox imports lesson-08 `propose`/`commit` unchanged | PLAN dedup L70-71; code L56 | PASS — de-dup real |
| Capstone = small governed fleet (registry/schemas/budget-guard/shared inbox); M7 imports it to wrap M6 coding agents | PLAN L81; row 13 | PASS |
| Azure AI Foundry Agent Service = managed instance: registry, Entra identity, RBAC, per-agent cost, approval gates | MS Learn connector | PASS (same evidence as L12 verdict) |

## STYLE result (PASS)
- H1 present: "# Fleet Patterns & Governance-as-Code".
- Seam lead: "The last lesson named the seven concerns … This one hands you the patterns" — functional, no throat-clearing.
- One `## Core concepts` block (4 propositions).
- Handoff `<div class="claude-handoff" data-exercise="…">` present and intact.
- Ending varies (reframe shape: "A fleet is not a bigger agent. It is a contract … one you can hand to the next system without rewriting a word"). No banned default opener.
- Acronyms: RBAC expanded to "role-based access control (RBAC)" at use; HITL appears only inside the source-derived pattern label "shared-inbox-HITL" (glossed in L12, the prior lesson). SWE = software engineering — domain-standard, used in PLAN's M7 framing; left as-is. JSON/YAML/CI/API audience-standard.
- Unity: second person, present tense, blunt voice — held.

## De-dup confirmation (REAL, import-level)
- **FleetBudgetGuard** (code block L29-48): `from governor.budget import TaskBudget, BudgetBreach   # reused, not redefined` — cap logic not retyped; fleet adds only attribution + team ceiling + admission control. Prose L50: "Define the governor once in lesson 06; the fleet inherits it." ✔
- **shared_inbox** (code block L54-65): `from hitl.propose import propose, commit   # the protocol, reused not re-taught` — commit gate is L08's unchanged; fleet adds queue, `inbox_id`, no-DM rule. Prose L69: "A fleet lesson that re-derives the propose-then-commit protocol has misunderstood the architecture." ✔
- Matches PLAN locked threading rule (L65-72): define once in L06/L08, reference at fleet scale in L13.

## M7-seeding confirmation
- `## This seeds the M7 finale` section present and KEPT (L86-92). States the L13 capstone (`module4-fleet/` package: registry, schemas, budget-guard, shared inbox) is imported by M7's governed multi-agent SWE-team finale to wrap the M6 coding agents — consistent with PLAN L81 and lesson-plan row 13. Nothing removed.

## Overall verdict: **PASS**
All 4 markers resolved to clean prose; every pattern, schema, governance rule, and story number traces to fleet-* source or PLAN. Both de-dups verified at the import line (L06 governor, L08 protocol). M7-seeding section preserved. MS Learn platform claim confirmed via connector. STYLE clean. Ships.
