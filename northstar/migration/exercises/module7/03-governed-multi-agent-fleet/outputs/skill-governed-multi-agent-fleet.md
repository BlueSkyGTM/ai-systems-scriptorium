# Skill — Governed Multi-Agent Fleet (SWE team)

## What it proves

You can run a team of agents as governed infrastructure. Five typed roles — an
architect, two coders, a reviewer, and a tester — coordinate over typed A2A
handoffs to ship a software feature, wrapped in a fleet governance layer that
keeps a human accountable for every action: a registry that enumerates the team,
a budget that caps it per-agent and as a whole, a shared HITL inbox that gates
the merge, a cross-agent audit that answers the accountability test, and a kill
switch the operator holds. It demonstrates the thesis of the course full circle —
a fleet of agents run as governed infrastructure is AI Platform Engineering — and
it is built by composition, not invention: the Module 6 coding agent is the coder
node, the Module 4 fleet is the governance.

## What it does

Given a feature request and a project directory, the fleet:

1. **plans** — the architect decomposes the request into ordered slices, one per
   coder, as a typed A2A artifact (not a string to interpret);
2. **implements** — each coder runs the M6 plan/act/observe loop in its sandbox,
   self-verifies with the deterministic verify gate, and hands back a typed
   result — under the fleet budget, the kill switch, and per-agent permissions;
3. **verifies** — the tester runs the acceptance suite and returns one
   deterministic verdict; the reviewer reads the diffs and the verdict and gates;
4. **gates the merge** — the merge proposal lands in the shared HITL inbox and the
   run **suspends**; a human approves it by `inbox_id`; only then does the merge
   commit. No agent has merge authority; nothing auto-merges;
5. **stays accountable** — every action across every agent is recorded under one
   correlation id and answers *which agent, what authority, what task, what
   evidence* for the whole task.

## How to invoke

```bash
python smoke.py            # the governed 5-agent team ships a feature, offline
python -m pytest tests/    # the BUILD->TEST gate: ship + every operator surface
```

Offline, standard library + pytest. No API key, no Docker, no network. The
registry is parsed by a stdlib fallback when PyYAML is absent, and validated by a
pure-Python JSON Schema checker when `jsonschema` is absent.

## How to extend

- **Point it at a new problem:** edit `registry.yaml` — add an agent, change a
  budget, raise an autonomy tier, add a human gate. The orchestrator reads the
  contract; nothing else changes. This is the M8 hand-off.
- **Real model on any node:** `AnthropicLLM` in `client_llm.py` already wraps the
  Messages API tool-use loop behind the same `respond(messages)` seam. Pass it per
  agent: `fleet.ship_feature(..., models={"coder-1": AnthropicLLM()})`.
- **Stricter merge gate:** require two approvers, or a tier promotion, by
  extending the inbox decision rule — the propose-then-commit protocol does not
  change, only the policy around it.
- **Harder sandbox:** swap `sandbox.run` for a container runner; the coder loop
  reads a `SandboxResult` either way.

## The portable seams

- **the model seam** — `respond(messages) -> ModelResponse` — every node is
  model-agnostic;
- **the verification interface** — `verify(project_dir) -> Verdict` — "done" is a
  fact from running tests, which is what lets the reviewer trust a coder;
- **the registry contract** — `registry.yaml` + its schema — the fleet is
  addressable: a control plane reads it to know what it governs.

## What Module 8 reuses

This is the governed fleet Module 8 operates. The M8 student is the operator,
judge, and architect-of-record: they configure the budgets, hold the kill switch,
work the HITL inbox to approve or reject the merge, read the cross-agent audit
after a run, and judge the team's output against an acceptance rubric. The fleet
is the substrate; the production task is the input. Point the registry at a real
problem and this team is what builds it — under a human who stays accountable.
