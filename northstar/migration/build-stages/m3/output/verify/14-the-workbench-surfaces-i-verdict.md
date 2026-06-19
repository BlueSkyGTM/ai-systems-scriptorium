# Verdict: 14-the-workbench-surfaces-i

## Markers resolved (4 / 4 — RESOLVED)

| # | Original query | Resolution | URL |
|---|----------------|-----------|-----|
| 1 | Azure AI Foundry Agent Service — capability manifest and per-agent rule enforcement for task adherence | Resolved. Grounded in Azure AI Foundry **Task Adherence** (Content Safety / Foundry Guardrails) — detects misaligned tool invocations as the runtime analogue of the rule ledger. | https://learn.microsoft.com/azure/ai-services/content-safety/concepts/task-adherence |
| 2 | Azure DevOps Pipelines — publishing structured JSON artifacts as pipeline stage outputs for cross-session state continuity | Resolved. Grounded in **PublishPipelineArtifact@1** / pipeline artifacts docs — later stages download exactly what an earlier stage published. | https://learn.microsoft.com/azure/devops/pipelines/artifacts/pipeline-artifacts?view=azure-devops |
| 3 | Azure AI — access patterns and scope-by-tool permission controls for AI agents acting on files and APIs | Resolved. Grounded in Azure Security Benchmark **AI-4: Apply least privilege for agent functions** — capability manifest, RBAC, scoped tokens, audit trail. | https://learn.microsoft.com/security/benchmark/azure/mcsb-v2-artificial-intelligence-security#ai-4-apply-least-privilege-for-agent-functions |
| 4 | Azure DevOps — publishing test results and exit codes as pipeline artifacts for cross-step fact verification | Resolved. Grounded in **Publish Pipeline Artifacts** + **Deployment gates** — downstream stages read the feedback log before advancing. | https://learn.microsoft.com/azure/devops/pipelines/release/approvals/gates?view=azure-devops |

## Source-verify fix

**"A 3000-line manual gets ignored; a 12-line router gets followed"** — false precision. Rewrote body sentence and Core concepts bullet to: *"A long manual no one reads; a short router they actually follow"* and *"outperform a long manual"* respectively. Rhetorical punch preserved; unsupported counts removed.

## New ending

Lesson 14 ends with the thread/handoff paragraph and Core concepts — no seam line. The §4 "An AI Platform Engineer who…" ban does NOT apply here (no seam line present). No rewrite needed.

## STYLE conformance

- **§1 Unity:** second person throughout, present tense, practitioner POV — PASS
- **§2 Simplicity:** no qualifiers, no passive constructions, active verbs — PASS
- **§3 One idea:** the lesson teaches one concept (the four workbench surfaces) — PASS
- **§4 Lead/ending:** lead grabs (model fails on the work, not the language) — PASS; no banned template ending present — PASS
- **§5 Core concepts:** four propositions, one line each — PASS
- **§7 Zinsser pass:** MS-Learn grounding clauses are light (one sentence each, not vendor-pitch); no inflation language introduced — PASS
- **§8 Variety:** rhythm varies across sections; one earned aside ("A long manual no one reads; a short router they actually follow" is punchy, not robotic) — PASS

## VERDICT: PASS
