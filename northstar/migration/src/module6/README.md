# Module 6 — Agent Artifacts

Single-agent portfolio builds, each solving a real business problem and shipping a skill artifact. This is
where Module 3 becomes proof — and where the build gate changes: from here on, an exercise isn't done because
it renders, it's done because it **runs**. Each artifact passes a local, offline BUILD→TEST gate (a `smoke`
run + tests with a deterministic mock model, no cloud or GPU required) and exposes the **operator surfaces** —
budget, kill-switch, an audit/verification gate, an acceptance eval — that you will drive as the operator in
Module 8.

Built in Claude Code on the Module 3 **agent-workbench pack** and the Module 5 **`module5-serving/`** platform.
Each binds to a real platform (capability + one concrete stack + a portable seam), and runs dry-run-first:
mocks and `.env.example` locally, the real service opt-in. The "strong project" bar holds throughout — a real
entry point (not a notebook), a README that frames the business problem, evaluation, tests, versioned.

| # | Artifact | Competency it proves | Reused in Module 7 as |
|---|----------|----------------------|-----------------------|
| 01 | **Terminal coding agent** | the canonical harness — plan/act/observe, tools, sandbox, cost ceiling, verification gate | the coder node of the SWE team |
| 02 | **Production RAG chatbot** (regulated vertical) | RAG + guardrails + citations + drift observability | the knowledge/retrieval service |
| 03 | **Real-time voice assistant** | streaming under a hard latency budget (VAD→STT→LLM→TTS, barge-in) | the human-interface channel |
| 04 | **Issue-to-PR autonomous agent** | autonomous worker — scoped creds, in-sandbox CI verification, never auto-merge | the autonomous-execution pattern |

Cloud prerequisites and the dry-run-first setup live in [`exercises/module6/_prereqs/CLOUD-SETUP.md`](../../exercises/module6/_prereqs/CLOUD-SETUP.md).

**→ Reused and composed into governed teams in Module 7.**
