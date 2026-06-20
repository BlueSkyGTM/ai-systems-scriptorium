"""Authorization — the orchestrator reads the registry to authorize every action.

Permissions are the *authority* clause of the accountability test, made explicit
and diffable instead of implied by whatever credential happened to be in the
environment (M4 lesson 12). This module turns the registry into the answer to two
questions the orchestrator asks before any agent acts:

1. **Is this agent on the registry at all?** An off-registry agent is refused
   before it runs a single action — it fails the accountability test (no
   identity, no owner) before it starts.
2. **May this agent call this tool / take this action?** A node attempting a tool
   outside its declared least-privilege grant is refused, and the refusal is
   loggable with the accountability sentence.

The refusal is the point. A governed fleet says no by reading a file, not by
trusting a prompt.
"""

from __future__ import annotations


class Unauthorized(Exception):
    """An action the registry does not permit. Refused before it runs."""


class FleetPolicy:
    """Indexes the registry and answers authorization questions against it."""

    def __init__(self, registry: dict):
        self._registry = registry
        self._by_id = {a["id"]: a for a in registry.get("agents", [])}

    def known(self, agent_id: str) -> bool:
        return agent_id in self._by_id

    def manifest(self, agent_id: str) -> dict:
        """The agent's registry entry — or refuse: an off-registry agent has no
        identity and no owner, so it fails the accountability test on arrival."""
        if agent_id not in self._by_id:
            raise Unauthorized(
                f"agent {agent_id!r} is not on the registry — refused (no identity, no owner)"
            )
        return self._by_id[agent_id]

    def owner(self, agent_id: str) -> str:
        return self.manifest(agent_id)["owner"]

    def authority(self, agent_id: str) -> str:
        """A one-line authority string for the audit record (clause 2)."""
        m = self.manifest(agent_id)
        perms = m["permissions"]
        return (
            f"owner={m['owner']} tier={m['autonomy_tier']} "
            f"tools={perms['tools']} can_merge={perms['can_merge']}"
        )

    def authorize_tool(self, agent_id: str, tool: str) -> None:
        """Refuse a tool outside the agent's least-privilege grant."""
        perms = self.manifest(agent_id)["permissions"]
        if tool not in perms["tools"]:
            raise Unauthorized(
                f"agent {agent_id} may not call {tool!r}; granted {perms['tools']}"
            )

    def authorize_merge(self, agent_id: str) -> None:
        """Refuse a merge by any agent. No agent has can_merge: true — the merge
        is the one fleet-level human gate, so even asking is a policy error."""
        if not self.manifest(agent_id)["permissions"].get("can_merge", False):
            raise Unauthorized(
                f"agent {agent_id} may not merge — merge is a human gate (shared inbox)"
            )

    def agents_by_role(self, role: str) -> list[str]:
        return [a["id"] for a in self._registry["agents"] if a["role"] == role]
