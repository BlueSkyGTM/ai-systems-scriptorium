"""Fleet budget guard — per-agent caps under one team ceiling.

The M6 budget governed a single agent. The fleet adds two things and nothing
else: **attribution** (every charge is tagged to an agent) and a **team ceiling**
(the total no agent, and no swarm of small agents, may cross). This is the M4
lesson-13 ``FleetBudgetGuard`` — the lesson-06 cap logic reused, not retyped.

Why per-agent attribution is not optional has a price tag. A real fleet capped
only its manager loop and watched that manager spawn twelve retries on a flaky
API, absorbing eight times the normal spend by morning — because nothing
attributed the burn to the runaway workers underneath. Cap the manager *and* the
workers. This guard trips on a per-agent cap OR the team cap, whichever comes
first, so neither a single greedy agent nor a swarm of small ones slips through.

Deliberately boring deterministic code. A budget you ask a model to enforce is a
budget the model can talk its way out of.
"""

from __future__ import annotations

from dataclasses import dataclass


class BudgetBreach(Exception):
    """Raised when a per-agent or team cap is crossed. The orchestrator catches
    this and stops the fleet before the next action."""


@dataclass
class TaskBudget:
    """One agent's cap. This is the M6/lesson-06 governor, unchanged in spirit:
    a dollar allowance the agent's spend is metered against."""

    max_usd: float
    spent_usd: float = 0.0
    calls: int = 0

    def charge(self, usd: float) -> None:
        self.spent_usd += usd
        self.calls += 1
        if self.spent_usd > self.max_usd:
            raise BudgetBreach(
                f"per-agent cap: ${self.spent_usd:.4f} > ${self.max_usd:.4f}"
            )


class FleetBudgetGuard:
    """Per-agent TaskBudgets under one team ceiling.

    The cap logic lives in ``TaskBudget`` (the lesson-06 governor); the fleet only
    adds attribution and the team total. ``charge`` raises ``BudgetBreach`` the
    moment either wall is hit — and the message names which wall, so an operator
    reading the trace knows whether to raise one agent's cap or the team's.
    """

    def __init__(self, team_daily_usd: float, per_agent: dict[str, TaskBudget]):
        self.team_daily_usd = team_daily_usd
        self.per_agent = per_agent
        self.team_spent = 0.0
        self._ledger: list = []  # (agent_id, usd) per charge — the per-role accounting

    def charge(self, agent_id: str, usd: float) -> None:
        """Charge one model call to its agent, then to the team. Raises on breach.

        The per-agent charge is attempted first: a single greedy agent trips its
        own wall. If it clears, the team total is summed — so a swarm of small
        agents, each under its own cap, still hits the team ceiling.
        """
        if agent_id not in self.per_agent:
            raise BudgetBreach(f"no budget on record for agent {agent_id!r}")
        self._ledger.append((agent_id, usd))
        # Per-agent wall (lesson 06). Sum the team total even if this raises, so
        # team_spent reflects the attempted spend for the trace.
        self.team_spent += usd
        try:
            self.per_agent[agent_id].charge(usd)
        except BudgetBreach as exc:
            raise BudgetBreach(f"agent {agent_id}: {exc}") from None
        # Team wall (the fleet's addition).
        if self.team_spent > self.team_daily_usd:
            raise BudgetBreach(
                f"team cap: ${self.team_spent:.4f} > ${self.team_daily_usd:.4f}"
            )

    def by_agent(self) -> dict:
        """Spend grouped by agent — the per-role accounting an operator reads."""
        out: dict = {}
        for agent_id, usd in self._ledger:
            out[agent_id] = round(out.get(agent_id, 0.0) + usd, 4)
        return out

    def summary(self) -> dict:
        return {
            "team_spent_usd": round(self.team_spent, 4),
            "team_daily_usd": self.team_daily_usd,
            "by_agent": self.by_agent(),
        }

    @classmethod
    def from_registry(cls, registry: dict) -> "FleetBudgetGuard":
        """Build the guard straight from the registry — every agent's per-agent
        cap and the team ceiling are read from the contract, not hardcoded."""
        per_agent = {
            a["id"]: TaskBudget(max_usd=float(a["budget_daily_usd"]))
            for a in registry["agents"]
        }
        return cls(team_daily_usd=float(registry["team_daily_usd"]), per_agent=per_agent)
