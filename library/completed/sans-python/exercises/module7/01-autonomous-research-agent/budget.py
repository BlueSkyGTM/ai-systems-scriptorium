"""Fleet budget — one spend ceiling shared across the whole team.

The M6 budget governed a single agent. A team needs the same governor at a
higher altitude: a research question that fans out to N sub-agents can burn N
times the tokens, and the runaway is now a *fleet* of loops, not one. So the
budget here is shared — the supervisor and every sub-agent charge the same
ledger — and a breach by any one of them stops the team before the next action.

This is the per-task governor from Module 4 (the fleet budget, lesson 06),
narrowed to one research team. Deliberately boring deterministic code: no model,
no judgment. A budget you ask a model to enforce is a budget the model can talk
its way out of.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class BudgetBreach(Exception):
    """Raised when a cap is crossed. The supervisor and sub-agents catch this
    and stop the team before the next action."""


@dataclass
class FleetBudget:
    """A shared stack of caps the whole team draws down.

    - ``max_usd``  — the per-question dollar allowance for the entire team. Maps
                     to business value: "answering this question is worth at most
                     $X." Every sub-agent's spend counts against the same pool.
    - ``max_calls`` — the total model-call cap across all agents; the fleet
                      version of M6's per-agent iteration cap. A team where every
                      sub-agent loops a little can blow this even if no single
                      agent looks runaway.

    Agents ``charge()`` before each model call. On any breach the charge raises
    ``BudgetBreach`` and the run stops before the next action. The ledger is
    labeled per agent so the trace shows who spent what.
    """

    max_usd: float
    max_calls: int
    spent_usd: float = 0.0
    calls: int = 0
    _ledger: list = field(default_factory=list)  # (agent, label, usd) per charge

    def check(self) -> None:
        """Raise BudgetBreach if a cap is already crossed, without charging.

        Callers check before each model call so a team already over budget stops
        before paying for one more action.
        """
        self._enforce()

    def charge(self, usd: float, agent: str, label: str = "model_call") -> None:
        """Record one call's spend against the shared pool, then enforce."""
        self.spent_usd += usd
        self.calls += 1
        self._ledger.append((agent, label, usd))
        self._enforce()

    def _enforce(self) -> None:
        if self.spent_usd > self.max_usd:
            raise BudgetBreach(
                f"fleet budget exceeded: ${self.spent_usd:.4f} > ${self.max_usd:.4f}"
            )
        if self.calls > self.max_calls:
            raise BudgetBreach(
                f"fleet call cap exceeded: {self.calls} > {self.max_calls}"
            )

    def remaining_usd(self) -> float:
        return max(0.0, self.max_usd - self.spent_usd)

    def by_agent(self) -> dict:
        """Spend grouped by agent — the per-role token accounting an operator reads."""
        out: dict = {}
        for agent, _label, usd in self._ledger:
            out[agent] = round(out.get(agent, 0.0) + usd, 4)
        return out

    def summary(self) -> dict:
        return {
            "spent_usd": round(self.spent_usd, 4),
            "max_usd": self.max_usd,
            "calls": self.calls,
            "max_calls": self.max_calls,
            "by_agent": self.by_agent(),
        }
