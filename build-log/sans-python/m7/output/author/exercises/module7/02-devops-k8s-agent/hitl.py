"""Propose-then-commit HITL gate — a mock Slack approval before ANY change.

This is M4 lesson 08, unchanged: the agent does not act on an irreversible thing
on its own authority. It persists a proposal with an idempotency key, surfaces a
real case for a human to judge (intent, blast radius, rollback), and commits ONLY
on a positive acknowledgement. Silence is not a yes. The "Slack" here is a mock —
a function that posts an approval card and returns the human's decision — so the
smoke path is offline and deterministic. [verify: Slack interactive messages
carry action buttons whose clicks POST back to the app; the real adapter swaps
`MockSlack` for that callback.]

The gate is the only path to `cluster.apply_remediation`. No approval, no change.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum

from audit import AuditLog
from k8s_mock import MockCluster
from mock_llm import Remediation


class Decision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PENDING = "PENDING"


class Rejected(RuntimeError):
    """Raised when a proposal is not positively acknowledged."""


@dataclass
class Proposal:
    """A persisted, idempotent record of an intended change awaiting a human."""

    key: str
    remediation: Remediation
    blast_radius: str
    status: Decision = Decision.PENDING
    result: dict | None = None


class MockSlack:
    """A stand-in for a Slack approval card.

    `post_approval` renders the case a human needs and returns their decision.
    The decision is supplied by the operator out of band (here: a scripted
    responder) — the gate never defaults to APPROVE on its own.
    """

    def __init__(self, responder=None) -> None:
        # responder: (Proposal) -> Decision. Default is REJECT (silence != yes).
        self._responder = responder or (lambda _p: Decision.REJECT)
        self.posted: list[str] = []

    def post_approval(self, proposal: Proposal) -> Decision:
        card = (
            f"*Remediation proposed* `{proposal.key}`\n"
            f"> intent: {proposal.remediation.rationale}\n"
            f"> change: {proposal.remediation.change} "
            f"on deploy/{proposal.remediation.deployment} "
            f"(ns {proposal.remediation.namespace})\n"
            f"> blast radius: {proposal.blast_radius}\n"
            f"> rollback: {proposal.remediation.rollback}\n"
            f"[Approve] [Reject]"
        )
        self.posted.append(card)
        return self._responder(proposal)


class HITLGate:
    """Propose-then-commit. Persists the proposal, commits only on a yes."""

    def __init__(self, cluster: MockCluster, slack: MockSlack, audit: AuditLog) -> None:
        self._cluster = cluster
        self._slack = slack
        self._audit = audit
        self._store: dict[str, Proposal] = {}

    def propose(self, remediation: Remediation, *, blast_radius: str) -> Proposal:
        """Persist the proposed action with an idempotency key. The run pauses
        here until a human answers — silence keeps it PENDING, never commits."""
        key = f"rem-{uuid.uuid4().hex[:10]}"
        proposal = Proposal(key=key, remediation=remediation, blast_radius=blast_radius)
        self._store[key] = proposal
        self._audit.record(
            "hitl", "propose",
            key=key,
            change=remediation.change,
            deployment=remediation.deployment,
            blast_radius=blast_radius,
            rollback=remediation.rollback,
        )
        return proposal

    def request_and_commit(self, proposal: Proposal) -> dict:
        """Post the approval card and commit ONLY on a positive acknowledgement.

        - PENDING/REJECT decision -> raise Rejected, cluster untouched.
        - APPROVE -> apply exactly once through the cluster's guarded write verb,
          verify, and record the outcome. Idempotent on the key.
        """
        if proposal.status is Decision.APPROVE and proposal.result is not None:
            return proposal.result  # already committed: return prior result

        decision = self._slack.post_approval(proposal)
        self._audit.record("human", "decision", key=proposal.key, decision=decision.value)

        if decision is not Decision.APPROVE:
            proposal.status = Decision.REJECT
            self._audit.record("hitl", "blocked", key=proposal.key,
                               reason="not approved — no change applied")
            raise Rejected(f"remediation {proposal.key} not approved")

        # Positive ack: this is the one place the cluster is mutated.
        result = self._cluster.apply_remediation(
            deployment=proposal.remediation.deployment,
            namespace=proposal.remediation.namespace,
            change=proposal.remediation.change,
            _authorized=True,
        )
        proposal.status = Decision.APPROVE
        proposal.result = result
        self._audit.record("hitl", "applied", key=proposal.key, result=result)

        # Post-action verify (HITL move 4): confirm the pod recovered.
        pods = self._cluster.list_pods(proposal.remediation.namespace)
        recovered = all(
            p.phase != "CrashLoopBackOff"
            for p in pods
            if p.owner_deployment == proposal.remediation.deployment
        )
        self._audit.record("hitl", "verify", key=proposal.key, recovered=recovered)
        return result
