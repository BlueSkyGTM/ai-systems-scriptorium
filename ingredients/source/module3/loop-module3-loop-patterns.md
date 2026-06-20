# Module 3 · Loop Patterns
> Source: `patterns/`. Repeatable agent loops (trigger -> action -> verification -> budget).

## Pattern · Changelog Drafter
- **Problem it solves:** Scans merged PRs, commits, and labels since the last release to produce high-quality categorized drafts of release notes without manual overhead.
- **Loop design:** Trigger: Daily or on-release cadence -> Action: Scan recent merges and draft categorized notes -> Verification: Human or verifier sub-agent checks for accuracy, tone, and completeness (the drafter never grades its own output or publishes directly) -> Budget: No-op early exit on ~5k tokens; maxes at ~80k tokens for draft generation, capped at 100k daily.
- **Seam relevance:** Human-in-the-loop verification gate required for any breaking changes, major version bumps, or marketing-sensitive releases.

## Pattern · CI Sweeper [THREAD: safety]
- **Problem it solves:** Reacts quickly to failing CI on main or active branches to diagnose, propose minimal fixes, and escalate when the loop cannot confidently resolve the issue.
- **Loop design:** Trigger: 5m-15m interval or `workflow_run` failure -> Action: Classify failure and draft minimal fix in isolated worktree -> Verification: Verifier sub-agent confirms tests pass and no unrelated files changed; implementer cannot merge -> Budget: Early exit required if CI is green (~5k tokens); max 3 attempts before escalating to human, capped at 1M tokens/day.
- **Seam relevance:** Escalates infrastructure failures, security-sensitive test failures, and max attempt limits directly to humans.

## Pattern · Daily Triage
- **Problem it solves:** Provides a prioritized, actionable picture of what needs attention (CI, issues, commits) each morning without requiring manual checks across multiple tools.
- **Loop design:** Trigger: 1d morning cadence (or 2h during active sprints) -> Action: Ingest CI failures, issues, and recent commits to append high-priority items to state -> Verification: Phase 1 is report-only; Phase 2 requires a verifier sub-agent to confirm scope and tests for small self-contained fixes -> Budget: ~50k tokens for standard triage; ~5k tokens for no-op early exit, capped at 100k daily.
- **Seam relevance:** Requires human handoff for design decisions, multi-file refactors, security, and ambiguous triage items.

## Pattern · Dependency Sweeper [THREAD: safety]
- **Problem it solves:** Discovers outdated or vulnerable dependencies, applies safe updates, and escalates risky changes (major bumps, high-severity CVEs) to a human.
- **Loop design:** Trigger: 6h-12h interval or on Dependabot/OSV alert -> Action: Triage updates by risk and apply safe patches/minor bumps in worktree -> Verification: Project test/build/lint suite must pass in isolated worktree; implementer never declares success -> Budget: ~300k tokens per L2 action, capped at 500k daily; escalates after 2 failed attempts on same dep.
- **Seam relevance:** Hard kill-switch prevents auto-merging major bumps, high-severity CVEs, or packages on an explicit denylist (auth/payments).

## Pattern · Issue Triage
- **Problem it solves:** Discovers, deduplicates, prioritizes, and labels incoming issues so the team always has a clean, actionable top-of-queue without manual backlog grooming.
- **Loop design:** Trigger: 2h or 1d cadence -> Action: Scan open issues and pull signals (age, linked PRs, reactions) to score and suggest labels -> Verification: L1 mode proposes only (no auto-label or close); L2 applies allowlisted labels only after verifier passes -> Budget: ~5k tokens for no-op early exit; maxes at ~60k tokens per triage pass, capped at 80k daily.
- **Seam relevance:** Humans exclusively own P0/P1 assignment, uncertain duplicate detection, and stale closures.

## Pattern · Post-Merge Cleanup
- **Problem it solves:** Sweeps for follow-up work (deprecations, TODOs, stale feature flags) after merges to main without blocking the active development loop.
- **Loop design:** Trigger: 6h-1d cadence or GitHub webhook on push to main -> Action: Scan recent diffs to identify cleanup opportunities and draft small fixes -> Verification: Verifier runs full test suite to confirm no unintended behavior changes; blocks auto-merges on >10 files -> Budget: ~5k tokens if no recent merges; ~150k tokens for L2 fix action, capped at 200k daily.
- **Seam relevance:** Defers architectural debt, production feature flags, and external API deprecations to human decision-making.

