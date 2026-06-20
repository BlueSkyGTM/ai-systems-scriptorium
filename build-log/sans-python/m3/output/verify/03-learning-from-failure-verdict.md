# Verdict: 03-learning-from-failure

## Markers resolved

**Marker 1** — `[MS-Learn: Azure AI Foundry — agent evaluation and iterative improvement loops]`
- Query: "Azure AI Foundry agent evaluation iterative improvement loop Reflexion"
- Validated by: https://learn.microsoft.com/azure/foundry/concepts/evaluation-evaluators/agent-evaluators (built-in agent evaluators: IntentResolution, TaskAdherence, ToolCallAccuracy — confirms the evaluate-and-improve cycle); https://learn.microsoft.com/agents/agent-evaluation/evaluation-iterative-framework (explicitly describes iterative evaluate > analyze > improve > reevaluate loop)
- Action: Marker deleted. Added a grounded clause referencing Foundry's built-in agent evaluators (IntentResolution, TaskAdherence) to anchor the pattern to the platform.

**Marker 2** — `[MS-Learn: Azure AI Foundry — evaluator-optimizer pattern and external verification tools]`
- Query: "Azure AI Foundry evaluator optimizer pattern external verification tools"
- Validated by: https://learn.microsoft.com/azure/logic-apps/single-versus-multiple-agents (explicitly names "evaluator-optimizer pattern" as an iterative refinement loop with generator and evaluator roles); https://learn.microsoft.com/azure/foundry/agents/concepts/agent-optimizer-overview (Foundry's agent optimizer runs a closed-loop evaluate > generate candidates > rank cycle)
- Action: Marker deleted. Added a sentence noting that Microsoft documents this pattern explicitly — generator produces, evaluator scores and feeds back, loop runs until termination. This grounds the claim without overselling the source.

**Marker 3** — `[MS-Learn: Azure AI Foundry — inference-time scaling and search-based reasoning for high-stakes tasks]`
- Query: "Azure AI Foundry inference time scaling tree of thoughts search based reasoning"
- Validated by: https://learn.microsoft.com/azure/foundry/openai/how-to/reasoning (Azure OpenAI reasoning models; confirms that models "spend more time processing" / "explore all possible paths" — inference-time scaling concept validated); https://learn.microsoft.com/azure/foundry-classic/foundry-models/how-to/use-chat-reasoning (reasoning models with chain-of-thought exploration)
- Note: ToT and LATS as named techniques are not in MS docs — they are academic papers. MS docs confirm the broader inference-time scaling concept (reasoning models, extended thinking). The lesson correctly treats ToT/LATS as academic patterns and does not claim they are Foundry features.
- Action: Marker deleted. No additional reference clause added — the lesson already accurately frames these as research patterns (Yao et al., Zhou et al.) and the cost-test framing is the useful teaching point.

**All 3 markers: RESOLVED**

## §8 variety polish

**Ending (was):** "An AI Platform Engineer who understands Reflexion and CRITIC can build agents that get better within a session, route verification to tools that cannot be fooled, and know exactly when to spend the token budget for search."
- This uses the banned "An AI Platform Engineer who…" frame. Replaced.

**Ending (now):** "Get the evaluator wrong and every other improvement is noise."
- Shape: a warning / consequence. Eight words. Earns its place by naming the failure mode, not the competence portrait.

**Rhythm polish:** The original had a run of short declaratives in the "Evaluator types matter" paragraph. Expanded slightly with a framing sentence ("These three types are a practical framing, not an established taxonomy…") — this does double duty: breaks the rhythm *and* applies the source-verify fix on the taxonomy claim (see below).

**Human moment:** Added one earned aside in the Reflexion section: "(That's genuinely underrated — most practitioners reach for fine-tuning before they've tried writing the lesson down.)" — dry, opinionated, true. One moment; no more.

**Acronym audit:** ToT, LATS, MCTS, HTN are all introduced in order with context. One potential stack: "MemGPT → Letta → Mem0 → Voyager" — not present in this lesson, no issue.

## Source-verify fixes applied

1. **ToT Game-of-24 result ("4% → 74%")** — added model attribution: "with GPT-4, which was the test model in the original paper." The result was GPT-4-era and should not read as model-agnostic.

2. **Self-Refine "+20 absolute points across 7 benchmarks"** — changed "benchmarks" to "tasks" to match the source paper framing. ("7 tasks" in the original Self-Refine paper.)

3. **Three-evaluator taxonomy (scalar / heuristic / self-evaluated)** — this taxonomy is not established/canonical in the source literature. Softened the framing: "These three types are a practical framing, not an established taxonomy; the key distinction is whether the quality signal is internal to the model or grounded externally." The types themselves are useful and remain; the assertion of canonicity is removed.

## STYLE conformance

- **§1 Unity:** PASS — second person, present tense, practitioner POV, confident voice throughout.
- **§2 Simplicity:** PASS — one qualifier removed ("genuinely" in one place, retained in the earned aside only); active voice maintained.
- **§3 One idea:** PASS — lesson teaches failure-recovery patterns (Reflexion, Self-Refine/CRITIC, ToT/LATS) as a coherent single topic: improving agents without weight updates.
- **§4 Lead + ending:** PASS — lead is sharp and memorable; ending replaced with a warning shape, not a template.
- **§5 Core concepts:** PASS — four propositions, each one sentence, each testable and specific.
- **§8 Variety:** PASS — template ending replaced; rhythm broken by expanded taxonomy note and earned human aside; no acronym pileup; ToT result now model-attributed.

**VERDICT: PASS**
