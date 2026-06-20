"""FleetContext — the governance handles every node runs under.

One object carries the operator console into every agent: the budget guard, the
audit log, the kill switch, and the policy. A node never reaches around these —
it charges the budget, checks the switch, and records to the audit through this
context, so governance is not optional plumbing a node can skip. Passing it
explicitly (rather than a global) keeps each node's dependence on the fleet
visible and testable.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

from governance.audit import AuditLog
from governance.fleet_budget import FleetBudgetGuard
from governance.killswitch import KillSwitch
from policy import FleetPolicy


@dataclass
class FleetContext:
    policy: FleetPolicy
    budget: FleetBudgetGuard
    audit: AuditLog
    kill_switch: KillSwitch
    correlation_id: str
    on_event: Optional[Callable[[dict], None]] = None  # live-trace callback

    def emit(self, event: str, **data) -> None:
        if self.on_event:
            self.on_event({"event": event, **data})
