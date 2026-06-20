# Module 3 · Fleet Templates
> Source: `templates/`. Starting points for building fleet infrastructure.

## `AGENT-MANIFEST.yaml`
- **Purpose:** Template for a single agent's manifest file, copied to `agents/manifests/<id>.yaml`. Defines the agent's identity, permissions, autonomy tier, economic limits, connectors, and required human gates.
- **Fleet pattern it implements:** Agent Registry & Identity Management.

## `FLEET-STATE.md`
- **Purpose:** A living document tracking all registered agents, human inbox items, watch lists, and recent fleet decisions for a specific team.
- **Fleet pattern it implements:** Fleet State & Registry Tracking.

## `audit-runbook.md`
- **Purpose:** Outlines the procedures for incident response, weekly accountability reviews, and the minimum required JSON format for exporting audit evidence.
- **Fleet pattern it implements:** Cross-Agent Audit.

## `fleet-budget.md`
- **Purpose:** Tracks token spend against monthly team totals and daily per-agent caps. Includes alert thresholds and an override log for budget changes.
- **Fleet pattern it implements:** Budget Guards & Admission Control.

## `fork-policy.md`
- **Purpose:** Defines the rules for cloning or forking existing agents, including registration requirements, default permissions, and the promotion path from experimental to active.
- **Fleet pattern it implements:** Agent Clone & Fork.

## `handoff-schema.json`
- **Purpose:** A JSON schema defining the required structure for data passed during a manager-to-worker agent handoff, including authority, constraints, and evidence.
- **Fleet pattern it implements:** Inter-Agent Handoff & Authority Delegation.

## `inbox-runbook.md`
- **Purpose:** Defines the channels, service level agreements (SLAs), and record shapes for human-in-the-loop (HITL) approvals of agent actions.
- **Fleet pattern it implements:** Shared Inbox HITL.

## `permissions-model.yaml`
- **Purpose:** Customizable YAML file establishing the permission levels (clone, run, edit) across a workspace, including default settings and structural rules for agents.
- **Fleet pattern it implements:** Fleet Permissions & Access Control.
