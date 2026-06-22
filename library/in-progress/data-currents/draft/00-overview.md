# Module 1: SQL as an Operator Skill

Every question a Production AI Engineer asks about their system lands in data first. Why did
retrieval quality drop for tenant 12 on Thursday? Why did costs spike between the 2 a.m. and 6
a.m. batches? Which routes are blowing the p95 SLO this week, and which evals moved with them? The
answers live in rows, not dashboards. This module teaches you to write the queries that reach them.

SQL is not the point. The production questions are the point. SQL is the language the data
platform speaks, and without it you are reading someone else's summary of your own system instead
of querying it directly. The gap this module closes is specific: by the end, you can sit down at
any trace store, warehouse, or local SQLite file and answer the twelve questions that come up in
every production incident.

---

## What This Module Covers

**Lesson 01: Your Telemetry Is a Table** introduces the operational mindset: every span, eval
verdict, and cost stamp your AI system emits is a queryable row. You load a realistic telemetry
dataset, write the foundational operator queries (`GROUP BY`, aggregate functions, `WHERE` on
time ranges), and answer three production questions: p95 latency by route, total cost by tenant,
and eval pass-rate over a rolling window. The exercise extends `module5-serving/` from Sans Python
with a live SQLite seam and a query runner.

**Lesson 02: Window Functions and CTEs for AI Telemetry** moves to the patterns that answer
questions ordinary aggregations cannot: running totals, per-tenant rank comparisons, rolling
averages over variable windows, and multi-step diagnostic CTEs that walk from a freshness breach
back to the corpus reload that caused it. These are the queries that turn "something changed" into
"exactly this changed, at this time, for this reason."

---

## Who This Is For

You have shipped a governed multi-agent fleet (Sans Python M7) and run your first seam queries
(M5 L14). You can write a `SELECT` and a `WHERE`. This module brings you to the SQL fluency a
Production AI Engineer needs on the job: not DBA depth, but the ability to answer production
questions independently, with a query, not a guess.

---

## The Artifact

Each lesson extends a shared artifact: `module1-sql/`. By the end of Lesson 02 you have a local
telemetry store, a query library of the twelve standard operator queries, and a smoke test that
asserts each query against known data. Module 2 (Batch Ingestion) will extend this store into a
warehouse target and add dbt transformation on top.

---

## Prerequisites

- Sans Python complete through M5 L14 (The Data Seam)
- Python 3.11+, `sqlite3` (stdlib), `duckdb` (optional but recommended for analytic query
  patterns)
- Familiarity with `SELECT`, `FROM`, `WHERE`, `GROUP BY` at the level of M5 L14

---

## Time Estimate

Lesson 01: 60-90 minutes including exercise. Lesson 02: 75-105 minutes including exercise.
