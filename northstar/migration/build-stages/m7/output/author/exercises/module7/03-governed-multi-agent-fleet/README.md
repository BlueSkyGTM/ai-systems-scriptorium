# Governed Multi-Agent Fleet — the SWE Team (course finale)

A software-engineering team that ships software on its own — an architect, two
coders, a reviewer, and a tester coordinating over typed A2A handoffs — wrapped
in a fleet governance layer so a human stays accountable for everything it does.
The build brief for Module 7, Artifact 03: the largest system in the course and
the one Module 8 operates.

## The business problem

A single coding agent (Module 6) fixes one bug in one repo. A real feature is
bigger than one context window: it needs a plan, parallel work, a review, and a
test pass. The settled answer is a *team* of agents. But the moment you run five
agents that can edit code and merge it, the question stops being "can they
build?" and becomes "**can a human stay accountable for what they built?**" An
unattended team of coding agents is not a productivity win; it is an incident
waiting for a correlation id nobody wrote.

So this artifact is not a from-scratch fleet and not a from-scratch coding agent.
It is the **composition**: the Module 6 coding agent reused as the coder nodes,
wrapped in the Module 4 fleet layer — a registry that knows every agent, a
fleet budget that caps the team, a shared HITL inbox where a human approves the
merge, a cross-agent audit that survives an incident review, and a kill switch
the operator holds. A fleet of agents run as governed infrastructure is the whole
thesis of the course, here in one runnable system.

## How to run

No API key, no Docker, no network. Standard library + pytest only.

```bash
# The governed team ships a feature end to end, offline:
python smoke.py

# The BUILD->TEST gate: the smoke run + every operator surface
python -m pytest tests/
```

`smoke.py` copies the broken fixture to a temp directory, loads the registry,
and drives the five-agent team: architect plans, two coders implement (the M6
loop), the tester runs the suite, the reviewer gates, the merge is **proposed to
the HITL inbox**, a simulated human approves it, the merge commits, and the audit
answers all four accountability clauses. It never auto-merges.

## What's here

| File | Role |
|------|------|
| `fleet.py` | the orchestrator — loads the registry, runs the team through A2A under governance |
| `registry.yaml` | the five agents with id / owner / permissions / autonomy tier / budget |
| `schemas/registry.schema.json` | the registry's JSON Schema (validated by `schema.py`, no jsonschema dep) |
| `schema.py` | registry loader + pure-Python schema validator (stdlib-only) |
| `policy.py` | registry-driven authorization — off-registry and out-of-grant actions refused |
| `a2a.py` | typed agent-to-agent handoff messages (skill, lifecycle, artifacts, correlation id) |
| `agents/architect.py` | plans the feature into slices |
| `agents/coder.py` | the M6 coding-agent loop reused as a coder node |
| `agents/reviewer.py` | reads diffs + tester verdict, gates the merge proposal |
| `agents/tester.py` | runs the suite, returns one deterministic verdict |
| `governance/fleet_budget.py` | per-agent `TaskBudget` under one team ceiling (breach stops the run) |
| `governance/inbox.py` | the shared HITL inbox — the merge needs human approval, by id |
| `governance/audit.py` | every action -> correlation id + the four-clause accountability record |
| `governance/killswitch.py` | one switch the operator owns; no agent can write it |
| `tools.py` `sandbox.py` `verify_gate.py` | the M6 coder's tool surface, sandbox, and verify gate, reused |
| `mock_llm.py` | the deterministic policies that drive the offline smoke run |
| `client_llm.py` | the opt-in real Anthropic adapter, behind the same `respond()` seam |
| `fixture/` | a tiny broken project: one failing test the team must fix |
| `smoke.py` / `tests/` | the runnable entry point and the BUILD->TEST gate |
| `outputs/` | the skill artifact |

## The operator console (what M8 drives)

This is the full console the M8 student operates. Every surface is a real control,
not decoration:

- **Registry** (`registry.yaml`) — the machine-readable source of truth for who
  is in the fleet. Edit it to point the team at a new problem; it is an input.
- **Fleet budget** (`governance/fleet_budget.py`) — a per-agent cap AND a team
  ceiling. A runaway coder trips its own wall; a swarm of small agents trips the
  team's. Breach stops the run before the next action.
- **HITL inbox** (`governance/inbox.py`) — the merge is the one irreversible
  action, so it is the one human gate. The merge proposal waits in the inbox; a
  person approves it by `inbox_id`. No off-channel approval, no auto-merge.
- **Cross-agent audit** (`governance/audit.py`) — every action across every agent
  is threaded by one correlation id and answers *which agent, what authority,
  what task, what evidence*. Run `answers_four_clauses(correlation_id)` to
  reconstruct the whole task.
- **Kill switch** (`governance/killswitch.py`) — one file the operator owns; every
  loop checks it before every action and none can write it.

## How it composes M6 + M4 (elevate, don't author)

Nothing here is rebuilt:

- **M6 (artifact 01)** ships the coder node whole — `agents/coder.py` drives the
  same plan/act/observe loop over the same `tools.py`, `sandbox.py`, and
  `verify_gate.py`. The verify gate is why the reviewer can trust a coder: the
  coder hands over a verdict from running tests, not a promise.
- **M4 fleet (lessons 12/13)** ships the governance — the registry/manifest
  contract, the `FleetBudgetGuard` (per-agent + team), and the shared HITL inbox
  (propose-then-commit at fleet scale). The audit and kill switch are the
  single-agent controls pointed at many agents.
- **M4 A2A (lesson 02)** ships the wire contract — `a2a.py` is the typed task /
  lifecycle / artifact shape so a bad handoff fails at the boundary.

## Strong-project checklist (the done-when)

- [x] Real entry point, not a notebook (`python smoke.py`)
- [x] README frames the business problem before the code
- [x] Acceptance gate: the team ships a feature only when the tester ACCEPTs and a
      human approves the merge; the verify gate is a pass/fail check on a fixture
- [x] Tests: end-to-end ship + every operator surface (budget per-agent AND team,
      HITL block, off-registry refusal, four-clause audit, kill switch)
- [x] Versioned, clean layout; no secrets committed; `.env` is opt-in
- [x] Ships `outputs/skill-governed-multi-agent-fleet.md`
- [x] Passes the BUILD->TEST gate offline (stdlib + pytest, no Docker/cloud)
