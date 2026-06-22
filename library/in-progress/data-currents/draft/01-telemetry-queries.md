# Your Telemetry Is a Table

The on-call alert fires at 3 a.m. p95 latency for the `/summarize` route is up 40%. You open the
dashboard, squint at the line, and see the spike. That tells you something happened. It does not
tell you which tenants are affected, whether eval quality moved with it, or how much it is costing
per hour. For those answers you need a query, and if you cannot write one you are waiting for
whoever built the dashboard to wake up.

This lesson is the move from watching to querying. Your telemetry is already a dataset. Every span
your observability layer emits, every eval verdict your judge returns, every cost stamp your FinOps
layer records: those are rows. The Production AI Engineer who can query them directly is the one
who answers the 3 a.m. question in ten minutes instead of four hours.

## The Shape of AI Telemetry

Production AI systems emit three categories of data that recur in every incident:

**Spans**: one row per request, carrying the route, tenant, latency in milliseconds, token counts,
and a timestamp. These are what your tracing library (LangWatch, Arize Phoenix, Langfuse) emits
at the span level. In Sans Python M5 L14 you saw these as a "table"; here you treat them as one.
[MS-Learn: Azure SQL Database for intelligent applications provides T-SQL surfaces for querying
telemetry data from AI workloads.]

**Eval verdicts**: one row per evaluated output, carrying the trace id of the span it evaluates,
the criterion (groundedness, relevance, faithfulness), and the verdict (pass/fail) with a score.
These are what your LLM-as-judge pipeline writes after each evaluation run.

**Cost stamps**: one row per request (or per billing period), carrying the tenant, model id, input
tokens, output tokens, and total cost in USD. When a tenant's bill doubles, the query starts here.

These three tables join on `trace_id`. The Production AI Engineer knows this join by reflex.

## The Twelve Operator Queries

Every production question maps to one of twelve query patterns. Master these and you can answer
any question that comes up in an incident or in a hiring screen.

### Query 1: P95 Latency by Route

The first question in every latency incident: which routes are slow, and how slow?

```sql
SELECT
    route,
    COUNT(*)                                          AS request_count,
    AVG(latency_ms)                                   AS avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency_ms
FROM spans
WHERE ts >= NOW() - INTERVAL '24 hours'
GROUP BY route
ORDER BY p95_latency_ms DESC;
```

`PERCENTILE_CONT` is the standard SQL function for computing a continuous percentile over an
ordered distribution. Azure SQL Database and Microsoft Fabric Warehouse both support it natively
in T-SQL. If your store is SQLite (which does not have `PERCENTILE_CONT`), use DuckDB, which does:
`QUANTILE_CONT(latency_ms, 0.95)`. [MS-Learn: T-SQL aggregate functions in Azure SQL Database
include `PERCENTILE_CONT` and `PERCENTILE_DISC` for ordered-set aggregation.]

What this query tells you: p95 latency by route, over the last 24 hours, ordered worst-first. The
answer to "which route is blowing the SLO" is in the first row.

### Query 2: Cost by Tenant

```sql
SELECT
    tenant_id,
    SUM(total_cost_usd)          AS total_cost_usd,
    SUM(input_tokens)            AS total_input_tokens,
    SUM(output_tokens)           AS total_output_tokens,
    COUNT(*)                     AS request_count,
    AVG(total_cost_usd)          AS avg_cost_per_request
FROM cost_stamps
WHERE billed_at >= DATE_TRUNC('week', NOW())
GROUP BY tenant_id
ORDER BY total_cost_usd DESC;
```

The answer to "which tenant is driving this week's cost spike" is in the first row. The `AVG`
column tells you whether the cost is driven by volume (many cheap requests) or per-call expense
(fewer but expensive model calls). Those are different fixes.

### Query 3: Eval Pass-Rate over a Rolling Window

```sql
SELECT
    DATE_TRUNC('day', ev.created_at)  AS eval_day,
    ev.criterion,
    COUNT(*)                           AS total_evals,
    SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END)  AS passes,
    ROUND(
        100.0 * SUM(CASE WHEN ev.verdict = 'pass' THEN 1 ELSE 0 END) / COUNT(*),
        1
    )                                  AS pass_rate_pct
FROM eval_verdicts ev
WHERE ev.created_at >= NOW() - INTERVAL '14 days'
GROUP BY eval_day, ev.criterion
ORDER BY eval_day, ev.criterion;
```

This query answers "is quality trending up or down, and on which criterion?" The 14-day window
gives you two weeks of history so you can see whether a drop is a blip or a trend. Run it by
joining `eval_verdicts` to `spans` on `trace_id` and adding a `WHERE route = '/summarize'` to
scope to one route.

### The Join That Connects All Three

