# Exercise 06 — Action Budgets & Cost Governors

## Goal

Add a deterministic cost governor to the `_harness/` orchestrator that defends Denial of Wallet with limits at three time scales — a per-task dollar budget, an iteration cap, and a velocity limit (spend per rolling window) — and prove each cap fires independently on a different failure mode.

## Why

A `_harness/` agent with a goal and an API key behind it can spiral and bill thousands of dollars before anyone notices — there is no segfault, just a metered loop running forever. A single monthly cap catches the runaway only after the wallet is gone. This exercise wires limits at different time scales so a runaway hits a wall in seconds, and it defines the governor the fleet lessons later reuse unchanged.

## Steps

1. **Budget object.** Add `module4-fleet/governor/budget.py` with a `TaskBudget` holding `max_usd`, `max_turns`, `velocity_usd`, and `velocity_window_s`, plus running `spent_usd`, `turns`, and a per-charge ledger of `(timestamp, usd)`. Implement `charge(usd)` that records the charge and raises `BudgetBreach` when any cap is crossed. Keep it pure deterministic code — no model calls.

2. **Wire it into the loop.** Wrap each `_harness/` agent action so its estimated cost is charged to the `TaskBudget` *before* the next action runs. Compute cost from a simple token-price table (input/output tokens × a per-token rate) so the numbers are real, not random.

3. **Per-task cap test.** Run a slow-grind task whose cumulative spend creeps past `max_usd`. Confirm `BudgetBreach` fires on the charge that crosses the line and the run stops before the next action.

4. **Iteration-cap test.** Run a task that loops without converging. Confirm it stops at `max_turns` rather than running forever.

5. **Velocity-limit test.** Run a burst that spends past `velocity_usd` inside `velocity_window_s` (e.g. >$50 in 10 min, scaled down for the test). Confirm the velocity limit cuts the run *mid-flight* — before either the per-task or any calendar cap would have — proving the time-derivative limit catches the spiral the static caps miss.

6. **Breach → stop contract.** On any `BudgetBreach`, the orchestrator halts the run and surfaces which cap tripped. (In exercise 07 this breach becomes the event that trips the kill switch; here, raising and stopping is enough.)

## Done when

- A slow grind trips the per-task dollar cap, a non-converging loop trips the iteration cap, and a burst trips the velocity limit — three distinct failure modes, three distinct caps, each demonstrated.
- The velocity limit cuts a burst before the per-task or calendar caps would, shown with timing.
- The governor is deterministic: no model decides whether to enforce a budget.
- A breach stops the run and reports the tripped cap.

## Stretch

Add tiered model routing to the governor: route cheap steps (classification, a rubric score) to a small model and reserve the expensive model for reasoning steps, then measure the spend difference against routing everything to the top model. Add prompt-prefix caching accounting so the budget stops charging full price for a re-sent stable prefix.
