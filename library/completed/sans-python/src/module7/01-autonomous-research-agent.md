# The Autonomous Research Agent

One agent grinding through a hard research question is slow, expensive, and, worse, answers to no one. This build replaces it with a team that splits the work, checks itself, and runs on a leash.

## The Business Problem

A real research question does not fit in one context window. Ask "what makes a multi-agent system reliable in production?" and a single agent has to hold the failure literature, the verification techniques, and the cost-governance patterns at once, then reason over all of it in one degrading buffer. It is slow because it works in sequence, and it is expensive because every turn re-reads everything. But the cost is not the part that should worry you.

The part that should worry you is that a lone agent grades its own homework. When it decides it is finished, nobody checked whether its answer is grounded in evidence or invented on the spot. Berkeley's MAST study put a number on where multi-agent systems break, and the largest single cause after specification was the *verification gap*: no independent check, so a wrong answer ships because nobody was assigned to catch it. Research that goes out on that basis is not a productivity win. It is a liability with citations.

A research team fixes both problems at once. A supervisor splits the question into independent sub-questions and fans them out to sub-agents, each working a fresh, isolated context; parallel, and cheap because no agent carries the others' baggage. And every finding passes a verification gate before it can enter the answer, so a fabricated citation is rejected rather than synthesized. The payoff is not "more agents." It is **governed parallelism**: a traceable, cited answer you can stand behind, produced for a bounded cost.

## The Capability, and What It Composes

The capability is a sentence: **plan a question into sub-questions, research each in a sandbox, verify every finding, synthesize the verified ones; all under a shared budget and a kill switch.** That is a plan-execute-verify loop with sub-agents, the shape the Module 5 capstone calls an autonomous research agent.

Here is the discipline that makes this a Module 7 build and not a from-scratch one: you compose it. Nothing below is new code you invent. It is patterns you already shipped, wired together at a higher altitude.

- **The sub-agent is the Module 6 worker.** The research sub-agent is the terminal coding agent's loop, observe, think, act, under a budget and a kill switch, pointed at a sub-question instead of a bug. The job changes (retrieve evidence, not edit code); the loop does not. You import the shape; you do not rebuild it.
- **The supervisor is the Module 4 supervisor-worker pattern.** One lead plans and delegates, workers execute in fresh parallel contexts and report back, the lead synthesizes. And you wire supervision as **direct tool calls**, not a supervisor library, the 2026 guidance from that lesson, because the context boundary is the one knob that decides both answer quality and the bill, and a library hides it.
- **The planning is Module 3's ReWOO / plan-and-execute.** The supervisor's Planner describes the whole decomposition before any tool fires; the Solver synthesizes a clean evidence packet at the end. Two model calls bracket a parallel middle, instead of re-conditioning on the full history every turn.
- **The verification gate is Module 3's CRITIC.** Route the check through an external signal the generator cannot hallucinate around. For the coding agent that signal was a test run; here it is the evidence the sub-agent actually retrieved. A finding is accepted only when every citation it makes is grounded in that evidence.
- **The budget and kill switch are Module 4's fleet governance.** The per-task governor, raised to a shared pool across the whole team, and one boolean every agent reads but none can write.

Name what you reuse and the build shrinks to the part that is genuinely new: the seams between these pieces.

## The Build Sequence

You assemble the team in the order the data flows.

1. **The shared budget and the kill switch first.** Build the governance before the agents, so there is no moment where an agent runs ungoverned. The budget is the Module 6 cost ceiling with one change that matters: it is a *single shared pool* the supervisor and every sub-agent charge. A fan-out to N sub-agents can burn N times the tokens, so the runaway you are guarding against is a fleet of loops, not one; and the cap belongs at the team level. The kill switch is the same read-only boolean as Module 6, now read by every team member.
2. **The sandbox.** A sub-agent's "execution" is retrieval, so its sandbox is a no-egress evidence corpus it can search and nothing else. The capstone runs each experiment with no network egress and strict limits; the same principle applied to reading means a sub-agent reaches a fixed, vetted corpus, never the open internet. It returns evidence as structured records; each with an id a finding can cite.
3. **The sub-agent.** Drop the Module 6 worker loop in. One sub-question, a fresh context, one tool (`search`), the shared budget, the kill switch. It loops until it emits a finding or a control surface stops it. Critically, it does **not** mark its own finding verified; that authority lives one level up.
4. **The verify gate.** Deterministic code, no model. It reads a finding and the set of evidence ids the sub-agent retrieved, and accepts only when every citation in the finding is grounded in that set. A finding with no citation, or one that cites a source the sub-agent never pulled, is rejected. That second case is the fabricated citation, the seed of a cascading error, caught before it spreads.
5. **The supervisor.** Now wire the four into the supervisor-worker flow: `plan` the question into sub-questions, `dispatch` one sub-agent per sub-question (each in its own sandbox), `verify` each returned finding through the gate, and `synthesize` only the accepted findings into one cited answer. Every step is a function call you wrote; there is no hidden routing.

The deterministic mock is what lets you prove all of this offline. One mock plays three roles, Planner, sub-agent, Solver, behind the same seams a real model would, the same trick Module 6 used to make its run reproducible. Swap the mock for the Anthropic adapter and the topology does not change. That is the point of building the seams yourself.

## The Operator Surfaces

Module 8 hands this running team to a student who is the operator; they set the budget, hold the kill switch, and judge the output. So the controls have to be real. This team exposes three, and the first two are raised a level from Module 6.

