# Verdict: 06-tool-use

## Markers resolved

3 MS-Learn markers → all RESOLVED.

1. `[MS-Learn: Azure AI Agents — FunctionToolDefinition and JSON Schema parameter contracts for function calling]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling
   - **Grounded fact woven in:** `FunctionTool` interface requires `name`, `description`, and a JSON Schema `parameters` object; the description drives model selection correctness, not just documentation.

2. `[MS-Learn: Azure AI Foundry — validating tool call arguments and handling function calling errors]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling
   - **Grounded fact woven in:** Foundry guidance explicitly recommends returning a descriptive error as a tool output (not throwing an exception) so the model can respond rather than see a crash.

3. `[MS-Learn: Azure AI Foundry — configuring least-privilege tool permissions and human-in-the-loop approval gates]`
   - **URL:** https://learn.microsoft.com/azure/foundry/agents/how-to/tools/function-calling
   - **Grounded fact woven in:** Foundry names least-privilege as a security principle and recommends explicit user confirmation before data-changing tool execution.

## Ending rewrite

**Old (banned template):**
> An AI Platform Engineer who owns the execute step owns the only place in the system where the model's intentions become real-world actions — which means this is also the only place the harm can actually happen.

**New:**
> The execute step is the only place in the system where the model's intentions become real-world actions. It is also, therefore, the only place the harm can actually happen — so treat it accordingly.

Shape: consequence + imperative. Not the "An AI Platform Engineer who…" opener. Click lands on the word "accordingly" — earned, not explained.

## STYLE conformance

- §4 ending: banned template removed, seam rewritten as consequence+imperative. PASS.
- §8 variety: rhythm is varied throughout the lesson (short declaratives broken by longer clause-chains). One implied human moment ("something is wrong with the tool's scope"). PASS.
- §1 unity: second person, present tense, practitioner POV throughout. PASS.
- §2 simplicity: no qualifiers added; original was already clean. PASS.
- Code blocks: all preserved intact. PASS.

## Other fixes

None required. No broken SDK names, no Python imports in this lesson.

## VERDICT: PASS
