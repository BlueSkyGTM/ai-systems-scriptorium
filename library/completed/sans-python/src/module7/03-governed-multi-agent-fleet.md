# The governed multi-agent fleet

A single coding agent fixes one bug in one repo. A feature is bigger than that — it needs a plan, parallel hands, a review, and a test pass — so the answer is a team of agents. The instant that team can edit code and merge it, the question stops being *can they build?* and becomes *can a human stay accountable for what they built?* This chapter is the system that answers yes, and it is the course's last and largest build.

## The business problem

You shipped a coding agent in Module 6. It reads a failing file, writes a fix, runs the tests, and stops when a gate accepts the result. It is real, and it is bounded. It also tops out fast: one context window cannot hold an architecture plan, two parallel code slices, reviewer commentary, and a test log at once. A real feature outgrows a single agent the way a real product outgrows a single engineer.

The settled 2026 answer is a team. An architect plans, coders work in parallel, a reviewer gates, a tester verifies — the software factory, staffed by agents. Stand that up and you get throughput. You also get a new and worse failure mode: five agents that can write code and merge it, running while you sleep, and no single place that can tell you what they did. That is not a productivity win. That is an incident waiting for a correlation ID nobody wrote.

So the problem this artifact solves is not "build a team that ships software." A team that ships software is a weekend hack. The problem is **building a team that ships software while a human stays accountable for every action it takes** — and that second clause is the entire job of an AI Platform Engineer. The team is the easy half, the way the model was the easy half of the coding agent. The governance is the work.

## Elevate, don't author

Here is the discipline that makes this the finale and not just another build: you do not write a coding agent, and you do not write a fleet. You already have both. The coder node *is* the Module 6 agent — the same loop, the same tool surface, the same sandbox, the same verify gate. The governance *is* the Module 4 fleet — the same registry contract, the same budget governor, the same propose-then-commit inbox. M7 is the composition of two things you built, not the invention of a third.

That is what the whole book has been pointing at. You built single agents and made them verifiable. You governed them with budgets, kill switches, and HITL. You assembled those controls into a fleet. Now the fleet wraps the agents, and the result builds software. If you find yourself rewriting the plan/act/observe loop or re-deriving propose-then-commit, stop — you have misread the architecture. The reuse is the lesson.

## The architecture

Five agents, four roles, coordinating over typed handoffs under one governance layer:

```
                         ┌──────────────────── fleet governance ────────────────────┐
                         │  registry · fleet budget · HITL inbox · audit · kill switch │
                         └───────────────────────────────────────────────────────────┘
                                                  │ governs every action
  feature request ─▶ architect ─A2A▶ coder-1 ┐
                       (plan)         coder-2 ┘─A2A▶ tester ─A2A▶ reviewer ─▶ merge PROPOSED
                                     (M6 loop)      (verify)      (gate)         │
                                                                                 ▼
                                                                    HITL inbox ── human approves ─▶ merge
```

The **architect** decomposes the feature into ordered slices — one per coder — and emits them as a typed plan, not a paragraph. Each **coder** runs the Module 6 loop on its slice: read, fix, run the suite in the sandbox, self-verify, hand back a verdict. The **tester** runs the acceptance suite and returns one deterministic ACCEPT or REJECT. The **reviewer** reads the diffs and the tester's verdict and decides whether to *propose* the merge. And the merge — the one irreversible action on the whole team — goes nowhere until a human approves it in the inbox.

Every arrow is a typed A2A message. Every box charges the budget, checks the kill switch, and writes an audit record before it acts. The governance is not a wrapper you bolt on at the end; it is the medium the agents move through.

## How it composes the parts you built

Three imports carry the whole system. Name them, because the reuse is the architecture.

**The coder node is the M6 agent.** `agents/coder.py` drives the same plan/act/observe loop over the same `tools.py`, `sandbox.py`, and `verify_gate.py` you shipped in Module 6. What M7 adds is governance threaded through the loop — every model call charges the fleet budget, the kill switch is read before every action, every tool call is checked against the agent's registry permissions and written to the audit. The loop did not change. The accountability around it did.

**The governance is the M4 fleet.** The registry-and-manifest contract is lesson 12's. The `FleetBudgetGuard` — per-agent `TaskBudget` under one team ceiling — is lesson 13's, which is itself the lesson-06 governor with attribution added. The shared HITL inbox is lesson 13's propose-then-commit-with-a-queue, which is lesson 08's protocol with more proposers. The audit and the kill switch are the single-agent controls pointed at five agents instead of one.

**The wire is M4 A2A.** `a2a.py` is the typed task / lifecycle / artifact shape from lesson 02 — a skill, a state (`submitted → working → completed | failed`), typed artifacts, and a correlation ID on every hop. A coder that receives a handoff for a skill it cannot perform fails at the boundary, not three steps downstream as a confident wrong answer.

