# Your Telemetry Is a Table

The on-call alert fires at 3 a.m. p95 latency on `/summarize` is up 40%, and the dashboard tells you
something happened but not which tenants are hit, whether quality moved with it, or what it is costing
per hour. For those answers you need a query, not a chart, and if you cannot write one you are waiting
for whoever built the dashboard to wake up.

Your observability layer is already emitting rows. Every span your tracing library records, every
verdict your LLM judge returns, every cost stamp your billing layer writes: those are tables. You build
the query that answers the 3 a.m. question in ten minutes.

## The Three Tables

Production AI telemetry compresses into three tables that recur in every incident.

```sql
CREATE TABLE spans (
    trace_id      TEXT PRIMARY KEY,
    route         TEXT NOT NULL,
    tenant_id     TEXT NOT NULL,
    latency_ms    INTEGER NOT NULL,
    input_tokens  INTEGER,
    output_tokens INTEGER,
    ts            TIMESTAMP NOT NULL
);
CREATE TABLE eval_verdicts (
    id         INTEGER PRIMARY KEY,
    trace_id   TEXT NOT NULL REFERENCES spans(trace_id),
    criterion  TEXT NOT NULL,   -- 'groundedness' | 'relevance'
    verdict    TEXT NOT NULL,   -- 'pass' | 'fail'
    score      REAL,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE cost_stamps (
    id             INTEGER PRIMARY KEY,
    trace_id       TEXT NOT NULL REFERENCES spans(trace_id),
    tenant_id      TEXT NOT NULL,
    total_cost_usd REAL NOT NULL,
    input_tokens   INTEGER,
    output_tokens  INTEGER,
    billed_at      TIMESTAMP NOT NULL
);
```

`spans` is one row per request: route, tenant, latency, token counts, timestamp. This is what your
tracing library (LangWatch, Arize Phoenix, Langfuse) emits at the span level.

`eval_verdicts` is one row per evaluated output: the trace it grades, the criterion (groundedness,
relevance), and the pass/fail verdict with an optional score. Your LLM-as-judge pipeline writes here
after each evaluation run.

`cost_stamps` is one row per request: the tenant, token counts, and total cost in USD. When a
tenant's bill doubles, the query starts here.

The three tables join on `trace_id`. That join is the reflex. Know it before anything else.

## Read-Only Is the Point

