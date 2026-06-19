# Memory & State

> **Migrated from** `aefs-module3-agent-engineering` (Ph14 07–09) + `asdg-module3-memory-state` (Ch08).

Memory is what lets an agent run longer than one context window. The progression:

- **Virtual context (MemGPT)** — map context management to OS virtual memory: main context = RAM, external
  store = disk, memory tools page in/out. A 4k-window agent with external memory catches long-horizon facts a
  128k baseline misses. The `core_memory_*` / `archival_memory_*` tool surface.
- **Memory blocks & sleep-time compute (Letta)** — typed, editable blocks (Human/Persona/custom) across three
  tiers (core/recall/archival); a background sleep-time agent consolidates memory off the critical path.
- **Hybrid memory (Mem0)** — three parallel stores behind one `add`/`search` surface: vector (semantic), KV
  (O(1) facts), graph (relationships), fused by relevance + importance + recency. A single store is always
  wrong for two of the three query classes a production agent issues.
- **Skill libraries (Voyager)** — executable code as a named, retrievable, composable skill refined by
  execution feedback — the reference for the Claude Agent SDK skills pattern.

**Memory tiers (asdg Ch08):** L1 working / L2 episodic / L3 semantic; short-term context (KV / paged
attention), long-term (vector + graph), semantic caching, state management / checkpointing.

**Layering note:** KV-cache / paged-attention is introduced here at the agent level; it's deepened in Module
5 at the serving level. Same concept, two altitudes — not a duplication.
