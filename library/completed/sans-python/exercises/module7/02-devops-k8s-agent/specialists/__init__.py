"""Read-only specialist agents for the K8s troubleshooting team.

Each specialist inspects one slice of the cluster — logs, metrics, object state —
and returns a typed Finding. None of them can mutate the cluster: they are handed
a `ReadOnlyView` that exposes only the read verbs, so a write attempt is a refused
call, not a policy someone has to remember to check. This is the M6 read-only /
scoped-credential discipline (issue-to-PR artifact 04) applied to a team of
inspectors instead of one coder.
"""

from .base import Finding, ReadOnlyView, WriteAttemptRefused
from .log_reader import LogReader
from .metrics_reader import MetricsReader
from .state_inspector import StateInspector

__all__ = [
    "Finding",
    "ReadOnlyView",
    "WriteAttemptRefused",
    "LogReader",
    "MetricsReader",
    "StateInspector",
]
