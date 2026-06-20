# Exercise 03 — The Four Primitives & Orchestration

**Goal** — Turn the `module4-fleet/` orchestrator into a real supervisor-worker system where the supervisor delegates to the researcher and writer through *direct tool calls* — owning every context boundary, with no supervisor library.

**Why** — Wiring supervision as tool calls keeps you in control of context flow, the one knob that decides both answer quality and cost; a supervisor library hides exactly that knob.

**Steps**

1. In `module4-fleet/orchestrator.py`, give the supervisor one tool per worker: `call_researcher(subtask)` and `call_writer(subtask)`. Each tool invokes the worker agent with a *fresh context* containing only its subtask.
2. Implement the supervisor loop: it produces a plan (who does what), calls the worker tools in order, collects each typed result, and synthesizes a final answer. Do **not** import any framework `create_supervisor()` helper — the control flow is your Python.
3. Enforce the context boundary on purpose: the supervisor passes each worker only its subtask, and each worker returns only its result. The supervisor never forwards one worker's raw output into another worker's context unless the plan requires it — and when it does, that forwarding is an explicit line you wrote.
4. Write `module4-fleet/PRIMITIVES.md` mapping your system's default on each of the four primitives:
   - **Agent** — what each agent is and its tool set.
   - **Handoff** — how control transfers (the tool call) and what context it carries.
   - **Shared state** — what's shared vs. private, and why.
   - **Orchestrator** — who decides who runs next.
5. In the same file, justify your topology choice (supervisor-worker here) and name one task shape that would push you to swarm or hierarchical instead.

**Done when**

- `orchestrator.py` runs a supervisor that delegates to both workers via direct tool calls and synthesizes a result — no supervisor framework imported.
- Each worker provably receives only its subtask (show it: print or log each worker's input context).
- `PRIMITIVES.md` fills all four knobs for your system and justifies the topology with a concrete alternative-trigger.

**Stretch** — Add a second worker context-flow mode behind a flag: one that forwards the researcher's full raw output into the writer's context, one that forwards only a supervisor-written summary. Run both and record the token-cost and quality difference. This is the fresh-context mechanism from lesson 01, measured.
