# VERIFY verdict — M5 L04 · Inference Metrics & Load Testing

**Verdict: PASS (edited in place).** All five markers resolved to clean prose. Every load-bearing claim source-checked or externally verified. No invented facts found.

## Claim ledger

| Claim | Status | Authority |
|---|---|---|
| TTFT = prefill + queue + network; the user-visible "did it hear me?" number | CONFIRMED | aefs ch08 ("TTFT = prefill + queue + network") |
| TPOT / inter-token latency = per-token decode gap, memory-bandwidth-bound, ~flat vs prompt length | CONFIRMED | aefs ch08, ch04 (decode is memory-bound) |
| E2E latency = TTFT + TPOT × output length | CONFIRMED | aefs ch08 verbatim |
| Throughput = fleet tokens/s; trades against latency; continuous batching lengthens queue → raises TTFT | CONFIRMED | aefs ch04 (continuous batching), ch08 |
| **TTFT ~162 ms / TPOT ~7.3 ms, ~1 s E2E (Llama-3.1-8B)** | CONFIRMED as single-source measurement | aefs ch08: "Reference (Llama-3.1-8B on TRT-LLM): mean TTFT 162ms / TPOT 7.33ms / E2E 1,093ms" |
| Goodput = fraction of requests meeting EVERY SLO simultaneously; high throughput at 60% goodput = failure | CONFIRMED | aefs ch08 + serving-benchmark literature (Goodput = #req meeting all SLOs / total) |
| Report p50/p90/p99, never mean; LLM latency right-skewed | CONFIRMED | aefs ch08 ("Always report P50/P90/P99, never mean") |
| Azure Monitor + Application Insights collect latency + token telemetry for Azure OpenAI deployments | CONFIRMED | MS Learn "Monitor Azure OpenAI" (metrics explorer, Log Analytics, token + latency metrics) |
| Client-side tokenization trap: generic tool tokenizes under Python GIL → inflated ITL = client bottleneck | CONFIRMED | aefs ch22 ("Locust runs tokenization client-side under the GIL…inflates reported ITL"); external (tianpan.co "Why k6 and Locust Lie") |
| Purpose-built tools push tokenization onto a separate process | CONFIRMED (tightened) | LLM-Locust / LLMPerf docs (separate process / Rust-backed tokenization) |
| Uniform-prompt trap: same prompt hits prefix cache; vary input length around mean/stddev | CONFIRMED | aefs ch22 (LLMPerf `--mean-input-tokens`/`--stddev-input-tokens`) |
| Four load shapes: steady / ramp / spike / soak | CONFIRMED | aefs ch22 verbatim ("steady, ramp, spike, soak") |
| Azure GenAI gateway toolkit ships a load-testing setup for gateway policies | CONFIRMED | MS Learn azure-openai-gateway-multi-backend: "GenAI gateway toolkit contains example API Management policies together with a load-testing setup" |
| M2 inner loop (quality) → M5 outer loop (serving perf + production control plane) | CONFIRMED | PLAN threads; asdg Ch14 (online eval / outer loop); accurate cross-ref |

## Markers resolved (5/5)
1. `[verify: TTFT/TPOT reference figures …]` → reframed as "in one TensorRT-LLM benchmark … Treat that as one data point on one engine and one GPU, not a target." Marker removed; "measure your own" caveat kept and strengthened.
2. `[verify: goodput as multi-constraint SLO metric]` → removed; claim confirmed verbatim against aefs + literature.
3. `[MS-Learn: Azure Monitor / App Insights …]` → removed; confirmed.
4. `[verify: client-side tokenization / GIL …]` → removed; confirmed (this is the literal aefs ch22 + the "k6 and Locust Lie" source).
5. `[verify: prompt-uniformity / prefix-cache skew …]` → removed; confirmed.
6. `[MS-Learn: APIM GenAI gateway toolkit load-testing setup]` → removed; confirmed verbatim and rephrased to "GenAI gateway toolkit."

## TTFT/TPOT number decision
**Kept, reframed as illustrative.** Source aefs ch08 gives the exact figures (162 ms / 7.33 ms / 1,093 ms) from one TRT-LLM Llama-3.1-8B run. Drafter's watch-item honored: now reads "in one TensorRT-LLM benchmark … one data point on one engine and one GPU, not a target," with "measure your own" retained. Not presented as a universal target.

## STYLE pass
- H1 present; lead grabs (REST one number vs LLM four); one `## Core concepts` block (4 props); handoff div present and well-formed.
- Ending lands as a forward consequence (hands to next two lessons) — not a template ending, no banned "An AI Platform Engineer who…" opener.
- Acronyms TTFT, TPOT expanded on first use (lines 9, 11). SLO: "service-level objective" spelled out at first use (line 21) then "SLO."
- Unity: second person, present tense, one voice throughout. Clean.

## FLAGGED for editor (non-blocking)
- Cross-ref nomenclature: this lesson calls siblings "chapter 1" / "chapter 2" and itself "This chapter," whereas L06 refers to "lesson 04" / "lesson 05." Pre-existing drafter inconsistency, not introduced here. Editor may want one convention across the chapter. Left as-is per "don't change voice."
