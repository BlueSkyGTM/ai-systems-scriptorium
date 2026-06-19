# Memory Tiers and Stores

Your agent's context window is not unlimited memory — it's a working surface that overflows. When it overflows, you need somewhere else to put things, and the architecture of that "somewhere else" determines whether your agent can run for minutes or months.

## Don't add memory until the window breaks

The complexity ladder governs here. A 128k-token window handles most tasks without any external memory. Add a memory layer only when you've hit a real overflow: a task that spans more turns than a single window can hold, a fact that must survive session boundaries, or a query pattern that a flat buffer can't answer. The right time to reach for the architecture below is when you have the problem, not when you anticipate it.

## The three tiers

Every durable agent memory architecture has three layers. They differ in speed, capacity, and what kind of recall they serve.

**L1 — working memory** is the active context window. It is the fastest tier — retrieval is immediate because the data is already in the prompt. The practical limit is your model's context length: claude-opus-4-8 supports 200k tokens, but you pay for every token on every call. The KV cache cuts that cost: when the static portions of your prompt (system prompt, tool schemas) stay unchanged across turns, the inference engine reuses the computed key-value pairs instead of reprocessing them. At the agent level that means "static content first, dynamic content last" — a design choice, not an implementation detail. This is where KV-cache optimization lives for you as the platform engineer; Module 5 deepens how the serving layer implements it below the API.

**L2 — episodic memory** holds interaction trajectories: summaries of what happened in past sessions, tool call sequences that worked, failures and their diagnoses. You store these in a vector database (Azure AI Search, Cosmos DB for NoSQL with DiskANN indexing) and retrieve them by semantic similarity. Latency is 100–300ms — fast enough to inject into a prompt before a turn, slow enough that you don't fetch it for every token. L2 is where Reflexion's post-failure reflections land: writing a reflection *is* a memory write, and the next session reads it back.

**L3 — semantic memory** holds facts and rules that don't change: entity relationships, user preferences, organizational knowledge. A knowledge graph (Neo4j, AWS Neptune) or a managed service like Mem0 handles this. Queries are relationship traversals, not vector similarity — "what does this user prefer?" not "what is similar to this embedding?" Latency is higher; call this tier when you need a structured fact, not a fuzzy match.

[MS-Learn: Azure Cosmos DB agent memory toolkit — storing turns, summaries, and facts with vector search, full-text search, and hybrid search across all three tiers]

## Virtual context: the MemGPT pattern

A bigger context window does not solve the problem. MemGPT (Packer et al., 2023) proved this: a 4k-window agent with external memory outperforms a 128k baseline on long-horizon tasks, because the external memory is *searchable* while the raw window is not.

The OS analogy maps the problem cleanly. Main context = RAM: fast, limited, everything in it is immediately addressable. External store = disk: slow, large, you page things in and out as needed. Memory tools = the page-in/page-out interrupt: the agent calls them explicitly, the result lands in context.

The tool surface looks like this:

```python
# Core memory: always in context, bounded
core_memory_append(section="human", content="User prefers TypeScript examples")
core_memory_replace(section="persona", old_content="...", new_content="...")

# Archival memory: external store, paged in on demand
archival_memory_insert(content="Meeting notes 2026-06-19: agreed on hybrid store pattern")
archival_memory_search(query="hybrid store architecture decision")
```

`core_memory_*` tools mutate the always-in-context block — a bounded region the agent can inspect and update directly. `archival_memory_*` tools write to and search the external store. The agent decides when to page in; the framework handles serialization. Letta (the 2026 successor to MemGPT) inherits this surface and adds typed memory blocks — more on that in lesson 11.

[MS-Learn: Microsoft Foundry Agent Service memory — long-term memory extraction, consolidation, and cross-session recall using the Memory Store API]

## Hybrid stores: why one store is always wrong

A production agent issues at least three distinct query classes in a single session: a semantic query ("what did we discuss about the deployment architecture?"), a point lookup ("what is this user's billing tier?"), and a relationship query ("which services depend on this component?"). A vector database answers the first well. It answers the second with unnecessary latency and the third not at all.

