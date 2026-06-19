# Module 4 · Performance Engineering — Inference Serving Chapters (ch15–20)

> Source: `code/ch15`–`code/ch20` README files (the inference-serving seam of the book). The training/CUDA/kernel chapters (ch01–14) are antilibrary (see `output/antilibrary.md`).
> Each section: GLM-extracted **key concepts** + **hands-on tasks**, followed by the full chapter README verbatim (collapsible). Code files are not extracted — students use the real chapter code.

## ch15 · Chapter 15 - Disaggregated Inference & KV Management

**Key concepts:** disaggregated prefill/decode, NVLink KV pooling, continuous batching, speculative decoding, MoE serving, guided decoding, KV cache management/eviction
**Hands-on tasks:** benchmark monolithic vs disaggregated inference paths; measure NVLink-pooled KV-cache latency vs local-only; deploy single-GPU and multi-GPU continuous batching schedulers and measure tokens/sec; benchmark speculative decoding orchestration; run deep-dive profiler traces on continuous batching, KV-cache NVLink pool, and speculative decoding targets to attribute gains to scheduling vs cache movement vs decode behavior; validate KV-cache eviction and promotion policies against decode-latency budget; benchmark MoE expert-parallel dispatch and topology-aware routing workloads

<details><summary>Full chapter README (verbatim)</summary>

# Chapter 15 - Disaggregated Inference & KV Management

## Summary
Addresses large-scale inference concerns: disaggregated compute/storage, KV-cache pooling over NVLink, continuous batching, and mixture-of-experts serving patterns. The repo chapter captures the disaggregated serving and KV-management themes directly, while the NIXL-specific connector story from the manuscript is only represented indirectly.

## Problem
Chapter 15 is where inference-system ideas have to justify themselves with end-to-end measurements. The useful question is not "can we disaggregate or batch this?" but "which orchestration changes actually reduce latency or increase throughput once KV movement and scheduling overhead are included?"

## Baseline Path
- monolithic or minimally coordinated inference execution
- straightforward KV management and queue draining
- easy to reason about, but expensive once prefill/decode and cache movement start to dominate

## Optimized Path
- disaggregated prefill/decode and batched scheduling where they help
- NVLink-pooled KV-cache strategies and topology-aware routing
- still measured through the shared benchmark harness, so the chapter is a performance case study instead of a pile of demos

## Measured Delta
Representative validated results from `artifacts/runs/20260303_163946__bench__profile_minimal_targets_20/`:

| Target | Baseline | Optimized | Measured delta | What changed |
| --- | ---: | ---: | ---: | --- |
| `continuous_batching` | `52.955 ms` | `12.719 ms` | `4.16x` | queueing and batching strategy |
| `kv_cache_nvlink_pool` | `1047.860 ms` | `171.477 ms` | `6.11x` | pooled KV-cache path |
| `guided_decoding` | `12.702 ms` | `2.131 ms` | `5.96x` | guided decode path |
| `speculative_decoding` | `103.323 ms` | `26.761 ms` | `3.86x` | speculative decode orchestration |

The chapter mixes system-level wins from queueing/orchestration with fabric/cache-path wins. Those are both valuable, but they are not the same optimization story.

## Profiler Evidence
Use deep-dive harness runs when you want to attribute the gains to scheduling, cache movement, or decode behavior instead of only quoting the runtime delta:

```bash
python -m cli.aisp bench run --targets ch15:continuous_batching --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch15:kv_cache_nvlink_pool --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch15:speculative_decoding --profile deep_dive --single-gpu
```

Those runs are the right place to check whether the win came from less queue idle time, less cache movement, or fewer wasted decode steps.

## Repro Commands
```bash
python -m ch15.compare
python -m cli.aisp bench list-targets --chapter ch15
python -m cli.aisp bench run --targets ch15 --profile minimal
python -m cli.aisp bench run --targets ch15:kv_cache_nvlink_pool --profile deep_dive --single-gpu
```

## Learning Goals
- Benchmark monolithic vs disaggregated inference paths and quantify fabric costs.
- Design KV-cache managers that gracefully span local and remote HBM pools.
- Implement continuous batching and queueing so decode throughput stays high.
- Serve MoE models efficiently by pairing routing with optimized communication.

## Directory Layout
| Path | Description |
| --- | --- |
| `baseline_inference_monolithic.py`, `optimized_inference_monolithic.py` | Single-box inference loops that establish the baseline before disaggregation. |
| `disaggregated_inference_multigpu.py` | Disaggregated inference demo that layers speculative decoding on top of prefill/decode pools. |
| `baseline_single_gpu_kv_handoff.py`, `optimized_single_gpu_kv_handoff.py`, `baseline_disaggregated_inference_multigpu.py`, `optimized_disaggregated_inference_multigpu.py`, `baseline_prefill_decode_disagg.py`, `optimized_prefill_decode_disagg.py`, `baseline_prefill_decode_disagg_multigpu.py`, `optimized_prefill_decode_disagg_multigpu.py`, `disaggregated_inference_single_common.py` | Disaggregated pipelines modeling remote prefills, decode overlap, and NVLink pooling (multi-GPU), plus a supplementary single-GPU KV-handoff comparison pair. |
| `baseline_kv_cache_management.py`, `optimized_kv_cache_management.py`, `kv_cache_management_math.py`, `baseline_kv_cache_nvlink_pool.py`, `optimized_kv_cache_nvlink_pool.py`, `baseline_kv_cache_nvlink_pool_multigpu.py`, `optimized_kv_cache_nvlink_pool_multigpu.py` | KV-cache orchestration utilities with local-only, math-only, and NVLink-pooled variants. |
| `baseline_continuous_batching.py`, `optimized_continuous_batching.py` | Single-GPU continuous batching scheduler for TTFT-aware queueing. |
| `baseline_continuous_batching_multigpu.py`, `optimized_continuous_batching_multigpu.py` | Multi-GPU continuous batching scheduler for scaled queueing throughput. |
| `baseline_moe_inference.py`, `optimized_moe_inference.py` | Inference-specific MoE workloads that pair router load with communication control. |
| `baseline_moe_overlap.py`, `optimized_moe_overlap_shared_expert.py`, `baseline_wide_ep.py`, `optimized_wide_ep.py`, `baseline_moe_dispatch.py`, `optimized_moe_dispatch.py`, `baseline_moe_routing_topology_aware.py`, `optimized_moe_routing_topology_aware.py` | MoE expert-parallel microbenchmarks that now split dispatch-path optimization from topology-aware routing locality so attribution stays clean. |
| `compare.py`, `requirements.txt`, `expectations_{hardware_key}.json`, `Makefile` | Harness entry and dependencies for inference-focused validation. |

