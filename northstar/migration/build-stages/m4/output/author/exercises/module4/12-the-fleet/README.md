# Exercise 12 — The Fleet: Graduation to Governed Many

## Goal

Turn the `_harness/` into a governed fleet by promoting `registry.yaml` into a real machine-readable fleet registry — identity, least-privilege permissions, autonomy tiers, per-agent budgets, and human gates — then make the orchestrator read that registry to authorize every agent action and answer the four-clause accountability test for one real action.

## Why

Below the 3-loop / 5-agent threshold you can hold the fleet in your head; above it, "I think that's all of them" stops being an acceptable answer to an incident reviewer. A fleet is governed only if it can answer, for any action, *which agent did it, with what authority, against what task, evidenced by what?* This exercise makes the registry the machine-readable source of truth those four clauses are answered from — the foundation lessons 13 and the M7 finale build on. The kill switch, budget, and HITL controls are reused from lessons 06–08 at fleet scale; this exercise builds the registry layer that knows *who* is being governed.

## Steps

1. **Promote the registry.** Extend `module4-fleet/registry.yaml` so each agent entry carries the full identity record: a stable `id`, a named `owner` (the accountable party), an `autonomy_tier` (`F0` manual … `F3` fully autonomous — start every agent at `F1`, report-only/human-gated), a `status` (`active`/`paused`/`retired`/`experimental`), least-privilege `permissions` (`tools` list + `can_write`), a `budget_daily_tokens` per-agent cap, and a `human_gates` list (e.g. `production_data_access`). Add a third agent so the fleet crosses the 5-agent line and the governance is non-trivial.

2. **Write the schemas.** Add `module4-fleet/schemas/agent-registry.schema.json` and `agent-manifest.schema.json` (JSON Schema, draft-07). Require `id`, `owner`, `autonomy_tier`, and `status` at minimum; constrain `autonomy_tier` to the `F0`–`F3` enum and `status` to its enum. Validate `registry.yaml` against the schema as a CI-style check: a malformed entry must fail validation *before* it governs anything.

3. **Authorize from the registry.** Change the orchestrator so it reads the registry and authorizes each agent action against that agent's declared `permissions`. An agent attempting a tool not in its `tools` list, or a write when `can_write: false`, is refused before the action runs — authority comes from the registry, never from whatever credential is in the environment.

4. **Log the accountability sentence.** On every action (allowed or refused), emit a structured audit record answering all four clauses: `which` (agent id), `authority` (the permission/tier that allowed it), `task` (the routed task), `evidence` (a correlation id + the registry path). This record is what an incident review reads.

5. **Reference, don't rebuild, the safety controls.** The kill switch (lesson 07), budget governor (lesson 06), and HITL gate (lesson 08) already exist in `module4-fleet/`. Wire the registry so each agent's `budget_daily_tokens` and `human_gates` *point at* those existing controls — do not re-implement them here. A `human_gates` entry means "route this action through the lesson-08 inbox"; it is a reference, not a new gate.

6. **Prove graduation.** Demonstrate that the fleet (now ≥5 agents) can answer all four accountability clauses for one real action, and that an out-of-permission action is refused with the refusal logged.

## Done when

- `registry.yaml` lists ≥3 agents, each with `id`, `owner`, `autonomy_tier`, `status`, least-privilege `permissions`, `budget_daily_tokens`, and `human_gates`; the fleet crosses the 5-agent graduation line.
- The registry validates against the JSON Schema, and a deliberately malformed entry (bad `autonomy_tier`, missing `owner`) fails validation before the orchestrator runs.
- The orchestrator authorizes actions from the registry: an agent attempting a tool outside its `permissions` is refused, and the refusal is logged.
- One real action produces an audit record answering all four accountability clauses (which / authority / task / evidence).
- The kill switch, budget, and HITL controls are referenced from the registry, not reimplemented in this exercise.

## Stretch

Add an `autonomy_tier` promotion path: an agent at `F1` (report-only) can be promoted to `F2` (write-capable) only by a reviewed change to the registry that passes schema validation and is recorded in the audit log — prove that an attempt to write while at `F1` is refused, and that promotion is a diffable registry change, not a runtime flag. Then write a tiny `fleet-audit` check that scores the fleet for the seven concerns (registry, identity, permissions, inbox, audit, economics, kill switch) and prints a readiness score — the same instrument real teams use to find shadow agents.
