# Exercise: Scheduling and Backfill

**Goal**: Confirm `pipeline_flow` is date-parameterized, document a nightly cron schedule, write a
backfill loop that runs the flow across three dates, and prove the loop is safe to repeat because the
MERGE is idempotent.

**Why**: A scheduled pipeline that is not idempotent cannot be safely backfilled; the MERGE contract
from M2 is what makes re-running a date produce zero drift.

---

## Steps

This exercise extends `module3-orchestration/`. Find the directory, run the existing `smoke.py` gate,
and confirm it passes before adding anything. You are continuing a build, not starting one.

**1. Confirm `pipeline_flow` accepts `run_date`.**

Open `pipeline_flow.py` and verify the flow signature:

```python
def pipeline_flow(run_date=None, corpus_csv=None, db_path=None, freshness_now_ts=None):
    if run_date is None:
        run_date = datetime.utcnow().strftime("%Y-%m-%d")
```

If this default branch is missing, add it. Call the flow twice: once with `run_date=None` (should
default to today) and once with an explicit date string. Both calls must succeed.

**2. Document the nightly cron schedule.**

At the top of `pipeline_flow.py`, add the deployment comment block exactly as shown:

```python
# Schedule: nightly at 02:00 UTC. To activate in a Prefect deployment:
#   from prefect.schedules import CronSchedule
#   @flow(..., schedules=[CronSchedule(cron="0 2 * * *")])
# The artifact is tested by calling pipeline_flow() directly; no server is required.
```

This documents the production shape without requiring a live Prefect server. `0 2 * * *` means
minute zero, hour two, any day, any month, any weekday: 02:00 UTC nightly. Do not attach the
schedule decorator to the function itself; the test path is direct invocation.

**3. Write the backfill loop.**

Add a `backfill.py` in `module3-orchestration/`:

```python
for run_date in ["2026-01-13", "2026-01-14", "2026-01-15"]:
    pipeline_flow(run_date=run_date, corpus_csv=csv, db_path=db)
# Because the M2 MERGE is idempotent, re-running a date that already loaded is safe.
```

The loop calls the same flow three times with consecutive dates. No new code beyond the loop: same
tasks, same dependency graph, only `run_date` changes per iteration.

**4. Write the idempotency test.**

In `smoke.py` (or a new `tests/test_backfill.py`), add:

- Run the backfill loop over `["2026-01-13", "2026-01-14", "2026-01-15"]`.
- Query `COUNT(*)` from `source_documents` (or the relevant versioned table) and record the count.
- Run the same three-date backfill loop a second time.
- Query `COUNT(*)` again and assert the count is unchanged.

The assertion proves idempotency: re-loading dates that are already in the database adds zero new
`source_document` versions. The MERGE found nothing new to insert on the second pass.

---

## Done When

- `pipeline_flow(run_date="2026-01-13", corpus_csv=..., db_path=...)` runs offline and returns
  without error.
- The cron comment block (`0 2 * * *`) is present at the top of `pipeline_flow.py`.
- `python backfill.py` runs all three dates without error (or the loop is callable from `smoke.py`).
- The idempotency assertion passes: a second backfill over the same three dates adds zero new rows
  to the versioned documents table.

---

## Stretch

Write a second backfill range that overlaps the first:

```python
for run_date in ["2026-01-14", "2026-01-15", "2026-01-16"]:
    pipeline_flow(run_date=run_date, corpus_csv=csv, db_path=db)
```

Assert that this overlapping run also adds zero new versions for 2026-01-14 and 2026-01-15 (already
loaded) and the correct count of new rows for 2026-01-16 (the new date). This confirms the MERGE
applies per-row, not per-run: already-seen rows are skipped regardless of which date range triggered
the load.
