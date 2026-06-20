# VERIFY verdict — 02 DevOps K8s Troubleshooting Agent

Artifact: `build-stages/m7/output/author/02-devops-k8s-agent.md`
Scaffold: `build-stages/m7/output/author/exercises/module7/02-devops-k8s-agent/`
Gate: GUIDE PROSE (claims + STYLE + guide-matches-scaffold). Code already passed BUILD→TEST.

## Verdict: **PASS** (edited in place; all markers resolved; claims verified)

---

## Markers resolved (all 4 substantive + 1 meta)

Every marker was an author-facing note to be verified, then folded into clean prose.
All underlying claims are **confirmed** against authoritative sources; no claim was softened
or flagged unverifiable.

1. **CrashLoopBackOff / OOMKilled diagnosis** (`[MS-Learn:]`, guide lines 48–56) — CONFIRMED
   via MS Learn "Troubleshoot OOMKilled in AKS clusters" and "Pod is stuck in
   CrashLoopBackOff mode": `kubectl describe pod` shows the OOMKilled termination reason and
   exit code 137; `kubectl logs <pod> --previous` reads the crashed container's last output;
   `kubectl top` shows working set vs limit; a too-low memory limit is a named cause of
   CrashLoopBackOff. Rewrote as confident prose (added the exit-137 detail and the "--previous
   because the live container is gone" rationale).

2. **AKS RBAC Reader role** (`[verify:]`, guide lines 73–75) — CONFIRMED via MS Learn "Azure
   built-in roles for Containers": "Allows read-only access to see most objects in a namespace…
   This role does not allow viewing Secrets, since reading the contents of Secrets enables
   access to ServiceAccount credentials in the namespace… (a form of privilege escalation)."
   Rewrote as confident prose; kept the Secrets/ServiceAccount escalation reasoning, which the
   docs state verbatim.

3. **Slack interactive approval-card shape** (`[verify:]` lived in scaffold `hitl.py`; the
   guide's meta-paragraph referenced it) — CONFIRMED via Slack docs
   (docs.slack.dev/interactivity/handling-user-interaction): a Block Kit button click sends an
   HTTP POST `block_actions` payload to the app's configured request URL, carrying user/action
   context and a `response_url`; the app acks 200 within 3s. Folded into the BUILD→TEST
   paragraph ("a Slack button click that POSTs a `block_actions` payload back to your app").

4. **Meta-marker paragraph** (guide lines 138–143) — the stale sentence stating claims are
   "marked `[MS-Learn:]`/`[verify:]` … and resolved at VERIFY" was author-process leakage and
   is now false. Replaced with clean prose naming the three real platform behaviors the mocks
   stand in for.

All three `[MS-Learn:]`/`[verify:]` markers inside the scaffold .py files (`k8s_mock.py`,
`specialists/base.py`, `hitl.py`) describe the *same* verified facts; they are code comments,
out of scope for guide-prose VERIFY, and accurate as written.

## Guide-matches-scaffold confirmation

- **M4 supervisor over read-only specialists, direct tool calls** → `supervisor.py`
  (`Supervisor.handle`): one "tool" per specialist, fresh `ReadOnlyView` each, synthesizes the
  remediation; checks the kill-switch before dispatch and before any change. ✔
- **Three specialists — log / metrics / state** → `specialists/log_reader.py`,
  `metrics_reader.py`, `state_inspector.py`, each `inspect(view, pod)` returning a `Finding`.
  Names in the handoff brief (`log_reader`, `metrics_reader`, `state_inspector`) match. ✔
- **Read-only enforced structurally** → `specialists/base.py` `ReadOnlyView`: forwards reads,
  refuses `apply_remediation`, and `__getattr__` refuses any guessed write verb. The cluster's
  own `apply_remediation` refuses an un-`_authorized` call. ✔
- **Propose-then-commit HITL gate over mock Slack, single write path** → `hitl.py`
  (`HITLGate.propose` / `request_and_commit`): idempotency key, posts card with
  intent/blast-radius/rollback, commits only on APPROVE, default responder REJECT
  ("silence is not a yes"), post-apply verify. ✔
- **Append-only audit log, one correlation id** → `audit.py` (`AuditLog`): records every step;
  test asserts a single correlation id threads the incident. ✔
- **Operator-owned kill-switch, read-only to the agent** → `killswitch.py`: `tripped()` only,
  fail-safe on unreadable; operator owns the `touch outputs/HALT` write. ✔
- **Fixture incident** → `k8s_mock.crash_looping_cluster()`: checkout pod, 64Mi limit, 118Mi
  working set, restart count 11, last reason OOMKilled — exactly as the guide describes. ✔
- **Four operator-surface tests + smoke** → `tests/test_smoke.py` + `smoke.py` match the four
  claims (read-only refused; gate blocks unapproved; approved applies once + audited;
  kill-switch halts). ✔
- `data-exercise="exercises/module7/02-devops-k8s-agent/"` resolves; `smoke.py` and
  `outputs/skill-devops-k8s-agent.md` exist. ✔

## STYLE result (full read)

- H1 present. ✔
- Seam lead: "A pod starts crash-looping at 2 a.m. …" — concrete, pulls the reader to the
  asymmetry thesis; no throat-clearing. ✔
- `## What you build` + `## Core concepts` present, in order, just before the handoff. ✔
- `claude-handoff` div present, correct `data-exercise`, opens and closes. ✔
- HITL expanded earlier ("propose-then-commit HITL"); RBAC, AKS, OOM used in established
  technical register; second person + present tense throughout. ✔
- Ending ("What Module 8 reuses") closes on a "the fleet inherits a team it can already trust
  to stop in the right place" reframe — not a banned template ending. ✔
- My edits preserved voice (blunt, opinionated, em-dash rhythm matched). ✔

## Defects fixed
1. Resolved 4 substantive markers → confident prose (claims all verified).
2. Removed the stale author-process meta-paragraph; replaced with a clean platform-behaviors
   sentence.

## FLAGGED (non-blocking)
- None. Every platform claim is grounded in a first-party source (MS Learn for AKS/K8s,
  Slack docs for the approval-card shape).
