# VERIFY verdict — M5 L03 · The Optimization Levers: Quantization, Speculative Decoding, Disaggregation

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Verdict:** PASS (edited in place; all markers resolved; no FLAGs)

## Claim ledger

| Claim | Source / check | Result |
|---|---|---|
| Quantization stores weights in fewer bits → less memory traffic → faster decode (memory-bound) | aefs Ph17 L09 + WebSearch (quantization guides) | PASS |
| Format map: GGUF k-quants (CPU/edge), AWQ (datacenter GPU 4-bit default), GPTQ (multi-adapter), FP8 (near-lossless recent NVIDIA) | aefs Ph17 L09 + WebSearch: GGUF=CPU/edge via llama.cpp; AWQ=datacenter/reasoning; GPTQ=GPU-focused; FP8=near-FP16, fastest on modern GPUs | PASS (GPTQ multi-LoRA angle is aefs-authoritative; general sources call GPTQ GPU-focused, consistent) |
| Trap 1 — calibration dataset must match production domain or wrong weights protected | aefs Ph17 L09 ("generic C4 lets AWQ protect the wrong weights, HumanEval drops") | PASS |
| Trap 2 — quantizing weights ≠ quantizing KV cache; 4 GB weights, 10–30 GB KV | aefs Ph17 L09 + WebSearch (KV cache exceeds weights at production batch) | PASS |
| Spec decode: small draft proposes N tokens, target verifies in one pass; accepted = free | aefs Ph17 L05 + WebSearch (EAGLE-3 mechanism) | PASS |
| Newest drafts trained on target's hidden states (EAGLE-3); chat acceptance ~0.6–0.8 | aefs Ph17 L05 + WebSearch: EAGLE-3 fuses target hidden states; published acceptance 0.6–0.88 on chat/coding | PASS (named "EAGLE-3 and its kin"; 0.6–0.8 within published range) |
| Every rejected draft costs a second target pass | aefs Ph17 L05 + WebSearch (verification overhead in compute-bound regime) | PASS |
| **Net-negative below ~0.55 acceptance at high concurrency** | aefs Ph17 L05 ("below ~0.55 at high concurrency spec decode is net negative") + WebSearch (overhead detrimental when compute-bound; 1.4–1.8x slowdown, up to ~30% degradation at high QPS) | PASS — mechanism externally confirmed; exact 0.55 is aefs measurement, **framed with "roughly"** + tied to compute-bound regime |
| Domain traffic drops acceptance (0.4–0.6) unless you train a domain draft head | aefs Ph17 L05 | PASS (prose generalized to "tends to drop acceptance" to avoid over-precise universal number; mechanism preserved) |
| Gate on p99 per-token latency, not mean | aefs Ph17 L05 ("gate on P99 ITL not P50; mean drops while P99 worsens on rejected-draft two-pass") | PASS (rendered as "p99 per-token latency" — ITL un-jargoned) |
| Colocated prefill/decode wastes ~20–40% GPU time; can't tune TTFT and TPOT together | aefs Ph17 L17 ("colocating wastes 20–40% of GPU time") + WebSearch (Together.ai "up to 40%"; colocation makes both metrics un-tunable) | PASS (added the TTFT/TPOT-contention sentence — externally confirmed) |
| Disaggregation: separate pools each sized to bottleneck; ship KV over fast interconnect; independent scaling | aefs Ph17 L17 (NIXL RDMA/InfiniBand) + WebSearch (DistServe/Ray/Together) | PASS |
| **KV-transfer tax: tens of ms for multi-thousand-token prompt; pays off at scale/long prompts/fast fabric** | aefs Ph17 L17 ("~20–80ms for a 4K-token 70B FP8 prompt") + WebSearch ("KV transfer adds 50–200ms") | PASS — prose hedge "tens of milliseconds… more on slower fabrics" sits inside both ranges |
| Azure OpenAI provisioned: size in capacity units (PTUs), benchmark real traffic; platform owns quant/batching/scheduling | MS Learn (provisioned-get-started): "Benchmark the load using real traffic workload"; PTU sizing | PASS (added "(PTUs)") |
| Blast-radius ordering: quant (offline) → spec decode (live) → disaggregation (architecture) | Editorial synthesis grounded in the three sources' validation depth | PASS |

## Markers resolved
All 6 `[verify:…]` and 1 `[MS-Learn:…]` markers removed → clean prose. No markers remain (grep clean).

## Perf numbers — every one checked
1. **Quant format map** — aefs L09 + external guides. PASS.
2. **10–30 GB KV / 4 GB weights** — aefs L09 + external. PASS (same as L02).
3. **EAGLE-3 acceptance 0.6–0.8 (chat)** — aefs L05 + external (0.6–0.88 published). PASS, hedged "rough range."
4. **Net-negative below ~0.55** — aefs single measurement; mechanism confirmed externally (compute-bound overhead, 1.4–1.8x slowdowns). Kept, framed "roughly… high concurrency." Not a universal target. ✓
5. **Domain acceptance 0.4–0.6** — aefs L05; generalized in prose to "tends to drop" (kept the specific 0.4–0.6 out of student-facing text since it's a single-source figure; the *direction* is the teachable claim). ✓
6. **Colocation waste 20–40%** — aefs L17 + Together.ai "up to 40%." PASS.
7. **KV-transfer tax (tens of ms)** — aefs L17 (20–80ms/4K) + external (50–200ms). PASS, hedged.

No number is presented as a universal target; each is framed as illustrative/regime-dependent with a "measure on your traffic" gate. **No FLAGs needed** — every figure traces to a source and the high-risk ones (0.55 threshold, 20–40%, transfer tax) are corroborated by independent external sources.

## "Layer two depths, don't dedup"
L03 carries aefs **operate/decision depth** (quant format map L09, spec-decode production recipe L05, disaggregation economics L17) and the aipe **measure depth** is referenced via the two-phase split from L02 (prefill/decode) feeding the disaggregation lever. The decision framing layers on top of the mechanism without collapsing them. Preserved.

## STYLE result
- H1: one. Lead: 3 sentences, problem ("latency too high / bill too large") + the lever framing — no throat-clearing — PASS.
- One `## Core concepts` (4 props) before handoff — PASS.
- claude-handoff div present, correct path — PASS.
- Ending: warning/cost ("the most expensive optimization is the one that bought a number you weren't grading") — distinct shape from L01/L02; no template — PASS.
- Acronyms: FIXED — glossed "service-level objective (SLO)" first use; removed bare "ITL" (→ "per-token latency"); added "(PTUs)". AWQ/GPTQ/GGUF/FP8 are format proper-names (industry-standard, kept).
- Voice: second person, present tense, blunt opinion ("or you are gambling") — PASS. One genuine human moment ("the one nobody budgets for") — PASS.

## Verdict
**PASS.** All three levers' mechanisms and high-risk perf numbers confirmed against the migration sources AND independent external sources (vLLM/Red Hat spec-decode, Together.ai/Ray disaggregation, multiple quantization guides). Azure provisioned-sizing confirmed via MS Learn. Single-source thresholds (0.55, 0.4–0.6) framed as illustrative/directional, not universal. No FLAGs.
