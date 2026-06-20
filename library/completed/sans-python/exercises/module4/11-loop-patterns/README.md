# Exercise: Loop Patterns in Practice

## Goal

Implement one concrete loop pattern end-to-end against the `_harness/` — a **CI-sweeper** — with a worktree-isolated action, a verifier that runs the real CI command, a hard attempt cap, and the kill switch on denylisted paths. Then declare the pattern in a machine-readable `registry.yaml` and validate it against a `registry.schema.json`, so the loop is a row of data your tooling can read.

## Why

An Production AI Engineer composes loops from a small named set instead of designing each from scratch, isolates every code-editing loop in a worktree so concurrent loops cannot collide, and treats the pattern set as everything-as-code: a schema-validated registry means a malformed loop fails validation in CI, not as a runaway in production.

## Setup

This exercise extends `module4-fleet/` and governs the seeded harness at `exercises/module4/_harness/`. It builds on exercise 10's four-stage loop and reuses the kill switch from exercise 07. Use one of the `_harness/` stub agents as the implementer and a second as (or a separate prompt for) the verifier.

## Steps

1. In `module4-fleet/loop/patterns/`, implement a **CI-sweeper** as a fill-in of the four-stage shape from exercise 10:
   - **Trigger:** an event signal that a check failed (simulate a failing-check payload). If the signal reports CI green, **early-exit** — the no-op path is mandatory for this pattern.
   - **Action:** the implementer agent drafts a minimal fix in an **isolated git worktree** — its own checkout on its own branch. Record a branch lock in shared state (`PR #N — worktree in progress`) so a second loop stands down. Discard the worktree on a REJECT.
   - **Verification:** an independent verifier runs the project's **real CI command** (e.g. a clean install + test, not a cached shortcut), defaults to `REJECT`, and confirms no unrelated files changed. Cap at **3 attempts** on the same failure before `ESCALATE_HUMAN`.
   - **Budget / kill-switch:** the exercise-07 kill switch blocks denylisted paths (auth, payments, secrets) — a fix touching a denylisted path escalates and never commits, even on a passing verifier.
2. Write the pattern into `module4-fleet/loop/registry.yaml` with: `id`, `goal`, `cadence`, `risk`, `week_one_mode`, `human_gates`, `state`, and a `cost` block (`tokens_noop`, `tokens_action`, `suggested_daily_cap`, `early_exit_required`).
3. Write `module4-fleet/loop/registry.schema.json` (JSON Schema, draft 2020-12) that constrains the registry: `id` matches `^[a-z][a-z0-9-]*$`, `cadence` matches `^[0-9]+[mhd](-[0-9]+[mhd])?$`, `risk` is an enum of `low|medium|high`, `human_gates` is a non-empty array, and `week_one_mode` is one of `L1|L2|L3`.
4. Add a validation step that checks `registry.yaml` against the schema. Prove a malformed entry (a bad `risk` value, a missing `human_gates`, an unparseable `cadence`) **fails validation** — the registry is the contract, and the schema enforces it.

## Done when

- `module4-fleet/loop/patterns/ci_sweeper.py` (or equivalent) runs against the `_harness/` and exercises all four stages.
- A green-CI trigger early-exits to a no-op; a failing-CI trigger runs the action in an isolated worktree with a branch lock recorded in shared state.
- The verifier runs the real CI command (clean install + test), defaults to REJECT, and the loop escalates after 3 failed attempts on the same failure.
- A fix touching a denylisted path escalates and never commits, even when the verifier would pass.
- `registry.yaml` validates cleanly against `registry.schema.json`, and at least one deliberately malformed entry is shown to fail validation.

## Stretch

Add a second pattern to the registry — a **daily-triage** loop (cron trigger, L1, no worktree) — and write a coordination check: when both a CI-sweeper and a PR-babysitter would act on the same PR, the second loop reads the first's branch lock from shared state and stands down. This is the multi-loop contention the registry exists to make legible, and the threshold where a set of loops becomes a fleet.