## Pattern · PR Babysitter [THREAD: safety]
- **Problem it solves:** Reduces time spent herding pull requests through review, CI, rebase, and merge cycles while keeping humans in the judgment seat.
- **Loop design:** Trigger: 5m-15m interval during active periods -> Action: Discover open PRs and propose minimal patches for actionable comments or CI failures -> Verification: Maker/checker pattern ensures a separate verifier sub-agent confirms tests pass and no unrelated files touched -> Budget: ~3k tokens for no-op early exit if watchlist is empty; maxes at ~250k tokens per fix attempt, capped at 2M daily.
- **Seam relevance:** Hard boundaries prevent auto-merging and escalate PRs requiring high-risk refactors, security changes, or exceeding max-fix-attempts.

## Pattern Registry

The `registry.yaml` and `registry.schema.json` files define and validate the structural metadata for all loop patterns. They are used by cost-tracking, auditing, and documentation tooling to ensure consistent configuration across loops. 

**`registry.yaml`**
```yaml
# Machine-readable pattern registry for loop-engineering
# Used by loop-audit, loop-cost, docs site, and tooling.

patterns:
  - id: pr-babysitter
    name: PR Babysitter
    file: pr-babysitter.md
    goal: Shepherd PRs through review, CI, rebase, and merge
    cadence: 5m-15m
    risk: medium
    tools: [grok, claude-code, codex, github-actions]
    skills: [pr-review-triage, minimal-fix, rebase-and-clean]
    state: pr-babysitter-state.md
    phases: [discover, triage, fix, verify, notify]
    human_gates: [security, payments, auth, max-fix-attempts]
    starter: starters/pr-babysitter
    week_one_mode: L1
    token_cost: high
    cost:
      tokens_noop: 3000
      tokens_report: 80000
      tokens_action: 250000
      suggested_daily_cap: 2000000
      early_exit_required: true

  - id: daily-triage
    name: Daily Triage
    file: daily-triage.md
    goal: Prioritized morning scan of CI, issues, commits, and chat
    cadence: 1d-2h
    risk: low
    tools: [grok, claude-code, codex, github-actions]
    skills: [loop-triage, minimal-fix]
    state: STATE.md
    phases: [report, act-small-wins, escalate]
    human_gates: [design-decisions, multi-file-refactors]
    starter: starters/minimal-loop
    week_one_mode: L1
    token_cost: low
    cost:
      tokens_noop: 5000
      tokens_report: 50000
      tokens_action: 200000
      suggested_daily_cap: 100000
      early_exit_required: false

  - id: ci-sweeper
    name: CI Sweeper
    file: ci-sweeper.md
    goal: React to failing CI with minimal fixes and escalation
    cadence: 5m-15m
    risk: medium
    tools: [grok, claude-code, codex, github-actions]
    skills: [ci-triage, minimal-fix]
    state: ci-sweeper-state.md
    phases: [detect, classify, fix, verify, escalate]
    human_gates: [infra-failures, max-attempts, security-tests]
    starter: starters/ci-sweeper
    week_one_mode: L2
    token_cost: very-high
    cost:
      tokens_noop: 5000
      tokens_report: 50000
      tokens_action: 200000
      suggested_daily_cap: 1000000
      early_exit_required: true

  - id: post-merge-cleanup
    name: Post-Merge Cleanup
    file: post-merge-cleanup.md
    goal: Follow-up tech debt and cleanup after merges to main
    cadence: 1d-6h
    risk: low
    tools: [grok, claude-code, codex, github-actions]
    skills: [post-merge-scan, minimal-fix]
    state: post-merge-state.md
    phases: [scan-merges, prioritize, fix-small, ticket-large]
    human_gates: [architectural-debt, feature-flags, large-diffs]
    starter: starters/post-merge-cleanup
    week_one_mode: L1
    token_cost: low
    cost:
      tokens_noop: 5000
      tokens_report: 40000
      tokens_action: 150000
      suggested_daily_cap: 200000
      early_exit_required: false

  - id: dependency-sweeper
    name: Dependency Sweeper
    file: dependency-sweeper.md
    goal: Discover, safely apply, and verify dependency + vulnerability updates with human gates on risky changes
    cadence: 6h-1d
    risk: medium
    tools: [grok, claude-code, codex, github-actions]
    skills: [dependency-triage, minimal-fix, loop-verifier]
    state: dependency-sweeper-state.md
    phases: [scan, triage-risk, patch-safe, verify-worktree, escalate-risky]
    human_gates: [major-bumps, high-sev-cve, denylisted-packages, max-attempts]
    starter: starters/dependency-sweeper
    week_one_mode: L2
    token_cost: medium
    cost:
      tokens_noop: 5000
      tokens_report: 60000
      tokens_action: 300000
      suggested_daily_cap: 500000
      early_exit_required: true

  - id: changelog-drafter
    name: Changelog Drafter
    file: changelog-drafter.md
    goal: Scan merged PRs and commits, draft categorized high-quality release notes or CHANGELOG entries for human review
    cadence: 1d
    risk: low
    tools: [grok, claude-code, codex, github-actions]
    skills: [changelog-scan, draft-release-notes, loop-verifier]
    state: changelog-drafter-state.md
    phases: [scan-merges, categorize, draft, review, publish]
    human_gates: [breaking-changes, security, major-features, marketing-sensitive]
    starter: starters/changelog-drafter
    week_one_mode: L1
    token_cost: low
    cost:
      tokens_noop: 5000
      tokens_report: 35000
      tokens_action: 80000
      suggested_daily_cap: 100000
      early_exit_required: false

  - id: issue-triage
    name: Issue Triage
    file: issue-triage.md
    goal: Discover, deduplicate, prioritize and label incoming issues/discussions so the team always has a clean actionable queue. Excellent low-risk companion to Daily Triage.
    cadence: 2h-1d
    risk: low
    tools: [grok, claude-code, codex, github-actions]
    skills: [issue-triage, loop-verifier]
    state: issue-triage-state.md
    phases: [discover, dedupe, score, propose-labels, human-review]
    human_gates: [security, p0-p1, ambiguous-duplicates, stale-closures]
    starter: starters/minimal-loop
    week_one_mode: L1
    token_cost: low
    cost:
      tokens_noop: 3000
      tokens_report: 30000
      tokens_action: 60000
      suggested_daily_cap: 80000
      early_exit_required: false
```

