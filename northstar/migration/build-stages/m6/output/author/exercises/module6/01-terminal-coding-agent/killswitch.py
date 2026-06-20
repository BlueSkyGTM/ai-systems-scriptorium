"""Kill switch — a boolean the agent reads but cannot write.

The defining property: the agent can read the switch and must never be able to
write it. If the off switch lives in the agent's reachable state, the agent can
disable its own kill switch, and you have a kill switch in name only.

Here the switch is a file the operator owns. The agent loop is handed a
``KillSwitch`` with ``tripped()`` only — no method writes the file. The operator
trips it from outside the process (``engage()`` in tooling, or ``touch`` on the
command line). In production this is a feature flag, a Redis key under a
read-only ACL, or a container-level stop; the file is the local stand-in. The
read-only boundary is the load-bearing line, not the storage mechanism.
"""

from __future__ import annotations

import os


class KillSwitch:
    """Read-only from the agent's side. The operator holds the write path."""

    def __init__(self, path: str):
        self._path = path

    def tripped(self) -> bool:
        """The only method the agent's loop is allowed to call."""
        return os.path.exists(self._path)


class OperatorKillSwitch(KillSwitch):
    """The operator's handle — it can engage and clear. The agent never gets
    one of these; it gets the read-only ``KillSwitch`` base above."""

    def engage(self, reason: str = "operator halt") -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(reason)

    def clear(self) -> None:
        if os.path.exists(self._path):
            os.remove(self._path)


class Halted(Exception):
    """Raised when the loop reads a tripped switch before an action."""
