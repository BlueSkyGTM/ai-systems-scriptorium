# Module 3 · Loop Stories
> Source: `stories/`. Narrative accounts of real loop runs — patterns succeeding and failing.

## Changelog Drafter — Week One (L1 Draft Only)
**What happened:** A daily changelog drafting loop was run at L1 (read + propose only) to categorize recent merges into `RELEASE_NOTES_DRAFT.md`. It successfully reduced human review time from ~15-20 minutes down to ~4 minutes, though initial runs required rule tweaks to filter out Dependabot noise and adjust the tone. The verifier successfully caught and surfaced a buried breaking change.
**What it demonstrates:** High-leverage, low-risk loop behavior using L1 (report/draft only) before escalating to automated pull requests.
**What the student learns:** The value of keeping loops in a read/propose-only phase to calibrate scanning rules and verifier accuracy before enabling autonomous actions.

## Daily Triage — Report-Only Onboarding
**What happened:** A team implemented a daily triage loop in report-only mode (L1) for two weeks, matching on-call findings manually without executing any automated fixes. After calibrating triage accuracy and eliminating false positives, they graduated to L2 for narrowly scoped single-file test failures, resulting in an auto-PR merged in 8 minutes.
**What it demonstrates:** The L1 report-only phase acts as a necessary calibration step before enabling L2 auto-fixes.
**What the student learns:** Skipping the report-only phase produces noisy, inaccurate loops; graduation criteria must be met before enabling actions.

## Dependency Sweeper Week One — Patch Volume and a Verifier Lie
**What happened:** A dependency sweeper loop running every 6 hours successfully bumped transitive patches and honored denylists, but the verifier falsely APPROVED a patch by running `npm test` on cached `node_modules` instead of a clean install (`npm ci`), causing CI to fail. The loop also triggered reviewer fatigue by opening 3 PRs in a single run.
**What it demonstrates:** A verification step that doesn't replicate the CI install path can produce false approvals, and uncapped actions cause reviewer fatigue.
**What the student learns:** Verification logic must exactly match CI (using `npm ci`, not just `npm test`), and loops require hard limits on actions per run.

## L1 → L2 Graduation — When We Turned On Auto-Fix
**What happened:** A daily triage loop transitioned from L1 report-only to L2 assisted small fixes after two weeks, increasing triage accuracy from 60% to 85% and fixing a broken doc link autonomously. However, the loop almost graduated too early while still misclassifying flaky tests, and later incorrectly tried to fix a typo in a generated file.
**What it demonstrates:** The operational impact of strict graduation criteria between loop levels (L1 to L2).
**What the student learns:** Safe loop graduation requires verifying low noise levels, testing the verifier independently, and defining denylists before enabling auto-fixes.

## Sample Loop Budget Tracking
**What happened:** A budget tracking document logged tokens, sub-agents, and budget caps for three concurrent loops (Daily Triage, Changelog Drafter, Post-Merge Cleanup). The scheduler automatically throttled the Daily Triage loop when it hit 85% of its daily token cap.
**What it demonstrates:** Active budget monitoring and automated scheduler throttling based on token usage.
**What the student learns:** Loops require explicit token caps and automated self-throttling mechanisms to prevent runaway costs.

## Sample Loop Run Log (Populated)
**What happened:** Structured JSON entries were appended to a run log after significant loop runs to track items found, actions taken, escalations, and token estimates for daily triage, changelog drafting, and post-merge cleanup. 
**What it demonstrates:** The mechanics of logging loop runs for rapid observability without reading full chat histories.
**What the student learns:** Maintaining compact run logs enables quick audits of loop behavior, escalations, and budget integration.

## Multi-Loop Collision — CI Sweeper vs PR Babysitter on PR #318
**What happened:** Two action loops running on different cadences (CI Sweeper at 15m, PR Babysitter at 10m) spawned conflicting worktree fixes for the same failing test on the same PR simultaneously. This collision cost 45 human minutes to untangle and consumed ~400k tokens (five times the normal cost).
**What it demonstrates:** Concurrent action loops will collide and duplicate work without state sharing.
**What the student learns:** Action loops must read all active pattern state files and enforce a "branch lock" before spawning worktrees to prevent collisions.

## Post-Merge Cleanup — small wins without the babysitter tax
**What happened:** A daily off-peak loop was used to scan recent merges for stale comments, documentation gaps, and lint issues. Running initially as an L1 report, the team successfully used the generated lists to manually action items, and the verifier later caught a doc fix that secretly changed a public API example.
**What it demonstrates:** Off-peak L1 scanning provides immediate team value for low-priority technical debt without the overhead of full autonomous fixes.
**What the student learns:** The L1 phase is useful for reporting, and denylists must be applied to sensitive directories (e.g., `auth/`, `payments/`).

## PR Babysitter — Week One (Example Story)
**What happened:** A 5-minute PR Babysitter loop with L2 assisted fixes reduced Slack pings from ~12/day to ~4/day, but early issues included an infinite fix loop on a flaky E2E test (killed by a human after 4 attempts) and notification fatigue from over-commenting. These were fixed by enforcing a max attempt counter and restricting comments to APPROVE or ESCALATE_HUMAN verdicts.
**What it demonstrates:** Unbounded retry limits on flaky tests cause infinite loops, and excessive bot updates cause notification fatigue.
**What the student learns:** Loops require explicit kill switches/max attempts for flaky tests, and communication must be strictly filtered to essential verdicts.

## Why We Killed Our CI Sweeper (After Day 4)
**What happened:** A CI Sweeper loop running every 5 minutes on red main consumed ~8M tokens in 48 hours and proposed 11 PRs (including symptom fixes and a prod config break) because it was run entirely unattended with no budget caps and a verifier in the same session. The team deleted the scheduler, switched to event-driven triggers only, and re-enabled it with strict report-only phases, separate verifiers, and a branch allowlist.
**What it demonstrates:** High-leverage entry loops become high-risk failures when run unattended without budgets, branch allowlists, or L1 calibration.
**What the student learns:** Unattended action loops must have daily token budgets, isolated verification, and branch allowlists to prevent runaway spend and bad merges.