## Running the Benchmarks
Use the benchmark harness for quick comparisons or drive the Typer CLI when you need repeatable artifact capture.
```bash
python -m ch15.compare
python -m cli.aisp bench list-targets --chapter ch15
python -m cli.aisp bench run --targets ch15 --profile minimal
```
- Override `--profile` or `--iterations` per workload when capturing Nsight traces.
- Benchmark validity profile defaults to strict. Virtualization is warning-only; use `--validity-profile portable` for broader compatibility on hardware-limited environments.
- Expectation baselines live next to each chapter in `expectations_{hardware_key}.json`; refresh with `--update-expectations` after validating new hardware. In portable mode, add `--allow-portable-expectations-update` to write expectation files explicitly.

## Validation Checklist
- `python -m cli.aisp bench run --targets ch15:disaggregated_inference_multigpu --profile minimal --ncu-replay-mode kernel` shows reduced fabric stalls compared to the baseline while maintaining accuracy parity (kernel replay avoids NCU application-replay stalls on this workload).
- `python optimized_kv_cache_management.py --validate` confirms eviction + promotion policies keep decode latency within the budget.
- `python compare.py --examples continuous_batching` (single GPU) and `python compare.py --examples continuous_batching_multigpu` (multi-GPU) show optimized scheduling increases tokens/sec vs naive queue draining.

## Notes
- `disaggregated_inference_multigpu.py` can run purely in simulation mode; set `--simulate-network` when hardware isn't wired for NVLink pooling.
- Use `torchrun --nproc_per_node <num_gpus>` to run the disaggregated pipeline on the desired GPU count (defaults to all visible GPUs, even count).
- `Makefile` wraps the MPI/UCX targets needed for the multi-node decode experiments.


</details>

## ch16 · Chapter 16 - Production Inference Optimization

**Key concepts:** paged attention, Flash SDP, block-sparse attention, quantization/precision (AWQ, GPTQ, SmoothQuant, FP8), continuous batching/scheduling, NVLink KV pooling (symmetric memory), MoE serving, piecewise graph capture/regional compilation, profiling (Nsight), goodput (TTFT/TPOT), cost-per-token (latency budgets), telemetry/monitoring (DCGM/Prometheus)
**Hands-on tasks:** benchmark Flash SDP vs baseline attention (deploy and measure 1.63x speedup); benchmark FlashInfer block-sparse attention (measure 3.94x delta); benchmark runtime scheduler coordination (measure 1.78x scheduling overhead reduction); benchmark AWQ/GPTQ/SmoothQuant quantized serving variants vs dense reference MLP; validate FP8 transformer-engine serving accuracy; validate NVLink-backed symmetric memory KV replica sync; deploy load-test harness and measure steady-state TTFT/TPOT over 120s; run Nsight deep-dive profiling on attention backend selection and scheduling behavior; run regional compilation target and audit steady-state replay metrics; run DCGM Prometheus exporter for per-GPU telemetry; run cache monitoring for allocator health

<details><summary>Full chapter README (verbatim)</summary>

# Chapter 16 - Production Inference Optimization

## Summary
Focuses on real-world inference services: paged attention, Flash SDP, FP8 serving, telemetry hooks, schedulers, and Blackwell-friendly load-test harnesses.

## Problem
Chapter 16 is where "serving optimization" stops being a collection of tricks and becomes a latency budget. The chapter is most useful when it proves which serving-path changes actually improve steady-state latency, scheduling efficiency, or memory behavior under the shared harness.

## Baseline Path
- straightforward serving loops with conservative attention and scheduling choices
- little or no graph capture, cache-aware staging, or backend specialization
- easier to debug, but usually too expensive for production latency targets

## Optimized Path
- Flash SDP, block-sparse attention, and scheduler-aware execution where they help
- selective graph/compilation techniques for steady-state serving paths
- the same benchmark harness contract as the rest of the repo, so the gains are comparable and reproducible

## Measured Delta
Representative validated results from `artifacts/runs/20260303_163946__bench__profile_minimal_targets_20/`:

| Target | Baseline | Optimized | Measured delta | What changed |
| --- | ---: | ---: | ---: | --- |
| `flash_sdp` | `0.322 ms` | `0.198 ms` | `1.63x` | Flash SDP path |
| `flashinfer_block_sparse` | `0.941 ms` | `0.239 ms` | `3.94x` | block-sparse attention path |
| `runtime_scheduler` | `112.762 ms` | `63.425 ms` | `1.78x` | scheduler/runtime coordination |

The good chapter-level read is "which serving-path changes help enough to matter?" rather than trying to average these into one generic serving number.

## Profiler Evidence
Use deep-dive runs when you want Nsight-backed evidence for backend selection and scheduling behavior:

```bash
python -m cli.aisp bench run --targets ch16:flash_sdp --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch16:flashinfer_block_sparse --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch16:runtime_scheduler --profile deep_dive --single-gpu
```

Those targets answer different questions:
- `flash_sdp`: better attention backend choice
- `flashinfer_block_sparse`: structured sparsity payoff
- `runtime_scheduler`: queueing and scheduling overhead reduction

