# VERIFY verdict — M5 L09 · Measure Before You Optimize: Profiling & Roofline

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Draft:** `build-stages/m5/output/author/09-measure-before-you-optimize.md` (edited in place)
**Verdict:** **PASS** (every perf number sourced, all 13 markers resolved, inference-only confirmed, STYLE held)

This is a perf-number-dense lesson; per the protocol every number was checked individually against the aipe source, with hardware specs cross-checked externally. The lesson is the discipline lesson (profile → name the bound → attribute → fix), so most "numbers" are illustrative deltas already framed as such.

---

## Claim ledger — every perf number → source → result

| # | Claim / number | Authority | Result |
|---|----------------|-----------|--------|
| 1 | Activation checkpointing on a non-memory-limited workload trades needed compute for spare memory and makes the job *slower* | aipe inference-reference-docs, "Profile before and after" (L293) | **PASS** — verbatim: "your workload is not memory-limited, but you decide to try enabling activation checkpointing... may actually slow down the job by using extra compute to reduce memory." Framed by draft as the cautionary case, exactly as the source intends. Training-flavored but used correctly as an illustration of misapplied optimization (see inference-only note). |
| 2 | "Profile before and after"; theory tweaks "might not help — or even hurt — in practice" | aipe reference, "Profile before and after" (L291–293) | **PASS** — source verbatim. Draft removed the stray quotation marks; meaning preserved. |
| 3 | The four bounds: profiling reveals compute-bound / memory-bound / I/O-bound / network-bound so you target the right fix | aipe reference (profiling framing) + standard usage | **PASS** — the "four bounds" framing is the draft's pedagogical synthesis of the source's repeated profiling guidance; the one-line quote is faithful in substance. Draft replaced "network-bound" naming with "communication-bound" in the body taxonomy and keeps "network-bound" in the quote — consistent. |
| 4 | Roofline: arithmetic intensity (FLOPs/byte) on x-axis, achieved performance (FLOPs/s) on y; diagonal = memory-bound, flat roof = compute-bound | aipe reference, "Read roofline and automated issue hints" (L721–723); standard roofline model | **PASS** — source: "Plot achieved FLOPs versus arithmetic intensity to see if you are bandwidth limited or ALU limited." The two-region model is the canonical Williams/Waterman roofline; correct as stated. ASCII diagram is schematic and accurate (slope = bandwidth, flat = peak FLOPs). |
| 5 | Nsight Compute ships a roofline pane that plots per-kernel and flags the limiter | aipe reference, "Read roofline and automated issue hints" (L721–723) | **PASS** — verbatim: "Nsight Compute now ships a Roofline pane and 'Issues' recommendations for every captured kernel." |
| 6 | LLM decode is structurally memory-bound (low arithmetic intensity, reloads weights + KV per token); prefill is compute-bound | aipe ch15–19 (decode memory-bound thesis); standard LLM serving knowledge | **PASS** — consistent with the source's decode/prefill framing throughout ch15–20 and the memory-bound decode premise the whole serving track rests on. Correct. |
| 7 | Two-step systems-to-kernel flow: Nsight Systems timeline first, then Nsight Compute on the dominant kernel | aipe reference, "Use a systems-to-kernel profiling flow" (L717–719) | **PASS** — verbatim: "Capture the big picture with Nsight Systems first... Once you know which kernels or streams dominate the gap, switch to Nsight Compute." Draft's "and it is the right order" matches the source's two-step intent. |
| 8 | Tag phases with named (NVTX) markers so the timeline reads like a story | aipe reference, "Use NVTX markers" / "Place NVTX ranges strategically" (L733–739) | **PASS** — source: "tagging phases with NVTX so you can see CPU prep, data transfers, and GPU kernels in one timeline"; "human-readable names so Nsight timelines tell a story at a glance." Draft glosses NVTX as "named markers" — reader-friendly, accurate. |
| 9 | **GPU at 50% utilization is a feeding problem, not a kernel problem** | aipe reference, "Monitor utilization metrics" (L317) | **PASS** — verbatim: "If GPUs are at 50% utilization, dig into why. It's likely data waiting/stalling and slow synchronization." Illustrative example, framed correctly ("A GPU sitting at 50% utilization is not a kernel problem"). |
| 10 | Utilization dips every five minutes coincide with checkpoint saves | aipe reference, "Monitor utilization metrics" (L731) | **PASS** — verbatim: "a drop in utilization every 5 minutes might coincide with checkpoint saving." Draft says "every five minutes" — exact match. Framed as "the reference's example," correctly attributed. |
| 11 | 80/20: if ~90% of time is in two kernels or one comm phase, optimize those and ignore the 1% kernel | aipe reference, "Optimize the expensive first" (L287–289) | **PASS** — verbatim: "If 90% of the time is in a couple of kernels or a communication phase, it's better to optimize those deeply than to microoptimize something taking 1% of the time." Exact. |
| 12 | **tensor-core decode kernel: 15.65x** | aipe inference-serving-chapters, ch18 `tensor_cores` (L342) | **PASS** — source table: `tensor_cores` 3.805 ms → 0.243 ms = **15.65x**, "tensor-core decode kernel." Exact match. Now framed "In the reference's own benchmark runs" + "Re-measure on your own hardware" — situational framing preserved. |
| 13 | **cache-aware rope/Q-path reuse: 23.53x** | aipe inference-serving-chapters, ch18 `rope_q_cache` (L343) | **PASS** — source table: `rope_q_cache` 106.429 ms → 4.523 ms = **23.53x**, "cache-aware rope/Q-path reuse." Exact match. |
| 14 | **smarter routing policy: 7.07x with workload unchanged** | aipe inference-serving-chapters, ch17 `routing_static` (L239) | **PASS** — source table: `routing_static` 5.680 ms → 0.804 ms = **7.07x**, "smarter routing policy without changing the underlying workload." Exact match, including the "workload unchanged" qualifier verbatim. (Note: ch20 `integrated_kv_cache` also = 7.07x; draft correctly attributes its 7.07x to ch17 routing, not the cache target.) |
| 15 | Those deltas were *attributed* via deep-dive profiling (cache movement vs scheduling vs decode) — not lucky batches | aipe inference-serving-chapters, ch15/ch18 "Profiler Evidence" sections (L43–52, L347–356) | **PASS** — source: deep-dive runs "are the right place to check whether the win came from less queue idle time, less cache movement, or fewer wasted decode steps"; ch18 "Re-measure it on your hardware before treating the chapter numbers as a decision threshold." Draft's attribution-discipline framing is faithful. |

