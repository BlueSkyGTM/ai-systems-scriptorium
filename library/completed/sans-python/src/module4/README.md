# Module 4: Multi-Agent Systems

The seam's defining material; where this course most *is* Production AI Engineering. The arc is one move,
made four times: single agent → runs safely for hours → coordinates with many → **governed as a fleet in
production.** The complexity ladder gates entry the whole way up: more agents, not a bigger agent, and only
past the rung below. The throughline artifact is `module4-fleet/`; a governed multi-agent system built on top
of the `module3-agent/` you already shipped, growing one governance capability per lesson from the seeded
`_harness/` starter.

The fifteen lessons:

**Multi-agent & swarms (01–04)**; when to split an agent and how the pieces talk. Why multi-agent (the
single-agent ceiling); communication protocols (MCP / A2A / ACP / ANP, and the FIPA-ACL heritage that shows
which "innovations" are reinventions); the four primitives & orchestration (supervisor / swarm / hierarchical,
supervised by direct tool calls); debate and the MAST failure taxonomy; most multi-agent failures are design
flaws, not model limits.

**Operational safety (05–09)**; how you run an agent that acts for hours without it bankrupting or betraying
you. Long-horizon durable execution (checkpoint / retry / replay, resume by `thread_id`); action budgets &
cost governors (Denial of Wallet); kill switches, circuit breakers, and canary tokens (the control plane the
agent reads but cannot write); HITL propose-then-commit with safe checkpoints/rollback; guardrails
(Constitutional AI + Llama Guard); and the honest limit, that a classifier is a layer, not a solution. These
five **define** the safety primitives the fleet later reuses.

**Fleet & loop engineering (10–13)**; the production operational layer, and the seam's center. "Loops live
inside fleets": the loop (`trigger → action → verification → budget/kill-switch`) and its named patterns; then
the fleet, registry, identity, permissions, inbox-HITL, audit, economics, kill-switch, as governance-as-code.
The single-agent controls from 06–08 are not rebuilt at fleet scale; they are imported.

**Computer-use, coding & voice (14–15)**; thin teaching. You learn how each works and where it breaks;
the build is the Module 6 artifact it seeds (coding → artifact 01, voice → artifact 03).

roadmap.sh treats multi-agent as a few subtopics; **this course makes it a full module**; agent
infrastructure and governance *is* the discipline. The frontier-safety *research/policy* layer (RSP, FSF,
METR, recursive self-improvement) is out of scope; the *operational* safety here is
kept. **→ Culminates in Module 7 (Multi-Agent Artifacts):** the fleet you assemble in lesson 13 is the
governance the finale runs on.
