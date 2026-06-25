# Retries and Idempotency

A flaky network blip fails one task and you do not want a human paged for a glitch that fixes itself
on the second try. Retries handle it. But a retry that re-runs a bad task can corrupt your data just
as surely as the original failure. The retry is only as safe as the task it re-runs.

## Why Retries Exist

An orchestrator treats each task as a unit of work with a pass/fail result. When a task fails, the
default behavior is to fail the entire flow. That is correct for logic errors. It is wrong for
transient ones: a brief SQLite lock, a momentary network timeout, a file system hiccup that clears in
under a second. These are not bugs in your code; they are noise in the environment, and failing a full
run on them wastes the work already done.

Both Airflow and Prefect give you a task-level retry knob. In Airflow, the parameters are `retries`
(the count of additional attempts) and `retry_delay` (how long to wait between them; set
`retry_exponential_backoff=True` to widen the gap each attempt). In Prefect, the equivalents are
`retries=` and `retry_delay_seconds=`. Same idea, same shape: re-attempt the failing task before
failing the run. The flow's other tasks are unaffected while the retry is in flight.

The DAG from the prior lesson wires `extract` and `ingest` in sequence. Those are the two I/O tasks,
and I/O tasks are where transient failures live. The artifact sets retries on both:

```python
@task(name="extract", retries=2, retry_delay_seconds=0.1)
def extract(run_date, corpus_csv):
    """retries=2 -> two more attempts on a transient failure before the task (and the flow) fails."""
    if not os.path.isfile(corpus_csv):
        raise FileNotFoundError(f"[extract] CSV not found: {corpus_csv}")
    return corpus_csv

@task(name="ingest", retries=2, retry_delay_seconds=0.1)
def ingest(csv_path, db_path):
    """retries=2 guards against transient SQLite lock contention. The MERGE underneath is idempotent."""
    return run_ingest(csv_path=csv_path, db_path=db_path)
```

`retries=2` means the task gets two additional attempts after the first failure, for three total tries
before the flow gives up. `retry_delay_seconds=0.1` is a short wait: in a test environment, a 0.1-second
pause is enough to clear the contention; in production you would set it higher.

## The Safety Condition

Here is what the retry mechanism does not guarantee: that re-running the task is safe.

Consider a task that appends rows. The first attempt inserts 120 rows, then dies on the commit. The
orchestrator retries. The second attempt inserts 120 rows again, this time successfully. You now have
240 rows. The retry made the failure worse.

This is the classic partial-success problem, and retries expose it. A task is only safe to retry if
re-running it after a partial success produces the same result as a clean first run. That property
has a name: **idempotency**.

A non-idempotent task (append rows, increment a counter, send an email) can corrupt state on retry.
An idempotent task (check-then-insert on a unique key, an upsert, a content-addressed write) cannot.

## Why the Ingest Task Is Safe

The `ingest` task calls `run_ingest`, which calls the `merge_gold` function you built in M2. That MERGE
is keyed on `(doc_id, content_hash)`: if the row already exists, the merge skips it. If the `ingest`
task completes its first attempt up to the SQLite commit and then the commit itself fails, the retry
runs the full merge again. The rows that made it in are skipped; the row that did not is inserted.
The result is identical to a clean first run.

Run the same ingest twice on an unchanged corpus and `merge_gold` returns `0` the second time. That
return value is the idempotency proof. A retried ingest cannot double-load because the contract
forbids it: same `(doc_id, content_hash)` pair, same skip path, every time.

The pairing is tight: `retries=2` on the `ingest` task is only valid because `merge_gold` underneath
it is idempotent. Remove idempotency and the retry parameter becomes a liability.

## What This Means at Scale

A production corpus pipeline runs nightly. Over a year, a transient SQLite lock happens. Without
retries, a human wakes up to a failed run, investigates, finds nothing wrong, and re-runs manually.
With retries plus an idempotent load, the pipeline heals itself in under a second and the on-call
engineer never sees it.

The same rule applies to the `extract` task. If the corpus CSV is momentarily unavailable because a
writer holds a lock, `retries=2` gives the pipeline three chances to read it before failing. The
extract task only reads and returns the path; reading is inherently idempotent.

Retries are a cheap configuration. Idempotency is design work. You pay for idempotency once, in M2,
and it makes every retry downstream free of risk.

## Core Concepts

- Both Airflow (`retries`, `retry_delay`) and Prefect (`retries=`, `retry_delay_seconds=`) retry a
  failing task a fixed number of times before failing the flow; the parameter names differ, the semantics
  are the same.
- A retry is only safe if the task is idempotent: re-running it after a partial success must produce
  the same result as a clean first run.
- A non-idempotent task (append, increment, send) retried after a partial success corrupts state; the
  retry mechanism itself becomes the hazard.
- The `ingest` task carries `retries=2` because `merge_gold` beneath it is keyed on `(doc_id,
  content_hash)`: the same pair always skips, so a retried ingest inserts zero duplicate rows.

<div class="claude-handoff" data-exercise="exercises/module3/retries-and-idempotency/">

**Build It in Claude Code**: Extend `module3-orchestration/` by adding `retries=2, retry_delay_seconds=0.1` to the `extract` and `ingest` task decorators, then write a pytest test that monkeypatches `run_ingest` to raise on the first call and succeed on the second, asserts the flow still completes, and asserts the task was attempted exactly twice; add a second assertion that re-running the ingest on an unchanged corpus returns zero new `source_document` versions, proving the underlying MERGE makes the retry safe.

</div>
