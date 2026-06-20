# Exercise: The Loop

## Goal

Wrap a `_harness/` stub agent as a governed loop with all four stages — `trigger → action → verification → budget/kill-switch` — running at **L1 (report-only)**. The loop discovers work, runs the agent, checks the result with an independent verifier, writes findings to a state file, and acts on nothing. It stops on a budget breach and halts on the kill switch.

## Why

An Production AI Engineer's unit of unattended infrastructure is the loop: one agent system you can run on a trigger and still trust, because the verifier sits in the wire and the off switch sits outside the agent. Climbing the L1/L2/L3 autonomy ladder in order — report-only first — is how you measure a loop before you let it act.

## Setup

This exercise extends the throughline artifact `module4-fleet/` and governs the seeded harness at `exercises/module4/_harness/` (a Python orchestrator + two stub agents + a registry stub). Reuse the budget governor from exercise 06 and the kill switch from exercise 07 — do not rebuild them.

## Steps

1. In `module4-fleet/loop/`, implement `run_loop(pattern, switch, budget)` with the four-stage shape:
   - **Trigger:** `pattern.trigger()` discovers work (e.g. a watchlist of harness tasks) and returns the items. If the list is empty, **early-exit to a no-op** — return `{"outcome": "no-op"}` having spent near-zero tokens. Prove this exit is the cheapest path the loop can take.
   - **Action:** `pattern.action(work, budget)` runs a `_harness/` stub agent on the work, charging the per-task budget (exercise 06) on every step. A budget breach raises and stops the run before the next action.
   - **Verification:** `pattern.verify(result)` is an **independent** check — a separate function or sub-agent with a different prompt and read-only access to the result. It defaults to `REJECT` and returns `APPROVE` only on evidence. The agent that produced the result must not be the one that approves it.
   - **Budget / kill-switch:** check the exercise-07 kill switch before every action; on any budget breach or a tripped switch, stop and record the reason.
2. Run the loop at **L1**: on `APPROVE`, write the finding to `loop/state.md` (a prioritized list a human reads) — **do not** open a PR, apply a label, or take any external action. On `REJECT`/`ESCALATE_HUMAN`, write the item to an escalation section of the state file.
3. Append a structured JSON entry per run to `loop/run-log.jsonl` (run id, items found, outcome, token estimate) — the audit trail.
4. Wire the kill switch from exercise 07 (a key the agent's credential can read but not write). Set it mid-run and prove the loop halts before the next action with `{"outcome": "halted", "reason": "kill_switch"}`.

## Done when

- `module4-fleet/loop/run_loop.py` (or equivalent) exists and runs against the `_harness/` without errors.
- An empty watchlist returns a no-op that spends near-zero — verified by a run that finds nothing and charges nothing.
- The verifier is a separate component from the action; a test shows the action result going to `REJECT` does **not** reach the commit/report path.
- A budget breach (per-task, iteration, or velocity cap from exercise 06) stops the run mid-loop.
- Setting the exercise-07 kill switch halts the loop before the next action — verified by output showing `"halted": true`.
- At L1 the loop writes only to `state.md` and `run-log.jsonl`; it takes no external action. No path from `action` to `commit` skips `verify`.

## Stretch

Graduate one narrow case to **L2**: pick a single safe, allowlisted action (e.g. tagging one item in the state file) and let the loop perform it itself — but only after the verifier passes and only within an explicit path allowlist. Everything outside the allowlist still escalates. Add a graduation gate: the loop refuses to run at L2 until the run log shows N consecutive L1 runs with no verifier rejections, encoding "measure before you climb" as code.
