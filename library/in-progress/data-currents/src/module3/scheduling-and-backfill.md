# Scheduling and Backfill

The pipeline that only runs when you remember to run it will be stale by the weekend. A schedule makes the cadence the system's job, and backfill is how you recover the days it missed.

You have a flow that extracts, ingests, transforms, and gates freshness. Right now you run it with `python pipeline_flow.py`. That works once. A nightly corpus load that depends on a human deciding to open a terminal is not a nightly load; it is a hope. A schedule eliminates the decision.

## The Date Parameter Is the Key

The flow accepts a `run_date`. When you call it without one, it defaults to today:

```python
@flow(name="corpus-pipeline", on_failure=[on_flow_failure])
def pipeline_flow(run_date=None, corpus_csv=None, db_path=None, freshness_now_ts=None):
    if run_date is None:
        run_date = datetime.utcnow().strftime("%Y-%m-%d")
    ...
```

That default is what the nightly run uses. The explicit argument is what the backfill uses. Same flow, same tasks, same dependency graph: only `run_date` changes. This is the design choice that makes scheduling trivial and backfill free.

## The Schedule Is Configuration

A nightly run at 02:00 UTC is a cron expression:

```
0 2 * * *
```

`0 2 * * *` means: minute zero, hour two, any day, any month, any weekday. In Prefect, you attach this to a deployment, not to the flow function:

```python
# Schedule: nightly at 02:00 UTC. To activate in a Prefect deployment:
#   from prefect.schedules import CronSchedule
#   @flow(..., schedules=[CronSchedule(cron="0 2 * * *")])
# The artifact is tested by calling pipeline_flow() directly; no server is required.
```

The comment documents the production shape without requiring a live Prefect server to test the logic. The flow is the unit of work; the deployment is what binds it to the clock. You can build, test, and prove correctness entirely by calling `pipeline_flow()` directly.

In Airflow, the equivalent is the `schedule` parameter on a DAG (the current name; older Airflow used `schedule_interval`, which is now deprecated):

```python
with DAG("corpus-pipeline", schedule="0 2 * * *", catchup=True) as dag:
    ...
```

`schedule="0 2 * * *"` is the same cron, the same nightly cadence. The parameter name is different; the intent is identical. [Airflow DAG scheduling and catchup: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html]

## Backfill Is a Loop

If the pipeline missed three nights, you run it three times, once per date:

```python
for run_date in ["2026-01-13", "2026-01-14", "2026-01-15"]:
    pipeline_flow(run_date=run_date, corpus_csv=csv, db_path=db)
# Because the M2 MERGE is idempotent, re-running a date that already loaded is safe.
```

No new code. No special backfill mode. The same `pipeline_flow` function, called in a loop over the date range you missed. Each invocation is independent, and the results are identical whether the loop ran once or twice: the M2 MERGE compares incoming rows against what already exists and skips rows that are already loaded. Re-running 2026-01-13 after it already ran produces no new `source_document` versions; the MERGE finds nothing new to insert.

In Airflow, the same recovery uses `catchup=True` on the DAG definition combined with a backfill command. When `catchup=True`, Airflow creates a DAG run for each missed schedule interval automatically on startup. The manual path is `airflow dags backfill --start-date 2026-01-13 --end-date 2026-01-15 corpus-pipeline`. The semantics match: run the DAG once per date in the range. [Airflow backfill: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html]

## Idempotency Is the Contract That Makes This Safe

Backfill is only safe because the underlying operation is idempotent. The M2 MERGE is not `INSERT`; it is `INSERT OR IGNORE` combined with a version comparison. Running it a second time for the same date finds the same rows already in the table and inserts nothing. The `source_documents` version count stays flat.

Without that contract, backfill is dangerous: every re-run adds duplicate rows, the version history lies, and the freshness check sees counts that do not reflect reality. The MERGE design in M2 was not just about incrementalism; it was about making the pipeline safe to run more than once, which is exactly what scheduling and backfill require.

## Core Concepts

- The `run_date` parameter is what separates a scheduled nightly run from a backfill: the same flow runs tonight or last Tuesday; only the argument changes.
- A cron schedule (`0 2 * * *`) is configuration attached to a deployment, not to the flow function; the flow itself is testable offline with no server.
- Airflow's `schedule` parameter (current; `schedule_interval` is deprecated) and Prefect's `CronSchedule` express the same nightly cadence; `catchup=True` plus the backfill command recover missed intervals.
- Backfill is safe only because the M2 MERGE is idempotent: re-running a date that already loaded adds zero new versions, so the loop can run twice with identical results.

The cadence is now the system's responsibility, and the system's memory goes back as far as you tell it. That is a different class of reliability than remembering to open a terminal.

<div class="claude-handoff" data-exercise="exercises/module3/scheduling-and-backfill/">

**Build It in Claude Code**: In `module3-orchestration/`, confirm `pipeline_flow` accepts a `run_date` argument (defaulting to today when omitted); add a documented `CronSchedule(cron="0 2 * * *")` comment block showing how to attach the nightly schedule in a Prefect deployment; write a backfill loop that calls `pipeline_flow` across three consecutive dates; then write a test that runs the same three-date backfill twice and asserts the second run adds zero new `source_document` versions to the database, proving the MERGE idempotency holds across repeated loads.

</div>
