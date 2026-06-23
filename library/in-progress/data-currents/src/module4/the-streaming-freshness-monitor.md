# The Streaming Freshness Monitor

A batch freshness check that runs once a night is useless for a stream that must be current within seconds. You cannot poll your way to real-time; you measure lag continuously, per event, per source.

That is the shift this lesson makes. M2 measured freshness as the age of a nightly load, in hours. Here you measure it as the gap between when an event was written and when it landed in the index, in seconds. Same question, different clock, different cadence.

## What Lag Means in a Stream

Every event carries an `event_time`: the moment the source system produced it. The consumer applies it to the index at `applied_time`. The lag is that gap:

```
lag = applied_time - event_time
```

When the consumer keeps pace, `applied_time` is close to the current wall clock and the gap is small. When the consumer falls behind, events queue up in the topic and the gap grows. Your SLO is a ceiling on that gap, measured in seconds, per source.

This is not a new idea. The unit changes. M2 asked whether a source's last successful load was more than 25 hours old. This asks whether a source's last applied event is more than 5 seconds behind. The breach condition is the same shape; the time scale is three orders of magnitude tighter.

## The LagMonitor

The monitor records lag per source and answers two questions: what is the current lag for this source, and has it breached the SLO?

```python
class LagMonitor:
    def __init__(self, slo_seconds: float = 5.0):
        self.slo_seconds = slo_seconds
        self._samples: dict[str, list[float]] = {}

    def record(self, source_id, event_time, applied_time=None) -> float:
        if applied_time is None:
            applied_time = time.time()
        lag = applied_time - event_time           # how far behind the index is
        self._samples.setdefault(source_id, []).append(lag)
        return lag

    def is_breached(self, source_id) -> bool:
        lag = self.current_lag(source_id)
        return lag is not None and lag > self.slo_seconds

    def status(self, source_id) -> str:
        lag = self.current_lag(source_id)
        if lag is None:
            return "no_data"
        return "breached" if lag > self.slo_seconds else "ok"
```

`applied_time` defaults to `time.time()` so production code calls `record(source_id, event_time)` and the wall clock fills in. For tests, you inject a fixed timestamp and the result is deterministic. No sleeps, no flakiness.

`current_lag` reads the most recent sample for a source. The list of samples lets you compute derived metrics later (peak lag, average over a window) without re-querying. The monitor accumulates; you decide what to do with the history.

## Why Injectable Clocks Matter

The batch freshness check in M2 also took an injectable `now_ts`. The pattern is the same: a real clock makes a test non-deterministic; an injected timestamp makes it a pure function. You pass `event_time=1000.0, applied_time=1003.0` and the lag is exactly 3.0 seconds. Pass `applied_time=1010.0` and the lag is 10.0 seconds, which breaches a 5-second SLO. The test does not depend on how fast the machine runs.

This is not a testing convenience. It is the contract between the monitor and the systems that call it: the caller controls the time, the monitor computes the lag. In production, the caller passes the wall clock. In a load test, the caller compresses time to replay a day of events in seconds.

## The Production Setting

Microsoft Fabric Real-Time Intelligence stores streaming events in an Eventhouse, a KQL database built for high-frequency append workloads. [MS-Learn Real-Time Intelligence / Eventhouse: https://learn.microsoft.com/fabric/real-time-intelligence/eventhouse] In that environment you query lag with KQL: compute `ingestion_time() - event_time` per row, aggregate by source, alert when the result exceeds your threshold. There is no built-in freshness SLA enforcement in Fabric Real-Time Intelligence; you build the lag check on top of the query layer, the same way M2 built `freshness_check.py` on top of the audit log.

The `LagMonitor` here is the local stand-in for that production monitoring. When a source breaches its SLO, `is_breached` returns `True`; that result feeds the same alerting M3 wired, the `on_failure` hook that fires the notification before anything downstream continues.

## Core Concepts

- Streaming freshness is event-to-applied lag measured in seconds, continuously, per source; the batch equivalent (last-load age in hours, checked nightly) is too slow for a stream.
- `lag = applied_time - event_time` is the single number that answers "how far behind is this source?"; a per-source SLO is the ceiling on that number.
- An injectable `applied_time` makes the lag computation a pure function: tests inject timestamps and assert exact lag values without sleeps or wall-clock dependence.
- A breach from `is_breached` or `status` routes to the same alerting channel M3 wired; the monitor detects, the orchestrator acts.

The streaming leg that cannot wait for a nightly run now has the check that matches its cadence. Seconds-scale lag, measured continuously, surfaced the moment it breaches. That is the seam closing.

Module 5 is where the batch and streaming legs land together, the warehouse and the lakehouse, and what it means to query across both.

<div class="claude-handoff" data-exercise="exercises/module4/the-streaming-freshness-monitor/">

**Build It in Claude Code**: Build a `LagMonitor` in `module4-streaming/` that records per-source event-to-applied lag against a configurable seconds-scale SLO; implement `record`, `current_lag`, `is_breached`, `status`, and `report` with `applied_time` as an injectable parameter so tests never touch the wall clock; finalize `smoke.py` to assert that a consumer applying events close to their event time is `ok`, and that a consumer whose `applied_time` is far past `event_time` is `breached`, both deterministically with injected timestamps and no real sleeps.

</div>