The reason the reviewer can trust a coder at all is the verification interface from Module 6. The coder does not say "I fixed it." It runs the tests and hands over a verdict. A claim is not evidence; a passing suite is. That one design choice — made for a single agent two modules ago — is what makes a team governable today.

## The build sequence

You assemble the system bottom-up, contract first, because every layer reads the one below it.

1. **The registry and its schema.** Write `registry.yaml` — five agents, each with an `id`, a named `owner`, an `autonomy_tier`, least-privilege `permissions`, and a per-agent `budget_daily_usd`, plus a team ceiling and the merge gate. Write the JSON Schema and validate against it, so a malformed registry fails before it governs anything. This is the floor; everything else reads it.
2. **The policy layer.** `policy.py` turns the registry into authorization: an off-registry agent is refused (no identity, no owner — it fails the accountability test on arrival), and a tool outside an agent's grant is refused. No agent has `can_merge: true`.
3. **The governance package.** The `FleetBudgetGuard` (per-agent caps under a team ceiling), the shared HITL `inbox` (the merge gate), the `audit` log (the four-clause record threaded by correlation ID), and the `killswitch` (read-only to agents).
4. **The A2A wire.** `a2a.py` — the typed handoff message and result, validated on receipt.
5. **The nodes.** The architect, the two coders (the M6 loop, imported), the tester, and the reviewer — each a function that takes a typed task, acts under the governance context, and hands back a typed result.
6. **The orchestrator.** `fleet.py` loads the registry, builds the console from it, and drives the team through the handoffs — suspending at the inbox until a human decides the merge.

The deterministic mock drives every node on the smoke path, so the run is reproducible and proves the *governance* was the interesting part. A real model plugs into the same `respond` seam on any node with no contract change.

## The operator console

Module 8 hands this running fleet to a student who is its operator — and an operator needs a console, not a black box. This artifact exposes the full one, and every surface is a real control.

**The registry** is the source of truth for who is in the fleet — five agents, each with an owner, a tier, a permission grant, and a budget, in a file you can `git diff` and review in a pull request. It is not documentation of the fleet; it is the fleet. Point it at a new problem by editing it.

**The fleet budget** caps spend two ways at once: a per-agent ceiling and a team total. The reason both exist has a price tag. A real fleet capped only its manager loop and watched that manager spawn twelve retries on a flaky API, absorbing eight times the normal spend by morning, because nothing attributed the burn to the runaway workers underneath. So a runaway coder trips its own wall, and a swarm of small agents each under its own cap still trips the team's. Either breach stops the run before the next action.

**The HITL inbox** gates the one action you cannot take back. The merge proposal lands in one queue, the run suspends, and a human approves it by `inbox_id` — or it never happens. There is no off-channel approval and no auto-merge. A team that let an engineer approve a deploy by DM "just this once" could not answer "evidenced by what?" at the incident review, and compliance flagged it as a bypass. The inbox is how the merge stays evidenced.

**The cross-agent audit** is the surface that defines whether the fleet is governed at all. For any action, you must be able to answer one sentence: *which agent did it, with what authority, against what task, evidenced by what?* Four clauses — which, authority, task, evidence — threaded by a single correlation ID from the feature request through the architect, the coders, the tester, the reviewer, and the human merge. When a task crosses five agents, "evidenced by what?" only has an answer because one ID runs through all of it. A fleet that cannot answer all four for every action is not governed; it is unattended.

**The kill switch** is one file the operator owns, every loop reads before every action, and no agent can write. The only thing that changes from the single-agent version is the number of readers. If the off switch lived in an agent's reachable state, the agent could disable its own stop — so it does not.

## The BUILD→TEST gate

The finale raises the same gate Module 6 introduced, now for a composition. `python smoke.py` and `python -m pytest tests/` run on the standard library plus pytest alone — no Docker, no cloud, no network, no API key. The registry parses through a stdlib fallback when PyYAML is absent and validates through a pure-Python JSON Schema checker when `jsonschema` is absent, so the offline path needs nothing installed. The real model is opt-in through `.env`.

The smoke run proves the composition runs, not just a single agent: the five-agent team ships a feature end to end, suspends at the inbox, commits the merge only on a human approval, and prints an audit that answers all four clauses under the fleet budget. The test suite then pins each operator surface — the team ships end to end; the budget stops a runaway on the per-agent cap *and* on the team cap; the inbox blocks an unapproved and an off-channel merge; an off-registry agent is refused; the audit answers all four clauses; the kill switch halts the fleet before the next action. The test that the team can ship is table stakes. The tests that it *cannot* merge without a human, *cannot* overspend, and *cannot* act off the registry are the ones that make it infrastructure.

## The strong-project bar

