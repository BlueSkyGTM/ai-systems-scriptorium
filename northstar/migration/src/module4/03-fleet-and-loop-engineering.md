# Fleet & Loop Engineering

> **Migrated from** `fleet-module3-*` (5 files: patterns, reference, schemas, stories, templates) +
> `loop-module3-*` (6 files: docs, patterns, reference, skills, stories, templates). **The strongest
> pure-seam material in the curriculum** — agent infrastructure and governance.

The relationship is the whole idea: **"Loops live inside fleets."** A loop graduates to a fleet at the
3-loop / 5-agent threshold. Both carry machine-readable registries and schemas — the everything-as-code
platform-engineering vocabulary applies directly.

## Loop (single agent-system operations)

The shape: **trigger → action → verification → budget / kill-switch.** Patterns (L1/L2/L3 autonomy,
worktrees, verifiers):
- daily-triage, PR-babysitter, dependency-sweeper, CI-sweeper, issue-triage.

A loop is one agent system run as governed infrastructure — the verification gate and budget/kill-switch are
non-negotiable, carried from Module 3's workbench and Module 4's operational safety.

## Fleet (3+ loops / 5+ agents governance)

The shape: **registry → identity → permissions → inbox-HITL → audit → economics → kill-switch.** Patterns:
- team-registry, cross-agent-audit, fleet-budget-guard, hierarchical-delegation, shared-inbox-HITL,
  agent-clone-fork.

This is the infrastructure-for-running-agents that *is* the seam — it matches platform-engineering's
golden-paths / IDP / everything-as-code framing, applied to a fleet of agents. The machine-readable
registries + schemas mean a fleet is addressable as code (pointed at by Claude Code today, local models
later).

## Why this is the seam's center

A fleet of agents run as governed infrastructure = AI Platform Engineering. This chapter is the direct
foundation of the **M7 governed-multi-agent-fleet finale** (artifact 10★) — the SWE team wrapped in the fleet
layer.
