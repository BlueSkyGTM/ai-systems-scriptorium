# The terminal coding agent

A chatbot writes code you paste. A coding agent reads the repository, makes the edit, runs the tests, and keeps going until they pass — and the gap between those two things is the entire job of this build.

## The business problem

The most expensive line on a software team's ledger is the developer hour, and a large share of it goes to work that is mechanical without being trivial: reproduce the failure, open the file, change three lines, run the suite, read the red, try again. By 2026 the settled answer to that drain is the terminal coding agent — a harness around a frontier model that runs the loop end to end, command line in, verified diff out.

Here is the part that surprises people who have only watched a model autocomplete a function: the model is the easy half. A capable model in a chat window already writes correct code most of the time. What it cannot do is *act* — touch a real file, run a real test, see the real result, and decide what to do next without a human relaying each step. The value is the closed loop, and the loop is yours to build.

So the hard part is not the model call. It is the harness: the tool surface that turns the model's intent into a file write, the sandbox that runs untrusted test code without hanging the loop, the budget that stops a runaway before it bills you for ten thousand turns, and the gate that refuses to call a task done because the model felt confident. Get those right and any model is shippable. Get them wrong and you have an expensive infinite loop waiting for the right prompt.

## The capability, the one stack, and the portable seam

The capability is narrow and complete: **plan, act, observe, repeat, under a cost ceiling and a verification gate.** You build it once, here, on one stack.

The stack is the **Claude Agent SDK in Python**, a **subprocess sandbox** (no Docker), and the Part-2 harness sequence from the Module 5 capstone, standing on the Module 3 agent-workbench pack. The loop you build is the Messages API tool-use loop: the model emits a `tool_use` block, your harness executes it and returns a `tool_result`, and the exchange repeats until the model stops calling tools. The same shape carries to other platforms — Azure AI Foundry's Agent Service exposes it as Runs and Run Steps, where a run polls through `requires_action` while you submit tool outputs — which is the point of building the loop yourself rather than renting it. The default model is `claude-opus-4-8`; a cheaper pass can run on `claude-haiku-4-5`.

But one stack is a teaching choice, not a lock-in, and the design protects you from it. Two interfaces carry across every model and every vendor you will ever swap in:

- **the model seam** — `respond(messages)` returns either a tool call or a final answer, plus a token cost. The loop knows nothing about Anthropic, OpenAI, or anyone else. Wrap a different vendor in a class with that one method and the loop does not change.
- **the verification interface** — `verify(project_dir)` returns a verdict from *running the tests*, not from asking the model. "Done" is a fact, not a claim.

Those two seams are the portable core. Everything vendor-specific lives behind the model seam in one adapter file; everything that decides truth lives behind the verification interface. Hold that line and the agent outlives the stack you built it on.

## The build sequence

The Module 5 capstone lays the harness down as a dependency-ordered arc — components 20 through 29 — and your artifact is the condensed payoff of that arc. You do not build all ten as separate modules; you build the spine they describe.

1. **The loop contract (20).** Freeze the agent loop as a small state machine: observe, think, act, repeat, with the model as a coprocessor wired in at the model seam. Everything else plugs into this shape.
2. **The tool registry (21).** A map of tool name to schema to handler. The registry validates arguments against the schema before dispatch, so a malformed call comes back as an observation the model can correct — not an exception that kills the run.
3. **The transport and dispatcher (22–23).** The capstone speaks JSON-RPC over stdio so a tool can live in its own process; your condensed scaffold collapses that wire format into an in-process registry, but the dispatch seam is the same. It is where the harness pays for the promises the schema made: it executes the validated call, scopes it to the project root, and turns a tool crash into a structured error string instead of a stack trace.
4. **Plan and execute (24).** What turns a script into an agent. The loop appends each action and its observation to the buffer, and the next think step reasons over what happened — read a malformed file, decide to fix it, run the tests, read the red.
5. **The verification gate (25).** The first of two layers between the model and the truth. Deterministic, no model: it runs the tests and returns one verdict.
6. **The sandbox runner (26).** A `subprocess` call with a wall-clock timeout. It bounds runaway *time* and captures output as structured data. Framed honestly: this is a dev-time guardrail, not an OS security boundary — and the capstone says so in the same breath, pairing the timeout with a denylist and a path jail.
7. **The eval harness (27) and observability (28).** A fixture is a goal plus a verifier; the harness scores pass/fail deterministically and the trace makes the run a white box you can read.
8. **The end-to-end agent (29).** Stitch it together. The capstone proves the point by driving the demo with a *deterministic* policy instead of a live model — which makes the run reproducible and shows the harness was the interesting part. A real model plugs into the policy seam with no contract change. Your scaffold does exactly this.

That last move is the one to internalize. A scripted policy and a frontier model are interchangeable at the seam, so you can prove the harness works without spending a cent, then swap the model in for production. The harness is what you were building all along.

## The operator surfaces

Module 8 hands the running system to a student who is the operator — they set the budgets, hold the kill switch, and judge the output against a rubric. So every artifact has to expose those controls for real, not as decoration. This one exposes three.

