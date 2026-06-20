"""The latency budget — measured per stage and end to end, enforced as a gate.

A voice agent lives or dies by one number: the time from the user finishing a
word to hearing a reply. The working target is ~450-600 ms mouth-to-ear. This
module reads the per-stage simulated latencies off a finished `TurnResult`,
sums them, and decides PASS/FAIL against a configured budget. That verdict is
the operator surface the student drives in M8: the budget is config, the gate
is enforced, and a blown budget stops the turn instead of shipping a laggy one.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The voice latency budget, mouth to ear. Roughly 450-600 ms is the working
# target below which conversation stops feeling broken. Configurable.
DEFAULT_BUDGET_MS = 600.0
DEFAULT_TARGET_MS = 500.0  # the design target the default stage costs sum to


@dataclass
class LatencyReport:
    """A per-stage + end-to-end latency report with a budget verdict."""

    stage_latencies_ms: dict
    budget_ms: float = DEFAULT_BUDGET_MS

    @property
    def total_ms(self) -> float:
        return sum(self.stage_latencies_ms.values())

    @property
    def within_budget(self) -> bool:
        return self.total_ms <= self.budget_ms

    @property
    def headroom_ms(self) -> float:
        """Positive = under budget; negative = over (blown)."""
        return self.budget_ms - self.total_ms

    def render(self) -> str:
        """A human-readable budget table for the smoke output."""
        lines = ["Latency budget (mouth to ear)", "-" * 38]
        width = max((len(n) for n in self.stage_latencies_ms), default=9)
        for name, ms in self.stage_latencies_ms.items():
            bar = "#" * int(ms / 10)
            lines.append(f"  {name:<{width}}  {ms:7.1f} ms  {bar}")
        lines.append("-" * 38)
        verdict = "PASS" if self.within_budget else "FAIL (BUDGET BLOWN)"
        lines.append(
            f"  {'TOTAL':<{width}}  {self.total_ms:7.1f} ms"
            f"   budget {self.budget_ms:.0f} ms  ->  {verdict}"
        )
        lines.append(f"  headroom: {self.headroom_ms:+.1f} ms")
        return "\n".join(lines)


def measure(turn_result, budget_ms: float = DEFAULT_BUDGET_MS) -> LatencyReport:
    """Build a `LatencyReport` from a finished `TurnResult`."""
    return LatencyReport(
        stage_latencies_ms=dict(turn_result.stage_latencies_ms),
        budget_ms=budget_ms,
    )


class BudgetExceeded(Exception):
    """Raised by `enforce` when a turn blows the latency budget."""


def enforce(report: LatencyReport) -> LatencyReport:
    """The gate. Pass the report through if within budget, else raise.

    This is the operator-surface enforcement point: in production you wire this
    to drop the turn, fall back to a cheaper stage, or alert — never silently
    ship a turn that took 1.2 s. Here it raises so the smoke + tests can assert
    a deliberately blown budget is caught.
    """
    if not report.within_budget:
        raise BudgetExceeded(
            f"latency {report.total_ms:.1f} ms exceeds budget {report.budget_ms:.0f} ms"
            f" (over by {-report.headroom_ms:.1f} ms)"
        )
    return report
