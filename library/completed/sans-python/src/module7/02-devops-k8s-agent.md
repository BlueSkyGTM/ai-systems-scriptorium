# The DevOps K8s Troubleshooting Agent

A pod starts crash-looping at 2 a.m., and the on-call engineer wants two things at
once: the diagnosis now, and the certainty that nothing touched production while
they were asleep. An agent can give them the first. The whole job of this artifact
is to give them the first without ever quietly taking the second.

## The Business Problem: an Agent That Must Not Make Things Worse

Incident response is where autonomy is most tempting and most dangerous. The toil
is real; reading logs, correlating metrics, walking object state across a dozen
pods; and an agent clears it in seconds. But the same agent, handed a credential
that can edit a deployment, is a machine for turning a one-pod incident into a
cluster-wide outage on its own initiative. The failure compounds the way the
issue-to-PR agent's did: the thing that broke the service is the thing reporting
the service is fine.

So the design is asymmetric, and the asymmetry is the artifact. The team can
**read** anything to diagnose. It can **change** nothing without a human's explicit
yes. Diagnosis is autonomous; remediation is gated. State that line as sharply as
you can, because everything below exists to enforce it: an incident agent earns its
keep by being fast at understanding and slow, deliberately, structurally slow, at
acting.

## Capability: a Supervisor over Read-Only Specialists, Behind a Human Gate

The capability is a small org chart. A **supervisor** receives the incident, fans
it out to **specialists** that each inspect one slice of the cluster, reads their
findings, and assembles a single proposed remediation. Then it stops at a gate. A
human sees the proposal, intent, blast radius, rollback, and clicks Approve or
Reject. Only on Approve does the change reach the cluster.

Nothing in that paragraph is a new idea, and that is the point. You are composing
three things you already built:

- **The supervisor and specialists are M4's supervisor-worker pattern** (lesson 03).
  The lead delegates through direct tool calls, one tool per specialist, and owns
  every context boundary. The specialists never see each other; they fan out and
  fan in. The lead reads findings, not raw cluster dumps.
- **The approval gate is M4's propose-then-commit HITL** (lesson 08), unchanged:
  persist the proposal with an idempotency key, surface the case a human can judge,
  commit only on a positive acknowledgement, verify after. Silence is not a yes.
- **The read-only discipline is M6's scoped-credential rule** (issue-to-PR artifact
  04) turned sideways; from "the coder cannot merge" to "the inspector cannot
  mutate"; plus M4's operator-owned kill-switch (lesson 07).

The specialists map onto the commands a human runs by hand. The state inspector is
`kubectl describe pod`: phase, restart count, last termination reason. A
`CrashLoopBackOff` pod with a rising `RESTARTS` count and an `OOMKilled` termination
reason (exit code 137) is the canonical signature, and `kubectl describe` surfaces it.
The log reader is `kubectl logs --previous`: the crashed container's last output, where
the cause is usually written in plain text; the AKS runbook points you at `--previous`
precisely because the live container is gone. The metrics reader is `kubectl top`:
working set against the configured limit. A container that exceeds its memory limit is
OOM-killed by the kernel, and a too-low limit is a named cause of `CrashLoopBackOff` on
AKS; exactly the fixture incident this build diagnoses.

## The Build Sequence

Build it from the cluster outward, because each layer constrains the next.

1. **Mock the cluster first.** A deterministic object with read verbs and exactly
   one guarded write verb. The fixture incident is an OOMKilled crash loop: a
   `checkout` pod with a 64Mi memory limit and a 118Mi working set. No real cluster,
   no `kubectl`, no network; the dry-run path has to run the same on every laptop.