This chapter now also includes a first-class post-training quantization target family:
- `awq_gptq_smoothquant`: reference dense serving path versus explicit AWQ, GPTQ, and SmoothQuant benchmark variants

## Repro Commands
```bash
python -m ch16.compare
python -m cli.aisp bench list-targets --chapter ch16
python -m cli.aisp bench run --targets ch16 --profile minimal
python -m cli.aisp bench run --targets ch16:flash_sdp --profile deep_dive --single-gpu
```

## Learning Goals
- Profile large decoder workloads to spot hotspots before deploying models.
- Adopt paged attention, Flash SDP, and piecewise compilation to hit latency targets.
- Integrate FP8 quantization, symmetric memory, and cache monitoring in serving loops.
- Simulate production loads (multi-node, MoE) while validating accuracy via perplexity checks.

## Directory Layout
| Path | Description |
| --- | --- |
| `inference_optimizations_blackwell.py`, `inference_profiling.py`, `inference_server_load_test.py`, `inference_serving_multigpu.py` | Top-level orchestration scripts for profiling and load testing multi-GPU inference deployments. |
| `baseline_flash_sdp.py`, `optimized_flash_sdp.py`, `baseline_dense_attention_flash.py`, `optimized_dense_attention_flash.py`, `optimized_dense_attention_flash_blackwell_variant.py` | Attention kernels that compare naive implementations versus Flash backends, including an explicit non-canonical hardware variant for the Blackwell-tagged dense-attention path. |
| `baseline_piece_graphs.py`, `optimized_piece_graphs.py`, `baseline_regional_compilation.py`, `optimized_regional_compilation.py` | Piecewise graph capture and regional compilation for stable low-latency decode, with explicit steady-state replay metrics such as `regional_compilation.capture_ms`, `regional_compilation.graph_bucket_count`, and `regional_compilation.steady_state_only`. |
| `baseline_awq_gptq_smoothquant.py`, `optimized_awq_gptq_smoothquant_awq.py`, `optimized_awq_gptq_smoothquant_gptq.py`, `optimized_awq_gptq_smoothquant_smoothquant.py`, `awq_gptq_smoothquant_benchmarks.py` | First-class post-training quantization benchmark family comparing a dense reference MLP against explicit AWQ, GPTQ, and SmoothQuant serving-style transforms. |
| `fp8_transformer_engine.py`, `test_fp8_quantization_real.py`, `symmetric_memory_inference.py`, `multi_gpu_validation.py` | Serving-time FP8 and symmetric-memory validations to guarantee accuracy and NVLink efficiency. |
| `moe_performance_benchmark.py`, `synthetic_moe_inference_benchmark.py`, `moe_workload.py` | MoE inference harnesses that stress router placement and per-expert batching. |
| `cache_monitoring.py`, `dcgm_prometheus_exporter.py`, `scheduler.py`, `perplexity_eval.py` | Telemetry, scheduling, and accuracy utilities wired into the inference pipeline. |
| `compare.py`, `requirements.txt`, `Makefile`, `expectations_{hardware_key}.json` | Harness entry and dependencies for inference-focused verification. |

## Running the Benchmarks
Use the benchmark harness for quick comparisons or drive the Typer CLI when you need repeatable artifact capture.
```bash
python -m ch16.compare
python -m cli.aisp bench list-targets --chapter ch16
python -m cli.aisp bench run --targets ch16 --profile minimal
```
- Override `--profile` or `--iterations` per workload when capturing Nsight traces.
- Benchmark validity profile defaults to strict. Virtualization is warning-only; use `--validity-profile portable` for broader compatibility on hardware-limited environments.
- Expectation baselines live next to each chapter in `expectations_{hardware_key}.json`; refresh with `--update-expectations` after validating new hardware. In portable mode, add `--allow-portable-expectations-update` to write expectation files explicitly.

## Validation Checklist
- `python optimized_dense_attention_flash.py --profile minimal` yields fewer page faults and improved throughput relative to the baseline script.
- `python symmetric_memory_inference.py --validate` confirms NVLink-backed KV replicas stay in sync with negligible skew.
- `python inference_server_load_test.py --duration 120` exercises the scheduler and should report stable TTFT/TPOT metrics after warm-up.
- `python -m cli.aisp bench run --targets ch16:regional_compilation --profile minimal --single-gpu` should emit `regional_compilation.capture_ms`, `regional_compilation.graph_bucket_count`, and `regional_compilation.steady_state_only=1` so replay-only timing stays auditable.

## Notes
- `dcgm_prometheus_exporter.py` emits per-GPU metrics consumable by Prometheus/Grafana without extra setup.
- `cache_monitoring.py` can be run standalone to sanity-check allocator health between runs.
- `optimized_dense_attention_flash_blackwell_variant.py` is an explicit non-canonical hardware variant of `baseline_dense_attention_flash.py`; keep it out of canonical expectation coverage unless it grows real hardware-specific behavior.


</details>

## ch17 · Chapter 17 - Disaggregated Prefill/Decode & Routing

**Key concepts:** disaggregated prefill/decode, MoE serving, routing, KV cache handoff, TTFT, TPOT, pipeline parallelism, topology-aware routing, profiling, roofline analysis
**Hands-on tasks:** benchmark static vs dynamic routing policies; deploy and measure topology-aware MoE expert routing vs uniform placement; benchmark disaggregated prefill/decode handoff measuring TTFT improvements across overlap, batched, and long-output TPOT variants on multi-GPU; profile routing workloads via deep-dive harness runs and roofline/Nsight captures; run pipeline parallelism benchmarks measuring prefill/decode overlap and idle bubbles

<details><summary>Full chapter README (verbatim)</summary>

# Chapter 17 - Disaggregated Prefill/Decode & Routing

## Summary
Centers the chapter on disaggregated prefill/decode serving, then layers routing and scheduling policies on top so Blackwell clusters can hand work between prefill/decode pools, MoE experts, and pipeline stages without sacrificing utilization.

