# Exercise 07 — Kill Switches, Circuit Breakers, Canary Tokens

## Goal

Give the `_harness/` agents a control plane they cannot subvert: a kill switch the agents can read but not write, a circuit breaker that trips on identical-call patterns (closed/open/half-open), and a canary token that alarms and trips the kill switch the instant an agent touches it.

## Why

The budget governor from exercise 06 decides *when* to stop; this exercise builds the *how*. A kill switch the agent can flip is theater — the defining property is that a misbehaving agent cannot disable the thing meant to stop it. The breaker stops a stuck agent from a retry storm, and the canary catches the breach you didn't predict. This is the control plane the fleet lessons later run at scale.

## Steps

1. **Read-only kill switch.** Add `module4-fleet/control/kill_switch.py`. Back it with a key the agents' credentials can **read but not write** — a Redis key under a read-only ACL, or (if no Redis) a file the agent process owns no write permission to while a separate operator script does. Check `tripped()` before every agent action; on trip, halt with no further actions. **Prove the agent cannot set the key itself** — attempt a write from the agent's credential and confirm it is denied.

2. **Circuit breaker.** Add `module4-fleet/control/breaker.py` implementing closed/open/half-open with `fail_max` and a cooldown. Trip it on the behavioral pattern, not only on errors: **five identical tool calls in a row** (same tool name + same args) trips the breaker. While open, calls fail fast; after cooldown, half-open lets one probe through; success closes it, failure reopens it.

3. **Drive the breaker.** Make a `_harness/` agent get stuck calling one tool with identical args. Confirm the breaker opens on the fifth identical call, the run fails fast instead of spending on calls six and seven, and a recovery path closes it via half-open.

4. **Canary token.** Plant a decoy credential — e.g. an unused, monitored env var `prod-db-admin` — that no legitimate task needs. Wire an access check so reading it raises an alarm and **trips the kill switch**. Make one agent enumerate its environment and touch the canary; confirm the alarm fires and the kill switch halts every agent.

5. **Budget breach → kill switch.** Connect exercise 06's `BudgetBreach` to this kill switch: a breach trips the switch, completing the loop where the governor decides and the control plane halts.

## Done when

- Every agent action checks the kill switch first; tripping it halts all agents before the next action.
- An attempt to write the kill-switch key from the agent's credential is **denied** — the agent can read it, not write it.
- The breaker opens on the fifth identical tool call, fails fast while open, and recovers via half-open.
- Reading the canary token raises an alarm and trips the kill switch.
- A `BudgetBreach` from exercise 06 trips the same kill switch.

## Stretch

Add a statistical detector — an EWMA or CUSUM on tool-call rate or error rate — that trips the breaker on a slow drift a fixed count misses, *layered on top of* the hard five-identical-calls rule (never replacing it). Then sketch a quarantine path: instead of killing a suspect agent, reroute its outbound calls to a stub honeypot endpoint and keep logging what it tries.
