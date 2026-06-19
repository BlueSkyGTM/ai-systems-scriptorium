# Module 3 · Fleet Schemas
> Source: `schemas/`. JSON Schema contracts for fleet-level agent identity and coordination.

## AgentManifest
- **Purpose:** Defines the identity, autonomy, and operational status of a single agent within the fleet.
- **Key fields:**

| Field | Type | Purpose |
| :--- | :--- | :--- |
| `id` | string | Unique identifier for the agent. |
| `owner` | string | Owner of the agent. |
| `version` | string | Semantic version of the agent manifest. |
| `description` | string | Description of the agent. |
| `identity` | enum | Core identity type (`claw`, `assistant`). |
| `permissions` | object | Operational permissions assigned to the agent. |
| `loops` | array | List of loops the agent participates in. |
| `autonomy_tier` | enum | Level of agent autonomy (`F0`, `F1`, `F2`, `F3`). |
| `status` | enum | Operational state (`active`, `paused`, `retired`, `experimental`). |
| `budget_daily_tokens` | number | Daily token budget limit. |
| `connectors` | array | List of connectors used by the agent. |
| `human_gates` | array | Required human approval gates. |
| `forked_from` | string | Original agent ID if this agent was forked. |
| `evidence` | object | Supporting evidence or metadata. |
| `last_reviewed` | string | Timestamp of the last manifest review. |

- **What the student implements:** An agent identity and configuration manifest declaring autonomy, status, and budget constraints.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/cobusgreyling/fleet-engineering/schemas/agent-manifest.schema.json",
  "title": "AgentManifest",
  "type": "object",
  "required": ["id", "owner", "version", "identity", "autonomy_tier", "status"],
  "properties": {
    "id": { "type": "string", "minLength": 1 },
    "owner": { "type": "string", "minLength": 1 },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "description": { "type": "string" },
    "identity": { "enum": ["claw", "assistant"] },
    "permissions": { "type": "object" },
    "loops": { "type": "array", "items": { "type": "string" } },
    "autonomy_tier": { "enum": ["F0", "F1", "F2", "F3"] },
    "status": { "enum": ["active", "paused", "retired", "experimental"] },
    "budget_daily_tokens": { "type": "number", "minimum": 0 },
    "connectors": { "type": "array" },
    "human_gates": { "type": "array", "items": { "type": "string" } },
    "forked_from": { "type": "string" },
    "evidence": { "type": "object" },
    "last_reviewed": { "type": "string" }
  },
  "additionalProperties": true
}
```

## AgentRegistry
- **Purpose:** Central registry listing all agents active within the fleet ecosystem.
- **Key fields:**

| Field | Type | Purpose |
| :--- | :--- | :--- |
| `agents` | array | Array of agent objects registered in the fleet. |
| `id` | string | Unique identifier for the agent. |
| `manifest` | string/null | Reference to the agent's manifest file. |
| `owner` | string | Owner of the agent. |
| `status` | enum | Operational state (`active`, `paused`, `retired`, `experimental`). |
| `pattern` | string | Deployment or architectural pattern used. |
| `evidence` | string | Link or reference to supporting evidence. |
| `description` | string | Description of the agent. |

- **What the student implements:** A centralized registry mapping all agents, their ownership, and current operational status.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/cobusgreyling/fleet-engineering/schemas/agent-registry.schema.json",
  "title": "AgentRegistry",
  "type": "object",
  "required": ["agents"],
  "properties": {
    "agents": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "owner", "status"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "manifest": { "type": ["string", "null"] },
          "owner": { "type": "string", "minLength": 1 },
          "status": { "enum": ["active", "paused", "retired", "experimental"] },
          "pattern": { "type": "string" },
          "evidence": { "type": "string" },
          "description": { "type": "string" }
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": true
}
```


---

## Live Registry Example — `agents/registry.yaml`

This file is the production fleet registry — the single source of truth holding every agent manifest, owner, status, and evidence pointer in the fleet. It is the file that governance checks, budget guards, and kill switches read against.

| Field | Meaning | What the student populates |
|---|---|---|
| `id` | Unique agent identifier across the fleet | A stable, hyphenated slug unique within the registry |
| `manifest` | Path to the agent's full manifest (null if inline/none) | A filepath string, or `null` when the registry entry is self-describing |
| `owner` | Accountable party for this agent | A team name, role, or individual responsible for the agent |
| `status` | Current lifecycle state | `active`, `paused`, `retired`, etc. |
| `evidence` | Path to the artifact proving this agent exists | A CI workflow path, script path, or config file |
| `description` | Human-readable summary of what the agent does | One-line plain-text description of the agent's purpose |

```yaml
# Reference repo automations — not LLM agents, but fleet-accountable workflows

agents:
  - id: audit-workflow
    manifest: null
    owner: maintainers
    status: active
    evidence: .github/workflows/audit.yml
    description: CI fleet-audit + registry validation

  - id: validate-registry
    manifest: null
    owner: maintainers
    status: active
    evidence: scripts/validate-registry.mjs
    description: Pattern registry schema check
```
