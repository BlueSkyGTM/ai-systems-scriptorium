# Reasoning & Loops

> **Migrated from** `aefs-module3-agent-engineering` (Ph14 01–05, 11) + `asdg-module3-agentic-systems`
> (Ch07). The single-agent reasoning spine.

The five ingredients that separate an agent from a chatbot: a message buffer, a tool registry, a stop
condition, a turn budget, and an observation formatter.

- **The agent loop (ReAct)** — Observe → Think → Act, built from stdlib in <200 lines. Every modern harness
  (Claude Agent SDK, OpenAI Agents SDK, LangGraph, AutoGen) runs this loop underneath. 2026 shift: native
  model reasoning replaces prompt-based `Thought:` tokens.
- **ReWOO / Plan-and-Execute** — decouple planning from execution: one plan DAG up front, parallel evidence
  fetches, one solver call (~5× fewer tokens, per-node failure localization).
- **Reflexion** — verbal reinforcement: after a failure the agent writes a reflection, stores it in episodic
  memory, conditions the next trial on it. Fixes failures in language, not gradients. (The pattern behind
  `CLAUDE.md` learnings and sleep-time compute.)
- **Tree-of-Thoughts / LATS** — reasoning as search: grow a tree of thoughts with per-node self-evaluation
  (ToT); LATS unifies ToT + ReAct + Reflexion under MCTS. Apply the cost-reality test — search's token
  multiplier is worth it only for high-stakes/offline work.
- **Self-Refine / CRITIC** — generate → feedback → refine; CRITIC routes the verification step through
  external tools (search, code, tests) because LLMs self-verify poorly on hard facts. Anthropic's
  "evaluator-optimizer."
- **Planning: HTN & evolutionary** — the two cases LLM planners miss: provably-correct plans (HTN, sound by
  construction) and machine-checkable optimization (evolutionary search where a fast deterministic evaluator
  exists). LLM as amplifier, not replacement.

**Complexity ladder (Gap 2):** the Anthropic workflow patterns (prompt chaining, routing, parallelization,
orchestrator-workers, evaluator-optimizer) cover most production cases. Start with direct calls → add a
workflow when steps are predictable → reach for an agent only when the next step genuinely depends on the
prior result.
