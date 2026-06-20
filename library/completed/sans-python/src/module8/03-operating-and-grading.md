# Operating and grading

The fleet ships the system. You run the fleet. This chapter is the operator's runbook for the four real controls on the Module 7 console, the acceptance rubric you grade the result against, and the distributed-systems vocabulary the exam assumes you already speak.

## The operator runbook

The console is not a dashboard you watch. It is four controls you work, each a real surface on the shipped fleet. Drive them through the exam harness — `run_exam.py` wraps them — or call them directly on the `Fleet` the adapter imports. Either way, these are the same surfaces the Module 7 finale built and the gate pins.

### Configure the registry and the budgets

`registry.yaml` in the fleet directory is the contract. It is not documentation of the fleet; it *is* the fleet — five agents, each with an `id`, an `owner`, an `autonomy_tier`, a least-privilege `permissions` block, and a `budget_daily_usd` cap, plus a `team_daily_usd` ceiling and the `fleet_gates: merge: human` rule. Every governance check reads against it, and a malformed entry fails schema validation before the fleet runs a single action.

You retarget the fleet by editing this one file. A tighter budget is a smaller `budget_daily_usd`. A stricter team ceiling is a smaller `team_daily_usd`. A new agent is a new list entry with its own owner and grant. The orchestrator reads the contract and runs whatever it points at — that is governance-as-code, and it is why the M8 hand-off costs nothing. The budget caps two ways at once on purpose: a per-agent wall catches a single runaway coder, and the team ceiling catches a swarm of small agents that each stay under their own cap. Either breach stops the run before the next action.

### Work the HITL inbox

The merge is the one irreversible action the fleet takes, so it is the one action no agent may auto-execute. The run drives to a merge *proposal* and suspends: the proposal lands in the shared inbox and nothing commits until a human decides. You work it in three moves. Read the queue — `fleet.inbox.pending()` returns the proposals awaiting a decision. Approve by id — `fleet.inbox.approve(inbox_id, by="you@team", reason="diff reviewed")` — naming yourself, because an approval with no named principal is refused; that name is the evidence clause. Then commit — `fleet.commit_merge(run, approver="you@team")`, which re-reads the gate and merges only if the proposal is approved.

There is no off-channel approval and no auto-merge. Try to commit without approving and the gate refuses; the system does not ship. That refusal is the control working, not a bug — a team that let a merge through on a "just this once" DM could not answer *evidenced by what?* at the incident review, which is exactly the failure the inbox exists to prevent. To reject, call `fleet.inbox.reject(inbox_id, by="you@team", reason="...")` and the merge never happens.

### Read the audit's four accountability clauses

After a run, you reconstruct what happened. `fleet.audit.answers_four_clauses(run.correlation_id)` returns the answer to one sentence, for the whole task across every agent: *which agent did it, with what authority, against what task, evidenced by what?* The four clauses — **which, authority, task, evidence** — are threaded by a single correlation id that runs from the feature request through the architect, the two coders, the tester, the reviewer, and the human merge. When a task crosses five agents, "evidenced by what?" only has an answer because one id runs through all of it.

The clause that matters most is `complete`. It is `True` only when every record in the chain carries all four clauses filled. An empty clause anywhere means the fleet cannot answer it — and a fleet that cannot answer all four for every action is not governed, it is unattended. Reading the audit is how you confirm, after the fact, that the system you just shipped stayed accountable the whole way.

### Hold the kill switch

The kill switch is one file the operator owns, every agent loop reads before every action, and no agent can write. The only thing that changes from the single-agent version is the number of readers. Trip it and the fleet halts before its next action and ships nothing — the harness exposes this as `run_exam(spec, kill_first=True)`, and on a live console it is a `touch` on the kill-switch path the registry names.

The defining property is the read-only boundary. The agents are handed a `KillSwitch` with `tripped()` and no write method; the operator holds the write path from outside the loop. If the off switch lived in an agent's reachable state, the agent could disable its own stop, and you would have a kill switch in name only.

## The acceptance rubric