2. **Make read-only structural, not a promise.** Hand each specialist a read-only
   *view* of the cluster, not the cluster. The view forwards the read verbs and
   refuses every write; there is no mutate method to call, and a guessed method
   name is refused too. This is the kill-switch lesson's rule applied to data
   access: the agent gets a handle with GET only. "Read-only" is then the shape of
   the only object the specialist can reach, not a rule a reviewer has to catch.
   This maps to the AKS RBAC Reader role, which grants read-only access to most
   objects in a namespace and holds no write data-action; and notably cannot view
   Secrets, because reading a Secret would expose the ServiceAccount credentials
   behind it. Read-only that still can't read everything: the same instinct, at the
   credential.

3. **Wire the supervisor as direct tool calls.** One tool per specialist. The lead
   calls each with a fresh view, records the finding, and moves on. No
   `create_supervisor()` helper; you own the context boundary, the knob M4 told you
   matters most. The lead checks the operator-owned kill-switch before it dispatches
   anything.

4. **Synthesize, don't let workers decide.** The supervisor folds the findings into
   one proposed change: raise the memory limit to give headroom, with the prior
   limit recorded as the rollback. Specialists report evidence and hypotheses; the
   lead decides the remediation. If the evidence yields no confident fix, the
   supervisor escalates rather than inventing one.

5. **Put the HITL gate in the only write path.** The supervisor never calls the
   cluster's write verb directly. It hands the remediation to the gate, which
   persists it with an idempotency key, posts a mock-Slack approval card, and
   commits only on a positive acknowledgement; then verifies the pod recovered.
   The supervisor re-checks the kill-switch before it even proposes a change.

## The Operator Surfaces

Module 8 hands the student the operator's seat: they hold the kill-switch, work the
approval queue, and read the audit trail to judge what the team did. That only works
if these surfaces are real in the code, not narrated in a README. This artifact
exposes four.

**Read-only enforcement on diagnosis.** A specialist holds a `ReadOnlyView` that
exposes only read verbs; any write is a refused call. The cluster's own write verb
refuses an un-authorized call too, so even a bug in the supervisor cannot mutate the
cluster outside the gate. The blast radius of a prompt-injected specialist is a
failed read, not a deleted deployment.

**The HITL approval gate (mock Slack).** No remediation reaches the cluster without
a human's yes. The gate persists the proposal, posts a card showing intent, blast
radius, and rollback, and commits only on Approve. A scripted "silence" responder
proves the default is Reject; absence of a no is never a yes. The EU AI Act's
human-oversight requirement reads against this directly: a person can interpret the
proposal, intervene, and reverse it via the stored rollback.

**The audit log.** Every action; triage, each specialist's inspect, the proposal,
the human's decision, the apply, the post-apply verify; is appended under one
correlation id. The trail is a byproduct of running the protocol, not extra work,
and it is what lets an operator replay an incident end to end.

**The kill-switch.** A file the operator owns (`touch outputs/HALT`). The supervisor
reads it before dispatch and before any change; it exposes no method to clear it.
Stopping the team is the operator's privilege, not the agent's.

## The BUILD→TEST Gate

The scaffold passes a local, offline gate before it ships. `python smoke.py` runs
the whole incident on the mock cluster; the supervisor fans out to the three
read-only specialists, they diagnose the OOM crash loop, the supervisor proposes
raising the limit, the gate blocks auto-apply, a simulated human approves, the fix
lands once, and the pod returns to `Running` with a complete audit trail.
`python -m pytest tests/` pins the four operator surfaces: a specialist write
attempt is refused (and the cluster stays crash-looping); the gate blocks an
unapproved remediation; an approved one applies exactly once and is fully audited;
the kill-switch halts the team before it inspects a single pod.

