# Verdict: 10-memory-tiers-and-stores

## Markers resolved

| Original marker | Status | Grounding clause | URL |
|---|---|---|---|
| Azure Cosmos DB agent memory toolkit — storing turns, summaries, and facts … | RESOLVED | "The Agent Memory Toolkit for Azure Cosmos DB (preview) handles exactly this pattern…" | https://learn.microsoft.com/azure/cosmos-db/gen-ai/agent-memory-toolkit |
| Microsoft Foundry Agent Service memory — long-term memory extraction, consolidation, and cross-session recall using the Memory Store API | RESOLVED | "Azure AI Foundry Agent Service provides a managed long-term memory solution (preview)…" | https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory |
| Azure Cosmos DB integrations for AI — LangGraph checkpointer, long-term memory, vector store, KV store, and semantic cache in one service | RESOLVED | "The Azure Cosmos DB integrations page covers exactly this pattern: LangGraph checkpointer (CosmosDBSaver)…" | https://learn.microsoft.com/azure/cosmos-db/gen-ai/integrations |
| Azure Foundry Agent Service memory security — prompt injection detection, retrieval-time Prompt Shields, and memory audit with Microsoft Sentinel | RESOLVED (partial) | "Azure AI Foundry Agent Service's memory security guidance recommends Azure AI Content Safety prompt injection detection…" | https://learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory#security-risks |

**Marker resolution note — "Microsoft Sentinel" claim:** The original marker included "memory audit with Microsoft Sentinel." MS Learn docs for Foundry Agent Service memory security do NOT mention Sentinel in the memory context; the guidance covers Azure AI Content Safety and adversarial testing only. Microsoft Defender for Cloud has Sentinel-adjacent AI agent alerts (jailbreak detection), but the memory audit path is not Sentinel-specific. The resolved grounding clause omits Sentinel and stays accurate to what MS Learn actually documents.

## Source verification — Cosmos DB 99.999% SLA

**CONFIRMED.** MS Learn states "99.999% availability guarantee" for Azure Cosmos DB for NoSQL (multi-region accounts or using Per Partition Automatic Failover). The ai-agents page states explicitly: "Use Azure Cosmos DB for NoSQL to build your AI agent memory system … offers 99.999% availability guarantee." The lesson's figure is correct; no change needed.

Source: https://learn.microsoft.com/azure/cosmos-db/ai-agents#building-a-robust-ai-agent-memory-system

## New ending (seam line)

> "Get the tier wrong and the agent either pays for every token twice or loses context when it matters most; get it right and state becomes a competitive advantage rather than a liability."

Replaces: "An AI Platform Engineer who knows when to add a memory tier and which store answers which query class ships agents that hold state under production load — not agents that lose context when the window fills." (banned opener, §4)

Shape: a consequence (cost of the wrong call vs. the upside of the right one). Earns the click by making the failure mode concrete.

## Fixes applied

1. Four `[MS-Learn: …]` markers deleted and replaced with light grounding clauses (one sentence + URL each).
2. Seam line rewritten — "An AI Platform Engineer who…" opener removed.
3. "Microsoft Sentinel" not carried into the grounding clause (claim unconfirmed by MS Learn memory-security docs; Prompt Shields + adversarial testing confirmed).

## STYLE conformance (§§1–4, 8)

- Unity: second person, present tense, practitioner POV throughout. No breaks.
- Simplicity: no qualifiers or dead adverbs found. Active voice throughout.
- One idea per lesson: memory tiers and stores. Held cleanly.
- Lead: "Your agent's context window is not unlimited memory — it's a working surface that overflows." Grabs; second sentence delivers the stakes. Pass.
- Ending: varied shape (consequence/cost). Not a template. Pass.
- §8 Variety: sentence lengths mix well; the OS analogy section provides the earned human moment ("the OS analogy maps the problem cleanly"). Code blocks break the rhythm appropriately.

## VERDICT: PASS (conditional)

Conditional on: Opus review of the Sentinel omission (was the original author referencing a real integration path? The MS Learn memory-security docs don't surface it, so it was dropped). All other claims are source-verified.
