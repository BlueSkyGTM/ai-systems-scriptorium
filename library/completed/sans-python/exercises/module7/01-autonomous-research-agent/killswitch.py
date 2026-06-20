"""Kill switch — one boolean the whole team reads but no agent can write.

This is the M6 kill switch (Module 6, artifact 01) lifted to a team. The
property that made it load-bearing for a single agent matters more for a fleet:
the switch is read before every action by the supervisor *and* every sub-agent,
and none of them holds a write path. Trip it once and the entire team halts at
its next action boundary — not just the agent that happened to check.

The switch is a file the operator owns. The supervisor and the sub-agents are
handed a ``KillSwitch`` with ``tripped()`` only; nothing they can reach writes
the file. The operator trips it from outside the process. In production this is
a feature flag or a Redis key under a read-only ACL; the file is the local
stand-in. The read-only boundary is the load-bearing line, not the storage.
"""

from __future__ import annotations

import os


class KillSwitch:
    """Read-only from any agent's side. The operator holds the write path."""

    def __init__(self, path: str):
        self._path = path

    def tripped(self) -> bool:
        """The only method the supervisor and sub-agents are allowed to call."""
        return os.path.exists(self._path)


class OperatorKillSwitch(KillSwitch):
    """The operator's handle — it can engage and clear. No agent gets one of
    these; agents get the read-only ``KillSwitch`` base above."""

    def engage(self, reason: str = "operator halt") -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(reason)

    def clear(self) -> None:
        if os.path.exists(self._path):
            os.remove(self._path)


class Halted(Exception):
    """Raised when an agent reads a tripped switch before an action."""
