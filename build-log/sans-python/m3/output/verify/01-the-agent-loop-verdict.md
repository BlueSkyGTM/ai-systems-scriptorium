# Verdict: 01-the-agent-loop

## Markers resolved

**Marker 1** — `[MS-Learn: Azure AI Agent Service — agent loop architecture and tool execution lifecycle]`
- Query: "Azure AI Foundry Agent Service agent loop architecture tool execution lifecycle"
- Validated by: https://learn.microsoft.com/azure/foundry/agents/overview (Run/Run Steps/Thread model confirms tool execution lifecycle within a loop); https://learn.microsoft.com/azure/durable-task/sdks/durable-agents-patterns (confirms agent loop with tool calls as activities)
- Naming fix: "Azure AI Agent Service" is now "Microsoft Foundry Agent Service" (confirmed by MS Learn)
- Action: Marker deleted. Added a brief grounded clause naming the Run/Run Steps model to anchor the claim structurally.

**Marker 2** — `[MS-Learn: Azure AI Foundry — configuring agent turn limits and cost controls]`
- Query: "Azure AI Foundry agent turn limits cost controls budget"
- Validated by: https://learn.microsoft.com/azure/foundry/concepts/manage-costs (cost controls via budgets, `max_output_tokens`, quotas); https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat (confirms `max_output_tokens` and `truncation` settings per turn)
- Note: MS docs do not use the term "turn limits" as a named feature; they use token caps, round budgets, and run-level controls. The lesson's concept is valid; the marker's framing slightly overstates the named feature.
- Action: Marker deleted. The surrounding text is accurate at the concept level and no fix to the claim was needed.

**Marker 3** — `[MS-Learn: Azure AI Foundry — implementing safety controls and agent kill switches]`
- Query: "Azure AI Foundry agent safety controls kill switch terminate"
- Validated by: https://learn.microsoft.com/azure/foundry/responsible-use-of-ai-overview (Discover/Protect/Govern framework; content filters and guardrails); https://learn.microsoft.com/azure/foundry/control-plane/govern-agent-infrastructure-entra-admin (stop/start/block controls for agent deployments)
- Note: MS Learn confirms platform-level stop/block controls. The "kill switch as a boolean the agent reads but cannot write" is a self-hosted pattern; in managed runtimes, the platform provides this at the deployment layer. The lesson now distinguishes both cases.
- Action: Marker deleted. Added a sentence noting that in managed runtimes (Foundry Agent Service) the platform provides stop/block controls; in self-hosted loops you wire this yourself.

**All 3 markers: RESOLVED**

## §8 variety polish

**Ending (was):** "An AI Platform Engineer who understands the five ingredients can reason about any agent harness — and knows exactly which surface to reach for when the loop breaks."
- This uses the banned "An AI Platform Engineer who…" frame. Replaced.

**Ending (now):** "Miss the turn budget and the kill switch, and you don't have a production agent — you have an expensive infinite loop waiting for the right prompt."
- Shape: a cost/consequence. Blunt, specific, earns its place.

**Rhythm polish:** The lesson had a solid rhythm already. One longer breathing sentence was added in the ReAct section (the Run/Run Steps clause) to vary the beat without disrupting flow.

**Human moment:** None added — the lesson's voice is already confident and concrete. The kill switch paragraph is pointed enough to read as a person with an opinion, not a robot.

**Acronym audit:** No stacks. ReAct, DAG, SDK — all single introductions with context. No change needed.

## Source-verify fixes

None required for Lesson 01. No defects in the editor's ledger for this lesson.

## STYLE conformance

- **§1 Unity:** PASS — second person, present tense, practitioner POV, confident voice throughout.
- **§2 Simplicity:** PASS — no qualifiers added; existing clutter already minimal; active voice maintained.
- **§3 One idea:** PASS — lesson teaches the agent loop and its five ingredients as one coherent concept.
- **§4 Lead + ending:** PASS — lead unchanged (strong, no throat-clearing); ending replaced with consequence shape, not template.
- **§5 Core concepts:** PASS — four propositions, each one sentence, testable and specific.
- **§8 Variety:** PASS — template ending replaced; rhythm intact with one longer clause added; no acronym pileup.

**VERDICT: PASS**
