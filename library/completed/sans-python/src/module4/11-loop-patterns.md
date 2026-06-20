# Loop patterns in practice

The four-stage shape is a template. The reason it earns a lesson of its own is that a handful of loops cover most of what an engineering team wants run unattended — and once you can name them, you stop designing loops from scratch and start composing them.

## The patterns are a small, named set

Loop engineering is not infinite. The recurring work a team wants off its plate falls into a few shapes, each a fill-in of trigger → action → verification → budget. Learn these five and you can read any loop someone hands you, and write most loops someone asks you for.

**Daily-triage.** *Trigger:* a morning cron (every weekday at 7 a.m.; tighter during a sprint). *Action:* ingest CI failures, open issues, and recent commits into one prioritized list. *Verification:* at L1, none beyond the report; at L2, a verifier confirms scope before any small fix. *Budget:* a no-op early exit when nothing is new, ~50k tokens for a full pass. This is the loop every team should run first — low risk, high signal, and the one that teaches you what the others will see.

**PR-babysitter.** *Trigger:* a short interval during active hours. *Action:* discover open PRs, propose minimal patches for actionable review comments or CI failures. *Verification:* a separate verifier confirms the tests pass and no unrelated files were touched — the maker/checker split, hard. *Budget:* tiny no-op when the watchlist is empty, capped per fix attempt, with a hard ceiling on fix attempts before it escalates. It herds PRs through CI and rebase; it never auto-merges, and security or auth changes go straight to a human.

**Dependency-sweeper.** *Trigger:* every six to twelve hours, or on a Dependabot / OSV alert. *Action:* triage updates by risk and apply the safe ones — patch and minor bumps — in an isolated worktree. *Verification:* the project's full build/test/lint suite runs in that worktree; the implementer never declares success. *Budget:* escalate after two failed attempts on the same dependency. A hard kill-switch blocks auto-merge of major bumps, high-severity CVEs, and denylisted packages (auth, payments).

**CI-sweeper.** *Trigger:* a five-to-fifteen-minute interval, or a workflow-failure event. *Action:* classify the failure and draft a minimal fix in a worktree. *Verification:* a verifier confirms tests pass and scope held; the implementer cannot merge. *Budget:* a strict early exit when CI is green, a hard cap of three fix attempts before escalation, and a daily token ceiling. This is the highest-leverage and the highest-risk pattern in the set — the one teams turn on too early and kill on day four.

**Issue-triage.** *Trigger:* every couple of hours or daily. *Action:* scan open issues, deduplicate, score by age and signal, suggest labels. *Verification:* L1 proposes only; L2 applies allowlisted labels after the verifier passes. *Budget:* cheap throughout. Humans keep P0/P1 assignment, uncertain duplicates, and stale closures. It is the low-risk companion to daily-triage.

Read the pattern names and the gates jump out: every one of them keeps a human on the high-stakes decision and lets the loop have the boring volume. That division — boring volume to the loop, judgment to the human — is the whole design, not a footnote to it.

## Worktrees: isolation is not optional

The moment a loop edits code, it needs a worktree. A git worktree gives each fix attempt its own checkout of the repo, on its own branch, so the agent builds and tests in isolation and you discard the whole thing on a REJECT without touching anyone's work.

Skip this and concurrent loops collide. Two action loops on different cadences — a CI-sweeper at fifteen minutes, a PR-babysitter at ten — once spawned conflicting fixes for the *same* failing test on the *same* PR at the same time; untangling the collision cost forty-five human minutes and five times the normal token spend. The fix is mechanical: one worktree per fix attempt, and a branch lock recorded in shared state so a second loop sees "PR #318 — worktree in progress" and stands down. Worktrees remove the mechanical collisions; you remain the ceiling on how many parallel loops a team can absorb.

## Verifiers: the checker that defaults to no

Every pattern above has a verification stage, and every one of them follows the same rule from lesson 10: the agent that made the change does not get to approve it. The verifier is a different sub-agent, a different prompt — *find reasons to reject* — with read-only access to the diff, the original issue, and the test commands. It runs the tests itself and returns one of three verdicts: APPROVE, REJECT, ESCALATE_HUMAN. Its default stance is REJECT; it approves only on evidence.

The failure mode this guards against has a name and a body count. A dependency-sweeper's verifier once falsely APPROVED a patch because it ran `npm test` against a cached `node_modules` instead of a clean install — the test passed in the worktree and failed in CI, because the verifier did not replicate the CI path. The lesson is exact: the verifier must run *what CI runs* (`npm ci`, not just `npm test`), or its approval means nothing. A verifier that does not reproduce the real gate is theater with a green check.

## Everything-as-code: the registry makes loops addressable

Five patterns, each with a cadence, a risk level, a token budget, human gates, and a starting autonomy level — that is structured metadata, and structured metadata belongs in a machine-readable file, not in prose. The platform-engineering instinct applies directly: a loop fleet is addressable as code. You write the patterns into a registry, validate the registry against a schema, and let your tooling — cost estimation, auditing, documentation — read the same file.

