# Exercise 05 — Safe Rollout: Shadow, Canary, A/B

## Goal

Add a shadow/canary router to `module5-serving/` that fronts two model backends behind one endpoint, mirrors traffic to a candidate in shadow mode, splits traffic by a configurable weight in canary mode, and auto-reverts to 0% when a gated metric crosses its threshold — all as config changes, no restart.

## Why

Swapping a model in production has no failing test when it gets worse; the regression is diffuse and the signal is delayed. Progressive delivery through a gateway lets a sliver of traffic find the regression before all of it does, and keeps rollback one flag away — the eval thread's outer loop, where the Module 2 judges now gate live traffic.

## Steps

1. **Two backends, one endpoint.** Add `module5-serving/router/gateway.py` exposing one stable local endpoint in front of two backend stubs — `stable` and `candidate`. Each stub returns a response plus mock per-request metrics (cost, latency, a refusal flag, output length) so the router has something to gate on. No real provider; the stubs are local.

2. **Shadow mode.** In shadow mode, every request is served by `stable` and returned to the caller unchanged, while a copy is sent to `candidate` and its response logged with a diff (cost delta, latency delta, length delta). Prove the caller's response is never affected by the candidate, and that the shadow log captures the operational deltas. Note in a comment what shadow cannot catch: quality, because no user reads the shadow output.

3. **Canary mode with a weight.** Add a routing weight in config (e.g. `canary_weight: 0.1`). Route that fraction of requests to `candidate`, the rest to `stable`. The weight lives in config the router re-reads — changing it must not require a restart.

4. **Gated metrics + auto-revert.** Reuse the metrics recorder from exercise 04. Declare canary gate thresholds (cost per request, latency p99, refusal rate). After each window of canary requests, check the candidate's metrics against the gates; if any is breached, set the canary weight to 0 automatically and log which gate tripped. Prove a deliberately bad candidate (inflated cost or refusal rate) gets reverted without a human flipping the flag.

5. **A/B vs canary, in one comment.** Add a short doc comment distinguishing the two: canary asks "is the candidate safe to ship?" (operational gates); A/B asks "do users prefer A or B?" (a randomized user-level product metric). You implement canary here; name A/B as the separate question.

6. **Promotion + rollback as config.** Show that moving the canary from 10% to 25% and slamming it back to 0% are config edits the running router picks up — seconds, not a deploy. Keep which backend is "live" as a flag, not hard-coded.

## Done when

- One endpoint fronts two backends; shadow mode mirrors to the candidate and logs a diff without ever altering the caller's response.
- Canary mode splits traffic by a config weight the running router re-reads — no restart to change it.
- A deliberately bad candidate trips a gate (cost, latency p99, or refusal rate) and the router auto-reverts the canary weight to 0, logging which gate tripped.
- Promotion and rollback are demonstrated as config changes, with timing showing they take seconds.

## Stretch

Wire the Module 2 LLM-as-judge stub as a quality gate on the canary: score a sample of candidate responses against a rubric and add the pass rate to the gate set, so the canary halts on a *quality* regression that the operational metrics (cost, latency, length) sail past. Add a digest-pinned "registry" dict so a revert names an exact prior version.