Hireability is the point, and the done-when is a checklist this build meets: a real entry point you run from a terminal, not a notebook; a README that frames the business problem — a team that ships software, governed so a human stays accountable — before any code; an acceptance gate that ships the feature only on a tester ACCEPT and a human-approved merge; tests covering the end-to-end ship and every operator surface; a clean, versioned layout with no secrets committed; and a shipped `outputs/skill-governed-multi-agent-fleet.md`. The done-when is not "the team merged once." It is "the gate is green offline, and a stranger can read the README and understand both what the fleet builds and why a human is still in the loop."

## The Module 8 hand-off

This is the system the exam operates. Module 8 does not have you build something new on top of the fleet; it points the fleet at a production problem and asks you to run it. You are the operator, the judge, and the architect-of-record. You configure the budgets in the registry. You hold the kill switch. You work the HITL inbox — approve the merge, or reject it and say why. You read the cross-agent audit after the run and confirm it answers the four clauses. You judge the team's output against an acceptance rubric. The fleet is the substrate; the task is the input; your judgment is the grade.

Build it so that hand-off costs nothing. The registry is the contract M8 edits to retarget the team — a new agent, a tighter budget, a stricter gate, all reviewed changes to one file. The orchestrator reads the contract and runs whatever it points at, with no rewrite. That is the meaning of governance-as-code: a control plane reading a registry to know what it governs, Claude Code today and a local model tomorrow, the contract unchanged.

And that is the thesis, full circle. The book started by naming one job — the person who builds, serves, and governs the systems that run models. You built single agents. You composed them into a team. The team builds the final system, and you govern it. A fleet of agents run as governed infrastructure, with a human accountable for every action it takes, is not a feature of AI Platform Engineering. It is the whole of it — and you just built one that runs.

## What you build

You build a governed five-agent software-engineering team that ships a feature on its own and proves a human stayed accountable for every step. An architect plans the feature into slices; two coder nodes — each the Module 6 coding agent, reused whole — implement and self-verify in their sandboxes; a tester runs the acceptance suite for a deterministic verdict; a reviewer gates; and the merge waits in a shared HITL inbox until a human approves it by ID. The whole run executes under a fleet budget that caps each agent and the team, threads every action through a cross-agent audit by correlation ID, and answers to a kill switch the operator holds. Deterministic mocks drive the offline smoke run so the BUILD→TEST gate is reproducible on the standard library alone; a one-line swap puts a live model behind any node. It is the largest system in the course, built by composition — and it is the fleet Module 8 operates.

## Core concepts

- A governed multi-agent fleet is built by composition, not invention: the coder nodes are the Module 6 coding agent reused whole, and the governance is the Module 4 fleet — a fleet artifact that rewrites the loop or re-derives propose-then-commit has misread the architecture.
- The hard half of a team of coding agents is not getting them to build; it is keeping a human accountable — the merge is the one irreversible action, so it is the one human gate, and no agent on the team has authority to merge.
- The accountability test — *which agent, with what authority, against what task, evidenced by what?* — is answerable only because one correlation ID threads every action across all five agents and the human merge; a fleet that cannot answer all four clauses for every action is unattended, not governed.
- The fleet budget caps per-agent and team-total at once because attribution is what catches the runaway delegation a manager-only cap misses; either wall stops the run before the next action.
- The operator console — registry, fleet budget, HITL inbox, cross-agent audit, kill switch — is the Module 8 substrate: the task is an input and the registry is the contract, so the fleet retargets to a production problem with no rewrite.

<div class="claude-handoff" data-exercise="exercises/module7/03-governed-multi-agent-fleet/">

**Build it in Claude Code** — assemble the governed SWE team. Write `registry.yaml` (architect, coder-1, coder-2, reviewer, tester, each with `id`/`owner`/`autonomy_tier`/least-privilege `permissions`/`budget_daily_usd`, a team ceiling, and a merge that is a human gate) and a JSON Schema you validate against with no `jsonschema` dependency. Import the Module 6 coding agent as `agents/coder.py` — do not rebuild the loop — and wrap it in the governance context: every model call charges the `FleetBudgetGuard` (per-agent under a team total), the kill switch is read before every action, and every action writes a four-clause audit record under one correlation ID. Build the architect, tester, and reviewer nodes; wire them with typed A2A handoffs (`a2a.py`); and have the orchestrator suspend at a shared HITL inbox so the merge needs a human approval by `inbox_id` — never auto-merge. Drive it all with deterministic mocks so `python smoke.py` ships a feature offline and prints the audit's four clauses, and write `tests/` that prove the team ships end to end, the budget stops a runaway on the per-agent *and* the team cap, the inbox blocks an unapproved merge, an off-registry agent is refused, the audit answers all four clauses, and the kill switch halts the fleet. Keep the smoke path standard-library-only; make the real model opt-in per node via `.env`. Open the repo and run the exercise for this lesson.

</div>
