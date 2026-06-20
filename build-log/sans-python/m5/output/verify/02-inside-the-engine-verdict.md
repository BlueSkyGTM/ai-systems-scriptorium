# VERIFY verdict — M5 L02 · Inside the Engine: Continuous Batching & Paged KV-Cache

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Verdict:** PASS (edited in place; all markers resolved; no FLAGs)

## Claim ledger

| Claim | Source / check | Result |
|---|---|---|
| Prefill is compute-bound and sets TTFT; decode is memory-bound and sets TPOT | aefs Ph17 L08 (TTFT = prefill+queue+network; TPOT memory-bound decode) | PASS |
| Static batching returns when slowest finishes, holds batch hostage | aefs Ph17 L04 / aipe ch15 (naive queue draining) | PASS |
| Continuous batching reschedules between every decode step; seqs join/leave | aefs Ph17 L04 ("sequences join/leave the batch between decode iterations via V1 scheduler") | PASS |
| **~4.16x gain, 53ms→13ms per iteration, scheduling alone** | aipe ch15 measured-delta table: `continuous_batching 52.955ms → 12.719ms = 4.16x` ("queueing and batching strategy") | PASS (exact match) — **reframed as illustrative** per protocol |
| Chunked prefill slices long prompt so decode never starves | aefs Ph17 L04 (chunked prefill ~512-token chunks; drops P99 ITL ~50→15ms) | PASS |
| Naive contiguous KV allocation wastes 60–80% (fragmentation + over-reservation) | vLLM PagedAttention blog (WebFetch): "existing systems waste 60%–80% of memory due to fragmentation and over-reservation" | PASS (exact match; added "and over-reservation" to be precise) |
| PagedAttention: fixed blocks + per-request block table = OS page table; waste <4% | vLLM blog (WebFetch): "near-optimal… a mere waste of under 4%"; waste only in last block | PASS (exact match; added "happens only in last partial block") |
| Prefix sharing: shared physical blocks for shared prefix; mechanism behind "static content first" | vLLM docs (prefix caching) + aefs Ph17 L06 | PASS |
| **KV cache 10–30 GB vs ~4 GB weights (7B @ 4-bit) at production batch** | aefs Ph17 L09 ("my model is 4GB now forgets the 10–30GB KV cache") + WebSearch (KV cache exceeds weight size at modest batch/ctx; 7B Q4 ≈ 3.5–4.5 GB; KV 9–54 GiB examples) | PASS (added "roughly" to the 4 GB; range well-confirmed) |
| Azure OpenAI provisioned deployment exposes utilization metric + returns HTTP 429 past 100% | MS Learn (provisioned-throughput): util metric in Azure Monitor, "returns a 429 on any new calls after utilization rises above 100%" | PASS (exact match; tightened wording to "once utilization passes 100%") |

## Markers resolved
All 6 `[verify:…]` and 1 `[MS-Learn:…]` markers removed → clean prose. No markers remain (grep clean).

## Perf numbers — every one checked
1. **4.16x / 52.955ms→12.719ms** — exact in aipe ch15. Traces to one reference microbenchmark → **kept but reframed as illustrative** ("in one reference microbenchmark… treat that number as an illustration of the mechanism, not a figure to quote back; your gain depends on prompt/output lengths"). Core-concepts line softened from "roughly a 4.16x gain" to "several-fold in one reference benchmark." Not presented as a universal target. ✓
2. **60–80% classic-allocator waste** — exact match to vLLM blog primary source. PASS.
3. **<4% PagedAttention waste** — exact match to vLLM blog primary source. PASS.
4. **10–30 GB KV cache / 4 GB weights** — aefs L09 + external corroboration. PASS.

## "Layer two depths, don't dedup"
L02 layers the aefs **operate/concept depth** (PagedAttention, continuous batching, chunked prefill — L04/L08/L09) with the aipe **measure depth** (the ch15 continuous-batching microbenchmark, 4.16x). Both depths present, not collapsed. The L02 prose explicitly carries the measured delta on top of the conceptual mechanism. Preserved.

## STYLE result
- H1: one. Lead: strong (REST-server contrast, "different machine," points below the API) — PASS.
- One `## Core concepts` (4 props) before handoff — PASS.
- claude-handoff div present, correct path — PASS.
- Ending: reframe/contrast ("A REST server scales by adding stateless replicas… an inference engine scales by packing more sequences… now not a black box") — distinct shape from L01/L03; no template — PASS.
- Acronyms: KV cache → "key-value cache" expanded; TTFT → "time to first token"; TPOT → "time per output token" — all glossed on first use — PASS.
- Voice: second person, present tense — PASS.

## Verdict
**PASS.** Two perf numbers (60–80%, <4%) confirmed verbatim against the vLLM primary source. The 4.16x figure confirmed exactly against the aipe migration source and reframed as illustrative per protocol. Azure 429/utilization confirmed verbatim. No FLAGs.
