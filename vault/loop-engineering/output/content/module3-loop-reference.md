# Module 3 · Loop Engineering — Reference

> Source: `LOOP.md` (core concept), `loop-budget.md` (kill switch / cost guard), `loop-run-log.md` (execution tracking). Full content preserved verbatim.

## Summary
Loop engineering is the discipline of designing agent loops that are safe, budgeted, and verifiable. This repository dogfoods its own canonical patterns by operating a collection of active loops—such as Daily Triage, PR Babysitter, and Dependency Sweeper—ranging from report-only (L1) to assisted patching (L2). Every loop operates within the trigger -> action -> verification -> budget/kill-switch shape, utilizing isolated git worktrees and verifiers for any code changes. Safety and observability are enforced through defined human gates, denylists, token caps, and live state tracking (`STATE.md`).

### `loop-budget.md` [THREAD: safety]
This file defines hard daily limits for max runs, tokens, and sub-agent spawns per loop pattern to act as a cost guard. If a budget is exceeded, high-cadence workflows are paused, the event is logged, and a global kill switch (`loop-pause-all` label or `STATE.md` flag) halts execution until cleared by a maintainer.

### `loop-run-log.md` [THREAD: safety]
This file tracks loop execution history by appending a structured JSON entry per run containing duration, tokens used, items found, and the outcome. Entries are retained for 30 days, providing a verifiable audit trail of agent actions and escalations.

## `LOOP.md` (verbatim)

# LOOP.md — Loop Engineering Reference

This file documents how the **loop-engineering** reference repository is operated with loop engineering patterns.

The goal of this repo is to be the canonical, copyable, high-signal collection of patterns, starters, and tooling. It eats its own dogfood aggressively.

## Active Loops

### Daily Triage (L1 — automated + report)
- Cadence: 1d weekdays (`/.github/workflows/daily-triage.yml`)
- Skill: `loop-triage` (from `skills/` and `starters/minimal-loop`)
- State: `STATE.md` (updated by workflow; human reviews weekly issue)
- Phase: Report-only. Human reviews and decides actions.
- Handoff: Design decisions, large refactors, new pattern acceptance.

### PR Babysitter (L2 — assisted, manual trigger)
- Cadence: 10–15m during active hours (maintainer `/loop` or future Action)
- Starter: `starters/pr-babysitter` (Grok, Claude Code, Codex)
- Worktrees for suggested fixes; verifier required; no auto-merge by default.

### Dependency Sweeper (L2 — patch-only)
- Cadence: 6h–1d
- Starter: `starters/dependency-sweeper`
- Patch + low-risk CVE only for first 30 days
- Verifier = full `npm ci && npm test` in worktree
- Human gate on majors and denylisted packages

### CI Sweeper / Post-Merge (opportunistic)
- `validate-patterns.yml` + `audit.yml` dogfood pattern validation and readiness scoring
- `audit.yml` posts loop readiness scores on PRs
- Future: sweeper reacting to failing validate/audit runs

### Changelog Drafter (L1 — draft only, high value)
- Cadence: 1d or on release prep (manual or tag-triggered)
- Starter: `starters/changelog-drafter`
- Produces `RELEASE_NOTES_DRAFT.md` (or section for GitHub release). Human approves before publish or CHANGELOG update.
- Excellent low-risk companion to Post-Merge Cleanup. This reference repo should run it for future releases.

## Multi-loop coordination

See [docs/multi-loop.md](docs/multi-loop.md). Priority: CI Sweeper → PR Babysitter → Dependency Sweeper → Post-Merge / Changelog Drafter (off-peak) → Daily Triage (report).

## Worktrees

- Any unattended code-change experiment runs in an **isolated git worktree** per attempt.
- One worktree per fix; discard after verifier REJECT or human escalation.

## Connectors (MCP)

- Optional for L1 daily triage — see [examples/mcp/](examples/mcp/)
- GitHub MCP read-only for issue/PR discovery
- Scope connectors to read + comment until the loop is trusted

## Budget & Observability

- Token caps: `loop-budget.md`
- Run history: `loop-run-log.md` (appended each weekday run by `daily-triage.yml`)
- Estimate: `npx @cobusgreyling/loop-cost --pattern daily-triage`
- Kill switch: `loop-pause-all` label or flag in `STATE.md`

## Safety & Gates (this repo)

- No auto-merge on main except trivial dependency patches (allowlist + verifier)
- Denylist: showcase HTML/CSS, core primitives docs, audit scoring logic without human review
- Live loop state: `STATE.md` at repo root

## How to run locally

```bash
node tools/loop-audit/dist/cli.js . --suggest
npx @cobusgreyling/loop-init . --pattern daily-triage --tool grok  # after npm publish
bash scripts/before-after-demo.sh
```

## Evolution

Journey recorded in `stories/`. Target: solid L2 with excellent observability.

---

*This file is both documentation and the seed for the loops that maintain the reference.*

## `loop-budget.md` (verbatim)

# Loop Budget — loop-engineering (reference repo)

> Dogfood file for the patterns that maintain this repository.

## Daily limits

| Loop | Max runs/day | Max tokens/day | Max sub-agent spawns/run |
|------|--------------|----------------|--------------------------|
| Daily Triage | 1 | 100k | 0 (L1) |
| Validate/Audit (CI) | 96 | 500k | 0 |
| Changelog Drafter | 1 | 100k | 2 |

## On budget exceed

1. Pause schedulers / disable high-cadence workflows
2. Append event to `loop-run-log.md`
3. Open maintainer issue

## Kill switch

- Label: `loop-pause-all`
- Resume only after cleared in `STATE.md`

## Estimate spend

```bash
npx @cobusgreyling/loop-cost --pattern daily-triage --level L1
```

## `loop-run-log.md` (verbatim)

# Loop Run Log — loop-engineering

Append one entry per run. Prune entries older than 30 days.

## Format

```json
{
  "run_id": "2026-06-09T08:15:00Z",
  "pattern": "daily-triage",
  "duration_s": 45,
  "items_found": 4,
  "actions_taken": 1,
  "escalations": 0,
  "tokens_estimate": 52000,
  "outcome": "report-only | fix-proposed | escalated | no-op"
}
```

## Recent Runs

<!-- Loop appends below this line -->

{"run_id":"2026-06-11T13:13:16Z","pattern":"daily-triage","duration_s":5,"items_found":1,"actions_taken":1,"escalations":0,"tokens_estimate":52000,"readiness_score":100,"outcome":"report-only","workflow_run":"27349302128"}
{"run_id":"2026-06-12T11:32:11Z","pattern":"daily-triage","duration_s":7,"items_found":1,"actions_taken":1,"escalations":0,"tokens_estimate":52000,"readiness_score":100,"outcome":"report-only","workflow_run":"27412994403"}
{"run_id":"2026-06-15T13:42:57Z","pattern":"daily-triage","duration_s":5,"items_found":1,"actions_taken":1,"escalations":0,"tokens_estimate":52000,"readiness_score":100,"outcome":"report-only","workflow_run":"27550503677"}
{"run_id":"2026-06-16T12:43:13Z","pattern":"daily-triage","duration_s":10,"items_found":1,"actions_taken":1,"escalations":0,"tokens_estimate":52000,"readiness_score":100,"outcome":"report-only","workflow_run":"27618341632"}
{"run_id":"2026-06-17T12:08:32Z","pattern":"daily-triage","duration_s":12,"items_found":1,"actions_taken":1,"escalations":0,"tokens_estimate":52000,"readiness_score":100,"outcome":"report-only","workflow_run":"27687793882"}
