"""An operator-owned kill-switch the supervisor reads but cannot write.

This is M4 lesson 07's rule, unchanged: the off switch lives outside the agent's
blast radius. The supervisor checks `tripped()` before dispatching specialists
and again before applying any remediation; it has no method to clear the switch.
Halting is the operator's privilege.

On the smoke path the switch is a file (`touch outputs/HALT`). In production it
is a feature flag or a Redis key under a read-only ACL — same contract, the agent
reads it and the operator owns the write.
"""

from __future__ import annotations

import os
from pathlib import Path


class Halted(RuntimeError):
    """Raised when the kill-switch is engaged. No further action runs."""


class KillSwitch:
    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = Path(path)

    def tripped(self) -> bool:
        try:
            return self._path.is_file() and self._path.read_text().strip() != ""
        except OSError:
            # A switch we cannot read is treated as tripped: fail safe.
            return True

    @property
    def path(self) -> Path:
        return self._path