You grade the produced system by criterion, not by feeling. The rubric is the hireability strong-project bar applied to a *system* instead of a single agent, and `rubric.py` checks it against the captured run. These seven criteria are the rubric — the same seven the checker grades, in the same order. The guide and the code are one rubric in two forms; if one changes, so does the other.

| # | Criterion | Passes when |
|---|-----------|-------------|
| R1 | **RUNS** | the fleet shipped the system end to end (the merge committed) |
| R2 | **EVAL-GATED** | the merge passed the tester ACCEPT and the reviewer gate |
| R3 | **AUDITED** | the cross-agent audit answers all four accountability clauses |
| R4 | **BUDGET-BOUNDED** | team spend stayed within the team cap and no per-agent cap breached |
| R5 | **HITL-GOVERNED** | the merge was human-approved through the inbox by id, never auto-merged |
| R6 | **PROBLEM-FRAMED** | the spec names the track, the reference architecture, and the business problem |
| R7 | **TESTED+VERSIONED** | the spec declares acceptance criteria and a version |

Read the rubric as the difference between a demo and infrastructure. R1 and R2 say the system works and the gate worked — table stakes. R3, R4, and R5 are the ones that make it governed: it can prove what it did, it stayed inside its budget, and a human approved the one irreversible action. R6 and R7 are the portfolio bar — a stranger can read the spec and know what problem this solves and how it is judged.

A deficient run fails the criterion it offends, which is what makes the rubric a gate and not a rubber stamp. Leave the merge unapproved and R5 and R1 fail — the fleet refused to auto-merge, so nothing shipped. Trip the kill switch and the whole run fails — nothing ships. Hand in a thin spec with no reference architecture and no version and R6 and R7 fail even if the fleet built something. The grade is reproducible from the captured record: the same run grades the same way every time, because the verdict is computed, not judged.

## Assumed, not taught: distributed-systems vocabulary

The exam asks you to operate a fleet at the scale of a system, and at that scale a vocabulary shows up that this course applies but does not teach as its own module. Naming it is deliberate (deviation D6: the curriculum is scoped one jump from the Platform Engineer role, and the System-Design roadmap is the structural benchmark for what sits just outside it).

You are assumed to already speak it: **load balancing** (spreading requests across replicas so no one node is the bottleneck), **caching** (serving a repeated result without recomputing it — the explanation cache in #11, the eval cache in a CI gate), **sharding and federation** (partitioning data or routing across partitions so one store does not have to hold or answer everything — the spine of multi-tenant isolation), **async and queues** (decoupling a slow producer from a fast consumer so a spike does not topple the system — the HITL inbox is a queue with a human consumer), and **CAP for distributed agent state** (when the fleet's state is spread across nodes you choose, under partition, between consistency and availability — and an agent that reads stale budget or a stale kill switch is a CAP decision you made by accident if you did not make it on purpose).

You will not find a lesson teaching these from scratch here; the Antilibrary names where they live. The exam expects you to apply them when the architecture you replicate demands one — to know that a multi-tenant RAG version leans on sharding, that an eval-gated CI/CD version leans on caching the golden-set results, that the inbox is an async queue with a human on the far end. Knowing the word is the floor; knowing which seam needs it is the job.

## Core concepts

- The operator console is four real controls, not a dashboard: configure the registry and dual budgets, work the HITL inbox to approve the merge by id, read the audit's four clauses by correlation id, and hold the read-only kill switch — each works the same surface the Module 7 fleet ships.
- The acceptance rubric is seven criteria graded by code — runs, eval-gated, audited, budget-bounded, HITL-governed, problem-framed, tested+versioned — and a deficient run fails the criterion it offends, so the grade is a reproducible gate, not an opinion.
- R3, R4, and R5 are what separate governed infrastructure from a demo: the system can prove what it did, stayed inside its budget, and merged only on a human's approval of the one irreversible action.
- Distributed-systems vocabulary — load balancing, caching, sharding, async queues, CAP for distributed agent state — is assumed and applied in the exam, not taught as a module (deviation D6); knowing which seam needs which is the job, not just knowing the word.
