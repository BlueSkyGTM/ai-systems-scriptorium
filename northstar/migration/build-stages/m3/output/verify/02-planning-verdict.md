# Verdict: 02-planning

## Markers resolved

**Marker 1** — `[MS-Learn: Azure AI Foundry — multi-step agent planning and parallel tool execution]`
- Query: "Azure AI Foundry multi-step agent planning parallel tool execution ReWOO Plan-and-Execute"
- Validated by: https://learn.microsoft.com/agents/architecture/multi-agent-workflow-oriented (confirms parallel/serial agent execution, fan-out patterns); https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns (confirms fan-out/fan-in for parallel tool execution)
- Note: ReWOO and Plan-and-Execute are academic paper patterns, not named Foundry features. MS docs confirm the underlying parallel-execution mechanism the lesson is grounded in. The lesson correctly attributes these to papers (Xu et al., 2023; LangChain).
- Action: Marker deleted. Added a grounded clause noting that Foundry's fan-out/fan-in patterns reflect the same decoupling principle, anchoring the academic claim to the platform reality.

**Marker 2** — `[MS-Learn: Azure AI Foundry — Plan-and-Execute agent pattern and replanning]`
- Query: (same search as Marker 1, plus "evaluator-optimizer pattern replanning")
- Validated by: https://learn.microsoft.com/azure/logic-apps/single-versus-multiple-agents (explicitly names "evaluator-optimizer pattern" as a high-complexity workflow pattern with iterative refinement loops); the workflow-oriented patterns doc confirms conditional re-orchestration.
- Note: "Plan-and-Execute" is not a named Foundry feature, but the replanning concept (re-invoking an orchestrator when early results redirect the plan) is validated structurally. The lesson's claim is accurate.
- Action: Marker deleted. Added a brief clause noting that the same logic applies in any runtime supporting conditional re-orchestration — keeps it grounded without becoming a vendor pitch.

**Both markers: RESOLVED**

## §8 variety polish

**Ending (was):** "An AI Platform Engineer chooses between ReAct and planning by drawing the dependency graph, not by reaching for the more impressive algorithm."
- This uses the banned "An AI Platform Engineer…" frame. Replaced.

**Ending (now):** "Draw the dependency graph first. The right algorithm follows from the shape of the graph, not from which one sounds more impressive."
- Shape: a directive / reframe. Same content, different construction — the lesson ends with an instruction, not a character portrait.

**Rhythm polish:** Lesson 02 had the most uniform rhythm of the three — mostly short declaratives. The Planner section already has a longer pseudocode block that breaks it. One longer sentence was added in the Plan-and-Execute section ("The same logic applies…") to vary the beat. The HTN and evolutionary search paragraphs are intentionally parallel in structure; that parallelism is earned (two counterexamples to LLM planners), not mechanical.

**Human moment:** None added — the lesson is functional and opinionated already. "LLM planners are not sound-by-construction" is as pointed as it needs to be.

**Acronym audit:** HTN, DAG, MAP-elites, AlphaEvolve — introduced in order with context. No stack. No change needed.

## Source-verify fixes

None required for Lesson 02. No defects in the editor's ledger for this lesson.

## STYLE conformance

- **§1 Unity:** PASS — second person, present tense, practitioner POV, confident voice throughout.
- **§2 Simplicity:** PASS — no qualifiers; active voice; concrete nouns throughout.
- **§3 One idea:** PASS — lesson teaches decoupled planning and when to use it; HTN/evolutionary search subsection is part of the same "where planners stop" idea.
- **§4 Lead + ending:** PASS — lead is tight and grabs; ending replaced with directive shape, no template.
- **§5 Core concepts:** PASS — four propositions, each testable, each one sentence.
- **§8 Variety:** PASS — template ending replaced; one longer sentence added for rhythm; no acronym pileup.

**VERDICT: PASS**
