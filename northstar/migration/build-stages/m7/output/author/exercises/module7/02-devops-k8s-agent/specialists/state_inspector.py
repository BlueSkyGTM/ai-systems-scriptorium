"""StateInspector — reads pod phase, restart count, and termination reason.

Mirrors `kubectl describe pod`: the object's current phase, how many times it
has restarted, and the container's last termination reason. [MS-Learn: a
CrashLoopBackOff pod with a rising RESTARTS count and an OOMKilled termination
reason is the canonical signature; `kubectl describe pod` surfaces it.]
Read-only: it reports state and the owning deployment so the supervisor knows
what a remediation would target, but it changes nothing.
"""

from __future__ import annotations

from .base import Finding, ReadOnlyView


class StateInspector:
    name = "state_inspector"

    def inspect(self, view: ReadOnlyView, pod_name: str) -> Finding:
        pod = view.get_pod(pod_name)

        if pod.phase == "CrashLoopBackOff":
            conf = 0.8 if pod.last_termination_reason == "OOMKilled" else 0.55
            return Finding(
                source=self.name,
                summary=(
                    f"pod {pod.name} in CrashLoopBackOff, "
                    f"{pod.restart_count} restarts, last reason "
                    f"{pod.last_termination_reason or 'unknown'}"
                ),
                hypothesis=(
                    "container repeatedly killed and restarted"
                    + (" (OOMKilled)" if pod.last_termination_reason == "OOMKilled" else "")
                ),
                confidence=conf,
                evidence={
                    "phase": pod.phase,
                    "restart_count": pod.restart_count,
                    "last_termination_reason": pod.last_termination_reason,
                    "owner_deployment": pod.owner_deployment,
                    "namespace": pod.namespace,
                },
            )
        return Finding(
            source=self.name,
            summary=f"pod {pod.name} phase {pod.phase}, {pod.restart_count} restarts",
            hypothesis="pod state nominal",
            confidence=0.2,
            evidence={"phase": pod.phase, "restart_count": pod.restart_count},
        )
