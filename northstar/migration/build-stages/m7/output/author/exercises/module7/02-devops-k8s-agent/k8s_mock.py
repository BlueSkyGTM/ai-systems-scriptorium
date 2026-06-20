"""A mock Kubernetes cluster — deterministic pod / log / metric state.

No real cluster, no kubectl, no network. The smoke path needs a cluster that
behaves the same on every laptop, so this is one: a small in-memory object that
answers the read-only queries a real `kubectl get/describe/logs/top` would, and
exposes exactly one mutating verb (`apply_remediation`) the HITL gate guards.

The split that matters is enforced here, not narrated: the read methods return
plain data; the single write method records an applied action and changes pod
state. A read-only specialist is handed this object but is wired (see
`specialists/`) so it can call only the read methods. The agent's tool surface is
the boundary — the same lesson AKS teaches with the RBAC Reader role, which can
list and describe objects but cannot mutate them. [MS-Learn: AKS RBAC Reader
grants read-only namespace access and cannot even view Secrets — a privilege-
escalation guard.]

Production swaps this object for the Kubernetes API behind a read-only
credential; the specialists' code does not change, because they only ever call
the read verbs. That is the portable seam.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

PodPhase = Literal["Running", "Pending", "CrashLoopBackOff", "Failed"]


class ReadOnlyViolation(PermissionError):
    """Raised if read-only code reaches for a mutating cluster verb.

    This should never trip on a clean run. It exists so a specialist that tries
    to write fails loudly instead of silently mutating production.
    """


@dataclass
class Pod:
    name: str
    namespace: str
    phase: PodPhase
    restart_count: int
    # The container's last termination reason, as `kubectl describe` would show.
    last_termination_reason: str
    # Lines `kubectl logs <pod> --previous` would return for the crashed run.
    logs: list[str] = field(default_factory=list)
    # The deployment that owns this pod (what a remediation actually edits).
    owner_deployment: str = ""
    # Resource limits the pod was scheduled with (None == unset).
    memory_limit_mib: int | None = None


@dataclass
class PodMetric:
    name: str
    namespace: str
    cpu_millicores: int
    memory_mib: int
    # The pod's memory limit, repeated here so the metrics reader can flag OOM.
    memory_limit_mib: int | None = None


class MockCluster:
    """An in-memory cluster with read verbs and one guarded write verb."""

    def __init__(self) -> None:
        self._pods: dict[str, Pod] = {}
        self._metrics: dict[str, PodMetric] = {}
        # Every mutation that lands is recorded so a test can prove the cluster
        # changed only through the one approved path.
        self.applied: list[dict] = []

    # --- construction (test/smoke setup, not an agent-facing verb) ----------- #

    def add_pod(self, pod: Pod, metric: PodMetric) -> None:
        self._pods[pod.name] = pod
        self._metrics[metric.name] = metric

    # --- READ verbs: what a read-only specialist may call -------------------- #

    def get_pod(self, name: str) -> Pod:
        return self._pods[name]

    def list_pods(self, namespace: str | None = None) -> list[Pod]:
        pods = list(self._pods.values())
        if namespace is not None:
            pods = [p for p in pods if p.namespace == namespace]
        return sorted(pods, key=lambda p: p.name)

    def get_logs(self, name: str, *, previous: bool = False) -> list[str]:
        # `previous=True` mirrors `kubectl logs <pod> --previous`: the crashed
        # container's output, which is where a CrashLoopBackOff cause hides.
        return list(self._pods[name].logs)

    def get_metric(self, name: str) -> PodMetric:
        return self._metrics[name]

    # --- WRITE verb: the only way cluster state ever changes ----------------- #

    def apply_remediation(self, *, deployment: str, namespace: str, change: dict,
                          _authorized: bool = False) -> dict:
        """Apply an approved change. The HITL gate passes _authorized=True.

        The `_authorized` flag is the contract, not real security: it documents
        that this verb runs ONLY downstream of a positive human acknowledgement.
        Code that calls it without going through the gate is a bug the audit log
        will expose. The smoke run reaches this exactly once, after approval.
        """
        if not _authorized:
            raise ReadOnlyViolation(
                "apply_remediation called without HITL authorization — "
                "remediation must pass the propose-then-commit gate"
            )
        # Effect of the canonical fix: raise the memory limit so the OOMKilled
        # container stops crash-looping, and reset its restart count.
        for pod in self._pods.values():
            if pod.owner_deployment == deployment and pod.namespace == namespace:
                if "memory_limit_mib" in change:
                    pod.memory_limit_mib = change["memory_limit_mib"]
                    m = self._metrics.get(pod.name)
                    if m is not None:
                        m.memory_limit_mib = change["memory_limit_mib"]
                pod.phase = "Running"
                pod.restart_count = 0
                pod.last_termination_reason = ""
        record = {"deployment": deployment, "namespace": namespace, "change": change}
        self.applied.append(record)
        return record


def crash_looping_cluster() -> MockCluster:
    """The fixture incident: a checkout pod OOMKilled into CrashLoopBackOff.

    Memory limit (64Mi) is below the pod's working set (~118Mi), so the kernel
    OOM-kills the container, Kubernetes restarts it, and it crashes again — the
    textbook CrashLoopBackOff. [MS-Learn: incorrect (too-low) resource limits are
    a named cause of CrashLoopBackOff on AKS.] The fix is to raise the limit.
    """
    cluster = MockCluster()
    cluster.add_pod(
        Pod(
            name="checkout-7f9c-abcde",
            namespace="storefront",
            phase="CrashLoopBackOff",
            restart_count=11,
            last_termination_reason="OOMKilled",
            owner_deployment="checkout",
            memory_limit_mib=64,
            logs=[
                "INFO  starting checkout service v2.3.1",
                "INFO  loading product catalog into cache",
                "WARN  cache warm reached 112Mi resident",
                "FATAL container killed: out of memory (limit 64Mi)",
            ],
        ),
        PodMetric(
            name="checkout-7f9c-abcde",
            namespace="storefront",
            cpu_millicores=120,
            memory_mib=118,
            memory_limit_mib=64,
        ),
    )
    # A healthy neighbor, so diagnosis has to localize rather than blame everything.
    cluster.add_pod(
        Pod(
            name="web-5d44-xyz",
            namespace="storefront",
            phase="Running",
            restart_count=0,
            last_termination_reason="",
            owner_deployment="web",
            memory_limit_mib=256,
            logs=["INFO  web up", "INFO  serving on :8080"],
        ),
        PodMetric(
            name="web-5d44-xyz",
            namespace="storefront",
            cpu_millicores=80,
            memory_mib=140,
            memory_limit_mib=256,
        ),
    )
    return cluster
