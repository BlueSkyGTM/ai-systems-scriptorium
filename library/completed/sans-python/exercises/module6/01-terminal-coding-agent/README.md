# Terminal Coding Agent

A plan/act/observe agent that fixes a bug in a code repository — under a cost
ceiling, a kill switch, and a verification gate. The build brief for Module 6,
Artifact 01.

## The business problem

A developer hour is the most expensive line item most software teams have, and
a large share of it goes to work that is mechanical but not trivial: reproduce
the failure, read the file, make the edit, run the tests, repeat until green. A
terminal coding agent does that loop on its own and hands back a verified diff.
The payoff is not "the model writes code" — chat already does that. The payoff
is the **closed loop**: the agent acts on a real repository, observes the test
result, and keeps going until a deterministic gate says the work is done.

The hard part is not the model call. It is the harness around it — the tool
surface, the sandbox that runs untrusted test code, the budget that stops a
runaway before it bills you, and the gate that refuses to call a task done on
the model's say-so. This artifact is that harness, small enough to read in one
sitting and real enough to pass a build gate.

## How to run

No API key, no Docker, no network. Standard library + pytest only.

```bash
# End-to-end happy path: plan -> read -> fix -> run tests -> verify, under budget
python smoke.py

# The BUILD->TEST gate: smoke + all four operator surfaces
python -m pytest tests/
```

`smoke.py` copies the broken fixture to a temp directory, runs the agent with a
deterministic mock model, prints the trace, and exits 0 only when the verify
gate ACCEPTs.

## What's here

| File | Role |
|------|------|
| `agent.py` | the plan/act/observe loop, under budget + kill switch + verify gate |
| `tools/` | `read_file`, `write_file`, `run_tests` — the scoped, validated tool surface |
| `sandbox.py` | subprocess runner with a wall-clock timeout (no Docker) |
| `budget.py` | the cost ceiling — per-task dollars + iteration cap; breach stops the run |
| `killswitch.py` | a boolean the agent reads but cannot write |
| `verify_gate.py` | runs the fixture's tests; default REJECT, ACCEPT only on a clean pass |
| `mock_llm.py` | the deterministic model that drives the offline smoke run |
| `client_llm.py` | the opt-in real Anthropic adapter, behind the same `respond()` seam |
| `fixture/` | a tiny broken project: one failing test the agent must fix |
| `smoke.py` | the end-to-end runnable entry point |
| `tests/` | the gate: smoke + budget breach + kill switch + verify-gate REJECT |
| `outputs/` | the skill artifact |

## The operator surfaces (what M8 drives)

Every artifact in this course exposes the surfaces a human operator runs:

- **Cost ceiling** — `Budget(max_usd, max_turns)`. Charged on every model call;
  on breach the run stops *before* the next action. Set it where a healthy task
  clears it and a runaway hits a wall in seconds.
- **Kill switch** — `KillSwitch(path)`. The loop checks it before every action.
  The agent is handed a read-only view; only the operator's `OperatorKillSwitch`
  can engage or clear it. The agent cannot turn off its own stop.
- **Verify gate** — `verify_gate.verify(project_dir)`. Deterministic, no model.
  Runs the tests; ACCEPT only on a clean pass, REJECT on anything else
  (failures, timeouts, collection errors). The agent never marks its own work
  done.

## Extending to a real model

The loop talks to the model through one method: `respond(messages)`. The mock
implements it; so does `AnthropicLLM` in `client_llm.py`. To swap:

1. `pip install anthropic`
2. `cp .env.example .env` and set `ANTHROPIC_API_KEY`
3. In `smoke.py`, replace `MockLLM()` with `AnthropicLLM()` from `client_llm`.

Nothing else changes — the loop, tools, budget, kill switch, and gate are all
model-agnostic. That is the portable seam.

## Strong-project checklist (the done-when)

- [x] Real entry point, not a notebook (`python smoke.py`)
- [x] README frames the business problem, not just the code
- [x] Tests: smoke + one test per operator surface
- [x] Evaluation: the verify gate is a pass/fail acceptance check on a fixture;
      a second approach (LLM self-report) is shown to be insufficient — the
      bad-patch test proves the gate catches what self-report misses
- [x] Versioned, clean layout (no secrets committed; `.env` is opt-in)
- [x] Ships `outputs/skill-terminal-coding-agent.md`
- [x] Passes the BUILD->TEST gate offline (stdlib + pytest, no Docker/cloud)