The hard constraint is that this gate runs on the Python standard library alone. The
cluster, the Slack approval, and the model are all mocks. The real-Kubernetes,
real-Slack, and real-model paths are guarded behind import checks and `.env`, opt-in
and never on the test path. The platform behaviors the mocks stand in for are real:
the AKS Reader role's read-only-minus-Secrets scope, the `kubectl describe`/`logs
--previous`/`top` diagnosis of an OOM crash loop, and a Slack button click that POSTs
a `block_actions` payload back to your app. Swap a mock for its real counterpart and
the team's shape does not change.

## Strong-Project Done-When

This is a portfolio piece, so it clears the hireability bar, not only the smoke
test. It has a real entry point (`smoke.py`), not a notebook. Its README frames the
business problem; an incident agent that diagnoses fast and cannot make things
worse; before a line of code. It ships operator-surface tests, not a happy-path
assertion. It is versioned with a clean layout and an
`outputs/skill-devops-k8s-agent.md` another agent can load and run. And it makes the
one claim that matters in an interview legible in the code: *this team diagnoses on
its own authority and changes nothing without a human's yes.*

## What Module 8 Reuses

This artifact is the **governed supervisor-and-specialist pattern**: a lead that
delegates to scoped workers, synthesizes their findings, and routes the irreversible
step through a human gate, with the kill-switch and audit trail beside it. Module
8's finale fleet is this same shape promoted; the specialists become a coding team,
the single approval card becomes a shared HITL inbox, and the per-incident audit
becomes a cross-agent one. You do not rebuild the supervisor in the finale; you
instantiate it. Build the read-only seam and the gate clean here, and the fleet
inherits a team it can already trust to stop in the right place.

## What You Build

You compose an M4 supervisor over three M6-style read-only specialists, behind an M4
HITL gate, to triage a Kubernetes incident without the authority to make it worse. A
deterministic mock cluster with one guarded write verb. Three specialists; log,
metrics, state; each holding a read-only view that refuses any write. A supervisor
that fans out through direct tool calls, synthesizes a remediation, and checks an
operator-owned kill-switch before it acts. A propose-then-commit gate over a mock
Slack card that is the single path to a cluster change and commits only on a positive
acknowledgement. An append-only audit log threading the whole incident under one
correlation id. The smoke runs a crash-looping pod end to end offline on the standard
library, and four tests prove diagnosis stays read-only, the gate blocks an
unapproved fix, an approved fix applies once and is audited, and the kill-switch
halts the team.

## Core Concepts

- The DevOps K8s agent is a composition, not a new agent: an M4 supervisor (lesson
  03) over read-only specialists (M6 scoping, artifact 04), behind an M4 HITL gate
  (lesson 08), with an M4 kill-switch and audit (lesson 07). The work is the wiring.
- The defining property is asymmetry: the team diagnoses on its own authority and
  changes nothing without a human's positive acknowledgement; autonomous read,
  gated write; so an incident agent cannot become the cause of a worse incident.
- Read-only is enforced structurally, not by convention: a specialist holds a view
  that exposes only read verbs and refuses every write, so it physically cannot
  mutate the cluster; the AKS RBAC Reader role is the same idea at the credential.
- The HITL gate is the single path to any cluster change: it persists the proposal
  with an idempotency key, surfaces intent/blast-radius/rollback, commits only on
  Approve, and verifies after; and the append-only audit log under one correlation
  id is what lets an operator (or an EU AI Act auditor) replay the incident.

<div class="claude-handoff" data-exercise="exercises/module7/02-devops-k8s-agent/">

**Build It in Claude Code**: Compose a governed K8s incident-response team. Build a
deterministic **mock cluster** (pod/log/metric reads + one guarded write verb; the
fixture is an OOMKilled `CrashLoopBackOff`). Build three **read-only specialists**
(`log_reader`, `metrics_reader`, `state_inspector`), each handed a view that refuses
any write. Wire a **supervisor** as direct tool calls that fans out, synthesizes a
remediation, and checks an operator-owned **kill-switch** before acting. Put a
propose-then-commit **HITL gate** (mock Slack) in the only write path; persist the
proposal, surface intent/blast-radius/rollback, commit only on Approve, verify after
— and append every step to an **audit log** under one correlation id. Prove it with
tests: a specialist write attempt is refused, the gate blocks an unapproved
remediation, an approved one applies exactly once and is audited, and the kill-switch
halts the team. Run `python smoke.py` and `python -m pytest tests/`; stdlib only,
offline.

</div>
