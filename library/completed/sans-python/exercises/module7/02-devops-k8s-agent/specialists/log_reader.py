"""LogReader — reads a crashed container's previous logs for a cause signal.

Mirrors `kubectl logs <pod> --previous`: the last run's output is where a
CrashLoopBackOff reason is usually written in plain text. [MS-Learn: examine a
crash-looping pod with `kubectl logs <pod-name>` / `--previous` to read the exit
message.] This specialist only reads; it forms a hypothesis from the log text and
hands it up. It does not touch the cluster's state.
"""

from __future__ import annotations

from .base import Finding, ReadOnlyView


class LogReader:
    name = "log_reader"

    def inspect(self, view: ReadOnlyView, pod_name: str) -> Finding:
        lines = view.get_logs(pod_name, previous=True)
        joined = "\n".join(lines).lower()

        if "out of memory" in joined or "oom" in joined:
            return Finding(
                source=self.name,
                summary="previous-run log ends in 'container killed: out of memory'",
                hypothesis="container is being OOM-killed (memory limit too low)",
                confidence=0.9,
                evidence={"last_log_line": lines[-1] if lines else ""},
            )
        if "fatal" in joined or "panic" in joined or "traceback" in joined:
            return Finding(
                source=self.name,
                summary="previous-run log ends in a fatal error",
                hypothesis="application-level crash on startup",
                confidence=0.6,
                evidence={"last_log_line": lines[-1] if lines else ""},
            )
        return Finding(
            source=self.name,
            summary="no crash signature found in previous-run logs",
            hypothesis="cause not visible in logs",
            confidence=0.2,
            evidence={"line_count": len(lines)},
        )
