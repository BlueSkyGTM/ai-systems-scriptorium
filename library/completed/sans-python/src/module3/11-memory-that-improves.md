# Memory That Improves

The memory system from lesson 10 stores and retrieves — but it doesn't get better. This lesson covers three patterns that make memory smarter over time without touching a model weight: typed blocks that consolidate off the critical path, skill libraries that turn execution history into reusable code, and checkpoints that let a failed run resume instead of restart.

## From Reflexion to General Memory Writes

In lesson 03, Reflexion wrote a verbal lesson after each failure and stored it in an episodic buffer. That was a specific instance of a general pattern: *any* meaningful event can become a memory write. This lesson generalizes it. The post-failure reflection is a write to episodic memory (L2). A discovered user preference is a write to the core block. A verified, reusable tool sequence is a write to the skill library. The shapes are different; the principle is the same: turn experience into structure the agent can retrieve later.

## Memory Blocks and Sleep-Time Compute (Letta)

Letta's 2026 architecture adds typed, editable memory blocks to the MemGPT pattern. A block is a named, bounded region with a schema — not a free-form string. The three built-in types are `Human` (facts about the user), `Persona` (the agent's own character and role), and `Custom` (domain-specific slots you define). Blocks live in core memory (always in context), recall memory (recent session history), and archival memory (long-term store) — the same three tiers from lesson 10, with blocks as the data model.

The block operations are:

```python
# Append new content to a block (bounded — triggers eviction if full)
block_append(block_label="human", content="Prefers concise answers, no preamble")

# Replace a field within a block
block_replace(block_label="persona", field="tone", value="direct, technical")

# Summarize a block when it hits capacity
block_summarize(block_label="human")
```

The problem these blocks solve is *memory rot*: a flat episodic buffer accumulates contradictions and stale facts across sessions. A typed block enforces schema on write, evicts on overflow (triggering a summarize), and makes the structure inspectable.

The bigger innovation is **sleep-time compute**: a background agent that consolidates memory asynchronously, off the critical path. While the primary agent is idle between sessions, a lighter model reviews recent episodic memories, merges duplicates, resolves contradictions, and writes cleaned facts back into the blocks. The user's next session starts with a consolidated, current memory state — not the raw accumulation of every prior turn.

The two-agent loop in pseudocode:

```python
# Primary agent: serves responses, writes raw observations to recall
async def primary_turn(user_message):
    response = await agent.run(user_message)
    recall_memory.append(user_message, response)
    return response

# Sleep-time agent: runs between sessions, never on the critical path
async def sleep_time_consolidate():
    raw = recall_memory.recent(limit=50)
    summary = await cheap_model.summarize(raw)
    block_replace(block_label="human", field="summary", value=summary)
    recall_memory.prune(older_than="24h")
```

The claude-haiku-4-5 model is the right choice for the sleep-time agent: cheap, fast, and capable enough for summarization work that the claude-opus-4-8 primary does not need to do.

This is the pattern behind Claude Code's `CLAUDE.md` learnings and the `/learn` command: when a session ends, the rule you write is a sleep-time consolidation into a persistent block the next session reads on startup.

