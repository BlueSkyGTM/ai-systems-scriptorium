# Exercise: The Streaming Freshness Monitor

## Goal

Build a `LagMonitor` that records per-source event-to-applied lag against a seconds-scale SLO and reports `ok` or `breached`, with an injectable clock so every assertion is deterministic.

## Why

A batch freshness check that fires once a night cannot guard a stream. The monitor you build here gives the streaming leg a continuous, per-source freshness signal that feeds the same alerting M3 wired.

## Steps

Work inside `module4-streaming/`. Read the current state of that directory before adding to it; you are extending a build, not starting one.

1. Add `lag_monitor.py` with the `LagMonitor` class. Implement four methods on top of the constructor the lesson provides:
   - `current_lag(source_id) -> float | None` -- return the most recent lag sample for the source, or `None` if no samples exist.
   - `is_breached(source_id) -> bool` -- return `True` when the current lag exceeds `slo_seconds`.
   - `status(source_id) -> str` -- return `"ok"`, `"breached"`, or `"no_data"`.
   - `report() -> list[dict]` -- return one dict per tracked source with keys `source_id`, `current_lag`, and `status`.

2. Wire `LagMonitor` into the module. If `module4-streaming/` already has a consumer or apply step, import and call `monitor.record(source_id, event_time, applied_time=applied_time)` at the point where an event lands. If not, add a stub caller in `smoke.py` that simulates the record calls directly.

3. Finalize `smoke.py` to assert both cases:
   - **Within SLO**: call `monitor.record("src_a", event_time=1000.0, applied_time=1002.0)` (2-second lag against a 5-second SLO) and assert `monitor.status("src_a") == "ok"`.
   - **Breached**: call `monitor.record("src_b", event_time=1000.0, applied_time=1010.0)` (10-second lag) and assert `monitor.status("src_b") == "breached"` and `monitor.is_breached("src_b") is True`.

4. Add a `tests/test_lag_monitor.py` with the same two assertions as named `pytest` functions. No imports beyond `pytest` and `lag_monitor`; no sleeps.

## Done When

- `python smoke.py` exits 0 and prints a line per source showing its lag and status.
- `python -m pytest` passes the within-SLO and breach assertions, both deterministically, with no real sleeps and no network calls.
- Both runs are offline.

## Stretch

Add `max_lag(source_id) -> float | None` that returns the largest lag seen across all samples for that source. In `tests/test_lag_monitor.py`, add a test that records three samples (2s, 4s, 8s) against a 5-second SLO and asserts `max_lag` returns `8.0` and `is_breached` returns `True` (because the most recent sample at 8s exceeds the SLO). Then add a `report()` variant that includes `max_lag` per source and assert the breach case appears in the report output.