## Problem
Chapter 17 is where routing and disaggregation ideas stop being whiteboard architecture and start paying rent. The useful question is not "can we route dynamically?" but "which router, queueing, and handoff changes actually improve TTFT, TPOT, or throughput once the full prefill/decode path is measured?"

## Baseline Path
- static or minimally adaptive routing
- conservative prefill/decode handoff with more blocking behavior
- easy to reason about, but expensive once queue imbalance and KV movement dominate

## Optimized Path
- topology-aware or telemetry-aware routing decisions
- disaggregated prefill/decode paths that reduce idle time and handoff overhead
- measured through the shared harness so routing wins are comparable to kernel and memory wins elsewhere in the repo

## Measured Delta
Representative validated results from `artifacts/runs/20260303_163946__bench__profile_minimal_targets_20/`:

| Target | Baseline | Optimized | Measured delta | What changed |
| --- | ---: | ---: | ---: | --- |
| `routing_static` | `5.680 ms` | `0.804 ms` | `7.07x` | smarter routing policy without changing the underlying workload |
| `moe_router_uniform` | `4.719 ms` | `0.931 ms` | `5.07x` | topology-aware expert routing instead of uniform placement |
| `prefill_decode_disagg_ttft` | `2678.148 ms` | `938.237 ms` | `2.85x` | disaggregated prefill/decode handoff optimized for TTFT |

This chapter mixes policy wins with orchestration wins. That is useful, but it means you should read each target as a specific system story rather than as one generic routing number.
Use the `prefill_decode_disagg*` targets as the chapter-native exemplars; `inference_full` remains a comparison pair for model-side work reduction rather than a disaggregated serving benchmark. Its structured metrics now expose `active_layers`, `identity_layers_skipped`, `story.comparison_pair=1`, and `story.chapter_native_exemplar=0`, while structured story metadata points to the `prefill_decode_disagg*` family as the chapter-native exemplar set.

## Profiler Evidence
Use deep-dive harness runs when you want evidence for where the gain came from instead of only the final runtime delta:

```bash
python -m cli.aisp bench run --targets ch17:routing_static --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch17:moe_router_uniform --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch17:prefill_decode_disagg_ttft --profile deep_dive --single-gpu
```

Those three targets answer different questions:
- `routing_static`: policy overhead versus routing quality
- `moe_router_uniform`: topology-aware MoE routing payoff
- `prefill_decode_disagg_ttft`: queueing and handoff behavior in a split prefill/decode system

## Repro Commands
```bash
python -m ch17.compare
python -m cli.aisp bench list-targets --chapter ch17
python -m cli.aisp bench run --targets ch17 --profile minimal
python -m cli.aisp bench run --targets ch17:prefill_decode_disagg_ttft --profile deep_dive --single-gpu
```

## Learning Goals
- Implement dynamic routers that react to TTFT, TPOT, and KV-locality metrics.
- Profile complete inference stacks (prefill + decode) under realistic synthetic loads.
- Blend pipeline parallelism with routing logic for long-context workloads.
- Document profiling steps (roofline, Nsight) specific to the routing lab.

## Directory Layout
| Path | Description |
| --- | --- |
| `baseline_dynamic_routing.py`, `optimized_dynamic_routing.py`, `dynamic_routing.py`, `early_rejection.py` | Routing controllers that evolve from static heuristics to telemetry-driven admission and rejection policies. |
| `baseline_inference_full.py`, `optimized_inference_full.py` | Control pair for full-depth inference versus early-exit pruning. Useful as an end-to-end inference sanity check, but not the chapter's primary disaggregated prefill/decode story. |
| `baseline_prefill_decode_disagg_overlap_multigpu.py`, `optimized_prefill_decode_disagg_overlap_multigpu.py`, `baseline_prefill_decode_disagg_batched_multigpu.py`, `optimized_prefill_decode_disagg_batched_multigpu.py`, `baseline_prefill_decode_disagg_ttft_multigpu.py`, `optimized_prefill_decode_disagg_ttft_multigpu.py`, `baseline_prefill_decode_disagg_tpot_long_multigpu.py`, `optimized_prefill_decode_disagg_tpot_long_multigpu.py` | Chapter-native end-to-end inference flows modeling separate prefill and decode pools, including overlap-focused, batched-handoff, TTFT-focused, and long-output TPOT-focused multi-GPU pairs. |
| `baseline_pipeline_parallelism.py`, `optimized_pipeline_parallelism.py` | Pipeline parallel workloads combining compute and KV-transfer scheduling. |
| `baseline_moe_router_uniform.py`, `optimized_moe_router_uniform_topology.py` | Comparable MoE router benchmark pair contrasting uniform vs topology-aware routing while keeping outputs invariant via shared expert weights. |
| `moe_router_uniform_demo.py`, `moe_router_topology_demo.py` | MoE routing demos (non-benchmark) contrasting uniform vs topology-aware expert selection. |
| `baseline_routing_static.py`, `optimized_routing_static.py` | Router variants for static/dynamic sharding decisions (comparable benchmarks). |
| `baseline_memory.py`, `optimized_memory.py`, `blackwell_profiling_guide.py` | Memory-bound case studies plus profiling guides tailored to routing workloads (use `aisp tools roofline` for roofline analysis). |
| `compare.py`, `Makefile`, `expectations_{hardware_key}.json`, `dynamo_config.yaml` | Harness entry, build rules, expectation baselines, and Dynamo config knobs. |

## Running the Benchmarks
Use the benchmark harness for quick comparisons or drive the Typer CLI when you need repeatable artifact capture.
```bash
python -m ch17.compare
python -m cli.aisp bench list-targets --chapter ch17
python -m cli.aisp bench run --targets ch17 --profile minimal
```
- Override `--profile` or `--iterations` per workload when capturing Nsight traces.
- Benchmark validity profile defaults to strict. Virtualization is warning-only; use `--validity-profile portable` for broader compatibility on hardware-limited environments.
- Expectation baselines live next to each chapter in `expectations_{hardware_key}.json`; refresh with `--update-expectations` after validating new hardware. In portable mode, add `--allow-portable-expectations-update` to write expectation files explicitly.