**The shared fleet budget.** A single agent's runaway bills you for one loop. A team's runaway bills you for every loop at once, and a budget metered per-agent would let three sub-agents each stay "under budget" while the team as a whole blows past what the question was worth. So the budget is one pool. Every model call from any agent, supervisor or sub-agent, charges the same ledger, and a breach by any one of them stops the team before the next action. The ledger is tagged by agent, so the operator reads per-role spend the way they would read a bill: who cost what.

**The per-result verification gate.** This is the surface that closes the MAST verification gap, and it is the heart of why a team is trustable. Every finding is gated before synthesis; not the answer at the end, each finding on the way in. The gate is deterministic and external: it does not ask the sub-agent whether it is confident; it checks the sub-agent's claim against the evidence the sub-agent actually retrieved. An ungrounded finding never reaches the report. The default is REJECT, and the only path to ACCEPT is grounded citation.

**The kill switch.** One boolean the whole team reads before every action and no agent can write. The read-only boundary is the entire point: if any agent could clear the switch, the team could disable its own stop. The operator holds the write path; the agents hold a view that only reads. Trip it once and the supervisor and every sub-agent halt at their next action boundary.

## The BUILD→TEST Gate

The scaffold passes locally and offline before it ships, and the bar is the same as Module 6, raised for composition. `python smoke.py` and `python -m pytest tests/` run on the **standard library plus pytest alone**; no Docker, no cloud, no network, no API key. The `anthropic` import sits behind a guard; the real model is opt-in through `.env`.

The smoke run is the proof that a *team* coordinates, not one agent. It plans the fixed question into three sub-questions, dispatches three sub-agents that each search their own sandbox and return a cited finding, gates each finding, and synthesizes the verified ones; and the trace shows every step, with spend attributed across the agents. The test suite then pins each claim: the composition completes as a team; an unverified sub-result is rejected and never synthesized; a fleet budget breach stops the whole team before the next action; the kill switch halts it. The reject-unverified test is the one that earns the gate's trust; a sub-agent declaring an answer is not evidence, and the test proves the gate catches the fabricated citation the sub-agent was confident about.

## The Strong-Project Bar

These artifacts exist to be hireable, so "done" has a checklist and this build meets it: a real entry point you run from a terminal, not a notebook, and one that runs a *team* rather than a single agent; a README that frames the business problem before the code and names exactly what it reuses from M3, M4, and M6; an evaluation that is a genuine per-result acceptance gate, with the sub-agent's self-report shown to be the weaker signal the gate has to backstop; tests over the composition and every operator surface; a clean, versioned layout with no secrets committed; and a shipped `outputs/skill-autonomous-research-agent.md`. The done-when is not "it runs once"; it is "it runs green on the gate, offline, and a stranger reading the README can see which earlier agents this team is built from."

## What M8 Reuses

This team is a **node pattern**, and that is the thing to carry forward. The shape, *a supervisor plans, sub-agents work in isolated sandboxes, a gate verifies each result before it is used, and a shared budget plus a kill switch govern the whole*, is the reusable unit. The Module 7 finale wires several such governed nodes under one operator console, and Module 8 points that console at a production problem: it configures the budget, holds the kill switch, reads the verified-versus-rejected split, and judges the synthesized answer against a rubric. The verification gate is what makes that judgment possible at all; the report M8 grades is assembled from grounded findings, not from promises. Build the gate honest here, and every team you compose on top of it inherits a spine you can trust.

## What You Build

You build an autonomous research team that answers a question no single agent could hold. A supervisor decomposes the question, dispatches one sub-agent per sub-question into its own no-egress sandbox, verifies each returned finding against the evidence it actually retrieved, and synthesizes only the verified findings into one cited answer; the whole team bounded by a shared budget and a kill switch it cannot disable. A deterministic mock plays planner, sub-agent, and solver so the build gate runs offline and reproducible; a one-line swap puts a live Anthropic model behind the same seams. It reuses the Module 6 worker, the Module 4 supervisor-worker pattern and fleet governance, and the Module 3 ReWOO and CRITIC patterns, composed, not rebuilt, and it becomes a node the Module 8 system governs.

## Core Concepts

- A research team beats a lone research agent not by adding agents but by adding governance: isolated sub-agent contexts make the work parallel and cheap, and a per-finding verification gate makes the answer trustable; the MAST verification gap closed with code.
- The build composes rather than authors: the sub-agent is the M6 worker loop, the supervisor is the M4 supervisor-worker pattern wired as direct tool calls, the planning is M3 ReWOO, and the gate is M3 CRITIC; naming what you reuse shrinks the build to the seams between them.
- A fleet budget is a single shared pool, not a per-agent allowance, because a team's runaway is N loops at once; a breach by any agent stops the whole team, and the ledger is tagged per agent so cost is attributable.
- The verify gate is deterministic and external: a finding enters the answer only when every citation is grounded in evidence the sub-agent actually retrieved, so a fabricated citation is rejected before it can cascade; the sub-agent never marks its own work done.

<div class="claude-handoff" data-exercise="exercises/module7/01-autonomous-research-agent/">

**Build It in Claude Code**: Compose the autonomous research team: a supervisor that plans a question into sub-questions and dispatches them through direct tool calls (the M4 supervisor-worker pattern), sub-agents that reuse the M6 worker loop to search a no-egress sandbox and return cited findings, a verify gate that grounds every citation against retrieved evidence and defaults to REJECT (M3 CRITIC), and the operator surfaces; a *shared* fleet budget that stops the whole team on breach, and a kill switch every agent reads but none can write. Drive it with a deterministic mock that plays planner, sub-agent, and solver so `python smoke.py` runs the whole team offline, and write `tests/` that prove the composition completes as a team, an unverified finding is rejected (not synthesized), a budget breach stops the team, and the kill switch halts it. Keep the smoke path standard-library-only; make the real Anthropic model opt-in via `.env`.

</div>
