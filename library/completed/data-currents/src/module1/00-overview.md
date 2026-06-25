# Module 1: SQL as an Operator Skill

Every production question a Production AI Engineer asks about their system lands in data first. Why
did retrieval quality drop for one tenant on Thursday? Why did cost spike between the 2 a.m. and 6
a.m. batches? Which routes are blowing the p95 SLO this week, and did any evals move with them? The
answers live in rows, not dashboards. This module teaches you to reach them with a query.

SQL is not the point; the production questions are. SQL is the language the data platform speaks, and
without it you are reading someone else's summary of your own system instead of querying it directly.
By the end of this module you can sit down at any trace store, warehouse, or local file and answer the
questions that come up in an incident or a hiring screen.

## What This Module Covers

**Your Telemetry Is a Table** establishes the operational mindset: every span, eval verdict, and cost
stamp your AI system emits is a queryable row. You build the three-table telemetry store and the
foundational `GROUP BY` queries that answer the first round of any incident, p95 latency by route,
cost by tenant, and eval pass-rate over a window.

**Window Functions** moves to the questions a plain `GROUP BY` cannot answer: the rolling pass-rate
that smooths daily noise, and the per-tenant cost rank this week against last. A window function
computes over a partition and keeps every row, which is exactly what a trend or a rank needs.

**CTEs and the Diagnostic Chain** turns a multi-step diagnosis into named steps that read
top-to-bottom. You write the freshness-breach chain and the deployment latency delta as common table
expressions instead of a nested pyramid of subqueries.

**The Lineage Walk** closes the module with the query that resolves an answer back to the exact
source-document version that produced it. It is the manual shape of the provenance Module 6 later
automates, and it finalizes the module's smoke gate and test suite.

## Who This Is For

You have shipped a governed multi-agent fleet (Sans Python M7) and run your first seam queries (M5
L14). You can write a `SELECT` and a `WHERE`. This module brings you to the SQL fluency a Production
AI Engineer needs on the job: not DBA depth, but the ability to answer production questions
independently, with a query, not a guess.

## The Artifact

Each lesson extends one artifact, `module1-sql/`: a local telemetry store, the query library that
reads it, and a deterministic smoke gate plus a `pytest` suite that assert the answers. By the end you
have the store, eight operator queries, and a green gate. Module 2 (Batch Ingestion) extends this same
store into a warehouse target and adds a dbt transformation layer on top.

## Prerequisites

- Sans Python complete through M5 L14 (The Data Seam)
- Python 3.11+, `sqlite3` (standard library), and `duckdb` (one pip install) for the analytic queries
- Comfort with `SELECT`, `FROM`, `WHERE`, and `GROUP BY` at the level of M5 L14

## Time Estimate

Each lesson runs 60 to 105 minutes including its exercise. The whole module fits a focused weekend.
