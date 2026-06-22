# The Batch Freshness SLO

A stale index answers yesterday's question with full confidence. No error, no warning: just a retriever serving last night's corpus to a user who needed this morning's. The problem is not that freshness breaks; it is that nobody defined it until the pager fired.

You build the definition here: a freshness SLO is a measured, alerting objective. You record each load, compare the last successful load's age to a per-source target, and fail a gate the moment a source goes stale.

## Two Tables, One Contract

The SLO lives in two tables that extend `module2-ingestion/`.

```sql
CREATE TABLE corpus_loads (
    load_id       TEXT PRIMARY KEY,
    source_id     TEXT NOT NULL,
    status        TEXT NOT NULL,
    loaded_at     TEXT NOT NULL,
    rows_ingested INTEGER NOT NULL
);
CREATE TABLE freshness_slos (
    source_id     TEXT PRIMARY KEY,
    max_age_hours INTEGER NOT NULL
);
-- seeded targets:  ('corpus_raw', 25)  nightly;  ('corpus_raw_realtime', 2)  near-real-time
```

`corpus_loads` is the audit log: every run of `ingest.py` appends one row recording the source, outcome, timestamp, and row count. `freshness_slos` is the contract: how many hours of lag each source is allowed before the system considers it stale.

These two tables are the same shape M1's freshness-breach query already reads. The `ctes-and-the-diagnostic-chain` lesson built that query against this exact schema; the loader you built in the merge lesson is what writes those `corpus_loads` rows. M1 was the question; M2 is what generates the answer.

## The Freshness Check

The check computes one thing per source: how long ago did the last successful load run, and does that duration exceed the SLO?

```python
rows = conn.execute("""
    SELECT s.source_id, s.max_age_hours, MAX(cl.loaded_at) AS last_load_ts
    FROM freshness_slos s
    LEFT JOIN corpus_loads cl
        ON cl.source_id = s.source_id AND cl.status = 'success'
    GROUP BY s.source_id, s.max_age_hours
""").fetchall()

for row in rows:
    if row["last_load_ts"] is None:
        age_hours, is_stale = float("inf"), True       # never loaded -> stale
    else:
        last_load = datetime.fromisoformat(row["last_load_ts"])
        age_hours = (now - last_load).total_seconds() / 3600
        is_stale  = age_hours > row["max_age_hours"]
# exit non-zero if ANY source is stale -> the gate
```

The `LEFT JOIN` is load-bearing: a source with no successful loads gets a `NULL` for `last_load_ts`, and the `None` branch assigns `float("inf")` hours and marks it stale. A source that has never loaded is not fresh by default; it is maximally stale.

Note the filter on `cl.status = 'success'`. A failed reload does not reset the age clock. If `corpus_raw` ran at midnight and failed, the last successful load was the night before, and the SLO is judged against that. This is the same semantics M1's CTE chain used: only successful loads count.

## What the Gate Means

Microsoft Fabric Data Factory records every pipeline run and lets you inspect its history in the monitor view. [MS-Learn: https://learn.microsoft.com/fabric/data-factory/monitor-pipeline-runs] But Fabric does not enforce a freshness SLA out of the box. There is no built-in guardrail that fires when a source goes stale. You build the SLO check yourself on top of that run history.

The `freshness_check.py` script is that check. When it exits zero, every source is inside its window. When it exits non-zero, at least one source has exceeded its target age, and the gate has fired. What happens next, whether that is a PagerDuty alert, a Slack notification, or a deployment block, is a decision the orchestrator makes. The gate's job is to produce a reliable non-zero exit when the contract is broken.

Two numbers make the contract meaningful. A nightly batch source with a 25-hour target has a one-hour margin before the next run should have landed. A near-real-time source with a 2-hour target goes stale fast, and the gate will tell you before users do.

## The M1 Connection

M1's `freshness_breach` query (Q7 in the diagnostic playbook) is what an on-call engineer runs when the pager fires at 2 a.m. It reads `corpus_loads` and `freshness_slos`, finds sources where the last successful load exceeds `max_age_hours`, and returns them sorted by age. That query works because this module wrote the rows it reads. `ingest.py` is the writer; Q7 is the reader. The two modules share a data contract, and the smoke gate in this exercise asserts it: run the freshness-breach query against the same tables and confirm it surfaces the stale source.

That is the compounding in action. M1 taught you to diagnose; M2 built the system that generates the evidence.

## Core Concepts

- A freshness SLO is a per-source numeric target (`max_age_hours`) compared against the age of the last successful load; a source with no successful loads is maximally stale, not provisionally fresh.
- `corpus_loads` is the audit log that makes the SLO measurable: every ingest run appends one row so the check always has a `MAX(loaded_at)` to work against.
- The gate exits non-zero when any source exceeds its target; it exits zero only when every source is inside its window. Zero means the whole contract is satisfied.
- M1's freshness-breach query reads the same `corpus_loads` and `freshness_slos` tables this module writes; the two modules share a data contract enforced by the smoke gate.

The SLO you define today is the number on-call reads at 2 a.m. Set it with intention, or someone else will set it with hindsight.

Module 3 orchestrates these loads on a schedule with retries and alerting, so the gate fires automatically rather than requiring a manual run.

<div class="claude-handoff" data-exercise="exercises/module2/the-batch-freshness-slo/">

**Build It in Claude Code**: Extend `ingest.py` to append a `corpus_loads` row (with `load_id`, `source_id`, `status`, `loaded_at`, and `rows_ingested`) on every run; seed `freshness_slos` with two targets (`corpus_raw` at 25 hours for the nightly batch, `corpus_raw_realtime` at 2 hours for the near-real-time source); build `freshness_check.py` that queries the last successful load age for each source against its SLO and exits non-zero when any source is stale; then finalize `smoke.py` to assert that a fresh source passes the check, a source whose load timestamp is seeded in the past beyond its SLO fails the check, and that M1's freshness-breach query run against the same tables returns exactly the stale source.

</div>
