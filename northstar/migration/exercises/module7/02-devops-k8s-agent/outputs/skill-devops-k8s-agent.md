---
name: devops-k8s-agent
description: Stand up a multi-agent K8s incident-response team — a supervisor routing read-only specialists (logs/metrics/state) that diagnose, with a propose-then-commit HITL gate (mock Slack) before any cluster change, an append-only audit log, and an operator kill-switch. Diagnosis is autonomous; remediation is gated.
version: 1.0.0
module: 7
artifact: 2
tags: [multi-agent, supervisor, read-only, hitl, kubernetes, devops, audit, kill-switch, operator-surfaces]
---

Given a Kubernetes incident (an alert pointing at a misbehaving pod), compose a
governed troubleshooting team: a supervisor that delegates to read-only specialists,
synthesizes a remediation, and routes EVERY change through a human gate. The team
can diagnose on its own authority and can change nothing on its own authority.

1. **Mock the cluster first.** Build a deterministic cluster object with read verbs
   (get/list pods, logs, metrics) and exactly one guarded write verb. No real
   cluster or kubectl on the dry-run path. The fixture incident is an OOMKilled
   CrashLoopBackOff: a memory limit set below the pod's working set.

2. **Read-only specialists.** Build one inspector per evidence slice — a log reader
   (`kubectl logs --previous`), a metrics reader (`kubectl top`), a state inspector
   (`kubectl describe`). Hand each a read-only view that exposes only read verbs;
   a write attempt is a refused call, not a policy to remember. This is the M6
   scoped-credential / read-only discipline applied to a team of inspectors. Map
   it to the AKS RBAC Reader role: read-only, no write data-action, no Secrets.

3. **Supervisor as direct tool calls.** The lead holds one tool per specialist,
   calls each with a fresh view, reads their findings, and synthesizes a
   remediation. No supervisor library — you own every context boundary (M4 lesson
   03). The lead never reads raw cluster state itself; it reads worker findings.

4. **Propose-then-commit HITL gate.** The supervisor never applies a change on its
   own authority. Persist the proposal with an idempotency key, surface the case
   (intent, blast radius, rollback), post it as a Slack approval card, and commit
   ONLY on a positive acknowledgement. Silence/timeout/reject is never a yes. The
   gate is the single path to the cluster's write verb. Verify the side effect after.

5. **Audit log + kill-switch.** Append every action — triage, each inspect, propose,
   the human decision, apply, verify — under one correlation id, so the incident
   replays end to end. Give the supervisor an operator-owned kill-switch it reads
   before dispatch and before any change but cannot clear.

6. **The acceptance gate.** `python smoke.py` runs the incident end to end on the
   mock cluster, offline, stdlib only; `python -m pytest tests/` pins the operator
   surfaces: a specialist write attempt is refused; the gate blocks an unapproved
   remediation; an approved one applies exactly once and is audited; the kill-switch
   halts the team before it acts.

Refuse to apply ANY remediation without a positive human acknowledgement. Refuse to
hand a specialist a credential that can write the cluster — diagnosis is read-only.
Refuse to let the supervisor mutate the cluster outside the HITL gate. Refuse a
kill-switch the agent can clear. Real Kubernetes/Slack/model are opt-in via `.env`,
never on the test path.
