"""Operator-surface tests for the DevOps K8s troubleshooting agent.

Run:  python -m pytest tests/        (or: python tests/test_smoke.py)

Each test pins one operator surface the M8 student will drive:
  - diagnosis is read-only: a specialist's write attempt is refused
  - the HITL gate BLOCKS an unapproved remediation (no cluster change)
  - an approved remediation applies exactly once and is audited
  - the kill-switch halts the team before it does anything
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Make the scaffold importable whether run from the dir or via `pytest tests/`.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import smoke  # noqa: E402
from audit import AuditLog  # noqa: E402
from hitl import Decision, HITLGate, MockSlack, Rejected  # noqa: E402
from k8s_mock import ReadOnlyViolation, crash_looping_cluster  # noqa: E402
from killswitch import KillSwitch  # noqa: E402
from mock_llm import synthesize_remediation  # noqa: E402
from specialists import LogReader, ReadOnlyView, WriteAttemptRefused  # noqa: E402
from specialists.base import Finding  # noqa: E402


# --------------------------------------------------------------------------- #
# 1. Diagnosis is read-only: a specialist cannot mutate the cluster.
# --------------------------------------------------------------------------- #

def test_specialist_cannot_write_cluster():
    cluster = crash_looping_cluster()
    view = ReadOnlyView(cluster)

    # The read path works...
    finding = LogReader().inspect(view, "checkout-7f9c-abcde")
    assert isinstance(finding, Finding)
    assert "oom" in finding.hypothesis.lower()

    # ...but any write verb on the view is refused.
    try:
        view.apply_remediation(deployment="checkout", namespace="storefront",
                               change={"memory_limit_mib": 256})
        assert False, "expected WriteAttemptRefused"
    except WriteAttemptRefused:
        pass

    # And a guessed mutating attribute is also refused (no write path to find).
    try:
        view.delete_pod("checkout-7f9c-abcde")
        assert False, "expected WriteAttemptRefused for unknown verb"
    except WriteAttemptRefused:
        pass

    # The cluster never changed: still crash-looping, nothing applied.
    assert cluster.get_pod("checkout-7f9c-abcde").phase == "CrashLoopBackOff"
    assert cluster.applied == []


def test_cluster_write_requires_authorization():
    """Even the cluster's own write verb refuses an unauthorized (un-gated) call."""
    cluster = crash_looping_cluster()
    try:
        cluster.apply_remediation(deployment="checkout", namespace="storefront",
                                  change={"memory_limit_mib": 256})
        assert False, "expected ReadOnlyViolation without HITL authorization"
    except ReadOnlyViolation:
        pass
    assert cluster.applied == []


# --------------------------------------------------------------------------- #
# 2. The HITL gate blocks an unapproved remediation.
# --------------------------------------------------------------------------- #

def test_hitl_blocks_unapproved_remediation():
    cluster, audit, supervisor, incident = smoke.build(approve=False)
    result = supervisor.handle(incident)

    assert result.outcome == "blocked", result
    # Nothing was applied to the cluster: still crash-looping.
    assert cluster.get_pod("checkout-7f9c-abcde").phase == "CrashLoopBackOff"
    assert cluster.applied == []
    # The trail shows the proposal, the human's reject, and the block — never an apply.
    actions = audit.actions()
    assert "propose" in actions
    assert "decision" in actions
    assert "blocked" in actions
    assert "applied" not in actions


def test_silence_is_not_a_yes():
    """A gate with the default responder (no explicit approve) must not commit."""
    cluster = crash_looping_cluster()
    audit = AuditLog()
    gate = HITLGate(cluster, MockSlack(), audit)  # default responder = REJECT
    evidence = {"suggested_limit_mib": 192, "memory_limit_mib": 64,
                "owner_deployment": "checkout", "namespace": "storefront"}
    remediation = synthesize_remediation([], evidence)
    proposal = gate.propose(remediation, blast_radius="1 deployment")
    try:
        gate.request_and_commit(proposal)
        assert False, "expected Rejected — silence is not a yes"
    except Rejected:
        pass
    assert cluster.applied == []


# --------------------------------------------------------------------------- #
# 3. An approved remediation applies exactly once and is audited.
# --------------------------------------------------------------------------- #

def test_approved_remediation_applies_once_and_is_audited():
    cluster, audit, supervisor, incident = smoke.build(approve=True)
    result = supervisor.handle(incident)

    assert result.outcome == "remediated", result
    pod = cluster.get_pod("checkout-7f9c-abcde")
    assert pod.phase == "Running"
    assert pod.restart_count == 0
    assert pod.memory_limit_mib == 192  # 1.5x of 118Mi rounded to 32Mi
    # Applied exactly once — the gate is the single write path.
    assert len(cluster.applied) == 1

    actions = audit.actions()
    for required in ("triage", "inspect", "propose", "decision", "applied", "verify"):
        assert required in actions, f"missing {required!r} in audit trail: {actions}"
    # One correlation id threads the whole incident.
    assert all(e.correlation_id == result.correlation_id for e in audit.entries)


# --------------------------------------------------------------------------- #
# 4. The kill-switch halts the team before it does anything.
# --------------------------------------------------------------------------- #

def test_kill_switch_halts_the_team():
    tmp = Path(tempfile.mkdtemp(prefix="k8s-kill-"))
    kill_path = tmp / "HALT"
    kill_path.write_text("operator halt: incident bridge active\n", encoding="utf-8")

    cluster, audit, supervisor, incident = smoke.build(approve=True, kill_path=kill_path)
    result = supervisor.handle(incident)

    assert result.outcome == "halted"
    assert result.reason == "kill_switch"
    # No specialist ran, no proposal, no change.
    assert cluster.applied == []
    assert audit.actions() == ["halted"]
    assert "inspect" not in audit.actions()


if __name__ == "__main__":
    test_specialist_cannot_write_cluster()
    test_cluster_write_requires_authorization()
    test_hitl_blocks_unapproved_remediation()
    test_silence_is_not_a_yes()
    test_approved_remediation_applies_once_and_is_audited()
    test_kill_switch_halts_the_team()
    print("all smoke tests passed")