```yaml
# module4-fleet/loop/registry.yaml — patterns as data, not prose
patterns:
  - id: ci-sweeper
    goal: React to failing CI with minimal fixes and escalation
    cadence: 5m-15m              # ^[0-9]+[mhd](-[0-9]+[mhd])?$
    risk: medium                 # low | medium | high
    week_one_mode: L2            # the autonomy rung it starts on
    human_gates: [infra-failures, max-attempts, security-tests]
    state: ci-sweeper-state.md
    cost:
      tokens_noop: 5000          # cost of a run that finds nothing
      tokens_action: 200000      # cost of a real fix
      suggested_daily_cap: 1000000
      early_exit_required: true  # the no-op exit is mandatory for this pattern
```

```json
// module4-fleet/loop/registry.schema.json — the contract the registry must satisfy
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["patterns"],
  "properties": {
    "patterns": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "goal", "cadence", "risk", "human_gates", "state"],
        "properties": {
          "id":     { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
          "cadence":{ "type": "string", "pattern": "^[0-9]+[mhd](-[0-9]+[mhd])?$" },
          "risk":   { "type": "string", "enum": ["low", "medium", "high"] },
          "human_gates": { "type": "array", "minItems": 1 }
        }
      }
    }
  }
}
```

The schema is the point. A registry no machine validates drifts the moment a second person edits it — a missing `human_gates` array, a `risk` of `"meduim"`, a cadence string nothing can parse. With a schema, a malformed pattern fails validation in CI instead of failing as a runaway loop in production. The control plane stays Python; the registry stays JSON and YAML; the contract between them is the schema. This is the same everything-as-code discipline the platform-engineering golden-path uses for services — applied now to a set of agents.

## How to pick and compose

Picking a pattern is reading the trigger column. Recurring time-boxed scan, no code changes? Daily-triage or issue-triage, at L1. React to a CI event with a fix? CI-sweeper or PR-babysitter, at L2, behind a verifier and a worktree. Keep dependencies current? Dependency-sweeper, with the kill-switch on majors. Match the work to the shape; do not invent a sixth pattern when one of the five fits.

Composing them is harder, because loops that act will contend. Running three action loops means a coordination priority and shared state they all read: CI-sweeper before PR-babysitter before dependency-sweeper, each checking the others' state files and respecting a branch lock before it spawns a worktree. The registry is what makes this legible — every loop's cadence, gates, and state file in one validated place, so you can see the contention before it costs you forty-five minutes. Three coordinated loops is also the threshold where a set of loops stops being a set and becomes a fleet, which is exactly where the next half of this chapter picks up.

## What you build

You implement one concrete pattern end-to-end against the `_harness/` — a CI-sweeper is the sharpest teacher, because it exercises every stage and every gate. Event trigger, worktree-isolated action, a verifier that runs the real CI command and defaults to REJECT, a three-attempt cap, and the lesson-07 kill-switch on the denylist. Then you write the pattern into a `registry.yaml` and validate it against the schema, so the loop is a row of data your tooling can read, not a paragraph only you can.

Pick the pattern that fits the trigger, give it a worktree and a verifier that reproduces the real gate, and write it into a schema-validated registry — do that and a new loop is a reviewed diff to a data file, not a fresh act of engineering every time.

## Core concepts

- The recurring loops worth running unattended form a small named set — daily-triage, PR-babysitter, dependency-sweeper, CI-sweeper, issue-triage — each a fill-in of the four-stage shape that hands boring volume to the loop and keeps judgment with the human.
- A loop that edits code runs in an isolated git worktree with a branch lock in shared state; without isolation, concurrent action loops collide on the same PR and duplicate paid work.
- The verifier must reproduce the real gate — run what CI runs (`npm ci`, not just `npm test`) — and default to REJECT; a verifier that does not replicate the CI path issues false approvals that fail downstream.
- Loop patterns are data: a machine-readable registry validated against a JSON Schema (cadence, risk, human gates, budgets, autonomy level) makes a fleet of loops addressable as code, so a malformed pattern fails validation instead of failing as a runaway.

<div class="claude-handoff" data-exercise="exercises/module4/11-loop-patterns/">

**Build It in Claude Code** — implement one concrete loop pattern end-to-end against the `_harness/`. Build a **CI-sweeper**: an event trigger (a failing-check signal) with a green-CI early exit; an action that drafts a minimal fix in an **isolated git worktree**; an independent **verifier** that runs the project's real CI command (not a cached shortcut), defaults to REJECT, and caps at three attempts before escalating; and the lesson-07 kill-switch blocking denylisted paths. Then declare the pattern in a `registry.yaml` and validate it against a `registry.schema.json` (id, cadence, risk enum, human_gates, cost) — prove a malformed entry fails validation.

</div>
