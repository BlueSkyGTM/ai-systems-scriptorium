"""Cost governor — the operator's spend ceiling.

A bug in a normal service throws and stops. A bug in an agent keeps reasoning,
keeps calling tools, and keeps billing. The budget is the limit that fires
before the invoice does. This is the per-task governor from M4 lesson 06,
narrowed to one agent.

Deliberately boring deterministic code — no model, no judgment. A budget you
ask a model to enforce is a budget the model can talk its way out of.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class BudgetBreach(Exception):
    """Raised when a cap is crossed. The loop catches this and stops."""


@dataclass
class Budget:
    """A stack of caps at two time scales.

    - ``max_usd``   — the per-task dollar allowance (maps to business value:
                      "this task is worth at most $X to me").
    - ``max_turns`` — the iteration cap; the runaway loop that never decides
                      it is done hits this wall.

    Callers ``charge()`` before each model call. On any breach the charge
    raises ``BudgetBreach`` and the run stops before the next action.
    """

    max_usd: float
    max_turns: int
    spent_usd: float = 0.0
    turns: int = 0
    _ledger: list = field(default_factory=list)  # (label, usd) per charge

    def check(self) -> None:
        """Raise BudgetBreach if a cap is already crossed, without charging.

        The loop calls this before each model call so a run that is already
        over budget stops before paying for one more action.
        """
        self._enforce()

    def charge(self, usd: float, label: str = "model_call") -> None:
        """Record one turn's spend, then enforce. Raises BudgetBreach on breach."""
        self.spent_usd += usd
        self.turns += 1
        self._ledger.append((label, usd))
        self._enforce()

    def _enforce(self) -> None:
        if self.spent_usd > self.max_usd:
            raise BudgetBreach(
                f"per-task budget exceeded: ${self.spent_usd:.4f} > ${self.max_usd:.4f}"
            )
        if self.turns > self.max_turns:
            raise BudgetBreach(
                f"iteration cap exceeded: {self.turns} > {self.max_turns}"
            )

    def remaining_usd(self) -> float:
        return max(0.0, self.max_usd - self.spent_usd)

    def summary(self) -> dict:
        return {
            "spent_usd": round(self.spent_usd, 4),
            "max_usd": self.max_usd,
            "turns": self.turns,
            "max_turns": self.max_turns,
        }
