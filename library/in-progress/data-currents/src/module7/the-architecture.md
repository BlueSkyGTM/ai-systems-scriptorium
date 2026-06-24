# The Architecture

Batch is comprehensive but stale by morning. CDC is fast but thin; neither alone is sufficient.

## The Dependency DAG

You compose batch and stream into a single execution graph. The batch leg runs first. The stream leg applies CDC events on top of the batch output. The flow then splits to write the Delta lakehouse and capture lineage. Both feed into a terminal freshness gate.

To maintain strict dependencies without creating artificial data blockers, you pass a parameter purely for Prefect's dependency graph. The `stream_results` parameter records the execution edge without imposing a strict data payload requirement.

```python
    The stream_results parameter is accepted (but not read) so Prefect
    records the dependency edge stream_apply -> land_lakehouse.
```

```python
    # ---- DAG ----------------------------------------------------------------
    # Leg 1: batch
    ingest_summary  = batch_ingest(csv_path=csv_path, db_path=db_path)

    # Leg 2: streaming (depends on batch so the corpus store is ready)
    stream_summary  = stream_apply(
        db_path=db_path,
        events=cdc_events,
        lag_monitor=lag_monitor,
        apply_time=stream_apply_time,
        corpus_version=stream_corpus_version,
        now_ts=stream_now_ts,
    )

    # Leg 3: lakehouse (depends on stream for post-stream snapshot)
    lakehouse_summary = land_lakehouse(
        db_path=db_path,
        delta_path=delta_path,
        stream_results=stream_summary,
    )

    # Leg 4: lineage (depends on stream so all version rows exist)
    lineage_summary = capture_lineage(
        db_path=db_path,
        lineage_db_path=lineage_db_path,
        delta_path=delta_path,
        stream_results=stream_summary,
    )

    # Leg 5: freshness gate (terminal; checks both legs)
    freshness_summary = freshness_gate(
        db_path=db_path,
        lag_monitor=lag_monitor,
        batch_now_ts=batch_now_ts,
    )
    # ---- End DAG ------------------------------------------------------------
```

## The Dual Freshness Gate

You cannot trust downstream indexes if inputs violate their SLOs. The batch leg operates on an hours SLO (see [M2 Freshness SLO](../module2/the-batch-freshness-slo.md)). The stream leg operates on a seconds SLO (see [M4 Streaming Monitor](../module4/the-streaming-freshness-monitor.md)). The `freshness_gate` task evaluates both. If either leg breaches its threshold, the task raises a `RuntimeError` and halts the flow.

```python
@task(name="freshness_gate", retries=0)
def freshness_gate(
    db_path: str,
    lag_monitor: LagMonitor,
    *,
    batch_now_ts: str | None = None,
    stream_source_id: str = STREAM_SOURCE_ID,
) -> dict:
    logger = get_run_logger()
    failures: list[str] = []

    # --- Batch leg ---
    batch_results = check_freshness(db_path=db_path, now_ts=batch_now_ts)
    stale_sources = [r for r in batch_results if r["is_stale"]]
    if stale_sources:
        ids = [r["source_id"] for r in stale_sources]
        msg = f"Batch freshness BREACH: stale sources {ids}"
        logger.error(f"[freshness_gate] {msg}")
        failures.append(msg)
    else:
        logger.info("[freshness_gate] batch leg: PASS")

    # --- Stream leg ---
    stream_breached = lag_monitor.is_breached(stream_source_id)
    if stream_breached:
        lag = lag_monitor.current_lag(stream_source_id)
        slo = lag_monitor.slo_seconds
        msg = f"Stream lag BREACH: lag={lag:.2f}s > SLO={slo}s for '{stream_source_id}'"
        logger.error(f"[freshness_gate] {msg}")
        failures.append(msg)
    else:
        logger.info("[freshness_gate] stream leg: PASS")

    if failures:
        raise RuntimeError(
            "[freshness_gate] GATE FAILED — " + "; ".join(failures)
        )

    return {
        "batch_results":    batch_results,
        "stream_lag_ok":    not stream_breached,
        "stream_source_id": stream_source_id,
    }
```

## The Alert Hook

Raising a `RuntimeError` transitions the flow to a `Failed` state. You attach an `on_failure` hook to the flow decorator to catch this state and broadcast the failure (see [M3 Alerting on Breach](../module3/alerting-on-breach.md)).

```python
@flow(
    name="multi-source-corpus-pipeline",
    description=(
        "M7 capstone: multi-source pipeline feeding an AI retrieval system. "
        "Composes M2 batch ingest, M4 CDC streaming, M5 Delta lakehouse, "
        "M6 lineage capture, and a dual freshness gate (hours SLO + seconds SLO). "
        "Schedule: nightly at 02:00 UTC (cron='0 2 * * *')."
    ),
    on_failure=[on_flow_failure],
)
```

```python
def on_flow_failure(flow, flow_run, state):
    """
    Prefect on_failure hook: fires when the flow enters a Failed state.
    Records the alert in ALERTS and prints to stderr.
    """
    message = (
        f"ALERT: flow '{flow.name}' run '{getattr(flow_run, 'name', '?')}' failed "
        f"at {datetime.utcnow().isoformat()} — state={state.name}"
    )
    ALERTS.append({
        "flow":     flow.name,
        "run":      getattr(flow_run, "name", "?"),
        "state":    state.name,
        "fired_at": datetime.utcnow().isoformat(),
        "message":  message,
    })
    print(f"[ALERT HOOK] {message}", file=sys.stderr)
```

## Core Concepts

- The `stream_results` parameter establishes a Prefect execution edge without passing actual data.
- The terminal `freshness_gate` enforces an hours SLO for batch and a seconds SLO for streaming.
- Raising a `RuntimeError` in a terminal task transitions the flow to a `Failed` state and triggers the alert hook.

A healthy stream cannot mask a stalled batch, meaning your production models will hallucinate on outdated context without a dual gate.

<div class="claude-handoff" data-exercise="exercises/module7/the-architecture/">
**Inspect It in Claude Code** · Exercise · exercises/module7/the-architecture/
</div>