# Verdict: 13 — Design Patterns and Anti-Patterns

## Markers resolved

| Original marker | Status | URL |
|---|---|---|
| `[MS-Learn: Azure AI Foundry Agent Service — HITL interrupts, checkpointing, and human approval gates in hosted agent workflows]` | RESOLVED | https://learn.microsoft.com/agent-framework/workflows/human-in-the-loop |
| `[MS-Learn: Microsoft Agent Framework — workflow orchestration anti-patterns and termination conditions for multi-agent systems]` | RESOLVED | https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/#multi-agent-feature-mapping |
| `[MS-Learn: Azure AI Foundry — agent safety controls, cost limits, and observability for production agent workloads]` | RESOLVED | https://learn.microsoft.com/azure/foundry/agents/concepts/limits-quotas-regions |

**Markers resolved: 3 / Unresolved: 0**

Note on the second marker: MS Learn does not have a dedicated "anti-patterns" page for Agent Framework. The closest authoritative content is the migration guide's multi-agent feature mapping, which documents explicit termination knobs (`max_round_count`, `max_stall_count`, `max_reset_count`) for Magentic orchestrations — directly relevant to the Infinite Loop Risk anti-pattern. That content was woven in. The anti-pattern names (agent-everything, premature-multi-agent, framework-as-architecture) are editorial framings, not MS claims — left as written per task brief.

## Fixes applied

### (A) HITL marker resolved — grounding clause woven after Golden Set pattern
Replaced the bare marker with a concrete grounding sentence: `ctx.request_info()` pauses the workflow, emits a `RequestInfoEvent`, and pending requests persist in checkpoints across restarts. This is accurate per https://learn.microsoft.com/agent-framework/workflows/human-in-the-loop. The grounding follows the pattern catalog naturally, before the anti-patterns section.

### (A) Termination/anti-patterns marker resolved — specific knob names cited
Replaced the anti-patterns marker with a grounding sentence citing `max_round_count`, `max_stall_count`, `max_reset_count` from Agent Framework's Magentic orchestration. Placed after the Infinite Loop Risk anti-pattern — where it grounds the claim without interrupting the catalog.

### (A) Foundry limits marker resolved — concrete numbers cited
Replaced the bare marker with hard limits from the MS Learn quotas page: 128 tools per agent, 100,000 messages per thread, rate limits at the model deployment level. Placed after the artifact inspection section, before the seam line.

### (B) STYLE §4 — banned ending rewritten
- **Before:** "An AI Platform Engineer who can name the pattern, cite the tradeoff, and identify the anti-pattern in a live codebase is the person who prevents the expensive rewrite — not the one who triggers it."
- **After (new seam line):** "Pattern vocabulary and anti-pattern recognition are the same skill: both require knowing what a shape is called before you can argue about whether it belongs here."
- Shape: reframe. The old ending named a role; the new one names the insight — what the lesson's vocabulary actually does for you.

## STYLE conformance

- §1 Unity: second person and present tense throughout. No drift.
- §2 Simplicity: grounding clauses kept lean. No qualifiers introduced. Active voice on all new sentences.
- §3 One idea: lesson stays on patterns + anti-patterns vocabulary. MS-Learn grounding reinforces rather than adds topics.
- §4 Lead: unchanged and strong ("Architecture reviews and technical interviews…").
- §4 Ending: consequence-adjacent reframe. Different shape from lesson 12's ending (consequence about orchestrator placement). Not predictable from the first sentence.
- §8 Variety: the lesson already has good rhythm variation (short declaratives in the catalog, longer explanatory sentences in anti-patterns). No mechanical repetition introduced.
- §5 Core concepts: 4 propositions, unchanged. All testable, one sentence each.

## VERDICT: PASS
