"""End-to-end smoke run: a mock K8s incident through a governed agent team.

Stdlib only. No cluster, no kubectl, no Slack, no network. The flow:

    alert: checkout pod in CrashLoopBackOff
      -> supervisor fans out to read-only specialists (logs / metrics / state)
      -> specialists diagnose (they CANNOT mutate the cluster)
      -> supervisor synthesizes a remediation (raise the OOM memory limit)
      -> HITL gate posts a mock-Slack approval card and BLOCKS auto-apply
      -> on a simulated human APPROVE, the remediation is applied once
      -> the pod recovers; the audit trail is complete under one correlation id

Run it:

    python smoke.py

It prints the outcome and exits 0 when the team diagnoses read-only, the gate
blocks auto-apply, the approved fix lands, and the cluster recovers.
"""

from __future__ import annotations

import sys
from pathlib import Path

from audit import AuditLog
from hitl import Decision, HITLGate, MockSlack
from killswitch import KillSwitch
from k8s_mock import crash_looping_cluster
from supervisor import Incident, Supervisor

HERE = Path(__file__).resolve().parent
OUTPUTS = HERE / "outputs"


def build(*, approve: bool, kill_path: Path | None = None,
          audit_path: Path | None = None):
    """Wire a fresh team around a fresh crash-looping cluster.

    `approve=True` scripts the human to click Approve on the Slack card;
    `approve=False` leaves the default (Reject), proving the gate blocks.
    """
    cluster = crash_looping_cluster()
    audit = AuditLog(path=audit_path)
    responder = (lambda _p: Decision.APPROVE) if approve else (lambda _p: Decision.REJECT)
    slack = MockSlack(responder=responder)
    gate = HITLGate(cluster, slack, audit)
    kill = KillSwitch(kill_path or (OUTPUTS / "HALT"))
    supervisor = Supervisor(cluster, gate, kill, audit)
    incident = Incident(
        pod_name="checkout-7f9c-abcde",
        namespace="storefront",
        alert="PodCrashLooping: checkout in storefront restarting repeatedly",
    )
    return cluster, audit, supervisor, incident


def main() -> int:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    audit_path = OUTPUTS / "audit.jsonl"
    if audit_path.exists():
        audit_path.unlink()

    cluster, audit, supervisor, incident = build(approve=True, audit_path=audit_path)
    result = supervisor.handle(incident)

    print(f"correlation : {result.correlation_id}")
    print(f"outcome     : {result.outcome}")
    print(f"reason      : {result.reason}")
    print("findings    :")
    for f in result.findings:
        print(f"  - [{f.source}] {f.hypothesis} (conf {f.confidence})")
    if result.remediation is not None:
        print(f"remediation : {result.remediation.change} on "
              f"deploy/{result.remediation.deployment}")
    print(f"audit trail : {audit.actions()}")

    pod = cluster.get_pod("checkout-7f9c-abcde")
    print(f"pod phase   : {pod.phase} (restarts {pod.restart_count}, "
          f"mem limit {pod.memory_limit_mib}Mi)")
    print(f"applied #   : {len(cluster.applied)} (exactly one, via the gate)")

    ok = (
        result.outcome == "remediated"
        and pod.phase == "Running"
        and len(cluster.applied) == 1
        and "applied" in audit.actions()
        and "verify" in audit.actions()
    )
    if ok:
        print("\nSMOKE PASS: read-only diagnosis -> proposal -> HITL gate -> "
              "approved apply -> recovery, fully audited.")
        return 0
    print(f"\nSMOKE FAIL: unexpected end state ({result.outcome}, {pod.phase}).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