## Validation Checklist
- `python optimized_dynamic_routing.py --trace` logs TTFT/TPOT trends that settle faster than the baseline's oscillations.
- `python optimized_pipeline_parallelism.py --profile minimal` shows overlapping prefill/decode segments with fewer idle bubbles.
- `python -m cli.aisp tools roofline` reproduces the documented roofline points using your latest captures.

## Notes
- `blackwell_profiling_guide.py` walks through Nsight Systems/Compute captures and interpreting roofline vs occupancy bottlenecks for routing-heavy workloads.
- `baseline_prefill_decode_disagg_overlap_multigpu.py` and `baseline_prefill_decode_disagg_batched_multigpu.py` run via torchrun and default to a 50/50 split when world size is even; override with `--prefill-ranks` (e.g., 2P1D). Use `torchrun --nproc_per_node` to choose the GPU count.
- The disaggregated prefill/decode baselines use per-request blocking handoff with per-request sync/barrier to model naive scheduling; optimized counterparts batch per group or send contiguous KV/seed slabs to overlap or boost throughput.


</details>

## ch18 · Chapter 18 - Advanced Attention & Decoding

**Key concepts:** FlexAttention, speculative decoding, paged attention, KV cache integration, vLLM serving integration, tensor-core attention kernels, decode latency optimization, continuous batching (V1 engine loop), block-table-driven sparse attention, latency/throughput tradeoffs
**Hands-on tasks:** benchmark FlexDecoding baseline vs optimized paths (KV-cache window slicing); measure tensor-core decode kernel speedups; benchmark cache-aware RoPE/Q-path reuse; run speculative decoding config sweeps measuring latency/throughput tradeoffs; compare paged-attention backend selection (dense vs flash) and layout strategies (masked decode vs block-table-driven FlexAttention); validate vLLM V1 serving integration with accuracy parity against native FlexAttention; profile targets with Nsight deep-dive for cache reuse and kernel selection evidence

<details><summary>Full chapter README (verbatim)</summary>

# Chapter 18 - Advanced Attention & Decoding

## Summary
Collects modern decoder techniques-FlexAttention, FlexDecoding, speculative and paged attention workflows-implemented in both PyTorch and CUDA/Triton so you can iterate quickly while validating kernels on real hardware.

## Problem
Chapter 18 is the "does decoder complexity actually buy you anything?" checkpoint. It puts flexible masking, speculative decoding, tensor-core kernels, and serving integration on the same chapter surface so you can see which tricks reduce latency and which ones only add engineering cost.

## Baseline Path
- straightforward FlexAttention / decode execution
- conservative serving integration without aggressive caching or graph replay
- good correctness anchor, but usually too much launch and data-movement overhead

## Optimized Path
- FlexDecoding, tensor-core-specialized kernels, and cache-aware paths
- graph replay and serving-integrated decode paths where they help
- still benchmarked through the shared harness instead of one-off scripts

## Measured Delta
Representative validated results from `artifacts/runs/20260303_163946__bench__profile_minimal_targets_20/`:

| Target | Baseline | Optimized | Measured delta | What changed |
| --- | ---: | ---: | ---: | --- |
| `flexdecoding` | `161.596 ms` | `81.980 ms` | `1.97x` | baseline masks the full KV cache; optimized slices to the active decode window |
| `tensor_cores` | `3.805 ms` | `0.243 ms` | `15.65x` | tensor-core decode kernel |
| `rope_q_cache` | `106.429 ms` | `4.523 ms` | `23.53x` | cache-aware rope/Q-path reuse |

The chapter has a mix of "moderate but real" improvements and "big kernel-level" improvements. Treat those as different stories rather than averaging them together into one headline number. `flexdecoding` is the chapter-native work-reduction story: the baseline scores the full KV cache with a sliding-window mask, while the optimized path trims the decode step down to the active window before attention. Re-measure it on your hardware before treating the chapter numbers as a decision threshold.

## Profiler Evidence
Use deep-dive harness runs when you want Nsight evidence for cache reuse, launch count, and kernel selection:

```bash
python -m cli.aisp bench run --targets ch18:flexdecoding --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch18:tensor_cores --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch18:rope_q_cache --profile deep_dive --single-gpu
```

For serving integration, use the chapter-specific vLLM path only after the direct benchmark targets are clean, because the chapter harness gives you the more trustworthy baseline/optimized comparison.

## Repro Commands
```bash
python -m ch18.compare
python -m cli.aisp bench list-targets --chapter ch18
python -m cli.aisp bench run --targets ch18 --profile minimal
python -m cli.aisp bench run --targets ch18:flexdecoding --profile deep_dive --single-gpu
```

## Learning Goals
- Prototype FlexAttention/FlexDecoding workloads with custom masks, score mods, and KV-cache integration.
- Evaluate speculative decoding pipelines that trade extra compute for lower latency.
- Test tensor-core optimized attention kernels tailored for Blackwell tmem limits.
- Validate integration points with serving frameworks (vLLM) using the provided runners.

