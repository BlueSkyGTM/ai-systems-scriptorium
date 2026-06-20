# DevOps K8s Troubleshooting Agent

A multi-agent incident-response team for Kubernetes. An alert fires; a **supervisor**
routes the incident to **read-only specialists** that inspect logs, metrics, and
object state; the supervisor assembles a remediation; and a **human-in-the-loop
gate** (a mock Slack card) blocks any change until a person approves it. On
approval the fix is applied once and the pod recovers — and every step is in the
audit log under one correlation id.

This is a **composition**, not a new agent. The supervisor + specialists are M4's
supervisor-worker pattern (lesson 03). The approval gate is M4's propose-then-commit
HITL (lesson 08). The read-only discipline and the operator-owned kill-switch are
M6's issue-to-PR scoping (artifact 04) and M4's control plane (lesson 07). The work
is the wiring and the gates.

## The business problem

When a pod starts crash-looping at 2 a.m., the expensive failure is not the slow
human — it is the fast agent that "fixes" the wrong thing and takes the service
down harder. An incident-response agent has to clear the toil of diagnosis without
ever being the cause of a worse outage. So the design is asymmetric on purpose:
the team can **read** anything to diagnose, and can **change** nothing without a
human's yes. Diagnosis is autonomous; remediation is gated. That single line is
what separates this from a bot that restarts the wrong deployment on a schedule.

## Run it (offline, standard library only)

```
python smoke.py            # a crash-looping pod, end to end
python -m pytest tests/    # operator-surface tests (or: python tests/test_smoke.py)
```

No cluster, no `kubectl`, no Slack, no network. The smoke path uses a deterministic
mock cluster, a mock Slack approval, and a mock model, so it is reproducible on any
laptop with no cloud account.

## What's here

| File | Role |
|------|------|
| `supervisor.py` | Routes an incident to specialists (direct tool calls), synthesizes a proposal, runs the control plane + gate. The lead never mutates the cluster on its own authority. |
| `specialists/` | `log_reader.py`, `metrics_reader.py`, `state_inspector.py` — **read-only** inspectors. Each gets a `ReadOnlyView`; a write attempt is refused, not just discouraged. |
| `k8s_mock.py` | A deterministic mock cluster: pod/log/metric state plus one guarded write verb. The fixture incident is an OOMKilled CrashLoopBackOff. |
| `hitl.py` | Propose-then-commit gate over a mock Slack card. Persists a proposal with an idempotency key; commits only on a positive ack; verifies after. |
| `audit.py` | Append-only audit log; every action carries the incident's correlation id. |
| `killswitch.py` | Operator-owned kill-switch the supervisor reads but cannot write. |
| `mock_llm.py` | The deterministic reasoning seam; a real model is opt-in behind a guarded import. |
| `smoke.py` | Wires the team around a fresh crash-looping cluster end to end. |
| `tests/test_smoke.py` | Pins the four operator surfaces below. |
| `outputs/` | The audit JSONL lands here; `skill-devops-k8s-agent.md` is the deliverable. |

## Operator surfaces (the things you drive)

- **Read-only enforcement on diagnosis.** Specialists hold a `ReadOnlyView` that
  forwards read verbs and refuses every write — there is no mutate method to call.
  A guessed write verb is refused too. The cluster's own write path also refuses an
  un-gated call. [Maps to the AKS RBAC Reader role: read-only namespace access,
  no write data-action, cannot even view Secrets.]
- **HITL approval gate (mock Slack).** No remediation reaches the cluster without a
  positive acknowledgement. The gate persists the proposal (intent, blast radius,
  rollback), posts a card, and commits only on Approve. Silence is not a yes.
- **Audit log.** Every step — triage, each inspect, propose, the human decision,
  apply, verify — is appended under one correlation id, so the whole incident
  replays for an operator or an auditor.
- **Kill-switch.** `touch outputs/HALT` (any content) halts the team before its
  next action. The supervisor reads it; it cannot clear it.

## The smoke flow

```
alert: checkout pod CrashLoopBackOff
  → supervisor checks kill-switch
  → fan out: state_inspector + log_reader + metrics_reader  (READ-ONLY)
  → findings: OOMKilled, "out of memory (limit 64Mi)", working set 118Mi > 64Mi
  → supervisor proposes: raise checkout memory limit 64Mi → 192Mi (rollback: 64Mi)
  → HITL gate posts a Slack card and BLOCKS auto-apply
  → simulated human clicks Approve
  → remediation applied once; pod returns to Running; audit trail complete
```

## Extend to real infrastructure (opt-in)

The smoke path is local. To run against real services, copy `.env.example` to
`.env`:

1. **Kubernetes.** Give the specialists a **read-only** credential — the AKS RBAC
   Reader role, scoped to one namespace. Never a Writer/Admin role: diagnosis is
   read-only by construction, and the credential should make a write impossible
   even if the code tried. Swap the `MockCluster` read verbs for Kubernetes API
   reads; the specialists' code does not change because they only ever read.
2. **Slack.** Swap `MockSlack` for a real bot that posts an interactive approval
   card and returns the button click. Keep the rule: commit only on Approve.
3. **Model.** Set `USE_REAL_LLM=1` and `ANTHROPIC_API_KEY` to reason over findings
   with a frontier model. Guarded so a missing SDK never breaks the gate.

The remediation always stays behind the human. Real Kubernetes and Slack are
something you turn on deliberately — not the path the tests run.
