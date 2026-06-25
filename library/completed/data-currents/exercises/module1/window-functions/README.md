# Exercise: Window Functions

## Goal

Extend `module1-sql/` with two window-function queries and assert them in the smoke gate.

## Why

A rolling average and a rank comparison are the two window-function patterns an AI engineer runs when a point-in-time metric is not enough: the trend question and the rank-movement question both require keeping every row.

## Steps

Before writing anything: open `module1-sql/`, run `python smoke.py`, and confirm the prior assertions pass. You are continuing a build. Do not overwrite what already works.

**1. Add the rolling 7-day pass-rate query.**

Create `queries/04_rolling_7d_pass_rate.sql` with the window query from the lesson. The inner subquery computes daily `pass_rate_pct` per criterion; the outer query adds `rolling_7d_pass_rate` via `AVG ... OVER (PARTITION BY criterion ORDER BY eval_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.

**2. Add the per-tenant cost-rank query.**

Create `queries/05_cost_rank_week_over_week.sql` with the two-CTE, self-join query from the lesson. `weekly_cost` aggregates by tenant and week; `ranked` applies `RANK() OVER (PARTITION BY cost_week ORDER BY weekly_cost_usd DESC)`; the final `SELECT` self-joins on tenant and a one-week offset.

**3. Wire both queries into `runner.py`.**

Add two entries to `runner.py` so both queries execute when you run the full query library. Print the result set for each.

**4. Extend `smoke.py` with two new assertions.**

After the existing assertions, add:

- Rolling average assertion: for the `groundedness` criterion, compute the expected 7-day rolling average for one date that falls seven or more days into the seed window (where all seven preceding days have data). Assert that the query result for that date matches within 0.1.
- Rank assertion: assert that `tenant_a` appears in the `rank_this_week = 1` row of the cost-rank result. The seed from lesson 1 plants `tenant_a` as the highest weekly cost driver; it must still rank first here.

Keep the existing assertions intact. `smoke.py` must pass all of them, old and new, in a single run.

## Done When

```
python smoke.py
```

exits 0, prints results for all five queries, and shows PASS for every assertion, including the two new ones. Offline only: no network calls, no API keys.

## Stretch

In `queries/05_cost_rank_week_over_week.sql`, add a `DENSE_RANK()` column alongside `RANK()`. Then add two rows to the seed data so that two tenants share the same weekly cost (and therefore tie in rank). Run the smoke gate and observe the difference in the two columns: `RANK()` leaves a gap after the tie; `DENSE_RANK()` does not. Add a comment at the top of the query file noting which column to use for billing reports versus public leaderboards, and why.