## Directory Layout
| Path | Description |
| --- | --- |
| `baseline_flexdecoding.py`, `optimized_flexdecoding.py`, `optimized_flexdecoding_graphs.py`, `v1_engine_loop.py`, `v1_engine_loop_common.py` | FlexDecoding benchmarks plus a V1 polling-loop correctness tool (not a benchmark pair). |
| `baseline_paged_attn_backend.py`, `optimized_paged_attn_backend.py`, `baseline_paged_attn_layout.py`, `optimized_paged_attn_layout.py`, `paged_attn_split_common.py` | Split paged-attention comparisons: dense math-versus-flash backend selection and dense masked decode versus block-table-driven FlexAttention sparse kernels. |
| `baseline_tensor_cores.py`, `optimized_tensor_cores.py`, `flashmla_kernel.cu`, `warp_specialized_triton.py` | Tensor-core attention kernels plus Triton equivalents for rapid validation. |
| `flex_attention_native.py`, `flex_attention_enhanced.py`, `flex_attention_large_model.py`, `kv_cache_integration_example.py` | FlexAttention examples ranging from toy sizes to large models with KV-cache reuse. |
| `baseline_vllm_v1_integration.py`, `optimized_vllm_v1_integration.py`, `baseline_vllm_decode_graphs.py`, `optimized_vllm_decode_graphs.py`, `configs/`, `spec_configs/`, `workload_config.py` | Serving integrations and config presets for pushing workloads through vLLM or custom harnesses. |
| `speculative_decode/spec_config_sweep.py` | Tooling to sweep speculative-decoding configs and summarize latency/throughput tradeoffs. |
| `compare.py`, `expectations_{hardware_key}.json`, `test_flex_attention.py` | Harness entry, regression thresholds, and pytest coverage for FlexAttention APIs. |

## Running the Benchmarks
Use the benchmark harness for quick comparisons or drive the Typer CLI when you need repeatable artifact capture.
```bash
python -m ch18.compare
python -m cli.aisp bench list-targets --chapter ch18
python -m cli.aisp bench run --targets ch18 --profile minimal
```
- Override `--profile` or `--iterations` per workload when capturing Nsight traces.
- Benchmark validity profile defaults to strict. Virtualization is warning-only; use `--validity-profile portable` for broader compatibility on hardware-limited environments.
- Expectation baselines live next to each chapter in `expectations_{hardware_key}.json`; refresh with `--update-expectations` after validating new hardware. In portable mode, add `--allow-portable-expectations-update` to write expectation files explicitly.

## Validation Checklist
- `python -m ch18.compare` runs the chapter baseline/optimized sweep through the shared harness.
- `python -m cli.aisp bench run --targets ch18:vllm_v1_integration --profile minimal` completes with accuracy parity vs the native FlexAttention path.
- `python -m pytest -q ch18/test_flex_attention.py` passes locally, confirming mask/score-mod helpers are wired correctly.

## Notes
- `flex_attention` scripts accept env vars like `BLOCK_SIZE`, `DOC_SPAN`, and `SEQ_LEN` so you can sweep shapes without editing code.
- `flashmla_kernel.cu` includes the Blackwell-specific tensor memory guard to keep compilation healthy on SM121 hardware.
- `paged_attn_backend` isolates SDPA backend choice on a dense layout, while `paged_attn_layout` converts a real per-batch block table into both a dense reference mask and a fused FlexAttention block-mask kernel.


</details>

## ch19 · Chapter 19 - Dynamic & Adaptive Inference Precision/Memory Systems

**Key concepts:** quantization/precision (FP4/FP6/FP8/NVFP4), KV cache quantization, dynamic precision switching, memory double buffering, adaptive memory allocators, MoE serving, KV-cache prefetch/compute overlap, profiling
**Hands-on tasks:** benchmark FP4/FP6/FP8 training and quantization recipes; deploy dynamic quantized cache vs FP32 baseline and measure speedup (1.13x) with GPU peak memory reduction; benchmark memory double-buffering path (1.97x); benchmark MXFP8 MoE path (7.71x); validate token-equivalence of dynamic vs fixed precision decode; profile targets with deep_dive harness to inspect compute vs memory vs allocator gains; run adaptive parallelism routing benchmarks on synthetic request streams

<details><summary>Full chapter README (verbatim)</summary>

# Chapter 19 - Dynamic & Adaptive Inference Precision/Memory Systems

## Summary
Explores dynamic precision, KV-cache quantization, memory double buffering, and adaptive allocators so inference-oriented low-precision experiments stay numerically safe while squeezing every byte of HBM.

## Problem
Chapter 19 is where adaptive precision and memory-system ideas have to prove they are more than paper wins. The useful question is not "can we quantize or double-buffer this?" but "which runtime precision and memory changes improve the real workload enough to justify the added complexity?"

## Baseline Path
- higher-cost cache, precision, and memory-management paths
- simpler allocator and buffering behavior
- cleaner as a reference, but often too expensive in memory traffic or precision budget

## Optimized Path
- quantized caches, lower-precision training/inference paths, and explicit buffering improvements
- adaptive allocator or overlap logic where memory behavior is the actual bottleneck
- benchmarked through the same harness contract so the speedup claims remain comparable and verified

## Measured Delta
Representative validated results from current expectation baselines and recent strict reruns:

| Target | Baseline | Optimized | Measured delta | What changed |
| --- | ---: | ---: | ---: | --- |
| `dynamic_quantized_cache` | `1.710 ms` | `1.517 ms` | `1.13x` | adaptive-bitwidth quantized refresh over the same full-cache footprint, with CPU-side verification output so the optimized path no longer pays a large GPU memory penalty |
| `memory_double_buffering` | `5.536 ms` | `2.809 ms` | `1.97x` | double-buffered memory path |
| `mxfp8_moe` | `16.037 ms` | `2.080 ms` | `7.71x` | lower-precision MoE path with materially better execution behavior |

This chapter is where "low precision" should be read as a systems decision, not just a dtype choice. Some wins come from lower math cost, others from lower memory traffic or better overlap.

`dynamic_quantized_cache` now uses the fair steady-state full-footprint refresh model introduced on `2026-03-17`. Repeated strict reruns on this virtualized host now land around `1.13-1.15x`, and the optimized path's GPU peak memory dropped from the earlier `~765 MB` down to `~269 MB`, below the baseline's `~404 MB`.

## Profiler Evidence
Use deep-dive harness runs when you want to inspect whether the gain came from compute reduction, memory reduction, or allocator/buffering behavior:

```bash
python -m cli.aisp bench run --targets ch19:dynamic_quantized_cache --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch19:memory_double_buffering --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch19:mxfp8_moe --profile deep_dive --single-gpu
```

Those targets make good chapter probes because they cover cache behavior, memory overlap, and lower-precision MoE execution without collapsing everything into one synthetic headline.

