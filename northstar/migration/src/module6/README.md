# Module 6 — Agent Artifacts

Single-agent portfolio builds, each solving a real business problem and shipping a skill artifact. This is
where Module 3 becomes proof. **These agents are the building blocks reused in Module 7** (the compounding
design).

Built in Claude Code via VS Code, on the M3 **agent-workbench pack** as the foundation.

| # | Artifact | Competency it proves | Reused in M7 as |
|---|----------|----------------------|-----------------|
| 01 | **Terminal coding agent** | the canonical harness — plan/act/observe, tools, sandbox, cost ceiling | the coder node of the SWE team |
| 08 | **Production RAG chatbot** (regulated vertical) | RAG + guardrails + citations + drift observability | the knowledge/retrieval service |
| 03 | **Real-time voice assistant** | streaming under hard latency budgets (ASR→LLM→TTS, barge-in) | human-interface channel |
| 16 | **Issue-to-PR autonomous agent** | autonomous cloud worker, scoped credentials, in-sandbox CI verification | the autonomous-execution pattern |

The Part-2 harness build sequence (20–29: loop contract → tool registry → JSON-RPC/stdio → dispatcher →
plan/execute → verification gates → sandbox runner → eval harness → observability → end-to-end agent) is the
buildable foundation of artifact 01.

**→ Reused and composed into teams in Module 7.**
