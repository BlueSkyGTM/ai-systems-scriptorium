# Exercise 14 — Computer-Use & Coding Agents

**Goal** — Read a coding-agent run trace and tag the untrusted-input boundary: every place the agent consumes input it must not trust, and where a sandbox boundary has to sit.

**Why** — The untrusted-input contract is the one thing from this lesson you carry into every computer-use, coding, and voice build. Seeing it in a live trace — not a definition — is the skill that keeps you from shipping an agent that treats a fetched page as a command. The coding agent itself is a Module 6 artifact; this is the read that prepares for it.

**Steps**

1. Get a trace. Use the `_harness/orchestrator.py` run trace (`python orchestrator.py "summarize the project status"`), or paste in a real coding-agent trace if you have one. You want a sequence of turns showing what the agent read and what it did.

2. Produce `module4-fleet/UNTRUSTED_INPUT_AUDIT.md` with three sections:

   **Untrusted inputs** — for each turn, list every input the agent consumed that it must NOT treat as permission: tool output, file content, a fetched web page, screen/DOM text, another agent's message. Cite the turn or line.

   **The one trusted source** — identify the direct user instruction(s) — the only input that counts as permission per the lesson's contract. State plainly how an observer (or the agent) tells it apart from the untrusted inputs above.

   **Sandbox boundary** — mark where a sandbox boundary must sit for this trace (the point past which generated code or actions execute). For one untrusted input of your choice, write one sentence on what would breach if a hostile value arrived there and no sandbox or deterministic control stopped it.

3. Verify your audit names at least one concrete indirect-prompt-injection scenario: a specific untrusted input that, if attacker-authored, could redirect the agent toward a real-world action.

**Done when**

- `UNTRUSTED_INPUT_AUDIT.md` exists with all three sections populated.
- Every "Untrusted inputs" entry cites a specific turn or line in the trace, not a general category.
- The "Sandbox boundary" section names a concrete breach tied to one untrusted input — what action could happen, not "something bad."
- At least one indirect-prompt-injection scenario is written out, with the attacker-controlled input named.

**Stretch** — Tie it back to the safety chapter: pick one breach from your audit and name which deterministic control from lessons 06–08 (kill switch, action budget, or HITL gate) would stop the action even if the untrusted input slipped past. One sentence; cite the control.
