"""Fleet kill switch — one switch the operator owns, every loop reads.

The single-agent kill switch (M6) was a boolean one agent read before each
action and could never write. At fleet scale the only thing that changes is the
number of readers: many loops, one switch, still in the operator's hand (M4
lesson 12). Every agent in the team checks it before every action; none of them
can create it.

The defining property is the read-only boundary, not the storage. Here the switch
is a file the operator owns. The orchestrator is handed a ``KillSwitch`` with
``tripped()`` only — no method on it writes the file. The operator trips it from
outside the loop (``engage()`` in tooling, or ``touch`` on the command line). In
production this is a feature flag or a Redis key under a read-only ACL; the file
is the local stand-in.
"""

from __future__ import annotations

import os


class KillSwitch:
    """Read-only from every agent's side. The operator holds the write path."""

    def __init__(self, path: str):
        self._path = path

    def tripped(self) -> bool:
        """The only method the fleet's loops are allowed to call."""
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


class FleetHalted(Exception):
    """Raised when an agent reads a tripped switch before an action."""