## Repro Commands
```bash
python -m ch19.compare
python -m cli.aisp bench list-targets --chapter ch19
python -m cli.aisp bench run --targets ch19 --profile minimal
python -m cli.aisp bench run --targets ch19:dynamic_precision --profile minimal --single-gpu
python -m cli.aisp bench run --targets ch19:mxfp8_moe --profile deep_dive --single-gpu
python -m cli.aisp tools ch19-adaptive-parallelism
python -m cli.aisp tools ch19-dynamic-precision -- --help
python -m cli.aisp tools ch19-dynamic-quantized-cache -- --help
```

## Learning Goals
- Benchmark FP4/FP6/FP8 training loops with calibration and validation hooks.
- Overlap KV-cache prefetch with compute while respecting precision constraints.
- Implement dynamic quantized caches that switch formats mid-run without drift.
- Design allocator helpers to monitor and rebalance fragmented memory pools.

## Directory Layout
| Path | Description |
| --- | --- |
| `baseline_nvfp4_training.py`, `optimized_nvfp4_training.py`, `native_fp4_quantization.py`, `native_fp6_quantization.py`, `native_fp8_training.py` | Training and quantization recipes that switch between FP8 and NVFP4 with automatic calibration. |
| `baseline_adaptive_parallelism.py`, `optimized_adaptive_parallelism.py`, `adaptive_parallelism_benchmark_common.py`, `adaptive_parallelism_strategy.py`, `adaptive_parallelism_worker_pool.py` | Chapter-native adaptive parallelism benchmark pair plus the routing helpers that model tensor/pipeline/hybrid/data worker-pool selection on the same synthetic request stream. |
| `baseline_dynamic_precision.py`, `optimized_dynamic_precision.py`, `dynamic_precision_benchmark_common.py`, `dynamic_precision_switching.py`, `token_precision_switching.py` | Chapter-native dynamic precision benchmark pair plus the confidence-driven precision helpers that keep decode outputs stable while switching precision modes. |
| `baseline_memory_double_buffering.py`, `optimized_memory_double_buffering.py`, `memory_allocator_with_monitoring.py`, `dynamic_memory_allocator.py`, `_allocator_worker.py` | Memory-management helpers covering double buffering, instrumentation, and adaptive worker pools. |
| `baseline_kv_prefetch_overlap.cu`, `optimized_kv_prefetch_overlap.cu`, `kv_prefetch_overlap_sm121` binaries | CUDA kernels proving that quantized KV prefetch can overlap with compute when using cp.async pipelines. |
| `baseline_dynamic_quantized_cache.py`, `optimized_dynamic_quantized_cache.py`, `dynamic_quantized_cache.py`, `token_precision_switching.py`, `dynamic_precision_switching.py` | Cache-refresh experiments comparing full-precision FP32 maintenance against adaptive-bitwidth quantized refresh on the same KV footprint. |
| `baseline_fp4_hardware_kernel.cu`, `optimized_fp4_hardware_kernel.cu`, `fp8_hardware_kernel.cu`, `custom_allocator_retry.py`, `adaptive_parallelism_strategy.py`, `adaptive_parallelism_worker_pool.py` | Hardware-level kernels and adaptive scheduling helpers for heterogeneous precision fleets. |
| `compare.py`, `arch_config.py`, `expectations_{hardware_key}.json` | Harness entry, architecture toggles, and stored expectation data. |

## Running the Benchmarks
Use the benchmark harness for quick comparisons or drive the Typer CLI when you need repeatable artifact capture.
```bash
python -m ch19.compare
python -m cli.aisp bench list-targets --chapter ch19
python -m cli.aisp bench run --targets ch19 --profile minimal
```
- Override `--profile` or `--iterations` per workload when capturing Nsight traces.
- Benchmark validity profile defaults to strict. Virtualization is warning-only; use `--validity-profile portable` for broader compatibility on hardware-limited environments.
- Expectation baselines live next to each chapter in `expectations_{hardware_key}.json`; refresh with `--update-expectations` after validating new hardware. In portable mode, add `--allow-portable-expectations-update` to write expectation files explicitly.

## Validation Checklist
- `python -m ch19.compare` runs the chapter baseline/optimized sweep through the shared harness.
- `python -m cli.aisp bench run --targets ch19:adaptive_parallelism --profile minimal` keeps the baseline Python routing loop and the optimized vectorized routing path output-equivalent on the same request stream.
- `python -m cli.aisp bench run --targets ch19:dynamic_precision --profile minimal --single-gpu` keeps the fixed-precision and dynamic-precision decode outputs token-equivalent on the same prompt stream.
- `python -m cli.aisp bench run --targets ch19:dynamic_quantized_cache --profile minimal` validates the adaptive-bitwidth quantized refresh against the same full-cache FP32 baseline while tracking bounded error.
- `nvcc -o optimized_kv_prefetch_overlap_sm121 optimized_kv_prefetch_overlap.cu` plus the baseline binary show measurable overlap improvements in Nsight Compute.

## Notes
- `arch_config.py` exposes `ENABLE_NVFP4`/`ENABLE_TF32` toggles per device, making it easy to compare precision recipes.
- `validate_quantization_performance.py` aggregates accuracy vs throughput numbers into CSV form for proof-of-benefit reporting.


</details>

## ch20 · Chapter 20 - AI-Assisted Performance Optimization & Case Studies

**Key concepts:** KV cache, paged attention, quantization/precision, profiling
**Hands-on tasks:** deploy and benchmark integrated paged KV-cache end-to-end (naive per-token vs block-wise paged); deploy and benchmark BF16 precision policy on eager MLP graph; run deep-dive profiler to break down gains by subsystem; run AI kernel generator and verifier helpers on CPU at seqlen 512; generate baseline-vs-tuned comparison reports; validate improvements against stored expectation baselines

<details><summary>Full chapter README (verbatim)</summary>

