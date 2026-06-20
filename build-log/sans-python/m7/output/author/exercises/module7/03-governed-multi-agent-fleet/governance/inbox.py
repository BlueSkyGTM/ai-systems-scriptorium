"""Shared HITL inbox — many proposers, one queue, a human on the merge.

The merge is the one irreversible action the SWE team takes, so it is the one
action no agent may auto-execute. The reviewer and tester can approve in spirit;
the *merge* waits for a person. This is the M4 lesson-08 propose-then-commit
protocol with more proposers (M4 lesson 13 shared-inbox-HITL): every agent's
proposed action routes to one central, trackable inbox; a principal approves or
rejects; nothing destructive auto-executes.

The governance rule is strict and learned the hard way: approve only through the
inbox, with an ``inbox_id`` on every decision. A team that let an engineer
approve a deploy by DM "just this once" could not answer "evidenced by what?" at
the incident review — that broke the evidence clause. So this inbox refuses an
off-channel approval: you commit a proposal by its ``inbox_id`` or you do not
commit it at all.

An inbox nobody uses is worse than no inbox; it manufactures false confidence.
The orchestrator suspends the run at the merge until a decision lands here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


class InboxError(Exception):
    """An illegal inbox operation — an off-channel approval, a double-commit, a
    missing proposal. The merge does not happen."""


@dataclass
class Proposal:
    """A proposed action awaiting a human. The agent's run suspends here."""

    inbox_id: str
    agent_id: str
    correlation_id: str
    action: str           # e.g. "merge"
    summary: str          # what the human is approving, in one line
    payload: dict = field(default_factory=dict)
    state: str = "pending"   # pending -> approved | rejected
    decided_by: str = ""
    decision_reason: str = ""


class SharedInbox:
    """One queue for the whole fleet. Proposals in, human decisions out."""

    def __init__(self) -> None:
        self._queue: dict[str, Proposal] = {}

    def new_id(self) -> str:
        return "inbox-" + uuid.uuid4().hex[:10]

    def submit(self, *, agent_id: str, correlation_id: str, action: str,
               summary: str, payload: dict | None = None) -> str:
        """An agent proposes an action. Returns the inbox_id the run waits on.

        The agent's run suspends at this point — the proposal is durable in the
        queue and nothing executes until a human decides through ``approve``.
        """
        inbox_id = self.new_id()
        self._queue[inbox_id] = Proposal(
            inbox_id=inbox_id,
            agent_id=agent_id,
            correlation_id=correlation_id,
            action=action,
            summary=summary,
            payload=payload or {},
        )
        return inbox_id

    def pending(self) -> list[Proposal]:
        """The operator's work queue — everything awaiting a decision."""
        return [p for p in self._queue.values() if p.state == "pending"]

    def get(self, inbox_id: str) -> Proposal:
        if inbox_id not in self._queue:
            raise InboxError(f"no proposal with inbox_id {inbox_id!r}")
        return self._queue[inbox_id]

    def approve(self, inbox_id: str, *, by: str, reason: str = "") -> Proposal:
        """Approve through the inbox, by id. The ONLY path to a commit.

        There is no ``approve_anything`` and no off-channel approval — you hold an
        ``inbox_id`` or you do not approve. That is the queue discipline the fleet
        adds on top of lesson 08's protocol.
        """
        proposal = self.get(inbox_id)
        if proposal.state != "pending":
            raise InboxError(
                f"proposal {inbox_id} already {proposal.state}; cannot re-decide"
            )
        if not by:
            raise InboxError("an approval must name the human principal (evidence clause)")
        proposal.state = "approved"
        proposal.decided_by = by
        proposal.decision_reason = reason
        return proposal

    def reject(self, inbox_id: str, *, by: str, reason: str = "") -> Proposal:
        proposal = self.get(inbox_id)
        if proposal.state != "pending":
            raise InboxError(f"proposal {inbox_id} already {proposal.state}")
        proposal.state = "rejected"
        proposal.decided_by = by
        proposal.decision_reason = reason
        return proposal

    def is_approved(self, inbox_id: str) -> bool:
        """The gate the orchestrator checks before it merges. Default: not approved."""
        return inbox_id in self._queue and self._queue[inbox_id].state == "approved"
