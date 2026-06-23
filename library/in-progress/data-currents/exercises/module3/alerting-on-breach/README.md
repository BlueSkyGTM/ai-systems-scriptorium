# Alerting on Breach

**Goal**: Close `module3-orchestration/` by making the freshness gate the final DAG task and wiring an on-failure hook that records an alert when any source is stale.

**Why**: A breach the orchestrator does not surface is a breach that stays hidden. This exercise completes the module's compounding chain: the `freshness_gate` task reuses M2's `check_freshness`, raises on a stale source to fail the Prefect run, and the `on_failure` hook fires the alert automatically.

## Before You Touch Code

Read `src/module3/alerting-on-breach.md` for the why, then read this brief for the what. Open `module3-orchestration/pipeline_flow.py` and read its current state. The DAG, retry logic, and schedule are already in place; you are extending, not replacing.

## Steps

1. Import `check_freshness` from `module2-ingestion/freshness_check.py` at the top of `pipeline_flow.py`.

2. Add the `freshness_gate` task exactly as shown in the lesson (with `retries=0`). It calls `check_freshness`, collects any stale results, and raises a `RuntimeError` naming the stale `source_id` values.

3. Move `freshness_gate` to the final position in `pipeline_flow`: call it after `transform`, passing `db_path` and the optional `now_ts` argument.

4. Add the module-level `ALERTS` list and the `on_flow_failure` hook exactly as shown in the lesson.

5. Wire the hook into the flow decorator:

   ```python
   @flow(name="corpus-pipeline", on_failure=[on_flow_failure])
   ```

6. Finalize `smoke.py` with two assertions:

   - **Clean run**: call `pipeline_flow` with the real corpus data. Assert the run completes without raising and that `ALERTS` is empty afterward.
   - **Breach fires alert**: call `pipeline_flow` with a `now_ts` far enough in the future that at least one source exceeds its `max_age_hours`. Assert the run raises (or returns a Failed state) and that `ALERTS` is non-empty after the call.

   Reset `ALERTS` between the two cases so assertions are independent.

7. Make sure `python -m pytest` covers the same two assertions as named tests in the existing test file (or a new `tests/test_alerting.py`).

## Done When

- `python smoke.py` exits 0 with both assertions passing: the clean run completes with an empty `ALERTS` list, and the stale-source run fails the flow and leaves `ALERTS` non-empty.
- `python -m pytest` passes the same two assertions as named tests.
- Both run offline, with no external services.

## Stretch

Assert that the alert payload in `ALERTS[0]` contains the specific `source_id` of the stale source, not just a non-empty list. Update `on_flow_failure` to extract the stale source names from the failure state message and record them in the alert dict.
