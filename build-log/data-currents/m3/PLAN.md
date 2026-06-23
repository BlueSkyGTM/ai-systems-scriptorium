# Module 3 — Orchestration — Build Plan (self-locked)

Status: **PLAN SELF-LOCKED 2026-06-21** (straight-through mandate; `GATE-LOCK-PLAN` self-cleared,
`GATE-APPROVE-SHIP` self-cleared M3–M8). M3 takes the M2 ingestion pipeline and schedules it: a DAG of
tasks with dependencies, retries on failure, a schedule + backfill, and an alert when a task fails or a
freshness SLO breaches. Authoring/debugging the graph, not operating the cluster.

## The stage in one line

M2 built the loader; M3 makes it run by itself, on time, and tell you when it does not. Seam: the AI
engineer owns the DAG that moves data (its dependencies, retries, and alerts), not the Airflow workers.

## Settled decisions

1. **Throughline extends M2.** `module3-orchestration/` orchestrates the M2 `ingest.py` + dbt build +
   `freshness_check.py` as a DAG. The reuse is real: the DAG's tasks call the M2 artifact.
2. **Teach Airflow/Prefect; run a real offline orchestrator.** The lessons teach the DAG model
   (tasks, dependencies, operators, retries, schedules) as Airflow/Prefect express it, grounded in
   MS-Learn (Apache Airflow job in Fabric Data Factory). The runnable artifact PREFERS **Prefect**
   (pip, runs a flow locally + unit-testable, offline); FALLBACK to a small stdlib DAG runner
   (topological order + retry/backoff + an alert hook) if Prefect is not cleanly offline-runnable. The
   artifact-engineer decides at build time and reports which held.
3. **Tasks are idempotent.** Because M2's load is an idempotent MERGE, a retried or backfilled task is
   safe to re-run. M3 leans on that property; it does not re-teach the merge.
4. **The alert is the freshness gate.** The DAG's final task runs M2's `freshness_check.py`; a breach
   fails the run and fires the alert hook. This is where M2's SLO becomes an operational signal.

## Proposed M3 split (5 lessons, one idea each)

| # | Lesson (slug) | One idea | Kind |
|---|---------------|----------|------|
| 0 | `00-overview` | A pipeline that runs by hand is not a system; here is the DAG, retries, schedule, and alert. | concept |
| 1 | `the-dag-tasks-and-dependencies` | A pipeline is a directed acyclic graph of tasks; the scheduler runs them in dependency order. | build |
| 2 | `retries-and-idempotency` | Tasks fail; idempotent tasks plus retries with backoff make the run resilient instead of fragile. | build |
| 3 | `scheduling-and-backfill` | The DAG runs on a schedule and backfills a date range; the nightly cadence and catching up are configuration, not code. | build |
| 4 | `alerting-on-breach` | The orchestrator is where a failed task or a breached freshness SLO becomes an alert; closes the module by wiring M2's freshness gate as the final task. | build |

## The artifact + oracle (locked first)

`module3-orchestration/`: a DAG/flow (`pipeline_flow.py`) with tasks extract -> ingest (M2) -> dbt build
-> freshness_check, plus retry config and an alert hook. Oracle (`smoke.py` + `pytest`, offline): the
DAG has the expected tasks + dependency edges (no cycles); a deliberately failing task retries N times
then marks the run failed; a successful run executes tasks in topological order and lands the M2 gold
tables; the freshness task fails the run + fires the alert hook when a source is stale; a backfill over
two dates runs the DAG twice idempotently. Negative case: a cyclic DAG / a missing dependency is
rejected, and a stale source fails the run.

## Fleet plan

- **Haiku fetch (2):** (a) MS-Learn Apache Airflow in Fabric Data Factory + dbt+Airflow pattern +
  scheduling/retries/monitoring, verified URL pack; (b) Prefect-offline feasibility + the
  Airflow-vs-Prefect DAG vocabulary (flows/tasks/retries/schedules) from authoritative docs.
- **Sonnet artifact-engineer (1):** builds + tests `module3-orchestration/`; confirms Prefect-vs-runner
  path; returns byte-identical code + a green run.
- **Sonnet authors (4):** L1–L4 around the locked code + grounding.
- **Opus conductor:** overview, schema/oracle lock, review (Zinsser + STYLE + STANDARDS), em-dash sweep
  + `mdbook build`, ship + push.
