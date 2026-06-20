# Skill — Terminal Coding Agent

## What it proves

You can build the canonical agent harness from the ground up: a plan/act/observe
loop that edits a real repository, runs its tests in a subprocess sandbox, and
stops only when a deterministic gate accepts the result — all under a cost
ceiling and a kill switch the agent cannot disable. It demonstrates that the
load-bearing engineering in a coding agent is the harness (tools, sandbox,
budget, verification), not the model call.

## What it does

Given a goal and a project directory, the agent:

1. **plans and acts** — reads the failing file, writes a fix, runs the tests,
   each as a validated, scoped tool call (`read_file` / `write_file` /
   `run_tests`);
2. **observes** — folds each tool result back into the message buffer so the
   next step reasons over what happened;
3. **stops on a verdict** — when the model declares done, the **verify gate**
   runs the tests and has the last word (default REJECT, ACCEPT only on a clean
   pass);
4. **stays bounded** — every model call is charged to a **budget** (per-task
   dollars + iteration cap) that stops the run on breach, and a **kill switch**
   the operator owns halts the loop before any action.

## How to invoke

```bash
python smoke.py            # end-to-end on the fixture with the deterministic mock
python -m pytest tests/    # the BUILD->TEST gate: smoke + the operator surfaces
```

Offline, standard library + pytest. No API key, no Docker, no network.

## How to extend

- **Real model:** implement nothing new — `AnthropicLLM` in `client_llm.py`
  already wraps the Anthropic Messages API tool-use loop behind the same
  `respond(messages)` seam the mock uses. Install `anthropic`, set
  `ANTHROPIC_API_KEY`, swap `MockLLM()` for `AnthropicLLM()`.
- **Different model vendor:** write one class with a `respond(messages)` method
  returning `(text | tool_call, cost_usd)`. The loop is model-agnostic.
- **Harder sandbox boundary:** replace `sandbox.run` with a container or
  microVM runner. The loop reads a `SandboxResult`; the boundary swap is local
  to one file.
- **Richer tools:** add to `TOOL_SCHEMAS` and `dispatch` in `tools/`. The
  registry validates and scopes every call to the project root.

## The portable seam

Two interfaces carry across every future build:

- **the model seam** — `respond(messages) -> (action, cost)` — makes the agent
  model-agnostic;
- **the verification interface** — `verify(project_dir) -> Verdict` — makes
  "done" a fact from running code, not a claim from the model.

## What M7 reuses

This agent is the **coder node** of the Module 7 multi-agent software team. The
architect plans, the coder (this artifact) edits and self-verifies in its
sandbox, the reviewer gates, the tester confirms. M7 imports this loop — the
tool surface, the sandbox, the budget, the kill switch, and the verify gate —
and composes it; it does not rebuild it. The verification interface is what lets
the reviewer trust the coder's output: a verdict file, not a promise.
