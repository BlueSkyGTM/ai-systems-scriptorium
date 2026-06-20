# VERIFY verdict — L12 "The Fleet — Graduation to Governed Many"

Lesson: `build-stages/m4/output/author/12-the-fleet.md` · Chapter: ch03 FLEET · Verifier: Sonnet VERIFY subagent

## Markers resolved (all removed → clean student-facing prose)

| Marker | Resolution |
|---|---|
| `[verify: … 3-loop / 5-agent graduation threshold]` | CONFIRMED + softened. Source `fleet-reference.md` L70: "When a team runs 3+ loops or 5+ agents, graduate"; `fleet-patterns.md` L2: "3+ loops / 5+ agents". Reworded "the field has converged" → "fleet engineering names a specific one … a working heuristic, not a law of nature" (watch-item: present as heuristic, not universal law). |
| `[verify: … four-clause accountability test]` | CONFIRMED. `fleet-reference.md` L37: "Which agent/workflow did it, with what authority, against what task, evidenced by what?" Marker removed; prose unchanged. |
| `[verify: … shadow agents found in audit]` | CONFIRMED. `fleet-stories.md` L24-27: "8 'official' … 14 actually running … 6 shadow agents with shared API keys and no owner." Marker removed. |
| `[verify: … budget cap stopped a runaway, per-agent attribution missing]` | CONFIRMED. `fleet-stories.md` L4-7: "12 sub-agent retries … 8× normal by 6am … sub-agents had no individual caps." Marker removed. |
| `[verify: … AgentManifest, AgentRegistry; autonomy tiers F0–F3]` | CONFIRMED. `fleet-schemas.md` L4-101: AgentManifest with `autonomy_tier` enum `F0,F1,F2,F3`; AgentRegistry index. Marker removed. |
| `[MS-Learn: Azure AI Foundry Agent Service — agent catalog, identity, RBAC, governance]` | CONFIRMED via connector. Rewritten to clean prose naming the platform and expanding RBAC ("role-based access control"). |

## Claim ledger (claim → source → verdict)

| Claim | Source | Verdict |
|---|---|---|
| "Loops live inside fleets" | reference L63 | PASS |
| Fleet = registry + identity + permissions + inbox + audit + economics + kill switch | reference L66 (exact) | PASS |
| 3-loop/5-agent graduation threshold | reference L70; patterns L2 | FIXED (softened to heuristic) |
| Four-clause accountability test (which/authority/task/evidence) | reference L37 | PASS |
| DM-approval breaks the *evidence* clause | stories L9-12 | PASS |
| 8 official vs 14 running; 6 shadows shared API key, no owner | stories L24-27 | PASS |
| Seven concerns in order: registry→identity→permissions→inbox-HITL→audit→economics→kill switch | reference L66 (enumerated set) + patterns | PASS |
| Registry = machine-readable list; audit finds unlisted agents | patterns L29-32; stories L24 | PASS |
| Identity = stable ID + named owner | patterns L31; schemas L13-15 | PASS |
| Permissions = least privilege, the *authority* clause | patterns; schemas `permissions` object | PASS |
| Inbox-HITL = L08 propose-then-commit, one inbox | patterns L24-27; PLAN dedup L70 | PASS |
| Audit = correlation-ID evidence trail | patterns L9-12 | PASS |
| Economics = team total + per-agent attribution (L06 governor at scale) | patterns L14-17; PLAN dedup L68 | PASS |
| Runaway: 12 retries, 8× spend by 6 a.m., manager-only cap | stories L4-7 | PASS |
| Kill switch = control plane, operator-owned, agent cannot write | reference L77-82 (kill switch); L07 framing carried | PASS |
| Three of seven (inbox-HITL, economics, kill switch) reused from L06-08, not rebuilt | PLAN dedup L65-72 | PASS |
| AgentManifest + AgentRegistry ship as JSON Schema; F0-F3 tiers | schemas L28-101 | PASS |
| registry.yaml example fields (id/owner/autonomy_tier/status/permissions/budget_daily_tokens/human_gates/evidence) | schemas AgentManifest field set | PASS — internally consistent with schema |
| Audit scores team 32/100; names shadows | stories L25 | PASS |
| Four duplicate "weekly report" agents, different credentials | stories L20 | PASS |
| Azure AI Foundry Agent Service: catalog/registry, Entra identity, RBAC, per-agent cost, approval gates | MS Learn connector (agent-identity; manage-costs; HITL approval workflows) | PASS — see MS notes below |

## Microsoft Learn confirmation (connector)
- **Identity**: `learn.microsoft.com/azure/foundry/agents/concepts/agent-identity` — each agent gets a Microsoft Entra agent identity (service principal); admins inventory agents, apply policy, audit activity.
- **RBAC**: same page — "apply least-privilege access with Azure role-based access control (RBAC)"; per-agent role assignments.
- **Per-agent budgets/cost**: `azure/foundry/concepts/manage-costs` — per-agent estimated cost column; AI Gateway enforces "global token caps and quotas"; budget alerts. (Note: Azure OpenAI has alerts/automation, not hard auto-cutoff budgets — lesson wording "tracks per-agent cost and quota centrally / budgets configured centrally" is accurate and does not overclaim a hard cap.)
- **Approval gates**: `azure/foundry/how-to/develop/langchain-agents` HITL — "require approval before tool calls execute"; Copilot Studio AI approvals with human stages.
- **Naming note**: Foundry RBAC roles + product recently renamed (Azure AI Foundry → Microsoft Foundry). Lesson retains "Azure AI Foundry Agent Service," still a valid in-use product name during rollout. Accepted.

## STYLE result (PASS)
- H1 present: "# The Fleet — Graduation to Governed Many".
- Seam lead grabs (twelve agents / the four you forgot / audit) — no throat-clearing, no "In this lesson".
- One `## Core concepts` block (4 propositions, voice-consistent).
- Handoff `<div class="claude-handoff" data-exercise="…">` present and intact.
- Ending varies (warning/cost shape: "a fleet you merely operate is one you find out about during the incident"). Banned "An AI Platform Engineer who…" opener not used.
- Acronyms: added "(human-in-the-loop)" gloss at first **Inbox-HITL**; RBAC expanded to "role-based access control" in MS prose. JSON/YAML/API/CI left (audience-standard).
- Unity: second person, present tense, blunt voice — held throughout.

## De-dup + M7-seeding confirmation
- De-dup referenced correctly: seven-concerns section states inbox-HITL/economics/kill switch are the L06-08 single-agent controls "pointed at many agents, not rebuilt"; Core concepts repeats it. (L12 is the concept lesson; the import-level de-dup lives in L13.)
- M7 seeding: L12 frames the registry as the artifact a control plane reads (Claude Code now, local model later) and the handoff builds the governed registry — consistent with PLAN L81. No M7-seeding section to preserve in L12 (that lives in L13); nothing removed.

## Overall verdict: **PASS**
All 6 markers resolved to clean prose; every claim traces to fleet-* source or the MS Learn connector. One claim FIXED (threshold softened from "field consensus" to "heuristic"). No invented specifics; story numbers (8/14, 6 shadows, 32/100, 8×, four duplicates) all sourced. STYLE clean. Ships.
