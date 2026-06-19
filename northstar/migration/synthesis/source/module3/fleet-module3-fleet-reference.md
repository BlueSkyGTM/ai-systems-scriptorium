# Module 3 · Fleet Engineering — Reference

> Source: `FLEET.md` (core concept), `fleet-budget.md` (multi-agent cost guard), `FLEET-STATE.md` (fleet state tracking). Full content preserved verbatim.

## Summary
Fleet engineering is the discipline of governing 3+ loops or 5+ agents, transitioning focus from single-agent execution to systemic concerns like registries, identity, permissions, inbox management, auditing, economics, and kill switches. FLEET.md serves as the canonical reference for these patterns, establishing a framework where every automated action must pass an accountability test defining which agent acted, with what authority, against what task, and with what evidence. The repository itself operates as a governed mini-fleet that dogfoods these concepts through CI workflows, budget guards, and human-maintained state tracking, ensuring sovereign control over automated processes.

### `fleet-budget.md` [THREAD: safety]
The fleet budget guard establishes per-agent and team-level token spending caps along with designated owners to prevent unbounded economic costs. In this reference repository, the policy strictly documents these budget patterns while enforcing zero unattended LLM spend.

### `FLEET-STATE.md` [THREAD: safety]
Fleet state tracking maintains a human-maintained catalog of all registered agents, their authorities, evidence paths, and current operational statuses to prevent stale or rogue automations. It also functions as a central ledger for the human inbox, watch lists, and recent fleet decisions, ensuring continuous oversight of the fleet's posture.

## `FLEET.md` (verbatim)

# FLEET.md — Fleet Engineering Reference

This file documents how the **fleet-engineering** reference repository operates as a governed mini-fleet.

The goal: be the canonical, copyable collection of fleet patterns, starters, and tooling — and eat our own dogfood.

## Active Fleet Posture

| Concern | This repo |
|---------|-----------|
| Registry | `patterns/registry.yaml` + per-pattern docs |
| Identity | Maintainers own patterns; contributors via PR |
| Permissions | Public read; write via PR + CODEOWNERS (future) |
| Inbox | GitHub Issues + Discussions for human gates |
| Audit | `fleet-audit` workflow on every push/PR |
| Economics | No unattended token spend on this reference repo |
| Sovereign control | CI can block; no auto-merge of fleet policy changes |

## Accountability Test (dogfood)

For any automated action in this repo, we should answer:

> *Which agent/workflow did it, with what authority, against what task, evidenced by what?*

Example:
- **Which**: `audit.yml` GitHub Action
- **Authority**: repository `GITHUB_TOKEN`, read-only on PRs
- **Task**: score fleet readiness of changed paths
- **Evidence**: workflow run URL + posted comment / check result

## Active Patterns (reference repo)

### Team Agent Registry (F1)
- Registry: `patterns/registry.yaml`
- Manifest template: `templates/AGENT-MANIFEST.yaml`
- State: `FLEET-STATE.md` (human-maintained catalog of what runs where)

### Cross-Agent Audit (F1)
- `fleet-audit` CLI + `.github/workflows/audit.yml`
- Scores projects for registry, identity docs, budget, kill switch

### Fleet Budget Guard (F1 — documentation only)
- Template: `templates/fleet-budget.md`
- This reference repo does not run paid agent loops

## Relationship to Loop Engineering

This repo does **not** replace [loop-engineering](https://github.com/cobusgreyling/loop-engineering). Loops live inside fleets.

```
Fleet  = registry + identity + permissions + inbox + audit + economics + kill switch
Loop   = schedule + state + sub-agents + verification (inside one agent system)
```

When a team runs 3+ loops or 5+ agents, graduate from loop-engineering checklists to fleet-engineering checklists.

## Multi-fleet note

See [docs/multi-fleet.md](docs/multi-fleet.md) for orgs with separate team fleets (platform, GTM, support).

## Kill switch

To pause all fleet automation for this repo:
1. Disable GitHub Actions workflows in repo settings, or
2. Add `FLEET_PAUSE_ALL=true` to repo variables (honored by future automation), or
3. Remove `FLEET.md` active pattern section and open an issue explaining why.

## Review cadence

- Weekly: scan `FLEET-STATE.md` for stale agent entries
- Monthly: re-run `fleet-audit .` on starters and update registry
- Per release: verify accountability test still passes for all workflows

## `fleet-budget.md` (verbatim)

# Fleet Budget — fleet-engineering reference repo

Review cadence: monthly (reference repo runs no paid agent loops)

## Team totals

| Period | Cap (tokens) | Spent | Owner |
|--------|--------------|-------|-------|
| Monthly | 0 | 0 | maintainers |

## Per-agent caps

| Agent ID | Daily cap | Owner | Notes |
|----------|-----------|-------|-------|
| audit-workflow | 0 | maintainers | CI only — no LLM spend |

## Policy

This reference repository documents fleet patterns. It does not run unattended LLM loops.

## `FLEET-STATE.md` (verbatim)

# Fleet State — fleet-engineering reference repo

Last review: 2026-06-10

## Registered agents / automations

| ID | Owner | Role | Authority | Evidence path | Status |
|----|-------|------|-----------|---------------|--------|
| `audit-workflow` | maintainers | Fleet readiness scoring | `GITHUB_TOKEN` read | `.github/workflows/audit.yml` | active F1 |
| `validate-registry` | maintainers | Pattern registry validation | CI read | `scripts/validate-registry.mjs` | active F1 |

## Human inbox (needs decision)

- [ ] Publish Fleet Engineering Substack essay and link here
- [x] GitHub Pages showcase live
- [x] npm publish workflows for `fleet-audit`, `fleet-init`, `fleet-budget` (tag to release)

## Watch list

- LangSmith Fleet product evolution — map new primitives to `docs/primitives-matrix.md`
- loop-engineering `multi-loop.md` — cross-link when fleet essay ships

## Recent decisions

- 2026-06-10: Scaffolded v0.1 reference repo locally; F1 posture (catalog + audit, no unattended agents)