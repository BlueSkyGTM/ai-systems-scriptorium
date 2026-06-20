# VERIFY verdict — Lesson 11: Loop Patterns in Practice

**Lesson:** `build-stages/m4/output/author/11-loop-patterns.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch03 LOOP)
**Date:** 2026-06-19

## Markers resolved (2 of 2)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: loop-engineering stories — multi-loop worktree collision on a shared PR]` (line 25) | `loop-module3-loop-stories.md` — "Multi-Loop Collision — CI Sweeper vs PR Babysitter on PR #318" | **PASS → removed.** All numbers trace verbatim. |
| `[verify: loop-engineering stories — dependency-sweeper verifier false-approve on cached install]` (line 31) | `loop-module3-loop-stories.md` — "Dependency Sweeper Week One — Patch Volume and a Verifier Lie" | **PASS → removed.** |

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Daily-triage: morning cron, ~50k tokens, no-op exit, L1 first | patterns "Daily Triage": 1d morning cadence, ~50k tokens, ~5k no-op | PASS |
| PR-babysitter: short interval, propose minimal patches, separate verifier, never auto-merge, security/auth → human | patterns "PR Babysitter": 5m-15m, maker/checker, escalate security | PASS |
| Dependency-sweeper: 6h-12h or Dependabot/OSV, patch+minor in worktree, full suite in worktree, escalate after 2 fails, kill-switch on majors/CVEs/denylist(auth,payments) | patterns "Dependency Sweeper": all points match | PASS |
| CI-sweeper: 5-15m or workflow-failure, classify+fix in worktree, verifier runs tests, 3-attempt cap, daily token ceiling, highest leverage+risk, killed day four | patterns "CI Sweeper" (5m-15m, max 3, 1M/day) + story "Why We Killed Our CI Sweeper (After Day 4)" | PASS |
| Issue-triage: every couple hrs/daily, dedup+score+labels, L1 proposes/L2 allowlisted labels, humans keep P0/P1+dupes+stale closures | patterns "Issue Triage": all points match | PASS |
| L1/L2/L3 autonomy ladder, boring-volume-to-loop / judgment-to-human | docs Readiness Levels; concept map (human gates) | PASS |
| Worktree per fix attempt + branch lock in shared state; concurrent loops collide without it | docs "Parallel Collision"; concepts "Orchestration Tax / Worktrees"; reference "one worktree per fix" | PASS |
| Worktree collision: CI-sweeper @15m vs PR-babysitter @10m, same test/PR, cost 45 human min + 5× tokens | story PR #318: "CI Sweeper at 15m, PR Babysitter at 10m... cost 45 human minutes... ~400k tokens (five times the normal cost)" | PASS |
| Verifier = different sub-agent, "find reasons to reject", read-only, runs tests, default REJECT, 3 verdicts | skills "loop-verifier"; templates verifier; docs "Verifier Theater" mitigations | PASS |
| Dep-sweeper verifier false-APPROVED running `npm test` on cached `node_modules` not clean install; must run `npm ci` | story: "falsely APPROVED a patch by running `npm test` on cached `node_modules` instead of a clean install (`npm ci`)" | PASS |
| Registry-as-code: patterns as machine-readable data validated against a schema | patterns "Pattern Registry" (registry.yaml + registry.schema.json) | PASS |
| registry.yaml example fields (id, goal, cadence, risk, week_one_mode, human_gates, state, cost) | matches source registry shape (subset) | PASS |
| registry.schema.json is valid JSON Schema draft-2020-12 | **Validated with jsonschema 4.26.0 (`Draft202012Validator.check_schema`)** | PASS |
| Full registry.yaml example validates against the schema | **Validated: 0 errors** | PASS |
| Malformed entry (risk `"meduim"`, unparseable cadence, empty human_gates) fails validation | **Validated: rejected with 3 errors** matching the exact failures the prose cites (line 79) | PASS |
| cadence regex `^[0-9]+[mhd](-[0-9]+[mhd])?$` matches all examples | **Tested: 5m-15m, 6h-12h, 1d, 2h, 10m, 15m all MATCH; `5min` correctly NO MATCH** | PASS |
| id regex `^[a-z][a-z0-9-]*$` matches all five pattern ids | **Tested: all five MATCH** | PASS |

## STYLE result — PASS

- H1 single, present tense, second person, blunt confident voice. ✓
- Lead (line 3): no throat-clearing; frames the composing-not-designing payoff. ✓
- One `## Core concepts` block, 4 testable propositions. ✓
- Handoff div present and well-formed. ✓
- Ending (line 91): payoff/reframe shape, varied vs. L10, no banned template. ✓
- "JSON Schema" introduced in context; CVE/OSV/PR/CI standard. Acronym parade respected. ✓
- Fix applied: 2 markers removed; shape-name arrow retained as defined notation (matches L10 + source).

## De-dup confirmation — PASS

- References lesson 10's verifier rule ("the same rule from lesson 10", line 29) and the lesson-07 kill-switch (lines 89, 102) **without re-teaching** them. ✓
- Does NOT redefine budget, kill-switch, or the verification-gate protocol. ✓

## FLAGGED items: none.

## Overall verdict: **PASS** (2 markers resolved, 0 defects, 0 FLAGGED; schema + regexes formally validated). Ship-ready.
