# Exercise 13 — Fleet Patterns & Governance-as-Code

## Goal

Implement two fleet patterns over the `module4-fleet/` registry — **fleet-budget-guard** and **shared-inbox-HITL** — by *reusing* the lesson-06 governor and the lesson-08 propose-then-commit protocol unchanged, then assemble the governed `module4-fleet/` package as the drop-in artifact the M7 finale imports.

## Why

A fleet pattern is a governance concern made concrete and reachable by name. Two of the six are the single-agent controls you already built, pointed at the fleet — and the discipline this exercise enforces is that you *import* them, never rebuild them. Fleet-budget-guard defends the runaway-delegation failure (a manager whose workers had no per-agent caps spent 8× normal before morning); shared-inbox-HITL defends the inbox-bypass failure (a DM approval that could not answer "evidenced by what?" at the incident review). The package you assemble is not a throwaway: **M7 imports it** to wrap the M6 coding agents in a governance layer, so the finale starts from a running fleet instead of a blank folder.

## Steps

1. **Fleet-budget-guard — reuse, don't rewrite.** Add `module4-fleet/governor/fleet_budget.py` with a `FleetBudgetGuard` that holds one `TaskBudget` per agent (imported from lesson 06's `governor/budget.py` — the cap logic is not retyped) under a single `team_daily_usd` ceiling. `charge(agent_id, usd)` charges the agent's own `TaskBudget` (which raises `BudgetBreach` per-agent on any cap) *and* sums to the team ceiling. On a tripped cap, apply admission control: pause that agent's scheduling and require an inbox approval (step 2) to raise it — not a code edit.

2. **Shared-inbox-HITL — reuse the protocol.** Add `module4-fleet/hitl/shared_inbox.py` where every agent submits proposals into one queue via lesson 08's `propose` / `commit` (imported from `hitl/propose.py` — the persist / surface-case / positive-ack / verify protocol is not re-taught). Each decision carries an `inbox_id`. Enforce the queue discipline: an approval that arrives off-channel (no `inbox_id`, i.e. a simulated DM) is rejected, and nothing destructive auto-executes.

3. **Prove the runaway-delegation case.** Run a manager agent that spawns several small worker charges. Show that a *manager-only* cap would let the aggregate slip through, but `FleetBudgetGuard` catches it on either the per-agent attribution or the team ceiling. This is the failure the per-agent attribution exists to prevent.

4. **Prove the inbox-bypass case.** Submit a destructive proposal, approve it correctly through the inbox (with `inbox_id`) and confirm it commits exactly once via the lesson-08 idempotency key; then attempt an off-channel approval of a second proposal and confirm it is rejected and logged as a bypass.

5. **Assemble the M7 package.** Package the governed fleet as the drop-in artifact M7 imports: `module4-fleet/` containing `registry.yaml` (from exercise 12), `schemas/` (registry + manifest JSON Schemas), `governor/fleet_budget.py`, `hitl/shared_inbox.py`, and the referenced lesson-06/07/08 controls. Add a one-line README stating that M7 imports this package to wrap its coding agents — it does not rebuild it.

6. **Confirm the imports are real.** Grep the two new files: `fleet_budget.py` must import `TaskBudget`/`BudgetBreach` from lesson 06, and `shared_inbox.py` must import `propose`/`commit` from lesson 08. A re-derived governor or a re-taught commit protocol fails this exercise — the architecture is reuse, not restatement.

## Done when

- `FleetBudgetGuard` charges every action to its agent's `TaskBudget` (imported from lesson 06) under a team ceiling, and trips on per-agent *or* team cap — the runaway-delegation case is caught where a manager-only cap would miss it.
- The shared inbox routes every agent's proposal through lesson 08's propose-then-commit (imported), stamps each decision with an `inbox_id`, and rejects an off-channel approval.
- An approved destructive action commits exactly once under the lesson-08 idempotency key; a crash-and-retry returns the prior result, not a second execution.
- The `module4-fleet/` package is assembled with the registry, schemas, budget-guard, shared inbox, and referenced controls — importable, with a README naming it as the M7 import.
- The two new files import (not reimplement) the lesson-06 governor and the lesson-08 protocol.

## Stretch

Add **cross-agent-audit**: a read-only playbook that, given a correlation id, reconstructs a multi-agent task's full chain (user → manager → workers → outcome) from the audit records, answering all four accountability clauses across agent boundaries. Then add **hierarchical-delegation** with a typed JSON handoff packet (authority, constraints, evidence) validated against a schema — workers start report-only, and promotion to write-capable is a human gate routed through the shared inbox. Together with the two required patterns, that is four of the six fleet patterns running over one registry — the governance layer M7's SWE team will run under.
