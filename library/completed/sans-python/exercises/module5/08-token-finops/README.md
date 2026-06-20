# Exercise 08 — Token FinOps & Cost Optimization

## Goal

Add a FinOps layer to `module5-serving/` that makes the bill a metric you can query and cut. Stamp every request with cost-attribution dimensions, compute a simulated token cost, and add two levers — a semantic cache and a tiered router — then prove on a fixed workload that each lever lowers the total spend and that the attribution report shows *where* it dropped.

## Why

When finance asks why the AI bill tripled, the only useful answer is a query — cost per customer, per feature, per route — and you can't run that query unless you instrumented attribution before the spend happened. This exercise builds the attribution layer and the two highest-payoff levers (caching and routing) at platform scale, on top of the Module 4 per-task budget governor. It is the same cost discipline read at a different altitude: the governor caps one task; FinOps sums and steers the whole platform's bill.

## Steps

1. **Attribution at the call site.** Add `module5-serving/finops/attribution.py` with a `Charge` carrying `user_id`, `tenant_id`, `task_id`, `route`, `in_tok`, `out_tok`, and a `usd()` method that prices it off a simulated rate card (two tiers: `big` and `small`, each with input/output per-million rates). Wrap the serving path so every simulated request emits a `Charge` to a ledger. Add a `report(ledger)` that sums cost grouped by any dimension — per user, per tenant, per route.

2. **Fixed workload.** Build a deterministic workload of N simulated requests (mix of repeated and unique queries, mix of easy and hard) so the three runs below are comparable. Each request carries a synthetic input/output token count.

3. **Baseline run.** Route every request to the `big` model, no cache. Record total cost and the per-dimension report. This is the bill you're trying to beat.

4. **Caching lever.** Add a semantic cache keyed by `(tenant_id, normalized_query)` — for the exercise a normalized exact-match key is enough; a near-match by simple similarity is the stretch. A cache hit returns the stored answer for **zero token cost**. Re-run the workload; show total cost dropping by the repeated-request share, and the report attributing the drop to cached routes. Confirm the cache key includes the tenant (carried over from exercise 07) so a hit never crosses tenants.

5. **Routing lever.** Add a `route(request) -> "big" | "small"` broker that sends easy requests (short, classification-shaped) to `small` and hard ones to `big`. Re-run with caching plus routing; show total cost dropping again, attributed to the share now served by the cheap tier. Add a guard that logs when the cheap-tier share crosses a threshold — the local stand-in for gating routing on a quality signal so cheap-model drift gets noticed.

6. **Per-task cap underneath.** Import the Module 4 `TaskBudget` and charge each task's cumulative `usd()` against it. Do **not** rebuild the governor — reuse it. Show that a task exceeding its cap still trips `BudgetBreach` and stops, proving FinOps sits on top of the per-task floor rather than replacing it.

## Done when

- Every simulated request emits a `Charge`, and `report()` can break the total down per user, per tenant, and per route.
- Three runs on the same workload show monotonically falling total cost: baseline > caching > caching+routing.
- The attribution report explains each drop — caching credited to repeated requests, routing credited to the cheap-tier share.
- The semantic cache is keyed by tenant; no cache hit crosses tenants.
- The Module 4 `TaskBudget` is reused unchanged as the per-task cap, and a task over budget still trips `BudgetBreach`.
- All costs are simulated — no real provider call anywhere.

## Stretch

Add a per-tenant quota: a Tokens-Per-Minute cap that returns a simulated `429` with a `retry_after_ms` once a tenant exceeds its window, and surface a `remaining_tokens` counter the caller can read to throttle before hitting the wall (mirroring Azure OpenAI's rate-limit headers). Then add a batch lane: requests marked non-interactive accumulate and price at half rate, and show the workload's cost dropping further when the non-interactive share moves to batch.
