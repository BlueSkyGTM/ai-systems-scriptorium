# VERIFY verdict — Lesson 05: Long-Horizon Agents & Durable Execution

**Lesson:** `build-stages/m4/output/author/05-long-horizon-durable-execution.md`
**Verifier:** Sonnet VERIFY subagent (M4 ch02 Op-Safety, safety-critical)
**Date:** 2026-06-19

## Markers resolved (4 of 4)

| Marker | Source checked | Result |
|---|---|---|
| `[verify: Temporal — durable execution / OpenAI Agents SDK integration]` | WebFetch Temporal blog (OpenAI Agents SDK integration) | **PASS → removed.** Each agent invocation wraps in a Temporal Activity; checkpoint/retry/replay; resumes from last checkpoint without reprocessing completed steps. GA March 2026 (matches Ph15 source). Tightened prose to add the GA date + "without reprocessing completed steps." |
| `[verify: LangGraph — checkpointers / Postgres persistence / thread_id]` | WebFetch docs.langchain.com/oss/python/langgraph/persistence | **PASS → removed.** Checkpointer persists graph state keyed by `thread_id`; HITL + fault tolerance. Step-level + Postgres detail corroborated by Ph14 L13 source ("checkpoint after every step… resumes from step 38"; "SQLite/Postgres/Redis"). |
| `[verify: Cloudflare Durable Objects — persistence model]` | WebSearch Cloudflare Agents docs / Durable Objects | **PASS → removed.** Each agent = Durable Object with built-in SQLite; state survives restarts, deploys, hibernation; holds per-key state for weeks. Corrected "across weeks"→"for weeks" + added "built-in SQLite." |
| `[MS-Learn: Microsoft Agent Framework durable execution / checkpoint / thread persistence]` | MS Learn connector: "Durable Task for AI agents", "Agent Framework Workflows — Checkpoints", "Durable Task extension for Microsoft Agent Framework" | **PASS → removed.** First-class `CheckpointStorage` (File/Cosmos); persistent sessions "survive process crashes, restarts, and scaling events without losing context"; resume/rehydrate from checkpoint. Reworded to MS's exact framing (crashes/restarts/scaling events). |

## Claim ledger

| Claim | Source | Verdict |
|---|---|---|
| Long run *will* be interrupted; single-process loop model collapses past minutes/hours | Ph15 L01 + L12 ("every assumption built around single-turn chat breaks when runs last longer than lunch") | PASS |
| Every LLM call is an *activity*: checkpoint / retry / replay | Ph15 L12 verbatim ("every LLM call becomes an activity with checkpoint, retry, and replay") | PASS |
| Rationale: LLM call is non-deterministic, expensive, slow, side-effectful | Ph15 L12 ("non-deterministic, expensive, failing, side-effectful — exactly the activity profile") | PASS |
| Replay reads completed steps from durable history without re-calling the model | Ph15 L12 / L16; MS Learn ("Completed agent calls aren't re-executed on recovery") | PASS |
| `thread_id` is the spine; keys checkpoint history, resumes a process | Ph15 L12 ("resume from the latest checkpoint keyed by `thread_id`") | PASS |
| Survives a deploy / pauses on human input / resumes from latest checkpoint | Ph15 L12 ("sessions pause on human-input, survive deploys, resume from the latest checkpoint") | PASS |
| Capability ≠ reliability; success drops sharply as horizon grows | Ph15 L12 ("METR's 35-minute degradation — success drops roughly quadratically"); L01 ("capability ceiling not a reliability floor"). Draft hedges to "sharply" — safe. | PASS |

## STYLE result — PASS

- Single H1, present tense, 2nd person, one blunt confident voice throughout. ✓
- Seam lead: states the problem (long run will be interrupted) + the AI-Engineer ∪ MLOps cusp made explicit in "The qualitative break" ("the AI Engineer asks whether the agent reasons well… the MLOps half asks what happens when the box disappears"). ✓
- One `## Core concepts` block, 4 testable propositions. ✓
- Handoff div well-formed (`data-exercise` set). ✓
- Ending (the budgets/kill-switches forward-pointer): consequence shape, not the banned template; varied vs. siblings. ✓
- Acronyms: LLM, RAM, ID — standard. ✓
- De-dup: budgets/kill-switches/checkpoints pointed forward to "next four lessons," HITL pause flagged as "lesson 08." Defined-here boundary respected. ✓

## Antilibrary fence — PASS
No frontier-safety/policy material (STaR/AlphaEvolve/DGM/RSP/FSF/METR-as-policy/CAIS). METR appears only implicitly as the hedged reliability caveat, no named policy content. ✓

## Overall verdict: **PASS** (4 markers resolved, 0 defects, 0 FLAGGED). Ship-ready.
