# VERIFY verdict — M5 L10 · The Production Performance Checklist

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Draft:** `build-stages/m5/output/author/10-the-performance-checklist.md` (edited in place)
**Verdict:** **PASS** (every perf/hardware number sourced + externally cross-checked, all 22 markers resolved, inference-only confirmed, STYLE held)

This lesson carries the module's single highest-risk number: the NVLink 5 hardware spec and the "14x PCIe Gen5" comparison. Both were cross-checked against NVIDIA and Microsoft Learn directly, not just the aipe book excerpt.

---

## Claim ledger — every perf/hardware number → source → result

| # | Claim / number | Authority | Result |
|---|----------------|-----------|--------|
| 1 | Source is a 200-plus-item reference checklist; curated subset (~two dozen) is the load-bearing, inference-relevant part; rest is training/kernel-deep antilibrary | aipe inference-reference-docs, "AI Systems Performance Checklist (200+ Items)" (L261–264) | **PASS** — source: appendix titled "AI Systems Performance Checklist (200+ Items)," derived from Fregly, *AI Systems Performance Engineering* (O'Reilly). Curation-to-inference is the PLAN's explicit ch4 mandate ("inference-only"). |
| 2 | 80/20: optimize top runtime/cost contributors deeply, not a 1%-of-time kernel | aipe reference, "Optimize the expensive first" (L287–289) | **PASS** — verbatim (same source line as L09 claim 11). |
| 3 | Lock versions/configs/benchmarks in source control so a regression is traceable | aipe reference, "Rigorous version control" (L339–341) | **PASS** — verbatim: "Maintain comprehensive version control... experiments can be reproduced exactly—and performance regressions can be easily identified." |
| 4 | Bring a perf benchmark into CI so a driver bump / dropped Tensor Core usage is caught by the pipeline | aipe reference, "Continuous integration for performance regression" (L343–347) | **PASS** — source: "Integrate automated performance benchmarks... into your CI/CD pipelines... helping catch regressions early." Faithful. |
| 5 | Hardware/interconnects/data paths cap performance; no software tweak outruns a starved GPU | aipe reference, "System Architecture and Hardware Planning" (L373–375) | **PASS** — verbatim: "Your hardware, interconnects, and data paths set the ceiling for performance and cost-efficiency—no software tweak can outrun a starved GPU." |
| 6 | HBM bandwidth + capacity is the spec to read first for decode-heavy workloads (decode memory-bound) | aipe ch15–19 decode-memory-bound thesis; "Place data for locality" (L417–419) | **PASS** — consistent with the decode-memory-bound premise and "keep hot weights, activations, and KV cache in HBM." Correct framing. |
| 7 | **NVLink 5 (fifth-gen NVLink): up to 1.8 TB/s bidirectional per GPU** | aipe reference, "Leverage high-bandwidth interconnects" (L387) **+ NVIDIA (WebFetch) + MS Learn (connector)** | **PASS — externally confirmed.** aipe L387: "NVLink 5 provides up to 1.8 TB/s bidirectional GPU-to-GPU bandwidth." NVIDIA NVLink page (WebFetch): fifth-generation NVLink = **1,800 GB/s (1.8 TB/s)** per GPU. MS Learn ND-GB200-v6 / ND-GB300-v6: "fifth-generation NVLink, providing a total of 4× 1.8 TB/s NVLink bandwidth per VM." Three independent sources agree. Draft says "the fifth generation of NVLink provides up to 1.8 TB/s bidirectional bandwidth per GPU" — exact. |
| 8 | **NVLink 5 is over 14x a PCIe Gen5 link** | aipe reference, "Leverage high-bandwidth interconnects" (L387) | **PASS (with note).** aipe L387 verbatim: "(over 14x PCIe Gen5)." Arithmetic sanity check: PCIe 5.0 x16 ≈ 128 GB/s bidirectional; 1,800 / 128 ≈ **14.1x** — the comparison is arithmetically sound. **Note:** NVIDIA's *current* public page pairs "over 14x" with **PCIe Gen6** for **NVLink 6** (next gen), not NVLink 5 vs Gen5 — i.e. NVIDIA's marketing has moved the "14x" headline forward a generation. The draft's claim traces to the aipe source and is numerically defensible (1.8 TB/s really is ~14x a Gen5 x16 link), so it is kept as the reference's figure. Not a blocking defect; see FLAGGED for the watch-item. |
| 9 | **KV cache pooled over NVLink: 6.11x latency improvement vs local-only** | aipe inference-serving-chapters, ch15 `kv_cache_nvlink_pool` (L37) | **PASS** — source table: `kv_cache_nvlink_pool` 1047.860 ms → 171.477 ms = **6.11x**, "pooled KV-cache path." Exact match. Framed "in the serving chapters' benchmark runs" + the on-thesis caveat "On a PCIe-only box, the same pooling would be a bottleneck" — situational framing intact. |
| 10 | **Topology-aware routing beat uniform placement 5.07x on a MoE target** | aipe inference-serving-chapters, ch17 `moe_router_uniform` (L240) | **PASS** — source table: `moe_router_uniform` 4.719 ms → 0.931 ms = **5.07x**, "topology-aware expert routing instead of uniform placement." Exact, including "same GPUs, same model, better placement" matching the source's invariant-output note. |
| 11 | `nvidia-smi topo -m` reads the box layout / NVLink islands before pinning | aipe reference, topology-aware scheduling (L443–445, L539–541) + standard nvidia-smi usage | **PASS** — `nvidia-smi topo -m` is the canonical topology-matrix command; source repeatedly prescribes colocating jobs within an NVLink domain and reading topology before placement. Correct. |
| 12 | Azure ND/NC GPU VMs differ in GPU gen, HBM, and whether they expose NVLink/NVSwitch across the VM's GPUs; pick the SKU from the measured bound | MS Learn (connector) | **PASS — confirmed.** MS Learn: ND-GB200-v6/ND-GB300-v6 (fifth-gen NVLink, 4×1.8 TB/s/VM), ND-H200-v5/ND-H100-v5 (900 GB/s NVLink 4.0, 141/80 GB HBM), older ND A100 v4 (NVLink 3.0). SKUs demonstrably differ in GPU gen, HBM, and intra-VM NVLink — exactly the draft's claim. Draft's added parenthetical ("ND-series GB200/GB300 v6 and H100/H200 v5 sizes... expose NVLink across the GPUs inside the VM") is accurate per the connector. |
| 13 | Goodput = useful work per dollar/watt, not raw FLOPs; peak FLOPs serving garbage isn't winning | aipe reference, "Design for goodput and efficiency" (L377–379) | **PASS** — verbatim: "design for goodput—useful work per dollar/watt—and not just raw FLOPS." |
| 14 | Track TTFT + TPOT next to throughput + cost-per-token; helping one while hurting another is a regression | aipe ch16 goodput/TTFT/TPOT (L107); reference "Track throughput and latency together" (L275) | **PASS** — ch16 key concepts list goodput (TTFT/TPOT) + cost-per-token; the regression principle is the reference's "track throughput and latency together." Faithful. |
| 15 | Throughput-per-dollar across instance types; second-best hardware at a fraction of cost often wins | aipe reference, "Leverage cloud flexibility for cost" (L311–313) | **PASS** — verbatim: "a slightly older GPU instance at a fraction of the cost can deliver better price/performance... Calculate metrics like throughput per dollar." |
| 16 | Quantize weights + KV cache (FP8, AWQ/GPTQ/SmoothQuant) to cut bytes a memory-bound path moves | aipe ch16 quantization family (L155–157, L178); ch19 dynamic quantized cache | **PASS** — ch16 has the first-class `awq_gptq_smoothquant` target family + FP8 transformer-engine; ch19 dynamic quantized cache. Correct. |
| 17 | Paged/block-wise KV allocation + eviction/promotion keeps decode latency in budget | aipe ch15 KV-cache management (L94); ch20 integrated paged KV cache (L541) | **PASS** — ch15 validates "eviction + promotion policies keep decode latency within the budget"; ch20 block-wise paged KV cache. Correct. |
| 18 | Nearing OOM makes the framework swap to host and collapses throughput; per-iteration climb is a leak | aipe reference, "Monitor memory usage" (L749–751) | **PASS** — source content (L751) on monitoring memory for swap/leak behavior. Faithful. OOM now expanded on first use. |
| 19 | Flash-style attention, BF16/TF32 on Tensor Cores does the same math faster | aipe ch16 Flash SDP / block-sparse (L135–136) | **PASS** — ch16 `flash_sdp` (1.63x) and `flashinfer_block_sparse` (3.94x); BF16/TF32 Tensor Core paths are standard. Draft wisely keeps these qualitative (no specific deltas quoted) — safe. |
| 20 | Structured sparsity (2:4 pruning) for sparse Tensor Core paths where accuracy survives | aipe reference, "Exploit structured sparsity acceleration" (L783–785) + Global Principles (L277) | **PASS** — verbatim: "2:4 structured sparsity pattern... enable sparse Tensor Core paths... 20%+ extra throughput." Draft keeps it qualitative — safe. |
| 21 | CUDA Graphs / regional compilation cuts per-launch overhead; audit capture is steady-state-only | aipe ch16 regional compilation (L177, L199) | **PASS** — ch16 emits `regional_compilation.steady_state_only=1` "so replay-only timing stays auditable." The "audit that the capture is steady-state-only so you are not timing warmup" caveat is exactly the source's intent. |
| 22 | **Continuous batching: 4.16x target; usually the first scheduling fix** | aipe inference-serving-chapters, ch15 `continuous_batching` (L36) | **PASS** — source table: `continuous_batching` 52.955 ms → 12.719 ms = **4.16x**, "queueing and batching strategy." Exact match. |
| 23 | **Runtime-scheduler fix: 1.78x with no model change** | aipe inference-serving-chapters, ch16 `runtime_scheduler` (L137) | **PASS** — source table: `runtime_scheduler` 112.762 ms → 63.425 ms = **1.78x**, "scheduler/runtime coordination." Exact match; "no model change" matches the source's framing. |
| 24 | Disaggregate prefill/decode when one starves the other (protects TTFT) | aipe ch17 prefill/decode disaggregation (L241, L279) | **PASS** — ch17 `prefill_decode_disagg_ttft` (2.85x, TTFT-focused handoff). Draft keeps it qualitative — safe. |
| 25 | Parallel data loading; default 1–2 loader workers is the hidden bottleneck | aipe reference, "Load data in parallel" (L585–587) | **PASS** — verbatim: "The default of one to two data loader workers may be insufficient." |
| 26 | Pin host memory + overlap H2D copies with compute via separate streams | aipe reference, "Pin host memory for I/O" + "Overlap compute and data transfers" (L589–595) | **PASS** — source verbatim on pinned memory + nonblocking async copies + dedicated streams. |
| 27 | Fast NVMe + async checkpoint/log writes so disk never stalls the loop | aipe reference, "Use fast storage (NVMe/SSD)" + "Overlap checkpointing with compute" (L597–607) | **PASS** — source verbatim. |
| 28 | NUMA affinity: pin GPU process+memory to nearest CPU node, or cross-NUMA can **halve** effective bandwidth | aipe reference, "Design for NUMA awareness" (L495–497) | **PASS** — verbatim: "costly cross-NUMA memory traffic that can halve effective PCIe/NVLink bandwidth." The "halve" figure is exact-to-source. |
| 29 | GPU persistence mode keeps driver warm; avoids re-init latency | aipe reference, "Use the latest NVIDIA driver and CUDA stack" (L511–513) | **PASS** — verbatim: "Enable persistence mode on GPUs at boot (nvidia-smi -pm 1) so the driver stays loaded and GPUs don't incur re-init delays." |
| 30 | MIG partitions a large GPU for many small jobs; MPS for shared-GPU processes; never MIG for tightly-coupled multi-GPU | aipe reference, "Multi-Instance GPU (MIG)" + "Multi-Process Service (MPS)" (L543–551) | **PASS** — verbatim MIG/MPS distinction + "Do not use MIG for tightly coupled parallel jobs." MIG/MPS now expanded on first use. |
| 31 | Keep ECC on; cost is a **few percent**, catches silent corruption that kills a long run | aipe reference, "ECC memory" (L561–563) | **PASS** — verbatim: "performance cost is minimal—on the order of a few percent loss in bandwidth and memory—but ECC catches memory errors." Exact. |
| 32 | Export per-GPU metrics (DCGM → Prometheus/Grafana); alert on anomalies, don't find them in the postmortem | aipe reference, "Automated monitoring and diagnostics" + alerts (L353–355, L767) | **PASS** — verbatim DCGM/Prometheus/Grafana + automated alerts on utilization drops/throttling/ECC. |
| 33 | On Azure, Azure Monitor + Application Insights are the equivalent telemetry sinks | MS Learn (connector) — Azure Monitor / App Insights | **PASS** — Azure Monitor + Application Insights are the standard Azure metrics/telemetry sinks; framed at literacy depth without a specific contested claim. Marker removed; safe. |
| 34 | Operator playbook: keep capability-limited outcomes truthful; skipped/partial not fake-green; root-cause locally, re-run the one target; never disable the profiler | aipe full-sweep-checklist, Operator Checklist (L42–44) | **PASS** — verbatim: "Keep capability-limited outcomes truthful: use `skipped` / `partial`, not fake green." / "Do not disable `nsys` or `ncu`." / root-cause "in the most local correct place," "rerun the affected target directly." All four sub-claims confirmed. |

**Every perf and hardware number in this lesson traces to source and matches exactly.** The two GPU benchmark deltas (6.11x, 5.07x) and the two scheduling deltas (4.16x, 1.78x) are exact-to-table. The NVLink 1.8 TB/s spec is triple-confirmed (aipe + NVIDIA + MS Learn). The "halve bandwidth," "few percent ECC," and "90%/1%" figures are exact-to-source.

## Markers resolved (22 / 22)

All `[verify: ...]` and `[MS-Learn: ...]` markers removed, prose left clean. Grep confirms zero `[verify:` / `[MS-Learn:` / `[FLAG` remain.
- Intro 200-item appendix → removed (claim 1)
- 80/20 ordering → removed (claim 2)
- version control + CI benchmark (2 markers) → removed (claims 3–4)
- hardware-sets-ceiling → removed (claim 5)
- NVLink interconnect figure → removed (claims 7–8)
- kv_cache_nvlink_pool 6.11x → removed (claim 9)
- topology mapping (2 markers) + moe_router_uniform 5.07x → removed (claims 10–11)
- Azure ND/NC SKU `[MS-Learn]` → removed (claim 12)
- goodput + TTFT/TPOT + cloud cost (3 markers) → removed (claims 13–15)
- memory-bound bullets: quantization, place-for-locality, KV management, monitor memory (4 markers) → removed (claims 16–18)
- compute-bound bullets: Flash/sparsity/regional-compilation (3 markers) → removed (claims 19–21)
- scheduling bullets: continuous_batching 4.16x, runtime_scheduler 1.78x, disaggregation (3 markers) → removed (claims 22–24)
- I/O bullets: parallel load, pin/overlap, NVMe/async (3 markers) → removed (claims 25–27)
- host bullets: NUMA, persistence, MIG/MPS, ECC (4 markers) → removed (claims 28–31)
- telemetry: DCGM + Azure Monitor `[MS-Learn]` (2 markers) → removed (claims 32–33)
- operator playbook (4 markers) → removed (claim 34)

## Inference-only confirmation

**PASS.** The curated checklist is inference/platform-relevant, not the training/CUDA antilibrary:
- Memory/compute/scheduling/I/O/host/telemetry sections are all framed for a **serving stack** (decode KV cache, prefill batches, continuous batching, TTFT/TPOT, goodput, serving SLA).
- Hardware items (NVLink pooling, topology, NUMA, MIG/MPS, ECC, persistence) are **operational platform** concerns for running inference on GPU hosts — not kernel authoring or training-pipeline construction.
- 2:4 structured sparsity and BF16/TF32 are framed as "use the better kernel/precision for the hardware" (selection), not "write a CUDA kernel."
- No gradient/optimizer/distributed-training-loop content leaked. The checklist deltas all come from the ch15–20 inference-serving chapters. The ~25-item curation honored the PLAN's "inference-only" mandate; the 200-item appendix is correctly named as antilibrary in the lesson body.

## STYLE pass

**PASS.** One H1 ("# The Production Performance Checklist"). Seam lead grabs and frames the seam ("what you reach for once the measurement points somewhere"). One `## Core concepts` block (4 propositions as claims). Handoff div present, scoped to the lesson-10 audit exercise. Acronyms expanded on first use: NVLink ("NVIDIA's high-bandwidth GPU-to-GPU interconnect"), NVSwitch (glossed), HBM ("high-bandwidth memory, the GPU's on-package DRAM"), KV cache ("key-value cache"), FLOPs ("floating-point operations per second"), MIG ("Multi-Instance GPU"), MPS ("Multi-Process Service"), OOM ("out-of-memory"). TTFT/TPOT written out as "time-to-first-token and time-per-output-token." Second person / present tense / active voice held. Ending lands as a reframe/consequence ("the first one told you where the bodies are and the second one hid them") — not a template ending, not the banned "An AI Platform Engineer who…" opener. The "Respect the reader's stamina" caution (STYLE §8) is honored — the dense checklist is grouped by bound with short glosses rather than a flat 25-item parade.

## Defects fixed

None requiring number correction. Edits during marker removal: expanded acronyms (HBM, NVLink, KV cache, FLOPs, MIG, MPS, OOM) for self-containment; reworded the NVLink figure to attribute it as "the fifth generation of NVLink" + "the reference's headline figure"; added an accurate Azure ND-series parenthetical confirmed via connector. Voice unchanged.

## FLAGGED

**One non-blocking watch-item (claim 8 — "over 14x PCIe Gen5"):** The figure traces to the aipe source and is arithmetically sound (1.8 TB/s ÷ ~128 GB/s PCIe 5.0 x16 ≈ 14x). However, NVIDIA's *current* public marketing attaches the "over 14x" headline to **NVLink 6 vs PCIe Gen6** (the next generation), not NVLink 5 vs Gen5. The claim is defensible as stated and faithful to the cited source, so it is **kept, not corrected**. Watch-item only: if a future pass tightens vendor-spec phrasing, consider softening to "an order of magnitude over a PCIe Gen5 link" to avoid coupling to a specific generation's marketing number. No correction made now — the number is right and sourced.
