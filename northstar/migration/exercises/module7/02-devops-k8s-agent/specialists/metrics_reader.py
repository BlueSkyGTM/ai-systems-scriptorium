"""MetricsReader — reads pod resource usage against its limit.

Mirrors `kubectl top pods`: working set vs. configured limit. When memory usage
sits at or above the limit, the kernel OOM-kills the container — the mechanical
cause behind an OOMKilled CrashLoopBackOff. [MS-Learn: pods that exceed their CPU
or memory limits are killed by Kubernetes; too-low limits are a named crash
cause on AKS.] Read-only: it reports the ratio and a proposed new limit, but
applies nothing.
"""

from __future__ import annotations

from .base import Finding, ReadOnlyView


class MetricsReader:
    name = "metrics_reader"

    def inspect(self, view: ReadOnlyView, pod_name: str) -> Finding:
        m = view.get_metric(pod_name)
        limit = m.memory_limit_mib

        if limit is not None and m.memory_mib >= limit:
            # Propose a headroom'd limit (1.5x working set, rounded to 32Mi).
            suggested = ((int(m.memory_mib * 1.5) + 31) // 32) * 32
            return Finding(
                source=self.name,
                summary=f"memory {m.memory_mib}Mi at/over limit {limit}Mi",
                hypothesis="memory limit set below the pod's working set",
                confidence=0.85,
                evidence={
                    "memory_mib": m.memory_mib,
                    "memory_limit_mib": limit,
                    "suggested_limit_mib": suggested,
                },
            )
        return Finding(
            source=self.name,
            summary=f"memory {m.memory_mib}Mi within limit {limit}Mi",
            hypothesis="resource usage nominal",
            confidence=0.2,
            evidence={"memory_mib": m.memory_mib, "memory_limit_mib": limit},
        )
