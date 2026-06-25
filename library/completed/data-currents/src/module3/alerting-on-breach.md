# Alerting on Breach

A pipeline that fails quietly is worse than one that fails loudly. When a source goes stale and the run ends with a zero exit and no noise, the problem hides until a user notices. The orchestrator's job is to make a breach impossible to ignore.

You close the module here by wiring M2's freshness check as the final task in the DAG, so a stale corpus fails the run, and a failure hook fires the alert before anything downstream continues.

## Why the Gate Lives Last

The DAG runs in order: `extract -> ingest -> transform -> freshness_gate`. Placing the gate at the end is deliberate. You want the data to land first; then you want the system to verify the contract was met. A gate that runs before the load is checking the previous run's data. A gate at the end checks this run's data.

When `freshness_gate` raises, Prefect marks the flow as `Failed`. Nothing downstream runs. The state machine does the work you would otherwise do by hand: scan the log, find the failure, escalate.

## The Gate Task

The gate reuses `check_freshness` from `freshness_check.py`, the function M2 built. It does not rewrite the logic; it calls it, reads the result, and raises when anything is stale.

```python
@task(name="freshness_gate", retries=0)
def freshness_gate(db_path, now_ts=None):
    """Raises -> Prefect Failed state -> on_failure hook fires, if ANY source is stale."""
    results = check_freshness(db_path=db_path, now_ts=now_ts)   # the M2 check, reused
    stale = [r for r in results if r["is_stale"]]
    if stale:
        raise RuntimeError(f"[freshness_gate] STALE sources detected: {[r['source_id'] for r in stale]}.")
    return results
```

`retries=0` is intentional. A retry cannot fix a stale source; only a fresh ingest can. Retrying here would waste time and mask the breach. The gate's only job is to detect and surface.

## The On-Failure Hook

Prefect's `@flow` decorator accepts an `on_failure` list: callables that run when the flow reaches a `Failed` state. You wire the alert there.

```python
ALERTS: list[dict] = []

def on_flow_failure(flow, flow_run, state):
    """Prefect on_failure hook (flow, flow_run, state): record an alert when the run fails."""
    ALERTS.append({"flow": flow.name, "run": flow_run.name, "state": state.name})
    print(f"[ALERT HOOK] flow '{flow.name}' run '{flow_run.name}' failed: {state.name}", file=sys.stderr)

@flow(name="corpus-pipeline", on_failure=[on_flow_failure])
def pipeline_flow(...):
    ...
    freshness_results = freshness_gate(db_path=db_path)   # the gate as the final DAG task
    ...
```

`ALERTS` is a module-level list, which makes it inspectable in tests: after a run, check that it is non-empty and contains the expected flow name. The `print` to `stderr` is the local stand-in for a real notification channel. In production, the same hook calls an external service.

## The Production Equivalent

In Microsoft Fabric Data Factory, you wire failure notifications via pipeline failure alerts and the Data Activator integration; a failure can trigger an Outlook or Teams activity that reaches whoever is on call. [MS-Learn pipeline alerts: https://learn.microsoft.com/fabric/data-factory/create-alerts-for-pipeline-runs] Airflow uses an `on_failure_callback` on the DAG or the operator, with the same contract: the callback fires on failure, you route to your notification channel inside it.

The hook here is the local, offline stand-in for those production channels. It does not ship a page or a Teams message; that is the wiring you add when you move the pipeline to a cluster. What it does ship is the pattern: the orchestrator, not a human, is responsible for routing a breach to the channel that gets it fixed.

## Core Concepts

- The freshness gate runs last in the DAG, after the load completes, so it measures this run's data and fails the run on the same contract M2 defined.
- A gate task with `retries=0` is correct: a retry cannot fix a stale source, and retrying hides the breach instead of surfacing it.
- Prefect's `on_failure` hook fires when the flow enters the `Failed` state; Airflow's `on_failure_callback` and Fabric Data Activator cover the same role in production.
- `ALERTS` is a module-level list that makes failure assertions deterministic in tests: a breach must produce a non-empty list with the flow name, not just a printed message.

The on-call engineer who reads a `[ALERT HOOK]` line at 2 a.m. already knows the source, the run, and the state; the breach is named before they open a dashboard. That is what the gate is for.

Module 4 adds streaming and change-data-capture for the sources that cannot wait for the nightly run.

<div class="claude-handoff" data-exercise="exercises/module3/alerting-on-breach/">

**Build It in Claude Code**: Make `freshness_gate` the final task in `pipeline_flow.py`, calling M2's `check_freshness` and raising a `RuntimeError` naming the stale source IDs when any source is stale; add the module-level `ALERTS` list and `on_flow_failure` hook wired via `@flow(on_failure=[on_flow_failure])`; then finalize `smoke.py` to assert that a fresh corpus run completes clean with `ALERTS` empty, and that injecting a future `now_ts` (making at least one source stale) fails the run and leaves `ALERTS` non-empty.

</div>
