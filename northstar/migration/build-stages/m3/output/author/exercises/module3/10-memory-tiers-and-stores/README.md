# Exercise 10 — Memory Tiers and Stores

## Goal

Add a Python memory layer to `module3-agent/` that implements all three memory tiers (L1 working, L2 episodic, L3 semantic) and a hybrid-store stub that routes queries to the right tier and fuses results.

## Why

A production agent that overflows its context window without external memory is a single-session tool. This exercise wires the memory architecture that makes an agent run longer than one window.

## Steps

1. **Create `module3-agent/memory/working.py`.**
   - Implement a `WorkingMemory` class that wraps the message buffer.
   - Enforce static-first ordering: system prompt and tool schemas are prepended, dynamic content (observations, user turns) is appended.
   - Add a `token_count()` method that returns the estimated token count of current context.
   - Add an `evict_oldest(n)` method that drops the `n` oldest dynamic turns when the count exceeds a configurable threshold.

2. **Create `module3-agent/memory/episodic.py`.**
   - Implement an `EpisodicMemory` class with `insert(content: str, metadata: dict)` and `search(query: str, top_k: int) -> list[dict]`.
   - Back the store with an in-memory dict keyed by UUID (the interface must be API-stable for a real vector store drop-in).
   - `search` does keyword overlap scoring for now — no embedding required.
   - Add a `recent(limit: int)` method that returns the most recent `n` entries by insertion time.

3. **Create `module3-agent/memory/hybrid_store.py`.**
   - Implement a `HybridStore` class with `add(content, user_id, metadata)` and `search(query, user_id, top_k) -> list[dict]`.
   - Route internally to three sub-stores: `EpisodicMemory` (vector tier stub), a dict-backed KV store (point lookup by key), and a dict-backed graph stub (adjacency list, query by entity name).
   - Fuse results by a weighted score: `0.5 * relevance + 0.3 * importance + 0.2 * recency`. Return the top-k unified results.

4. **Wire episodic memory into the agent loop.**
   - At session start, call `episodic.search(goal, top_k=3)` and inject the results as a system message block labeled `[Memory from prior sessions]`.
   - After each turn, call `episodic.insert(observation, metadata={"turn": turn, "tool": tool_name})`.

5. **Write a smoke test.**
   - Insert three episodic memories with different content. Search for a query that matches one. Assert the match appears in the top result.
   - Run the agent loop for three turns with a toy tool. Assert the episodic store has three entries at the end.

## Done when

- `python -m pytest module3-agent/tests/test_memory.py` passes with no errors.
- Running the agent loop prints `[Memory from prior sessions]` on the second session startup (after at least one prior turn has been stored).
- `hybrid_store.search(query, user_id)` returns a list of dicts with `content`, `score`, and `source_tier` fields.

## Stretch

Replace the keyword-overlap `search` in `EpisodicMemory` with a real embedding call using `claude-haiku-4-5` as the embedding model (via the Anthropic API `embed` endpoint). Confirm the smoke test still passes and that semantic matches now score higher than keyword matches.
