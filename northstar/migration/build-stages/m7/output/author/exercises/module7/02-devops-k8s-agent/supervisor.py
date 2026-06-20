"""The supervisor: route an incident to read-only specialists, assemble a proposal.

This is M4 lesson 03's supervisor-worker pattern, wired as direct calls (no
supervisor library): the supervisor holds one "tool" per specialist, calls each
with a fresh read-only view, reads their findings, and synthesizes a remediation.
The specialists never see each other; the supervisor owns every context boundary.

It is also the M4 control plane in miniature: it checks the operator-owned
kill-switch before dispatch and again before any change, and it routes EVERY
remediation through the HITL gate. The supervisor can diagnose on its own
authority; it cannot change the cluster on its own authority. That asymmetry is
the whole artifact — an incident-response agent that must not make things worse.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from audit import AuditLog
from hitl import Decision, HITLGate, Rejected
from killswitch import Halted, KillSwitch
from k8s_mock import MockCluster
from mock_llm import Remediation, synthesize_remediation
from specialists import Finding, LogReader, MetricsReader, ReadOnlyView, StateInspector


@dataclass
class Incident:
    """The trigger payload: an alert pointing at a pod."""

    pod_name: str
    namespace: str
    alert: str


@dataclass
class IncidentResult:
    outcome: str  # "halted" | "diagnosed" | "remediated" | "blocked" | "no-fix"
    reason: str = ""
    findings: list[Finding] = field(default_factory=list)
    proposal_key: str | None = None
    remediation: Remediation | None = None
    applied: dict | None = None
    correlation_id: str = ""


class Supervisor:
    """Owns the team, the control plane, and the gate. No library does this for it."""

    def __init__(self, cluster: MockCluster, gate: HITLGate, kill: KillSwitch,
                 audit: AuditLog) -> None:
        self._cluster = cluster
        self._gate = gate
        self._kill = kill
        self._audit = audit
        # One "tool" per specialist — calling it is delegating to a worker.
        self._specialists = [StateInspector(), LogReader(), MetricsReader()]

    def handle(self, incident: Incident) -> IncidentResult:
        cid = self._audit.correlation_id

        # --- Control plane: kill-switch checked before any work. ------------- #
        if self._kill.tripped():
            self._audit.record("supervisor", "halted", reason="kill_switch")
            return IncidentResult("halted", reason="kill_switch", correlation_id=cid)

        self._audit.record("supervisor", "triage",
                           pod=incident.pod_name, alert=incident.alert)

        # --- 1. Fan out to read-only specialists (fresh view each). ---------- #
        findings: list[Finding] = []
        for specialist in self._specialists:
            view = ReadOnlyView(self._cluster)  # read-only handle, no write verb
            finding = specialist.inspect(view, incident.pod_name)
            self._audit.record(
                specialist.name, "inspect",
                hypothesis=finding.hypothesis, confidence=finding.confidence,
            )
            findings.append(finding)

        # --- 2. Synthesize: the supervisor assembles, workers don't. --------- #
        evidence = self._merge_evidence(findings)
        remediation = synthesize_remediation(findings, evidence)
        self._audit.record("supervisor", "propose_remediation",
                           change=remediation.change, deployment=remediation.deployment)

        # No actionable change derived -> escalate, do not invent one.
        if not remediation.change:
            self._audit.record("supervisor", "no_fix",
                               reason="no confident remediation")
            return IncidentResult(
                "no-fix", reason="no confident remediation",
                findings=findings, remediation=remediation, correlation_id=cid,
            )

        # --- Control plane: re-check the switch before proposing a change. --- #
        if self._kill.tripped():
            self._audit.record("supervisor", "halted", reason="kill_switch")
            return IncidentResult("halted", reason="kill_switch",
                                  findings=findings, correlation_id=cid)

        # --- 3. HITL gate: the ONLY path to a cluster change. ---------------- #
        blast_radius = (
            f"1 deployment ({remediation.deployment}) in ns "
            f"{remediation.namespace}; reversible via stored rollback"
        )
        proposal = self._gate.propose(remediation, blast_radius=blast_radius)
        try:
            applied = self._gate.request_and_commit(proposal)
        except Rejected:
            return IncidentResult(
                "blocked", reason="remediation not approved",
                findings=findings, proposal_key=proposal.key,
                remediation=remediation, correlation_id=cid,
            )

        self._audit.record("supervisor", "resolved", key=proposal.key)
        return IncidentResult(
            "remediated", reason="approved and applied",
            findings=findings, proposal_key=proposal.key,
            remediation=remediation, applied=applied, correlation_id=cid,
        )

    @staticmethod
    def _merge_evidence(findings: list[Finding]) -> dict:
        """Fold the specialists' evidence into one dict the synthesizer reads."""
        merged: dict = {}
        for f in findings:
            merged.update(f.evidence)
        return merged
