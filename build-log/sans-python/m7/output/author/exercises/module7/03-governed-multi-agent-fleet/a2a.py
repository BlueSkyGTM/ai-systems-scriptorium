"""A2A — typed agent-to-agent handoff messages between the team's nodes.

Two agents that talk by passing raw strings will eventually lie to each other
(M4 lesson 02). The fix is a wire contract: a typed message the sender fills and
the receiver validates, so a malformed handoff fails at the boundary instead of
three steps downstream as a confident wrong answer.

This is the A2A task shape from M4 lesson 02 — a skill, typed input, an explicit
lifecycle (``submitted -> working -> completed | failed``), and typed artifacts —
expressed as Python dataclasses because the control plane is Python. The M4
chapter types the same contract in TypeScript for cross-language handoffs; the
fields are identical. Every handoff also carries a ``correlation_id`` so the
audit trail can thread one task across every agent that touches it (the fourth
accountability clause: evidence).

The architect hands a plan to the coders; the coders hand diffs to the reviewer
and tester; the reviewer hands a verdict back. Each hop is one of these messages,
validated on receipt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# A2A task lifecycle (M4 lesson 02). The client sees state transitions, not the
# peer's internals; a stall is visible instead of silent.
STATES = ("submitted", "working", "completed", "failed", "canceled")


class A2AError(Exception):
    """A handoff that fails validation at the boundary. Never a wrong answer
    three turns later that costs an afternoon to trace."""


@dataclass
class A2ATask:
    """A typed task message — not a string shoved into a prompt.

    - ``skill``         names the capability requested; the receiver matches it
                        against the roles it can perform (its 'Agent Card').
    - ``sender`` / ``recipient`` are registry agent ids — who is talking to whom.
    - ``correlation_id`` threads the whole chain for the audit (one id, user
                        request to final outcome).
    - ``input``         is the typed payload the skill expects.
    """

    skill: str
    sender: str
    recipient_role: str
    correlation_id: str
    input: dict = field(default_factory=dict)

    def validate(self, accepted_skills: set[str]) -> None:
        """Receiver-side check. A skill the recipient cannot perform fails here."""
        if self.skill not in accepted_skills:
            raise A2AError(
                f"unaccepted skill {self.skill!r} for role handling "
                f"{sorted(accepted_skills)} (handoff from {self.sender})"
            )
        if not self.correlation_id:
            raise A2AError("handoff missing correlation_id — audit chain would break")


@dataclass
class A2AResult:
    """The typed result of a task — an explicit state plus typed artifacts.

    A mismatch returns ``state='failed'`` with a reason at the wire, not a wrong
    answer downstream.
    """

    task_skill: str
    sender: str
    correlation_id: str
    state: str
    artifacts: dict = field(default_factory=dict)
    reason: str = ""

    def __post_init__(self) -> None:
        if self.state not in STATES:
            raise A2AError(f"invalid A2A state {self.state!r}; expected one of {STATES}")

    @property
    def ok(self) -> bool:
        return self.state == "completed"

    @classmethod
    def completed(cls, task: A2ATask, agent_id: str, **artifacts) -> "A2AResult":
        return cls(task.skill, agent_id, task.correlation_id, "completed", dict(artifacts))

    @classmethod
    def failed(cls, task: A2ATask, agent_id: str, reason: str) -> "A2AResult":
        return cls(task.skill, agent_id, task.correlation_id, "failed", {}, reason)
