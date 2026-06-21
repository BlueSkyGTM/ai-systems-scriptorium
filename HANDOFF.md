# HANDOFF — Stress-Test the Method on the Remaining Books

**For:** the next session. **Written:** 2026-06-21.

You are a cold agent. This file is your only briefing. If you can run the whole job below from this file
plus the repo's own structure, with no human re-orienting you, that fact is itself the first data point
of the test.

## The job

Stress-test whether the Scriptorium's **method** (not Claude's raw ability) can carry the repo's remaining
books to completion, and document the result honestly into `build-log/stress-test/`.

## The hypothesis (Ray's, stated strong on purpose)

Given the assets already in this repo — the vault ore, the contracts ([STANDARDS.md](platform/conventions/STANDARDS.md) /
[STYLE.md](platform/conventions/STYLE.md) / [AUTHORING.md](platform/conventions/AUTHORING.md)), the pipeline, and the
deferred-context routing — **the remaining books should be completable *effectively* by a cold agent working from
structure and context optimization alone**: no human re-briefing, no context-poisoning, consistency enforced
mechanically.

## The honest counter-hypothesis (the real thing to settle)

Ray's own caveat: *"a lot of what makes this work is built in by Anthropic."* So the test is **not** "did the books
get made." It is: **which part did the work, the architecture or Claude's built-in capability?** A cold agent +
one `CLAUDE.md` + good prompts is a strong baseline. Your job is to separate the structure's contribution from that
baseline, honestly. A negative result ("the structure was mostly ceremony; Claude would have done it anyway") is a
real, valuable result. **Do not flatter the method.**

## How to run it

1. **Orient only from the structure.** Start at [`CLAUDE.md`](CLAUDE.md) → [`CONTEXT.md`](CONTEXT.md), follow the
   routing. Do not ask a human to explain the project. If you cannot proceed from structure alone, stop and log
   exactly where it failed; that is a finding.
2. **Get status** from [`CATALOG.md`](CATALOG.md) and each `build-log/<book>/build-progress.md`. Remaining: **Just
   Python M2–M8**, and the planned books **Machine Math, Data Currents, Weights and Measures, Anatomy of an Answer,
   Local Metal** (plus the stubs **Show, Don't Tell** and **Simple Systems** — reconcile/decide before starting;
   note "Simple Systems" was also floated as an engine name in a prior session, so treat the book stub carefully).
3. **Advance them via the real pipeline** ([`platform/pipeline/CONTEXT.md`](platform/pipeline/CONTEXT.md)): process
   ore → `GATE-LOCK-PLAN` → author with the tiered fleet (conductor → handler → spawn-and-collapse workers, per
   [`platform/ORCHESTRATION.md`](platform/ORCHESTRATION.md)) → VERIFY → BUILD/TEST → `GATE-APPROVE-SHIP`. Hold every
   lesson to `STANDARDS.md` + `STYLE.md`. Run `python platform/bin/route-lint` after any structural change; it must
   exit 0.
4. **Honor the human gates by ID** ([`platform/HUMAN-GATES.md`](platform/HUMAN-GATES.md)). Ray is the only human;
   stop and ask at `GATE-NAME-BOOK`, `GATE-LOCK-PLAN`, `GATE-APPROVE-SHIP`, `GATE-PUBLISH`. Push each finished stage
   to `BlueSkyGTM/ai-systems-scriptorium` main.

## What to measure (document in `build-log/stress-test/`)

For every book/module you touch, record honestly:

- **Cold-proceed?** Did the structure let you act with no re-brief? Y/N + evidence.
- **Structure vs. baseline.** What did the *architecture* do here (a deferred load/don't-load, a route-lint catch,
  a contract enforcing consistency, a gate stopping you, spawn isolation keeping a worker clean) versus what plain
  Claude + one `CLAUDE.md` would have done anyway? Be specific. **This is the core measurement.**
- **Strain / overhead.** Where did the method cost more than it returned?
- **Context economy.** Did deferred context keep you lean — did you load only a boundary's slice, never the 767MB
  vault?
- **Drift caught.** Did route-lint or the contracts catch an error a human eye would have missed?

Keep a running `build-log/stress-test/FINDINGS.md` with the verdict so far.

## Verdict criteria

- **HOLDS** if a cold agent advances multiple books to standard, the advances are attributable to the structure
  (not to human re-orientation), consistency holds mechanically, and you stay lean against the vault.
- **MOSTLY BUILT-IN / FAILS** if you need constant re-orientation, the structure adds ceremony without catching
  real errors, or plain Claude would plausibly have matched the output.

## Boundaries

- Do **not** read or modify anything under `skills/` or `gstack/`. Do not route into `archive/`. Do not author
  against `vault/` (raw ore; process via `ingredients/`).
- Do **not** publish (`GATE-PUBLISH`) anything.
- The **`agent-os-starter` / Deferred Context engine is OUT OF SCOPE** for this test. Its analysis lives in
  `build-log/bot-bottega/` (read it for *why* the method works — the 9 sims, the role analysis, the
  deferred-context + name-handoff findings — but do not build the engine here). This test is only: *does the
  existing method complete the books?*

## The frame, in Ray's words

He suspects he is onto something but cannot fully conceptualize it, and grants that much of the leverage may be
Anthropic's built-ins. This test exists to find out which. Credit the structure only where it earns it.
