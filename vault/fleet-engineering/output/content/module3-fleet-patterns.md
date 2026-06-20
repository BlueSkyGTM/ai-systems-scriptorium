# Module 3 · Fleet Patterns
> Source: `patterns/`. Patterns for coordinating 3+ loops / 5+ agents.

## Pattern · Agent Clone & Fork
- **Problem it solves:** Spreading a proven agent across teams without permission chaos or configuration drift.
- **Fleet design:** Agents are distributed using a tiered permission model (`can run`, `can clone`, `can edit`). Forks are tracked via registration (e.g., recording `forked_from` and `owner`), while human gates govern production promotion, upstream merges, and canonical retirement.
- **Seam relevance:** Surfaces when teaching agent identity and registry propagation across multi-agent topologies.

## Pattern · Cross-Agent Audit [THREAD: safety]
- **Problem it solves:** Answering accountability questions across agent boundaries during incidents and compliance reviews.
- **Fleet design:** Coordination is tracked via a minimum evidence chain spanning user requests to agent outcomes, mapped by correlation/trace IDs. Governance is enforced using read-only audit playbooks that query time ranges, agent IDs, principals, and tool classes.
- **Seam relevance:** Surfaces when implementing audit trails and traceability for multi-agent handoffs.

## Pattern · Fleet Budget Guard [THREAD: safety]
- **Problem it solves:** Attributing and capping token/API spend before fleet scale causes unexpected financial costs.
- **Fleet design:** Coordination is managed via a centralized team cap artifact that assigns daily limits, owners, and alert thresholds per agent. Governance is enforced through admission control that pauses the specific agent's scheduler upon exceeding a cap and requires human inbox approval to raise it.
- **Seam relevance:** Surfaces when integrating budget guards and admission control into the fleet layer.

## Pattern · Hierarchical Delegation
- **Problem it solves:** Routing tasks from a manager agent/loop to specialized workers without handoff failures.
- **Fleet design:** A manager agent coordinates with worker agents using typed, auditable JSON schema handoff packets. Governance is enforced by constraining workers to report-only outputs initially, with human gates required for autonomy tier promotion or resolving cross-worker conflicts.
- **Seam relevance:** Surfaces when designing multi-agent delegation topologies, registries, and node identities.

## Pattern · Shared Inbox HITL [THREAD: safety]
- **Problem it solves:** Providing a single place for humans to review, approve, or reject agent actions across the fleet.
- **Fleet design:** Agents propose actions that route to a central, trackable inbox managed by principals. Governance is strictly enforced by allowing only approve-only workflows, ensuring no auto-execution of destructive tools without required human approval and `inbox_id` linkage.
- **Seam relevance:** Surfaces when integrating human-in-the-loop governance and preventing inbox bypass failure modes.

## Pattern · Team Agent Registry [THREAD: safety]
- **Problem it solves:** Knowing what agents exist, who owns them, and what each is allowed to do before scaling further.
- **Fleet design:** Agents are coordinated via a machine-readable registry index and per-agent manifests. Governance is enforced by requiring manifests to support the four accountability clauses and utilizing human gates for new production data access or credential model changes.
- **Seam relevance:** Surfaces as the foundational pattern for establishing identity, ownership, and F1 autonomy limits in a fleet.