# Chapter 20 - AI-Assisted Performance Optimization & Case Studies

## Summary
Combines AI-assisted kernel exploration with end-to-end case studies: prototype or verify generated kernels, then test whether memory, pipeline, and inference optimizations still hold up once they are composed into a full workload.

## Problem
Chapter 20 is where AI-generated ideas and isolated wins have to survive contact with the full stack. The useful question is not only "did one optimization help in isolation?" but also "can we validate generated or staged optimizations once memory, pipeline, and inference changes are stacked together in one end-to-end workload?"

## Baseline Path
- sequential or minimally optimized end-to-end execution
- independent subsystems with little cross-stage coordination
- useful as a proof baseline, but usually leaves bandwidth and overlap on the table

## Optimized Path
- staged pipeline, memory, and KV-cache optimizations combined into one workload
- the same harness contract as every other chapter, so the end-to-end gains stay comparable to the lower-level chapters
- better for answering whether the optimizations compose cleanly instead of fighting each other

## Measured Delta
Representative validated results:

| Target | Baseline | Optimized | Measured delta | What changed |
| --- | ---: | ---: | ---: | --- |
| `integrated_kv_cache` | `986.812 ms` | `139.676 ms` | `7.07x` | block-wise paged KV-cache integration across the end-to-end loop |
| `bf16_mlp` | `0.616 ms` | `0.234 ms` | `2.63x` | BF16 precision policy on the same eager MLP graph |

The current `integrated_kv_cache` proof point comes from `artifacts/runs/20260328_162954__bench__profile_minimal_targets_ch20_integrated_kv_cache/`. The `bf16_mlp` row remains from `artifacts/runs/20260303_163946__bench__profile_minimal_targets_20/`.

This chapter is the best place to check whether wins compose. `pipeline_sequential` now remains available as an informational overlap demo, while canonical chapter claims focus on the pairs that still hold up as end-to-end improvements. The AI-assisted kernel-generation thread is represented here by `ai_kernel_generator.py` plus the verifier helpers, even though the full manuscript chapter covers a broader RL/AlphaTensor narrative than the current harness surface.

## Profiler Evidence
Use deep-dive harness runs when you want to see how the end-to-end gain breaks down by subsystem:

```bash
python -m cli.aisp bench run --targets ch20:integrated_kv_cache --profile deep_dive --single-gpu
python -m cli.aisp bench run --targets ch20:bf16_mlp --profile deep_dive --single-gpu
```

That is the right place to answer whether the gain came from overlap, memory movement, or simply removing one obvious bottleneck from the baseline.

## Repro Commands
```bash
python -m ch20.compare
python -m cli.aisp bench list-targets --chapter ch20
python -m cli.aisp bench run --targets ch20 --profile minimal
python -m cli.aisp tools ch20-ai-kernel-generator -- --device cpu --seqlen 512
python -m cli.aisp tools ch20-ai-kernel-workflow -- --device cpu --seqlen 512
```

## Learning Goals
- Chain memory, pipeline, and KV-cache optimizations together to see cumulative impact.
- Generate automatic reports that compare baseline vs tuned end-to-end runs.
- Prototype new kernels via the AI kernel generator and slot them into the harness.
- Validate improvements with workload-specific acceptance tests.

## Directory Layout
| Path | Description |
| --- | --- |
| `baseline_bf16_mlp.py`, `optimized_bf16_mlp.py`, `ai_kernel_generator.py`, `core/optimization/inductor_guard.py` | Precision-policy workload plus the shared Inductor cudagraph guard used by the compiled end-to-end paths. |
| `baseline_pipeline_sequential.py`, `optimized_pipeline_sequential.py`, `baseline_end_to_end_bandwidth.py`, `optimized_end_to_end_bandwidth.py` | Pipeline and bandwidth case studies showing how optimizations interact across stages. `pipeline_sequential` currently remains informational after the fairness refresh. |
| `baseline_integrated_kv_cache.py`, `optimized_integrated_kv_cache.py` | Integrated KV-cache demos contrasting naive per-token cache handling with the restored block-wise paged-cache path used by the end-to-end benchmark. |
| `baseline_memory_standard.py`, `optimized_memory_standard.py` | Memory-focused harness verifying allocator changes at system level. |
| `baseline_training_single.py`, `optimized_training_single.py`, `test.cu`, `Makefile` | Single-device training case study plus CUDA kernels used in the final report. |
| `compare.py`, `arch_config.py`, `expectations_{hardware_key}.json` | Harness driver, architecture settings, and expectation baselines. |

## Running the Benchmarks
Use the benchmark harness for quick comparisons or drive the Typer CLI when you need repeatable artifact capture.
```bash
python -m ch20.compare
python -m cli.aisp bench list-targets --chapter ch20
python -m cli.aisp bench run --targets ch20 --profile minimal
```
- Override `--profile` or `--iterations` per workload when capturing Nsight traces.
- Benchmark validity profile defaults to strict. Virtualization is warning-only; use `--validity-profile portable` for broader compatibility on hardware-limited environments.
- Expectation baselines live next to each chapter in `expectations_{hardware_key}.json`; refresh with `--update-expectations` after validating new hardware. In portable mode, add `--allow-portable-expectations-update` to write expectation files explicitly.

## Validation Checklist
- `python -m ch20.compare` emits per-stage summaries that show each optimized variant meeting or exceeding stored expectations.
- `python -m ch20.ai_kernel_generator --emit test.cu` produces CUDA kernels that compile via `nvcc` and integrate into the harness without manual edits.
- `python -m cli.aisp bench run --targets ch20:integrated_kv_cache --profile deep_dive` is the stronger canonical end-to-end paged-cache proof after restoring block-wise processing in the optimized path.

## Notes
- `core/optimization/inductor_guard.py` is the canonical helper for gating Inductor cudagraph features in the compiled chapter 20 paths.
- `ai_kernel_generator.py` logs generated code to `artifacts/` for reproducibility; capture the log with your proof-of-benefit bundle.


</details>