You query telemetry you do not own. The data team designed the schema, manages the indexes, and
controls write access. Your role gives you a read replica or a read-only role against the warehouse,
and that is enough. Warehouses serve this pattern with role-based access and read scale-out: your
query does not touch the write path. The operator skill is writing the query, not designing the
schema. [Azure SQL Database read scale-out: https://learn.microsoft.com/azure/azure-sql/database/read-scale-out]

## Three Queries That Answer the Incident

### P95 Latency by Route

The first question in every latency incident: which routes are slow, and how slow at the tail?

```sql
SELECT
    route,
    COUNT(*)                          AS request_count,
    ROUND(AVG(latency_ms), 1)         AS avg_latency_ms,
    ROUND(QUANTILE_CONT(latency_ms, 0.95), 1) AS p95_latency_ms
FROM spans
WHERE ts >= NOW() - INTERVAL '24 hours'
GROUP BY route
ORDER BY p95_latency_ms DESC;
```

The first row is the answer to "which route is blowing the SLO."

**Dialect note.** In a warehouse (Azure SQL, Microsoft Fabric), p95 is:

```sql
PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms)
```

DuckDB, which runs the exercise offline, uses `QUANTILE_CONT(latency_ms, 0.95)` instead.
[T-SQL PERCENTILE_CONT: https://learn.microsoft.com/sql/t-sql/functions/percentile-cont-transact-sql]

### Cost by Tenant

When a cost spike hits, the question is: who, and is it volume or per-call expense?

```sql
SELECT
    tenant_id,
    ROUND(SUM(total_cost_usd), 6)   AS total_cost_usd,
    SUM(input_tokens)               AS total_input_tokens,
    SUM(output_tokens)              AS total_output_tokens,
    COUNT(*)                        AS request_count,
    ROUND(AVG(total_cost_usd), 6)   AS avg_cost_per_request
FROM cost_stamps
WHERE billed_at >= DATE_TRUNC('week', NOW())
GROUP BY tenant_id
ORDER BY total_cost_usd DESC;
```

The `avg_cost_per_request` column splits the diagnosis: high count with low average means volume;
low count with high average means expensive model calls. Those are different fixes.

**Dialect note.** `DATE_TRUNC('week', NOW())` runs in DuckDB and Postgres. T-SQL uses `DATETRUNC`
or `DATE_BUCKET`.
[T-SQL DATE_BUCKET: https://learn.microsoft.com/sql/t-sql/functions/date-bucket-transact-sql]

### Eval Pass-Rate by Day and Criterion

Quality questions need a window, not a point. Two weeks of daily pass-rate tells you whether a drop
is a blip or a trend.

```sql
SELECT
    DATE_TRUNC('day', ev.created_at)  AS eval_day,
    ev.criterion,
    COUNT(*)                          AS total_evals,
    SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END) AS passes,
    ROUND(100.0 * SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pass_rate_pct
FROM eval_verdicts ev
WHERE ev.created_at >= NOW() - INTERVAL '14 days'
GROUP BY eval_day, ev.criterion
ORDER BY eval_day, ev.criterion;
```

The `CASE WHEN` conditional sum is the standard pattern for computing a rate inside a `GROUP BY`.
Read it as: count the rows where verdict is 'pass', divide by total rows, multiply by 100.

## The Join That Connects All Three

When quality fails, you want to know whether it correlates with latency or cost. One query reaches
all three tables.

```sql
SELECT s.route, s.tenant_id, s.latency_ms, c.total_cost_usd, ev.criterion, ev.verdict
FROM spans s
JOIN cost_stamps c    ON s.trace_id = c.trace_id
JOIN eval_verdicts ev ON s.trace_id = ev.trace_id
WHERE s.ts >= NOW() - INTERVAL '1 hour'
  AND ev.verdict = 'fail';
```

The row that comes back is the full picture: this route, this tenant, this latency, this cost, this
criterion failed. The join key is `trace_id` on every leg. That is why it is the one thing to
memorize.

Knowing this join cold is what separates the engineer who can read an incident from the one who is
waiting for the dashboard team.

## Core Concepts

- AI telemetry is three tables: `spans` (latency, route, tenant), `eval_verdicts` (criterion and
  verdict, joined by `trace_id`), and `cost_stamps` (tenant, tokens, cost). They join on `trace_id`.
- `GROUP BY` with `COUNT`, `SUM`, and `ROUND(AVG(...))` answers the first-round questions in a
  latency, cost, or quality incident; window functions and CTEs come in later lessons.
- The warehouse standard for p95 latency is `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY
  latency_ms)`; DuckDB's offline equivalent is `QUANTILE_CONT(latency_ms, 0.95)`.
- The AI engineer queries telemetry read-only against a schema the data team owns; the skill is
  writing the query, not designing the schema or managing the index.

<div class="claude-handoff" data-exercise="exercises/module1/your-telemetry-is-a-table/">

**Build It in Claude Code**: Create the `module1-sql/` artifact: write `db/schema.sql` with the
three core tables (`spans`, `eval_verdicts`, `cost_stamps`), write `db/seed.py` to deterministically
populate it with synthetic telemetry (4 routes, 3 tenants, ~140 spans over 14 days, with `/summarize`
carrying the highest p95, `tenant_a` the highest weekly cost, and `tenant_b` groundedness pass-rate
near 60%), then place the three foundational queries in `queries/`, wire a `runner.py` that runs them
via DuckDB over the SQLite file, and write a `smoke.py` that resets, seeds, queries, asserts the
seeded outliers, and exits non-zero on failure.

</div>
