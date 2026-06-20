# Exercise 08 — HITL Propose-Then-Commit + Checkpoints/Rollback

## Goal

Put a propose-then-commit human-in-the-loop (HITL) gate in front of the `_harness/` agents' mutating actions, and prove the double-execute defense: persist a proposal with an idempotency key and a surfaced case, commit only on positive acknowledgement, verify after, and confirm a crash-and-retry returns the prior result instead of firing the irreversible action twice.

## Why

Some actions can't be taken back — a wire, a delete, a merge. A popup over a tool call fails two ways: the approval is lost when the process dies before the human answers, and a reviewer asked yes/no fifty times a day rubber-stamps the one that matters. This exercise builds the durable, structured protocol the 2026 consensus uses, and closes the retry-double-execute hole that durable execution (exercise 05) otherwise opens. HITL is defined here; the fleet's shared-inbox HITL later applies this same protocol with more proposers.

## Steps

1. **Proposal store.** Add `module4-fleet/hitl/store.py` — a durable (JSON-on-disk) `ProposalStore` keyed by idempotency key, holding status (`pending`/`committed`/`rejected`), the serialized action, and the surfaced case: intent, data lineage (input sources), blast radius (what it touches + magnitude), and rollback plan.

2. **Propose.** Add `module4-fleet/hitl/propose.py`. Before any mutating `_harness/` action, `propose()` writes the proposal with an idempotency key and **suspends the run** (reuse exercise 05's pause-on-input checkpoint). The action does not run yet.

3. **Commit on positive ack only.** Implement `commit(key, ack)`: run the action **only** on an explicit positive acknowledgement. On no/timeout/silence, mark `rejected` and do not run. After running, **verify** the side effect actually landed; record proposer, approver, timestamp, outcome.

4. **Double-execute defense (the core proof).** Implement the four-part guard: idempotency key (a retried commit with the same key returns the prior result, no re-run) + precondition check (state still matches what was approved) + post-action verify + rollback-on-fail. Then: commit an action, simulate a crash *after* it ran but *before* it recorded, retry with the same idempotency key, and confirm the action fires **exactly once**. Drop the idempotency key and show the retry double-executes — to demonstrate why all four pieces are required.

5. **Rubber-stamp mitigation.** For high-blast-radius actions, replace the yes/no with a challenge-and-response checklist surfaced from the proposal (dollar amount? target? reversible?) that the approver must actively answer. Scale the friction to blast radius — a trivial action gets a glance, a wire gets the full checklist.

## Done when

- A mutating action persists a proposal with an idempotency key and a surfaced case, suspends, and commits only on positive acknowledgement; silence/timeout never commits.
- After commit, the side effect is verified and the full transaction (proposer/approver/timestamp/outcome) is recorded.
- A crash-and-retry with the same idempotency key fires the irreversible action **exactly once**; removing the idempotency key reproduces the double-execute, showing why the guard is needed.
- High-blast-radius actions require a challenge-and-response checklist, not a single yes/no.

## Stretch

Add a precondition that *fails*: between approval and commit, mutate the underlying state so it no longer matches what the human approved, and confirm the precondition check refuses to commit and re-proposes instead of acting on stale approval. Then rehearse a rollback — force a post-action verify failure and confirm the rollback plan runs and leaves the system consistent (the EU AI Act Art. 14 "rehearsed rollback" property).
