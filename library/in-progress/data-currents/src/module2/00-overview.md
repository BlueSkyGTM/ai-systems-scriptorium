# Module 2: Batch Ingestion

In Module 1 you queried the corpus and walked its lineage. Something had to fill those tables first.
This module builds it: the nightly reload that ingests raw documents, cleans them, versions them, and
lands the `source_documents` and `chunks` tables the lineage walk reads. You treat the reload as a
production system, not a cron job that overwrites everything and hopes.

The difference is in four moves. The load is an idempotent merge, so re-running is safe and a changed
document is a new version, not a silent overwrite. The transform runs as a medallion, so raw data is
cleaned and made trustworthy before anything queries it. The transform is dbt, so it is versioned,
reviewed, and gated by tests. And the whole thing carries a freshness SLO, so a stale index trips a
gate instead of quietly serving yesterday's answer.

## What This Module Covers

**The Incremental Merge** replaces truncate-and-reload with an idempotent upsert keyed on a content
hash. Re-running an unchanged source changes nothing; a changed document writes a new version and
keeps the old. This is what makes the lineage walk from Module 1 have versions to walk.

**The Medallion Pattern** structures the transform into bronze (raw), silver (cleaned and typed), and
gold (serving) layers. The cleaning happens in silver; the tables the book queries are gold. Each
layer raises the trust you can place in the data.

**dbt as the Transform Layer** turns those layers into versioned models with tests that gate
promotion. A model is a `SELECT` that materializes; a test asserts a property; `dbt build` runs the
models and then the tests, and a failing test blocks the build.

**The Batch Freshness SLO** makes staleness a measured objective. You record every load, compare the
last successful load's age to a per-source target, and fail a gate when a source goes stale. It writes
the `corpus_loads` rows the Module 1 freshness-breach query reads.

## Who This Is For

You finished Module 1: you can write operator SQL over telemetry and walk lineage. Now you build the
pipeline that produces the corpus those queries read. This is the data engineer's batch layer seen
from the AI engineer's seat: you author and test the transform and own the freshness target, you do
not operate the cluster.

## The Artifact

You build `module2-ingestion/`, which extends the Module 1 store. It holds a dbt medallion project
(bronze, silver, gold models plus schema tests), an `ingest.py` loader that performs the idempotent
merge and writes a load-audit row, and a `freshness_check.py` gate. The gold tables it produces are
the ones Module 1 queries, so the lineage walk runs unchanged against your output. Module 3 takes this
pipeline and orchestrates it on a schedule with retries and alerting.

## Prerequisites

- Module 1 complete (the `module1-sql/` store and the lineage walk)
- Python 3.11+, `duckdb`, and `dbt-duckdb` (one pip install); everything runs offline
- Comfort with `SELECT`, `GROUP BY`, and CTEs at the Module 1 level

## Time Estimate

Each lesson runs 70 to 110 minutes including its exercise. The dbt lesson takes longest the first
time, because installing and wiring the project is its own small task.
