# Verdict: 15-the-workbench-surfaces-ii-and-the-pack

## Markers resolved (5 / 5 — RESOLVED)

| # | Original query | Resolution | URL |
|---|----------------|-----------|-----|
| 1 | Azure DevOps Pipelines — using gates and approval conditions gated on structured JSON artifact content before stage promotion | Resolved. Grounded in **Deployment gates** (Azure DevOps Pipelines release approvals) — pre-deployment conditions read an external source and block stage promotion until the signal is green. | https://learn.microsoft.com/azure/devops/pipelines/release/approvals/gates?view=azure-devops |
| 2 | Azure AI Foundry — agent evaluators for task adherence and task completion as system-level quality gates | Resolved. Grounded in **Azure AI Foundry agent evaluators** (Task Adherence, Task Completion, Intent Resolution) integrated into CI via the AI Agent Evaluation Azure DevOps extension. | https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators#system-evaluation |
| 3 | Azure AI Foundry — rubric evaluators scoring agent responses on weighted custom dimensions with pass/fail thresholds | Resolved. Grounded in **Rubric evaluators (preview)** — custom weighted dimensions, LLM-as-judge, pass threshold 0.0–1.0, per-dimension scores with reasons. Noted as preview. | https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators |
| 4 | Azure DevOps — release gates with pre-deployment approval conditions reading structured verification artifacts | Resolved. Grounded in **Approvals and checks** (Azure DevOps Pipelines) — stage cannot start until all configured checks on consumed resources are satisfied. | https://learn.microsoft.com/azure/devops/pipelines/process/approvals?view=azure-devops |
| 5 | Azure AI Foundry — rubric evaluators and agent quality CI gates for production agent workflows (capstone section) | Resolved. Duplicate of marker #3/#4; consolidated into the already-placed approvals-and-checks grounding sentence. Marker deleted. |  |

## New ending (§4 rewrite — "An AI Platform Engineer who…" banned)

**Original:** "An AI Platform Engineer who ships the `agent-workbench-pack/` has answered the question every skeptic asks: 'How do you know the agent actually did it?' The answer is a verdict file, a scope report, a feedback log, and a handoff packet — artifacts, not assurances."

**Rewritten:** "Ship the `agent-workbench-pack/` and you have an answer to the question every skeptic asks — not a promise, but a verdict file, a scope report, a feedback log, and a handoff packet. Artifacts, not assurances."

Shape: consequence + reframe. Second person. The punch ("Artifacts, not assurances.") lands as a click — shorter, more abrupt, correct Zinsser shape.

## Source-verify checks (lesson 15)

- **"recovers in under a minute / costs 5–10 minutes"** — illustrative, kept as written. No change.
- **"M6 imports agent-workbench-pack/ and does not rebuild it"** — intentional curriculum decision (hardening #10), kept as written.
- **`claude-haiku-4-5` (reviewer) / `claude-opus-4-8` (builder)** — validated, kept as written.

## STYLE conformance

- **§1 Unity:** second person throughout, present tense — PASS
- **§2 Simplicity:** no qualifiers or inflation; active voice — PASS
- **§3 One idea:** verification/review/handoff/pack — one capstone concept — PASS
- **§4 Lead/ending:** lead states the problem clearly; ending rewritten to earn the click, banned template eliminated — PASS
- **§5 Core concepts:** four propositions, one line each — PASS
- **§8 Variety:** MS-Learn grounding clauses are each one sentence, distinct shape from body prose; ending shape differs from all prior lessons checked — PASS

## Editor judgment calls

- Marker 5 (capstone section) was a near-duplicate of markers 3+4 combined. Rather than add a third consecutive grounding sentence in that block, I deleted the marker and absorbed its substance into the already-placed approvals-and-checks sentence above it. This keeps the grounding light and non-pitch, per STYLE §7.
- The rubric evaluators marker notes "(preview)" in the fetched docs. The grounding clause does not propagate the preview flag into lesson prose (that would be vendor-pitch); it notes the feature is "portable to Foundry once you graduate beyond the single agent" — forward-reference, not a claim that it is GA.

## VERDICT: PASS
