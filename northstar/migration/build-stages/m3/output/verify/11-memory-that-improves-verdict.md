# Verdict: 11-memory-that-improves

## Markers resolved

| Original marker | Status | Grounding clause | URL |
|---|---|---|---|
| Microsoft Agent Framework memory and ContextProvider — InMemoryHistoryProvider, audit stores, and HistoryProvider chains for durable session state | RESOLVED | "Microsoft Agent Framework formalizes this pattern through ContextProvider and HistoryProvider…" | https://learn.microsoft.com/agent-framework/get-started/memory |
| Azure AI Foundry agent service skills and tool catalog — registering reusable tools and managing tool governance across agent sessions | RESOLVED (reanchored) | "Azure AI Foundry Agent Service's Toolbox is the production version of this pattern…" | https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog |
| Azure Durable Task for AI agents — automatic checkpointing, resume from last checkpoint, and configurable retry policies for long-running agent loops | RESOLVED | "Azure Durable Task handles this in production: the runtime checkpoints every state transition…" | https://learn.microsoft.com/azure/durable-task/sdks/durable-task-for-ai-agents |

**Marker reanchoring note — "skills and tool catalog":** The original marker described "registering reusable tools and managing tool governance across agent sessions." Foundry Agent Service does not have a distinct "skills" surface (that's the gstack concept). The actual MS Learn product is the Foundry tool catalog and Toolbox (a versioned, MCP-compatible bundle of reusable tools). The grounding clause was reanchored to Toolbox, which is the closest real product to what the lesson describes.

## Source verification — Letta block API names

**UNRESOLVED via MS Learn connector** (Letta is not a Microsoft product; connector is MS-only).

<!-- VERIFY-UNRESOLVED: Letta memory blocks API — real names for block_append, block_replace, block_summarize -->

The task states the naming concern as: "the source uses `block_append`/`replace`/`summarize` — make the lesson match the actual Letta naming (don't invent a `block_` prefix if Letta doesn't use it)." The lesson uses `block_append`, `block_replace`, `block_summarize` — all carry the `block_` prefix. Without access to Letta's primary documentation or SDK, I cannot confirm whether these names are accurate or whether the correct names drop the prefix (e.g., `append`, `replace`, `summarize` on a block object). The instruction's own parenthetical ("the source uses `block_append`/`replace`/`summarize`") is itself ambiguous: it lists both `block_append` (with prefix) and `/replace`/`summarize` (without). I have left the lesson as written (`block_append`, `block_replace`, `block_summarize`) since they match the full-prefix form in the instruction's first example. **Opus should verify against the Letta SDK or GitHub docs before shipping.**

## Source verification — CosmosCheckpointStorage

**CORRECTED.** The lesson originally used `CosmosCheckpointStorage` as the class name. MS Learn does not use this name. The verified class names are:
- `CosmosDBWorkflowCheckpointStorage` — Microsoft Agent Framework Python (`azure-cosmos` package)
- `CosmosDBSaver` / `CosmosDBSaverSync` — LangGraph Python

The lesson now reads: "a `CosmosDBWorkflowCheckpointStorage` provider (Microsoft Agent Framework) or via Azure Durable Task directly."

Source: https://learn.microsoft.com/azure/cosmos-db/gen-ai/integrations#langgraph

## Source verification — @skill decorator

**Softened.** The `@skill(name=..., description=...)` decorator is not a real package API. The code block now carries a comment: "# A skill decorator (illustrative — your library wires the registration pattern)". The prose that follows was changed from "The skill decorator registers…" to "A skill decorator such as the one above registers…".

## New ending (seam line)

> "Memory that gets better with use is not a nice-to-have; it is the difference between an agent that costs the same on run 1000 as on run 1, and one that already knows what works."

Replaces: "An AI Platform Engineer who ships this knows how to make memory an asset rather than a liability — one that compounds with use, survives failures, and shrinks the cost of every run that follows." (banned opener, §4)

Shape: a reframe — flips the framing from individual engineer action to systemic cost curve. The contrast (same cost vs. already knows) provides the click.

## Fixes applied

1. Three `[MS-Learn: …]` markers deleted and replaced with light grounding clauses.
2. `CosmosCheckpointStorage` corrected to `CosmosDBWorkflowCheckpointStorage`.
3. `@skill` decorator comment added + prose softened to "a skill decorator such as…".
4. Seam line rewritten — "An AI Platform Engineer who…" opener removed.
5. Foundry "skills" marker reanchored to Toolbox (correct product).

## STYLE conformance (§§1–4, 8)

- Unity: second person, present tense throughout. One brief slip in the sleep-time pseudocode comments ("# Sleep-time agent: runs between sessions") — these are code comments, not prose; no fix required.
- Simplicity: no qualifiers or dead adverbs. Active voice. Pass.
- One idea per lesson: memory that improves (blocks, skills, checkpoints — three patterns all serving the same principle). Held.
- Lead: "The memory system from lesson 10 stores and retrieves — but it doesn't get better." Grabs immediately; establishes the gap. Pass.
- Ending: varied shape (reframe via cost comparison). Not a template. Pass.
- §8 Variety: the Voyager digression ("in Minecraft, an agent builds a library…") is the earned human moment — concrete and unexpected for a platform engineering course. Rhythm mixes code blocks with short declarative runs and one longer-sentence explanation (the sleep-time compute paragraph). Pass.

## VERDICT: PASS (with one open item)

Open item: Letta `block_append`/`block_replace`/`block_summarize` naming must be confirmed against Letta's primary docs (GitHub / letta.com) before shipping. If the real API drops the `block_` prefix, rename accordingly and update the "What you build" section too.
