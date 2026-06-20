# Exercise 02 — Communication Protocols

**Goal** — Replace string-passing between the two `module4-fleet/` agents with a real wire-format handoff: discover the worker's skills via an A2A Agent Card, delegate a task over a typed A2A message, and prove a malformed handoff fails at the boundary.

**Why** — A typed wire contract is where the AI Engineer's "can these agents coordinate" meets the MLOps engineer's "is every handoff typed and auditable"; raw strings fail both on misinterpretation, deadlock, and scale.

**Steps**

1. In `module4-fleet/`, have the worker (researcher) publish an **Agent Card** at a well-known path (`/.well-known/agent.json` served by `http.server`, or a local JSON file the supervisor reads). The card lists the worker's `skills`, each with an input schema.
2. Reuse your Module 3 MCP TypeScript types for the wire contract. Add `wire/a2a.ts` defining the `A2ATask`, `A2AState` (`submitted | working | completed | failed | canceled`), and `A2AResult` shapes from the lesson. Keep the control plane in Python; the typed wire format is the place a strong type earns its keep.
3. Wire the handoff: the supervisor reads the worker's Agent Card, selects a `skill`, and sends a typed `tasks/send` message. The worker validates the incoming `skill` against its card and the input against that skill's schema before doing any work.
4. On success, the worker returns an `A2AResult` with `state: "completed"` and a typed `artifacts` array — not a free-text string.
5. **Break it on purpose.** Send a task naming a skill the worker doesn't advertise, or an input that violates the schema. Confirm the worker returns `state: "failed"` with a reason *at the boundary* — before any downstream step runs.
6. Add a short `module4-fleet/wire/README.md` noting which layer of the four-protocol stack (MCP / A2A / ACP / ANP) each piece belongs to, and the one FIPA-ACL ancestor the task lifecycle echoes.

**Done when**

- The supervisor discovers the worker's skills from its Agent Card rather than hard-coding them.
- A valid handoff produces a typed `A2AResult` with `state: "completed"` and typed artifacts.
- A malformed handoff returns `state: "failed"` with a reason at the boundary — verified by a test or a run whose output shows the failure happening before any downstream work.
- No agent-to-agent step passes a raw string the receiver parses by guesswork.

**Stretch** — Add the audit layer: log every task transition (`submitted → working → completed/failed`) to an append-only `runs.jsonl` the agents can read but not rewrite. That is the ACP layer in miniature, and the fleet audit in lesson 13 builds on it.
