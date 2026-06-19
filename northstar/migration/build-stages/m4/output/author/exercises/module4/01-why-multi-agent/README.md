# Exercise 01 — Why Multi-Agent

**Goal** — Stand up `module4-fleet/` on top of the `_harness/` starter, then prove a single agent hits one of the three single-agent walls and document where multi-agent earns its place.

**Why** — Multi-agent is the next rung of the complexity ladder; an AI Platform Engineer reaches for it only when a single agent hits a nameable wall, never as a default.

**Steps**

1. Copy the `_harness/` starter into your working area as `module4-fleet/` — this is the throughline artifact every M4 exercise extends. It already contains a Python orchestrator, two stub agents (researcher, writer), and a fleet registry.
2. Run the harness once as-is (`python orchestrator.py`) and confirm it routes a task to one stub agent and prints a result. Read the README so you know what the substrate gives you.
3. Pick one of the three walls from the lesson and force it with the *single* researcher agent alone:
   - **Context overflow** — feed it an input larger than a chosen token cap and watch it truncate or degrade.
   - **Mixed expertise** — give one agent a prompt that demands two conflicting roles (research *and* terse editing) and observe the dilution.
   - **Sequential bottleneck** — give it N independent sub-tasks and measure the wall-clock cost of doing them one at a time.
4. Write `module4-fleet/CEILING.md` (4–6 sentences): which wall you hit, the evidence (a number, a degraded output, a timing), and why splitting into more agents — not a bigger one — is the fix.
5. Add a one-line note to `CEILING.md` naming the cost you now accept by going multi-agent (latency, tokens, or debugging).

**Done when**

- `module4-fleet/` exists, derived from `_harness/`, and `python orchestrator.py` runs without errors.
- You have reproduced one of the three walls with concrete evidence (a printed metric or a captured degraded output), not an assertion.
- `CEILING.md` names the wall, the evidence, the fix, and the cost accepted — no "looks like it would fail."

**Stretch** — Quantify the bottleneck: run the same N sub-tasks sequentially through one agent and fanned out across two harness agents, and record the wall-clock and token deltas. Decide from the numbers whether the split is worth it for this task size.
