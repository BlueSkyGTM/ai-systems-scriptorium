# Module 4 Harness — the `module4-fleet/` substrate

This is the starter substrate every Module 4 exercise builds on. Copy it to `module4-fleet/` and extend it
lesson by lesson. It is deliberately minimal — a starter, not a finished system. The governance lessons add
the rest on top.

## What's here

```
_harness/
├── README.md              (you are here)
├── orchestrator.py        minimal supervisor: routes a task to one of two agents, collects the result
├── registry.yaml          machine-readable fleet registry: agents with id, role, permissions
└── agents/
    ├── researcher.py       stub agent — reuses the module3-agent loop shape
    └── writer.py           stub agent — reuses the module3-agent loop shape
```

## Design

- **Control plane is Python.** The orchestrator and agents are plain Python — no agent framework imported.
  This is the everything-as-code stance the module teaches: you own the control flow.
- **Agents reuse the `module3-agent` loop shape.** Each agent is the same Observe → Think → Act skeleton you
  built in Module 3, with a deterministic stub model so the whole harness runs offline. No API key needed.
- **The registry is machine-readable.** `registry.yaml` lists each agent's `id`, `role`, and `permissions`.
  Everything that governs the fleet — identity, what each agent may touch — lives as code you can diff and
  review, not as prose in a system prompt.

## Run it

```bash
python orchestrator.py "summarize the project status"
```

The supervisor reads the registry, picks an agent by role, runs that agent's stub loop, and prints the
result plus a small trace. Swap the deterministic stub for a real model call when you want a live run; the
shape doesn't change.

## What later lessons add (on top of this, not instead of it)

This harness is the floor. As you work through Module 4 you bolt governance onto it:

- **Lesson 02** — a typed A2A wire contract for the agent↔agent handoff (no more passing raw strings).
- **Lesson 03** — a real supervisor-worker orchestrator with direct tool calls and owned context boundaries.
- **Lesson 04** — debate topologies and a MASFT failure-mode tagger over the run traces.
- **Later (Op-Safety + Fleet chapters)** — action budgets, a kill switch the agent reads but cannot write,
  human-in-the-loop propose-then-commit, and a full fleet registry with identity, audit, and economics.

Keep the harness coherent as you grow it: every capability is a layer the next lesson assumes is there.
