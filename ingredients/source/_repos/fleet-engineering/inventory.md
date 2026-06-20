# fleet-engineering — Inventory
> Module 3 · multi-agent / fleet governance. No antilibrary — all content is seam material.

## Structure

| Section | Files | Purpose |
|---------|-------|---------|
| `patterns/` | 8 files (README.md, agent-clone-fork.md, cross-agent-audit.md, fleet-budget-guard.md, hierarchical-delegation.md, registry.yaml, shared-inbox-hitl.md, team-agent-registry.md) | Production fleet patterns |
| `schemas/` | 2 files (agent-manifest.schema.json, agent-registry.schema.json) | Schema definitions for manifests and registries |
| `stories/` | 6 files (README.md, budget-cap-saved-runaway.md, inbox-bypass-incident.md, langsmith-git-backup.md, registry-before-inbox.md, shadow-agents-audit.md) | Narrative case studies and incident stories |
| `templates/` | 8 files (AGENT-MANIFEST.yaml, FLEET-STATE.md, audit-runbook.md, fleet-budget.md, fork-policy.md, handoff-schema.json, inbox-runbook.md, permissions-model.yaml) | AGENT-MANIFEST, permissions, budget templates |
| `agents/` | 1 file (registry.yaml) | Live fleet registry |
| `examples/` | 7 files (README.md, diy, langsmith-fleet, openhermit) | Reference implementations and examples |
| `tools/` | 14 files (fleet-audit, fleet-budget, fleet-init) | Readiness scorer, scaffold CLI, and budget tooling |
| `starters/` | 13 files (README.md, fleet-plus-loop, minimal-fleet) | Starter scaffolds for fleet deployments |
| `docs/` | 18 files (GITHUB_PAGES.md, RELEASE.md, _config.yml, accountability-test.md, assets, concepts.md, failure-modes.md, five-concerns.md) | Core discipline framework and concept docs |
| `tests/` | 3 files (fixtures) | Test fixtures |
| Root reference | FLEET.md, FLEET-STATE.md, fleet-budget.md, AGENTS.md, README.md | Top-level reference and posture files |

## AGENTS.md

The repository serves as the open reference for **Fleet Engineering**, providing the framework for governing populations of agents with accountability. It establishes specific conventions for AI agents working in the repo, such as utilizing fleet maturity levels (F0–F3) and distinguishing between "Claw" agents (fixed service credentials) and "Assistant" agents (acting on behalf of a user). Agents are directed to read concept and accountability docs before making changes, and must follow strict rules such as not breaking the registry schema or enabling unattended write automation without documented human gates.

## Notes

* `patterns/registry.yaml` is the PATTERN registry (distinct from `agents/registry.yaml`, the live fleet registry).
* `tests/fixtures` present.
* 2 images + Mermaid in 5 files.
