# Module 3: Orchestration

Module 2 built the loader. It still runs because you run it. A pipeline that depends on you remembering
to type a command is stale by the weekend and silently broken the first time you take a day off. This
module makes the pipeline run by itself, on a schedule, with retries when a step flakes, and an alert
when something it cannot fix goes wrong.

You author and debug the graph; you do not operate the cluster. That is the AI engineer's half of
orchestration: the DAG that moves your data, its dependencies, its retry policy, and its alerts are
yours, while the workers that execute it are the platform's. The lessons teach the Airflow DAG model
because that is the vocabulary every data team and every interview uses; the artifact runs Prefect,
which executes the same DAG offline so you can build and test it without standing up a server.

## What This Module Covers

**The DAG: Tasks and Dependencies** models the pipeline as a directed acyclic graph: tasks with
dependencies the scheduler runs in order, each task's output feeding the next. The order stops being a
thing you remember and becomes a contract the scheduler enforces.

**Retries and Idempotency** makes the run resilient. A task that fails on a transient blip retries with
a backoff instead of paging a human; and because Module 2's load is an idempotent merge, retrying the
ingest is safe. The two ideas are a pair: a retry is only safe when the task can be re-run.

**Scheduling and Backfill** turns the cadence into configuration. The flow takes a run date, so the same
code runs tonight on a cron schedule or backfills last week's missed days, and the merge keeps the
backfill idempotent.

**Alerting on Breach** wires Module 2's freshness gate as the final task. A stale corpus raises, the run
fails, and an on-failure hook fires the alert. This is where the SLO you defined stops being a number in
a table and becomes a signal someone acts on.

## Who This Is For

You finished Module 2: you have a loader that ingests, transforms, and checks freshness. Now you make it
a system that runs on its own and surfaces its own failures. You write the DAG and own its policy; you
do not run the orchestration platform.

## The Artifact

You build `module3-orchestration/`, a Prefect flow that reuses the Module 2 loader and freshness check as
tasks: extract, ingest, transform, and a freshness gate, with retries, a documented nightly schedule, a
backfill loop, and an on-failure alert hook. It runs offline with no server. Module 4 adds the streaming
and change-data-capture sources that cannot wait for the nightly run.

## Prerequisites

- Module 2 complete (the `module2-ingestion/` loader and freshness check)
- Python 3.11+ and `prefect` (one pip install); the flow runs offline with an ephemeral local server
- Comfort with functions, decorators, and the Module 2 ingest contract

## Time Estimate

Each lesson runs 70 to 100 minutes including its exercise. The first Prefect run takes a minute to spin
up its local server; after that the loop is fast.
