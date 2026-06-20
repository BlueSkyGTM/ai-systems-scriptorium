---
name: issue-to-pr-agent
description: Stand up an autonomous worker that turns a tracker issue into a reviewed PR — issue→branch→fix→CI→PR — with scoped creds, a kill-switch, a CI gate that defaults REJECT, and no auto-merge.
version: 1.0.0
module: 6
artifact: 4
tags: [agent, loop, github, ci, autonomous, hitl, operator-surfaces]
---

Given a repository, an open issue, and an autonomy level (L1 report / L2 assisted / L3 unattended), wire the
M4 four-stage loop around a coding step and produce a review-ready PR — or an escalation — without ever merging.

1. **Trigger.** Define what fires the loop (a labeled issue, a webhook, a cron scan) and the no-op early exit:
   no open issue ⇒ spend nothing. Name the trigger and the empty-watchlist exit before anything else.

2. **Scoped credentials.** Hand the agent a capability broker, never a raw token. Scope it to ONE repo and a
   branch prefix allowlist (`agent/…`); never `main`/`master`. The grantable actions are read/branch/commit/
   open_pr — `merge` is not among them. An out-of-scope request is a hard stop, not a retry.

3. **Action (the coder).** Read the issue, draft a minimal fix on an isolated branch. In production this slot
   is a real coding agent (artifact 01); on the dry-run path it is a deterministic mock so the loop, not the
   model, is what you test. Report tokens so the budget can charge the step.

4. **Verification (CI gate).** Run *what CI runs* against the head commit — the real test/build/lint command,
   not a cached shortcut. Default the verdict to REJECT; APPROVE only on a green exit. A verifier that does not
   reproduce the real gate issues false approvals.

5. **Budget + kill-switch.** Charge every step against a per-run dollar/token/step ceiling; on breach the next
   action does not run. Read an operator-owned kill-switch before every action; the agent can read it but has
   no method to clear it.

6. **The PR — and the merge that isn't.** On APPROVE, open a PR (branch + rationale + CI evidence). STOP. The
   merge is a human action behind an HITL gate. On REJECT, write an escalation note to a human; never open a PR
   on a red gate, never merge on either.

Refuse to auto-merge under any autonomy level — merging to trunk is always a human decision. Refuse to start at
L3: climb L1→L2→L3 by measuring triage accuracy first. Refuse a verifier that does not reproduce the real CI
path. Refuse a credential scope that includes trunk or a second repo. Refuse to run with no budget ceiling.
