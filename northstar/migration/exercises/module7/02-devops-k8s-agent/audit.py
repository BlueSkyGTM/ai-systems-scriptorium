"""Append-only audit log: every action carries a correlation id.

The audit trail is a byproduct of doing the protocol, not extra work (HITL lesson,
move 5). Every step the team takes — each specialist read, the supervisor's
proposal, the human's decision, the apply, the kill — is appended here under one
correlation id per incident, so an operator (or an EU AI Act auditor) can replay
exactly what happened and who approved it.

Stdlib only: an in-memory list plus an optional JSONL file. No database, no
network. The append-only discipline is the load-bearing part — entries are added,
never edited, so the record cannot be quietly rewritten after the fact.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AuditEntry:
    correlation_id: str
    actor: str            # which agent/human/operator took the action
    action: str           # what they did (e.g. "inspect", "propose", "approve")
    detail: dict
    ts: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps(
            {
                "correlation_id": self.correlation_id,
                "ts": round(self.ts, 6),
                "actor": self.actor,
                "action": self.action,
                "detail": self.detail,
            },
            sort_keys=True,
        )


class AuditLog:
    """Append-only. One correlation id threads a whole incident."""

    def __init__(self, correlation_id: str | None = None,
                 path: str | Path | None = None) -> None:
        self.correlation_id = correlation_id or f"inc-{uuid.uuid4().hex[:12]}"
        self._entries: list[AuditEntry] = []
        self._path = Path(path) if path else None
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, actor: str, action: str, **detail) -> AuditEntry:
        entry = AuditEntry(
            correlation_id=self.correlation_id,
            actor=actor,
            action=action,
            detail=detail,
        )
        self._entries.append(entry)
        if self._path is not None:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(entry.to_json() + "\n")
        return entry

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def actions(self) -> list[str]:
        """The ordered action names — handy for asserting the trail in tests."""
        return [e.action for e in self._entries]
