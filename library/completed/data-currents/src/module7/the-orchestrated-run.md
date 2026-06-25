# The Orchestrated Run

Composition is a claim until something runs it on a schedule and proves it.

## What Each Task Does

Orchestration turns five functions into one scheduled, retryable, verifiable run. You define the retry policy per task to match the failure domain. 

```python
@task(name="batch_ingest", retries=2)
@task(name="stream_apply", retries=2)
@task(name="land_lakehouse", retries=1, retry_delay_seconds=0.1)
@task(name="capture_lineage", retries=1, retry_delay_seconds=0.1)
@task(name="freshness_gate", retries=0)
```

You apply higher retry counts to network-bound I/O tasks like batch ingest and streaming. You give the freshness gate zero retries because a stale corpus is not a transient glitch. A stale corpus means your data is old, and retrying a failed gate adds delay without fixing the underlying staleness. When the gate fails, the run fails immediately. Review the mechanics of DAGs in [M3 DAG Tasks and Dependencies](../module3/the-dag-tasks-and-dependencies.md) and retry semantics in [M3 Retries and Idempotency](../module3/retries-and-idempotency.md).

## What the Smoke Test Proves

The smoke oracle is what makes "it works" a machine fact. You run seven assertion groups against a fresh temp directory: batch leg, streaming leg, lakehouse time-travel, lineage trace, freshness pass, impact analysis, and negative run.

The exact assertion count is 22. A deficient run MUST fail the gate. You verify each condition using the `check()` helper.

```python
def check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    marker = "  " if condition else "!"
    msg = f"[{status}] {marker}{label}"
    if detail:
        msg += f"\n        {detail}"
    print(msg)
    RESULTS.append((label, condition, detail))
    return condition
```

The oracle calculates the final exit status using a summary block.

```python
total   = len(RESULTS)
passed  = sum(1 for _, ok_, _ in RESULTS if ok_)
failed  = total - passed
print(f"Results: {passed}/{total} passed, {failed} failed")
```

## How to Run It

You execute the pipeline, run the oracle, and trigger the formal CI test suite.

```bash
python pipeline_flow.py
python smoke.py
python -m pytest tests/ -v
```

## Running in Deployment

You deploy the pipeline using a nightly cron schedule.

```python
cron='0 2 * * *'
```

This schedule runs the flow at 02:00 UTC every day. Review deployment patterns in [M3 Scheduling and Backfill](../module3/scheduling-and-backfill.md).

## Success Metrics

Your pipeline meets the production bar when specific conditions hold. Smoke exits 0, all 22 assertions pass, and the negative run fails the gate and fires the alert.

## Core Concepts

* Orchestration binds independent data flows into a single scheduled, retryable run.
* Freshness gates use zero retries because stale data indicates systemic failure, not a transient error.
* The smoke oracle provides machine-verified proof of pipeline integrity across 22 assertions.
* A deficient run must fail the gate, fire the alert hook, and abort the process.

The run you cannot prove is a run you cannot ship.

<div class="claude-handoff" data-exercise="exercises/module7/the-orchestrated-run/">
**Inspect It in Claude Code** · Exercise · exercises/module7/the-orchestrated-run/
</div>