"""drift.py -- log a rolling quality metric (the M5 observability move).

A serving stack can be perfectly healthy while the answers quietly get worse: the
corpus shifted, the model updated, the traffic mix changed. No infrastructure
metric moves. Quality drift is caught only by sampling a quality signal over live
traffic and watching it against a baseline.

This is a small, offline version of that: a rolling window of per-answer quality
scores, a mean over the window, and a breach flag when the mean falls below an SLO
floor. Operator surface: the drift metric and its SLO threshold.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, List


@dataclass
class DriftReading:
    n: int
    rolling_mean: float
    baseline: float
    floor: float
    breached: bool


class DriftMonitor:
    """Rolling-window quality monitor with an SLO floor.

    `baseline` is the quality you measured at deploy (e.g. eval faithfulness).
    `floor` is how far below baseline you tolerate before the SLO is breached.
    """

    def __init__(self, baseline: float, *, window: int = 20, tolerance: float = 0.15) -> None:
        self.baseline = baseline
        self.floor = max(0.0, baseline - tolerance)
        self.window = window
        self._scores: Deque[float] = deque(maxlen=window)

    def record(self, score: float) -> DriftReading:
        self._scores.append(float(score))
        mean = sum(self._scores) / len(self._scores)
        return DriftReading(
            n=len(self._scores),
            rolling_mean=mean,
            baseline=self.baseline,
            floor=self.floor,
            breached=mean < self.floor,
        )

    def history(self) -> List[float]:
        return list(self._scores)


if __name__ == "__main__":
    mon = DriftMonitor(baseline=0.9, window=5, tolerance=0.2)
    # A run that degrades: the rolling mean eventually drops below the 0.7 floor.
    for s in [0.9, 0.9, 0.8, 0.4, 0.3, 0.2, 0.1]:
        r = mon.record(s)
        flag = "BREACH" if r.breached else "ok"
        print(f"n={r.n} mean={r.rolling_mean:.2f} floor={r.floor:.2f} -> {flag}")
