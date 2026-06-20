# Autonomous Research Agent

A research *team* that answers a question it cannot fit in one context: a
supervisor decomposes the question, sub-agents research each piece in their own
sandboxes, a verification gate checks every finding, and the supervisor
synthesizes a cited answer — all under one shared budget and one kill switch.
The build brief for Module 7, Artifact 01.

## The business problem

A serious research question — "what makes a multi-agent system reliable in
production?" — does not fit in one agent's context, and one agent grinding
through it sequentially is slow, expensive, and impossible to trace. Worse, a
single agent that decides it is finished has no one checking whether its answer
is grounded or invented. The research that ships on that basis is a liability.

A research *team* fixes both problems. A supervisor splits the question into
independent sub-questions and fans them out to sub-agents that each work a fresh,
isolated context. Every sub-agent's finding passes a verification gate before it
can enter the answer — a fabricated citation is rejected, not synthesized. The
whole team runs under a single cost ceiling and a kill switch the agents cannot
disable. The payoff is not "more agents"; it is **governed parallelism**: a team
that produces a traceable, cited answer you can stand behind, for a bounded cost.

## What this composes (elevate, don't author)

This artifact reinvents nothing. It wires together patterns you already built:

| Reused from | What it contributes here |
|-------------|--------------------------|
| **M6 worker** (terminal coding agent, artifact 01) | `subagent.py` is the M6 loop — observe/think/act under a budget + kill switch — pointed at a research sub-question instead of a bug. |
| **M4 supervisor-worker** (four-primitives lesson) | `supervisor.py` plans, dispatches sub-agents, and synthesizes — wired as **direct tool calls**, not a supervisor library, so every context boundary is yours. |
| **M3 ReWOO / plan-execute** (planning lesson) | the supervisor's Planner decomposes before any tool fires; the Solver synthesizes a clean evidence packet. |
| **M3 CRITIC** (learning-from-failure lesson) | `verify_gate.py` grounds every finding against external evidence the sub-agent retrieved — the verification gap (MAST) closed with code. |
| **M4 fleet budget + kill switch** | `budget.py` is the per-task governor raised to a *shared* fleet pool; `killswitch.py` is one boolean the whole team reads but none can write. |

## How to run

No API key, no Docker, no network. Standard library + pytest only.

```bash
# End-to-end: plan -> dispatch sub-agents -> verify each -> synthesize, under budget
python smoke.py

# The BUILD->TEST gate: the composition + every operator surface
python -m pytest tests/
```

`smoke.py` runs the team on a fixed question with a deterministic mock model and
the fixture corpus, prints the team trace, and exits 0 only when the supervisor
synthesizes a cited answer from at least one verified finding.

## What's here

| File | Role |
|------|------|
| `supervisor.py` | the M4 supervisor: plan → dispatch → verify → synthesize, via direct tool calls |
| `subagent.py` | the M6 worker loop reused as a research sub-agent (search under budget + kill switch) |
| `sandbox.py` | a no-egress evidence corpus a sub-agent searches (read-only; no network) |
| `verify_gate.py` | grounds every citation against retrieved evidence; default REJECT |
| `budget.py` | the **shared fleet budget** — one pool across all agents; breach stops the team |
| `killswitch.py` | one boolean the whole team reads but no agent can write |
| `mock_llm.py` | the deterministic model (planner + sub-agent + solver) that drives the offline run |
| `client_llm.py` | the opt-in real Anthropic adapter, behind the same `plan`/`respond`/`synthesize` seams |
| `corpus.py` | the fixture evidence set the sandboxes search |
| `smoke.py` | the end-to-end runnable entry point |
| `tests/` | the gate: composition completes + reject-unverified + budget breach + kill switch |
| `outputs/` | the skill artifact |

## The operator surfaces (what M8 drives)

- **Fleet budget** — `FleetBudget(max_usd, max_calls)`. *Shared* across the
  supervisor and every sub-agent; a runaway is now N loops, not one, so the cap
  is at the team level. Charged on every model call; on breach the whole team
  stops before the next action. `summary()["by_agent"]` gives per-role spend.
- **Per-result verification gate** — `verify_gate.verify(finding, evidence_ids)`.
  Deterministic, no model. A finding reaches the answer only when every citation
  it makes is grounded in evidence the sub-agent actually retrieved. A fabricated
  citation is rejected — the cascading-error seed, removed.
- **Kill switch** — `KillSwitch(path)`. Read before every action by the
  supervisor and every sub-agent; none holds a write path. Only the operator's
  `OperatorKillSwitch` engages or clears it. Trip it once, the team halts.

## Extending to a real model

The team talks to the model through three seams: `plan(question)`,
`respond(messages)`, `synthesize(question, findings)`. The mock implements all
three; so does `AnthropicLLM` in `client_llm.py`. To swap:

1. `pip install anthropic`
2. `cp .env.example .env` and set `ANTHROPIC_API_KEY`
3. In `smoke.py`, replace `MockLLM()` with `AnthropicLLM()` from `client_llm`.

Nothing else changes — the topology, sandbox, budget, kill switch, and gate are
all model-agnostic. That is the portable seam.

## Strong-project checklist (the done-when)

- [x] Locally-runnable *composition*, not a notebook (`python smoke.py` runs a team)
- [x] README frames the business problem, not just the code
- [x] Tests: the composition completes + one test per operator surface
- [x] Evaluation: the verify gate is a per-result acceptance check; the
      fabricated-citation test proves it catches what a sub-agent's self-report misses
- [x] Versioned, clean layout (no secrets committed; `.env` is opt-in)
- [x] Ships `outputs/skill-autonomous-research-agent.md`
- [x] Passes the BUILD->TEST gate offline (stdlib + pytest, no Docker/cloud)