**The cost ceiling.** A bug in a normal service throws and stops. A bug in an agent keeps reasoning, keeps calling tools, and keeps billing — the failure has a name, Denial of Wallet, and the only defense is a limit that fires before the invoice. The budget charges every model call and carries two caps: a per-task dollar allowance that maps to business value, and an iteration cap that catches the loop that never decides it is done. On breach it stops the run *before* the next action. It is deliberately boring deterministic code — a budget you ask a model to enforce is a budget the model can talk its way out of.

**The kill switch.** A boolean the agent reads before every action and cannot write. That second clause is the whole point: if the off switch lives in the agent's reachable state, the agent can disable its own stop, and you have a kill switch in name only. Here the operator holds the write path and the agent is handed a read-only view. In production this is a feature flag or a Redis key under a read-only ACL; locally it is a file the agent can stat but never create.

**The verification gate.** An agent that decides it is finished is not finished — it is optimistic. The gate is the antidote: deterministic code, no model, that runs the fixture's tests and returns one verdict. The default is REJECT. It accepts only on a clean pass; failing tests, a timeout, an import error all reject. The agent never marks its own work done, and that is not a nicety — it is the difference between a demo and a thing you would let near a codebase.

## The BUILD→TEST gate

This module adds a runnable code gate, and the agent has to pass it locally and offline before it ships. The bar is exact: `python smoke.py` and `python -m pytest tests/` run on the **standard library plus pytest alone** — no Docker, no cloud, no network, no API key. Every third-party import sits behind a guard, and the real model is opt-in through `.env`.

The smoke run copies the broken fixture to a throwaway directory, drives the loop with the deterministic mock, and prints the trace: read the file, write the fix, run the tests, verify ACCEPT, exit zero. The test suite then pins each claim the harness makes — the smoke run fixes the fixture, a budget breach stops the run, the kill switch halts before the next action, and the verify gate REJECTs a bad patch even when the model declares success. That last test is the one that earns the gate's trust: a model saying "I fixed it" is not evidence, and the test proves the gate catches the lie.

## The strong-project bar

Hireability is the whole point of these artifacts, and "strong project" has a checklist. This build meets it: a real entry point you run from a terminal, not a notebook; a README that frames the business problem before the code; an evaluation that is a genuine pass/fail acceptance check, with the model's self-report shown to be the weaker approach the gate has to backstop; tests covering the smoke path and every operator surface; a clean, versioned layout with no secrets committed; and a shipped `outputs/skill-terminal-coding-agent.md`. The done-when is not "it runs once" — it is "it runs green on the gate, offline, and a stranger can read the README and know why it exists."

## What you build

You build a terminal coding agent that fixes a bug in a small Python project and proves it. The loop reads the failing file, writes a corrected version, runs the suite in a subprocess sandbox, and stops only when a deterministic gate accepts the result — the whole time bounded by a dollar-and-turn budget and a kill switch it cannot touch. A deterministic mock model drives the offline smoke run so the build gate is reproducible; a one-line swap puts a live Anthropic model behind the same seam. It is small enough to read in a sitting and real enough to become the coder node of a software team.

## What M7 reuses

Nothing here is a throwaway. In Module 7 this exact agent becomes the **coder node** of the multi-agent software team: an architect plans, the coder edits and self-verifies in its sandbox, a reviewer gates, a tester confirms. M7 imports this loop — the tool surface, the sandbox, the budget, the kill switch, the verify gate — and composes it. It does not rebuild it. And the reason the reviewer can trust the coder at all is the verification interface you built here: the coder hands over a verdict file, not a promise. That is what compounding means — the single agent you make verifiable today is the team member you can govern tomorrow.

## Core concepts

- The hard part of a coding agent is the harness — tool surface, sandbox, budget, verification gate — not the model call; a capable model is the easy half.
- The model seam (`respond(messages)`) and the verification interface (`verify(project_dir)`) are the portable core: they make the agent model-agnostic and make "done" a fact from running tests rather than a claim from the model.
- A deterministic policy and a frontier model are interchangeable at the loop's seam, so you can prove the harness works offline before spending a cent on inference.
- The three operator surfaces are real controls, not decoration: a cost ceiling that stops the run on breach, a kill switch the agent reads but cannot write, and a verify gate that defaults to REJECT.

<div class="claude-handoff" data-exercise="exercises/module6/01-terminal-coding-agent/">

**Build It in Claude Code** — build the terminal coding agent: a plan/act/observe loop calling `read_file`/`write_file`/`run_tests` tools, a subprocess sandbox with a timeout (no Docker), and the three operator surfaces — a budget that stops the run on breach, a kill switch the agent reads but cannot write, and a verify gate that runs the fixture's tests and defaults to REJECT. Drive it with a deterministic mock model so `python smoke.py` fixes a broken fixture offline, and write `tests/` that prove the smoke run passes, a budget breach stops the run, the kill switch halts before the next action, and the gate rejects a bad patch. Keep the smoke path standard-library-only; make the real Anthropic model opt-in via `.env`.

</div>
