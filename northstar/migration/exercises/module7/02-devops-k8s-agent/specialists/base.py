"""The read-only contract every specialist runs under.

The enforcement is structural, not a code-review convention: a specialist never
touches the `MockCluster` directly. It gets a `ReadOnlyView` — a wrapper that
forwards the read verbs and answers every mutating verb with a refusal. So
"read-only" is not a rule the specialist has to honor; it is the shape of the
only object it can reach.

This is the kill-switch lesson's rule turned sideways: the agent gets a handle
with GET only, never SET. [verify: maps to the AKS RBAC Reader credential, which
can list/describe/read-logs but holds no write data-action on the cluster.]
"""

from __future__ import annotations

from dataclasses import dataclass, field

from k8s_mock import MockCluster, Pod, PodMetric


class WriteAttemptRefused(PermissionError):
    """Raised when read-only code reaches for a mutating verb. By construction,
    a well-behaved specialist never triggers this; a misbehaving one fails loud."""


@dataclass
class Finding:
    """One specialist's structured contribution to the diagnosis.

    Specialists report evidence and a hypothesis with a confidence; they do NOT
    decide the remediation. Assembling findings into a proposal is the
    supervisor's job — the four-primitives split (workers fan out, the lead
    synthesizes).
    """

    source: str            # which specialist produced this
    summary: str           # one-line human-readable evidence
    hypothesis: str        # what this specialist thinks is wrong
    confidence: float      # 0.0–1.0
    evidence: dict = field(default_factory=dict)


class ReadOnlyView:
    """A read-only handle on the cluster. The only object a specialist holds.

    It forwards every READ verb to the underlying cluster and refuses every
    WRITE verb. The write surface is denied here so a specialist physically
    cannot mutate the cluster — there is no method to call. `apply_remediation`
    is present only to refuse it with a clear error, in case a specialist (or a
    prompt-injected model standing in for one) reaches for it.
    """

    def __init__(self, cluster: MockCluster) -> None:
        self._cluster = cluster

    # --- forwarded READ verbs ------------------------------------------------ #

    def get_pod(self, name: str) -> Pod:
        return self._cluster.get_pod(name)

    def list_pods(self, namespace: str | None = None) -> list[Pod]:
        return self._cluster.list_pods(namespace)

    def get_logs(self, name: str, *, previous: bool = False) -> list[str]:
        return self._cluster.get_logs(name, previous=previous)

    def get_metric(self, name: str) -> PodMetric:
        return self._cluster.get_metric(name)

    # --- refused WRITE verbs ------------------------------------------------- #

    def apply_remediation(self, *_args, **_kwargs):
        raise WriteAttemptRefused(
            "a read-only specialist may not apply remediation — "
            "diagnosis inspects, it never mutates"
        )

    # Any other mutating attribute access is refused too, so a specialist cannot
    # discover a write path by guessing a method name.
    def __getattr__(self, item: str):
        raise WriteAttemptRefused(
            f"read-only view exposes no attribute {item!r}; "
            "specialists may only inspect the cluster"
        )
