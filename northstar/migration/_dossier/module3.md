# Module 3 — Migration Dossier (Agent Foundations)

Source: `../sub-repos/synthesis/source/module3/` (Tracks A–D) + `module1/ts-*` (threaded in). This is the
**single-agent** half of the old Module 3 split. The multi-agent half (Tracks E–H) → Module 4.

## Source files in

| Source file | Verdict | Destination / note |
|-------------|---------|--------------------|
| `aefs-module3-agent-engineering.md` (Ph14 42 lessons) | **KEEP — single-agent** | Phase 14 → M3. The reasoning loop, planning, memory, frameworks, and the **agent-workbench** thread (31–42). Phases 15–16 in this same file → **M4**. |
| `aefs-module3-tools-protocols.md` (Ph13, 23 lessons) | **KEEP — canonical MCP spine** | → `src/module3/02`. The deep MCP treatment (server→client→transports→sampling→security→OAuth→gateways). |
| `asdg-module3-agentic-systems.md` (Ch07) | **KEEP** | Agent fundamentals, ReAct, tool use, HITL, agent eval → merged into 01/02. |
| `asdg-module3-memory-state.md` (Ch08) | **KEEP** | L1–L3 memory tiers, Mem0, caching → `src/module3/03`. |
| `asdg-module3-frameworks-tools.md` (Ch09) | **KEEP** | LangGraph/DSPy/LlamaIndex landscape → `src/module3/04`. |
| `asdg-module3-design-patterns.md` (Ch15) | **KEEP** | Pattern catalog + anti-patterns → `src/module3/04`. |
| `module1/ts-module1-typescript-topics.md` | **THREAD IN (from M1)** | TS break-in set + generics/interfaces → `src/module3/06`. Point-of-use: typed tools / MCP contracts. |

## Merges

- **MCP (covered 4×) → one spine.** `aefs` Ph13 (23 lessons) is canonical; `asdg` Ch17 + Ch07.03 + the `aefs`
  Ph14 tool lessons fold in as lighter references. One MCP spine here.
- **Agent fundamentals** — `aefs` Ph14 (01–11) + `asdg` Ch07 → one progression (loop → planning → memory).
- **Frameworks** — `aefs` Ph14 (13–18: LangGraph/AutoGen/CrewAI/OpenAI-SDK/Claude-SDK/Agno/Mastra) +
  `asdg` Ch09 → one landscape + selection guide.

## Cuts / threads-out

- **DSPy** tagged optimize-territory (keep as a framework mention, not a deep dive).
- Phase 14 lessons **19–22** (benchmarks SWE-bench/GAIA/WebArena/OSWorld; computer-use; voice) are
  **thin-teaching → M4 Track H** (realized in artifacts), not deep here.
- Phase 14 **23–24** (OTel GenAI, observability platforms) → forward-pointer to M5 observability.

## Key kept thread: the Agent Workbench (Ph14 31–42)

A strong single-agent **operational** thread — the seven workbench surfaces (instructions, state, scope,
feedback, verification, review, handoff) that decide whether an agent ships. Model-independent, builds to a
reusable `agent-workbench-pack/`. → `src/module3/05`. This directly seeds the M6 coding-agent artifact.

## Gap 2 (complexity ladder)

Runs through this module as the editorial spine — lessons 12 (Anthropic workflow patterns) and 28 carry the
`[GAP 2]` tag. The bridge opened at the end of M2 continues here as the governor.

## Accounted-for check

6 module3 source files + 1 threaded-in. Single-agent kept; multi-agent (Ph15–16) → M4; benchmarks/
computer-use/voice → M4 thin; DSPy optimize-tagged. Nothing uncatalogued.
