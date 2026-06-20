"""Cross-agent audit — the evidence trail that answers the fourth clause.

The whole standard for a governed fleet is one sentence (M4 lesson 12):

    Which agent did it, with what authority, against what task, evidenced by what?

Four clauses — **which / authority / task / evidence** — and a fleet that cannot
answer all four for every action is unattended, not governed. This module is how
the fleet answers them in code rather than from memory.

Every action any agent takes appends an ``AuditRecord`` carrying all four clauses,
tied to a ``correlation_id`` that threads the whole chain — user request to
architect to coders to merge. When a task crosses five agents, "evidenced by
what?" only has an answer because one id runs through all of it (the
cross-agent-audit pattern, M4 lesson 13). The log is append-only and read-only on
query — nobody edits the record after the fact.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field


def new_correlation_id() -> str:
    """One id per top-level task. It threads every record the task produces."""
    return "corr-" + uuid.uuid4().hex[:12]


@dataclass(frozen=True)
class AuditRecord:
    """One action, with all four accountability clauses. Frozen: write once.

    - ``agent``     — which agent did it (clause 1).
    - ``authority`` — under what authority: the permission/tier it acted on (clause 2).
    - ``task``      — against what task (clause 3).
    - ``evidence``  — evidenced by what: the result, verdict, or artifact (clause 4).
    """

    correlation_id: str
    agent: str
    authority: str
    task: str
    evidence: str
    ts: float = field(default_factory=time.time)

    def as_dict(self) -> dict:
        return asdict(self)


class AuditLog:
    """Append-only audit trail. Read-only once written; queryable by the operator.

    The orchestrator records every action here. An incident review reconstructs
    what happened across agent boundaries from records nobody had to remember to
    write — they fall out of the inbox and the orchestrator doing their jobs.
    """

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def record(self, *, correlation_id: str, agent: str, authority: str,
               task: str, evidence: str) -> AuditRecord:
        rec = AuditRecord(correlation_id, agent, authority, task, evidence)
        self._records.append(rec)
        return rec

    # --- read-only query surface (the operator reads; nobody edits) ------------

    def by_correlation(self, correlation_id: str) -> list[AuditRecord]:
        """Every record for one task, in order — the chain across all agents."""
        return [r for r in self._records if r.correlation_id == correlation_id]

    def by_agent(self, agent: str) -> list[AuditRecord]:
        return [r for r in self._records if r.agent == agent]

    def all(self) -> list[AuditRecord]:
        return list(self._records)

    def answers_four_clauses(self, correlation_id: str) -> dict:
        """Reconstruct the accountability sentence for a task across every agent.

        Returns a dict with the four clauses filled from the chain — the literal
        answer to 'which agent, what authority, what task, what evidence' for the
        whole task, not one action. An empty list in any clause means the fleet
        cannot answer it, which is the definition of unattended.
        """
        chain = self.by_correlation(correlation_id)
        return {
            "which_agents": [r.agent for r in chain],
            "under_what_authority": [r.authority for r in chain],
            "against_what_task": sorted({r.task for r in chain}),
            "evidenced_by_what": [r.evidence for r in chain],
            "complete": bool(chain) and all(
                r.agent and r.authority and r.task and r.evidence for r in chain
            ),
        }