**`registry.schema.json`**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/cobusgreyling/loop-engineering/patterns/registry.schema.json",
  "title": "Loop Pattern Registry",
  "type": "object",
  "required": ["patterns"],
  "additionalProperties": false,
  "properties": {
    "patterns": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "id",
          "name",
          "file",
          "goal",
          "cadence",
          "risk",
          "tools",
          "skills",
          "state",
          "phases",
          "human_gates"
        ],
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^[a-z][a-z0-9-]*$"
          },
          "name": { "type": "string", "minLength": 3 },
          "file": {
            "type": "string",
            "pattern": "^[a-z0-9-]+\\.md$"
          },
          "goal": { "type": "string", "minLength": 10 },
          "cadence": {
            "type": "string",
            "pattern": "^[0-9]+[mhd](-[0-9]+[mhd])?$"
          },
          "risk": {
            "type": "string",
            "enum": ["low", "medium", "high"]
          },
          "tools": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "enum": ["grok", "claude-code", "codex", "github-actions", "cursor", "windsurf", "aider"]
            }
          },
          "skills": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string", "minLength": 2 }
          },
          "state": {
            "type": "string",
            "pattern": "^[A-Za-z0-9-]+\\.md$"
          },
          "phases": {
            "type": "array",
            "minItems": 2,
            "items": { "type": "string", "minLength": 2 }
          },
          "human_gates": {
            "type": "array",
            "minItems": 1,
            "items": { "type": "string", "minLength": 2 }
          },
          "starter": { "type": "string" },
          "week_one_mode": {
            "type": "string",
            "enum": ["L1", "L2", "L3"]
          },
          "token_cost": {
            "type": "string",
            "enum": ["low", "medium", "high", "very-high"]
          },
          "cost": {
            "type": "object",
            "required": [
              "tokens_noop",
              "tokens_report",
              "tokens_action",
              "suggested_daily_cap",
              "early_exit_required"
            ],
            "additionalProperties": false,
            "properties": {
              "tokens_noop": { "type": "integer", "minimum": 1000 },
              "tokens_report": { "type": "integer", "minimum": 1000 },
              "tokens_action": { "type": "integer", "minimum": 1000 },
              "suggested_daily_cap": { "type": "integer", "minimum": 10000 },
              "early_exit_required": { "type": "boolean" }
            }
          }
        }
      }
    }
  }
}
```