```sql
SELECT
    s.route,
    s.tenant_id,
    s.latency_ms,
    c.total_cost_usd,
    ev.criterion,
    ev.verdict
FROM spans s
JOIN cost_stamps c   ON s.trace_id = c.trace_id
JOIN eval_verdicts ev ON s.trace_id = ev.trace_id
WHERE s.ts >= NOW() - INTERVAL '1 hour'
  AND ev.verdict = 'fail';
```

This is the query you write when quality fails and you want to know whether it correlates with
high cost or high latency. The row that comes back tells you the full picture: this tenant, this
route, this latency, this cost, this criterion failed.

## Reading Telemetry Data Out of the Wild

Production telemetry rarely arrives in three clean tables. Spans may be JSON blobs in an
object-store bucket. Eval verdicts may live in a trace tool's Postgres database. Cost stamps may
be CSV exports from the model provider's billing API. Before you can query, you need a seam.

The pattern the Production AI Engineer uses is simple: land the raw data in a local store (SQLite
or DuckDB), normalize the schema into three tables, and query. Lesson 02's exercise will formalize
this into a dbt model; for now the manual ETL teaches you the schema contract you are normalizing
toward.

A minimal span schema:

```sql
CREATE TABLE spans (
    trace_id     TEXT PRIMARY KEY,
    route        TEXT NOT NULL,
    tenant_id    TEXT NOT NULL,
    latency_ms   INTEGER NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    ts           TIMESTAMP NOT NULL
);
```

A minimal eval_verdicts schema:

```sql
CREATE TABLE eval_verdicts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id   TEXT NOT NULL REFERENCES spans(trace_id),
    criterion  TEXT NOT NULL,   -- 'groundedness' | 'relevance' | 'faithfulness'
    verdict    TEXT NOT NULL,   -- 'pass' | 'fail'
    score      REAL,
    created_at TIMESTAMP NOT NULL
);
```

These are the tables the exercise builds. Write the schema once; query it forever.

## Why This Is an Operator Skill, Not a DBA Skill

The DBA owns the schema design, the index strategy, the query plan, and the capacity plan for a
database that serves hundreds of concurrent users. None of that is your job. Your job is narrower
and more specific: write the query that answers the production question, against a schema the data
team owns, using the read access your role gives you.

The distinction matters on the hiring screen. "I ran SQL against our trace warehouse to diagnose
a latency regression" is an AI engineer answer. "I designed the warehouse schema and managed the
indexes" is a data engineer answer. You are the former, and knowing exactly what you own makes
you credible to both the AI team and the data team. [MS-Learn: Azure SQL Database supports role-
based access control and read-only replicas, which is the typical access pattern for AI engineers
querying production telemetry without affecting write performance.]

## The Literacy Test

M5 L14 introduced the binary: either you can answer "where did the latency, the money, or the
quality go" with a `GROUP BY`, or you are guessing from a chart someone else built. The three
queries in this lesson pass that test. You can answer the three questions an engineering manager
will ask in the first five minutes of a production incident, with numbers, not graphs.

The next lesson adds window functions and CTEs: the patterns for questions that `GROUP BY` alone
cannot answer, such as "which tenants ranked highest for cost last week versus this week" and
"how does eval pass-rate trend when I smooth over a seven-day rolling average."

## Core Concepts

- AI telemetry is three tables: spans (latency + route + tenant), eval verdicts (criterion +
  verdict joined by trace_id), and cost stamps (tenant + token counts + cost). They join on
  `trace_id`.
- The three foundational operator queries: p95 latency by route (`PERCENTILE_CONT`, `GROUP BY
  route`), cost by tenant (`SUM`, `GROUP BY tenant_id`), and eval pass-rate over a rolling window
  (`DATE_TRUNC`, conditional `SUM`, `GROUP BY day + criterion`).
- `PERCENTILE_CONT` is the T-SQL standard for p-percentile latency; DuckDB's `QUANTILE_CONT` is
  the drop-in for local SQLite-adjacent work. [MS-Learn: T-SQL percentile functions in Azure SQL.]
- The Production AI Engineer's SQL access is read-only against schemas the data team owns; the
  operator skill is writing the query, not designing the schema.

<div class="claude-handoff" data-exercise="draft/exercises/01-telemetry-queries/">

**Build It in Claude Code**: Add a SQLite telemetry seam to `module5-serving/`. Create the three
tables (`spans`, `eval_verdicts`, `cost_stamps`), load a realistic synthetic dataset (100 spans
across four routes and three tenants, covering a 14-day window), then implement and run the three
foundational operator queries: p95 latency by route, cost by tenant, and eval pass-rate by day and
criterion. Prove it: `python smoke.py` loads the dataset, runs all three queries against known
values, and prints pass/fail for each assertion. `python -m pytest tests/` asserts p95 is correct
for the highest-latency route, the correct tenant is the top cost driver, and pass-rate for a
known failing criterion matches the seeded data.

</div>