Microsoft Agent Framework formalizes this pattern through `ContextProvider` and `HistoryProvider`: `InMemoryHistoryProvider` keeps history in session state, and a second provider with `store_context_messages=True` acts as an audit store — both chained via `context_providers=[...]`. ([Microsoft Agent Framework memory and persistence](https://learn.microsoft.com/agent-framework/get-started/memory))

## Skill Libraries (Voyager)

A skill library treats executable code as a retrievable asset. Voyager (Wang et al., 2024) is the reference: in Minecraft, an agent builds a library of named Python functions (skills), each tagged with a natural-language description. When a new task arrives, the agent searches the library by description similarity and retrieves relevant skills to compose, rather than re-deriving behavior from scratch. The loop runs three ways:

1. **Attempt** — the agent tries a task using available skills.
2. **Verify** — an external check (a test, an assertion, an execution result) confirms success or failure.
3. **Refine** — on failure, the agent revises the skill code and overwrites the library entry.

The result is a library that gets sharper with use. A skill that fails twice gets rewritten. A skill that succeeds consistently gets promoted (tagged as high-confidence and preferred in future retrieval).

This is the reference architecture for the Claude Agent SDK skills pattern: capabilities are programs stored in a library and loaded on demand, not re-derived from a prompt each session. A skill is named, has a description the retrieval system queries against, and is callable by the agent loop.

```python
# A skill decorator (illustrative — your library wires the registration pattern)
@skill(name="parse_json_schema", description="Parse and validate a JSON Schema, return typed fields")
def parse_json_schema(schema: str) -> list[dict]:
    import json
    import jsonschema
    data = json.loads(schema)
    # validate and extract fields ...
    return fields
```

A skill decorator such as the one above registers the function in the library with a name and a description the retrieval system queries against. The agent searches by description at task time, retrieves the matching skill, and calls it — the same composition pattern the agent loop uses for tool calls, but with code that survives sessions.

Azure AI Foundry Agent Service's Toolbox is the production version of this pattern: a curated bundle of versioned tools, configured once and exposed as a single MCP-compatible endpoint that any agent can consume. ([Agent tools overview for Foundry Agent Service](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog))

## Checkpointing and Resume

A 40-step agent run that fails at step 37 costs everything: tokens spent, time elapsed, intermediate results computed. Checkpointing fixes this. After each successful step, the agent writes its full state — message buffer, tool call history, intermediate results, turn number — to a durable store. When the run fails, the harness rehydrates from the last checkpoint and continues from step 37, not from zero.

The checkpoint state shape for `module3-agent/`:

```python
@dataclass
class AgentCheckpoint:
    run_id: str
    turn: int
    messages: list[dict]      # full message buffer
    tool_results: list[dict]  # results already computed
    memory_snapshot: dict     # current L1/L2 state
    timestamp: str

def save_checkpoint(cp: AgentCheckpoint, path: str):
    with open(path, "w") as f:
        json.dump(asdict(cp), f)

def load_checkpoint(path: str) -> AgentCheckpoint:
    with open(path) as f:
        return AgentCheckpoint(**json.load(f))
```

In production, the store is Cosmos DB with a `CosmosDBWorkflowCheckpointStorage` provider (Microsoft Agent Framework) or via Azure Durable Task directly. The Durable Task runtime checkpoints every state transition automatically and resumes from the last checkpoint on any infrastructure failure — process crash, deployment, scale-in event. You get this without adding retry logic to your agent code.

Azure Durable Task handles this in production: the runtime checkpoints every state transition — LLM responses, tool results, control flow — and resumes automatically from the last checkpoint on any infrastructure failure, without adding retry logic to your agent code. ([Durable Task for AI agents](https://learn.microsoft.com/azure/durable-task/sdks/durable-task-for-ai-agents))

## Safety: the Memory Attack Surface Expands

Skill libraries and memory blocks extend the attack surface from lesson 10. A poisoned skill — malicious code injected into a library entry via an adversarial tool result — executes the next time the agent retrieves and calls it. Sleep-time consolidation running a cheaper model is a lower-scrutiny path: an attacker who can influence the recall buffer may be able to plant content that the sleep-time agent summarizes into a core block without the primary agent's guardrails in place. Run Prompt Shields on inputs to the sleep-time agent as well, not just the primary. Version your skill library so a malicious write can be rolled back.

## What You Build

You extend `module3-agent/` with three additions. First, `memory/blocks.py`: a typed block manager with `block_append`, `block_replace`, and `block_summarize`. Second, `memory/skills.py`: a skill library with `register`, `search` (keyword similarity over descriptions), and `call`. Third, `memory/sleep_agent.py`: a stub sleep-time consolidation loop that reads from recall memory, summarizes with claude-haiku-4-5, and writes back to the human block. The existing checkpoint hook from the agent loop writes a full `AgentCheckpoint` after each turn; a `--resume` flag on the loop entry point reloads from the last checkpoint.

Memory that gets better with use is not a nice-to-have; it is the difference between an agent that costs the same on run 1000 as on run 1, and one that already knows what works.

## Core Concepts

- Any meaningful event — a failure, a discovered preference, a verified tool sequence — is a candidate memory write; Reflexion's post-failure reflection is one instance of this general pattern.
- Typed memory blocks (Human/Persona/Custom) prevent memory rot by enforcing schema on write and summarizing on overflow; sleep-time compute consolidates off the critical path so latency stays low.
- A skill library stores executable code as named, retrievable, refinable assets — the pattern behind the Claude Agent SDK skills system, where capabilities load from a library rather than re-derive from a prompt.
- Checkpointing every turn means a failed long run resumes from the last checkpoint; without it, every failure discards all tokens spent.

<div class="claude-handoff" data-exercise="exercises/module3/11-memory-that-improves/">

**Build It in Claude Code** — extend `module3-agent/` with typed memory blocks (block_append/replace/summarize), a skill library with register/search/call, and a sleep-time consolidation stub using claude-haiku-4-5. Wire a checkpoint/resume hook into the agent loop: save state after each turn, add a --resume flag that reloads from the last checkpoint.

</div>