Mem0 (Chhikara et al., 2025) makes the argument concrete. It wires three parallel stores behind one `add`/`search` surface:

- **Vector store** — semantic similarity. You query by meaning. HNSW or DiskANN indexing. Answers the "what's relevant to this topic?" class.
- **KV store** — O(1) fact lookup. You query by key. Answers the "what is the value of X?" class. No embedding required.
- **Graph store (Mem0g)** — relationship traversal. You query by entity linkage. Answers the "who/what connects to Y?" class.

On `search`, the system runs all three in parallel and fuses the results by a weighted score: relevance (vector similarity), importance (a learned signal), and recency (timestamp decay). The agent sees a ranked list; it does not manage three separate calls.

```python
from mem0 import MemoryClient

client = MemoryClient()

# One surface — three stores write in parallel
client.add(
    messages=[{"role": "user", "content": "Prefers Python over TypeScript for scripting"}],
    user_id="user_42",
    metadata={"importance": "high"}
)

# One search — three stores queried, results fused
results = client.search(
    query="language preference",
    user_id="user_42"
)
```

Azure Cosmos DB for NoSQL is the production substrate for this pattern: it supports vector search (DiskANN, IVF, HNSW), full-text search, and point lookups in a single service with 99.999% availability. You do not need three separate managed services.

[MS-Learn: Azure Cosmos DB integrations for AI — LangGraph checkpointer, long-term memory, vector store, KV store, and semantic cache in one service]

## Safety: memory is attackable

Memory persists across sessions, which means a poisoned memory persists too. An attacker who plants a malicious instruction in your archival store via indirect prompt injection has a persistent foothold — unlike a compromised prompt, a compromised memory survives the session reset. Namespace your memory by `user_id` and enforce it at query time so retrieval cannot cross tenants. Apply Azure AI Content Safety Prompt Shields at write time, not just at inference time, to catch injection attempts before they enter your store. Log every memory write with full provenance so you can audit and roll back.

[MS-Learn: Azure Foundry Agent Service memory security — prompt injection detection, retrieval-time Prompt Shields, and memory audit with Microsoft Sentinel]

## What you build

You add a Python memory layer to `module3-agent/`. The harness gains three files: `memory/working.py` (the L1 context manager with KV-cache-aware static-first ordering), `memory/episodic.py` (an L2 stub — `insert` writes to a dict, `search` does keyword match, the interface is API-stable for a real vector store), and `memory/hybrid_store.py` (a Mem0-pattern stub that routes queries to the right tier and returns a fused ranked list). The existing ReAct loop wires episodic memory to the observation formatter: post-turn observations append to L2, and session start fetches the top-3 relevant memories into L1.

An AI Platform Engineer who knows when to add a memory tier and which store answers which query class ships agents that hold state under production load — not agents that lose context when the window fills.

## Core concepts

- Add a memory tier only when the context window actually overflows; the wrong time is before you have the problem.
- The three tiers — L1 working (context window + KV cache), L2 episodic (vector store, semantic retrieval), L3 semantic (graph/KV, fact lookup) — differ in speed, capacity, and query class, not just size.
- A single store is always wrong for two of the three query classes a production agent issues; a hybrid store (vector + KV + graph behind one surface) is the 2026 production standard.
- Memory is attackable — a poisoned write persists across sessions; apply content safety at write time, namespace by user, and log all writes with provenance.

<div class="claude-handoff" data-exercise="exercises/module3/10-memory-tiers-and-stores/">

**Build it in Claude Code** — add a Python memory layer to `module3-agent/`: an L1 context manager with static-first KV-cache ordering, an L2 episodic stub with insert/search, and a hybrid-store stub that fuses results from all three tiers. Wire episodic memory into the ReAct loop so session start injects the top-3 relevant memories into L1. Open the repo and run the exercise for this lesson.

</div>