**Every perf number in this lesson traces to the aipe source and matches exactly.** No number was wrong; none required correction or softening beyond the situational framing the source itself prescribes (and the draft already carries it: "on one target," "Re-measure on your own hardware," "not numbers to quote at a stranger's stack").

## Markers resolved (13 / 13)

All `[verify: ...]` markers removed, prose left clean:
1. L9 activation-checkpointing case → removed (claim 1)
2. L22 four-bounds one-liner → removed (claim 3)
3. L46 Nsight roofline pane → removed (claim 5)
4. L52 systems-to-kernel flow → removed (claim 7)
5. L54 NVTX markers → removed (claim 8)
6. L54 GPU 50% utilization → removed (claim 9)
7. L54 checkpoint-save dip → removed (claim 10)
8. L56 optimize-the-expensive-first → removed (claim 11)
9. L58 tensor_cores / rope_q_cache / routing_static deltas → removed (claims 12–14)
10. L58 ch15 Profiler Evidence (attribution) → removed (claim 15)
11. L62 align workloads before timing → removed (PASS, aipe "Align workloads before timing" L273)
12. L62 measure the steady state → removed (PASS, aipe "Measure the steady state" L274)
13. L62 track throughput and latency together → removed (PASS, aipe "Track throughput and latency together" L275); + "log the environment every run" → removed (PASS, aipe L281)

No markers remain (grep confirmed zero `[verify:`/`[MS-Learn:`/`[FLAG`).

## Inference-only confirmation

**PASS.** No training/CUDA-kernel-authoring material leaked from the 200-item antilibrary appendix. The lesson is profiling/attribution discipline applied to inference serving:
- The roofline, the four bounds, the two-step Nsight flow, NVTX tagging, steady-state measurement, and the 80/20 rule are general perf-engineering tools framed entirely around inference (decode memory-bound, prefill compute-bound, KV cache, decode kernels).
- The single training-flavored item — activation checkpointing (a training memory technique) — is used **only** as the source's cautionary example of an optimization misapplied to the wrong bound. It is not taught as an inference technique; it illustrates "the application was a guess." Correct and on-thesis.
- The perf deltas all come from ch15/ch17/ch18 inference-serving chapters, never the ch01–14 training/CUDA chapters.

## STYLE pass

**PASS.** One H1 ("# Measure Before You Optimize: Profiling & Roofline"). Seam lead grabs and states the stakes ("An optimization applied to the wrong bottleneck is... negative work"). One `## Core concepts` block (4 propositions stated as claims). Handoff div present, well-scoped to the lesson-09 exercise. Acronyms expanded on first use: FLOPs ("FLOPs, floating-point operations"), HBM ("HBM, the GPU's on-package DRAM"); roofline is explained in full; NVLink not used in this lesson. Second person / present tense / active voice held throughout. Ending lands as a reframe, not a template ("Measure first. The lever comes second, and only the measurement tells you which one.") — not the banned "An AI Platform Engineer who…" opener. Voice is blunt and opinionated with earned warmth ("a rumor, not a result"; "guessing with a budget"). No template ending.

## Defects fixed

None beyond marker removal. All numbers were correct as drafted; minor copy-edits during marker removal (stray quote marks around the "profile before and after" gloss; "reveals if" → "reveals whether"). Voice unchanged.

## FLAGGED

None. Every perf number is exact-to-source and the deltas are already framed as illustrative/situational per the source's own re-measure caution.
