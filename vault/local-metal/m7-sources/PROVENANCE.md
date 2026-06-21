# Local Metal — Module 7 Source Provenance

Cited-resource record for Module 7 ("Perf and Tuning"), the final module. Per the authoring directive,
every external resource a lesson cites is captured here as tracked ore: the URL, what it grounds, the
source type, and the retrieval date. The shipped book cites the URLs; this manifest preserves the
underlying fact against link rot. Retrieved 2026-06-21 by the M7 source-fetch tier (three Haiku
fetchers, one of them a local `aipe` ore survey) and the authoring fleet (Sonnet workers + conductor),
grounded via official Ollama + NVIDIA docs, reputable benchmarks, and the local AI-performance ore.

## GPU profiling (Lesson 1: where-the-time-goes)

| Fact grounded | Source | Type |
|---|---|---|
| `nvidia-smi dmon -s um` streams `sm%` (compute) + `mem%` (memory) per second; `-s pum` adds power | https://docs.nvidia.com/deploy/nvidia-smi/index.html | NVIDIA (authoritative) |
| LLM generation is memory-bandwidth-bound: each token reads the full weights from VRAM for a small matrix-by-vector op | https://www.baseten.co/blog/llm-transformer-inference-guide/ | engineering blog |
| Bandwidth-bound signature: high `mem%` (70-90%) with `sm%` not pegged (30-60%) | https://medium.com/@arjunravi726/why-llm-inference-is-memory-bound-not-compute-bound-ba59c48739e0 | community |
| RTX 4060 Ti tok/s (8B ~34, 14B ~22-23); 288 GB/s bandwidth limit (128-bit bus) | https://www.hardware-corner.net/gpu-ranking-local-llm/ | community benchmark (representative) |
| VRAM headroom / above ~95% triggers CPU offload cliff | https://sergiiob.dev/posts/gpu-vram-cpu-offload-llama-cpp-deep-dive/ | community |

## The tuning levers (Lesson 2: the-tuning-levers)

| Fact grounded | Source | Type |
|---|---|---|
| `OLLAMA_FLASH_ATTENTION=1` enables flash attention (memory-efficient attention, modest single-stream speedup, prerequisite for KV-cache quant) | https://github.com/ollama/ollama/blob/main/docs/faq.mdx | Ollama (authoritative) |
| `OLLAMA_KV_CACHE_TYPE` f16/q8_0/q4_0 (q8_0 ~1/2, q4_0 ~1/4 KV-cache VRAM; mainly a VRAM/context win; needs flash attention) | https://github.com/ollama/ollama/blob/main/docs/faq.mdx | Ollama (authoritative) |
| `OLLAMA_NUM_PARALLEL` (default 1) sets concurrent requests; raises aggregate throughput under load; scales VRAM by N x context | https://github.com/ollama/ollama/blob/main/envconfig/config.go | Ollama (source) |
| `num_ctx` / `OLLAMA_CONTEXT_LENGTH` sets the window (more context = more KV-cache VRAM); `OLLAMA_KEEP_ALIVE` controls model unload delay | https://docs.ollama.com/faq | Ollama (authoritative) |
| Flash attention speedup scales with memory bandwidth (2.5-4.5x on RTX 3090; modest on a 4060 Ti) | https://github.com/dao-ailab/flash-attention | flash-attention repo |

## Throughput under load + recording (Lessons 3-4: throughput-under-load, record-the-tuning)

| Fact grounded | Source | Type |
|---|---|---|
| `/api/generate` `eval_count` timing field (basis for tok/s aggregation) | https://github.com/ollama/ollama/blob/main/docs/api.md | Ollama (authoritative) |
| `OLLAMA_NUM_PARALLEL` is the headline before/after lever (aggregate throughput under concurrency) | https://github.com/ollama/ollama/blob/main/envconfig/config.go | Ollama (source) |

## aipe ore (local depth references)

| Repo-relative path | Covers |
|---|---|
| vault/ai-performance-engineering/code/ch15/ | KV-cache management, continuous batching, throughput-under-load patterns (baseline/optimized) |
| vault/ai-performance-engineering/code/ch16/ | Production inference optimization: paged/flash attention, quantization (AWQ/GPTQ/SmoothQuant), telemetry |
| vault/ai-performance-engineering/code/ch19/ | KV-cache quantization, dynamic precision, bandwidth-vs-compute analysis |
| vault/ai-performance-engineering/code/docs/gb300-sol-roofline.md | Roofline / bandwidth-vs-compute saturation analysis |
| vault/ai-performance-engineering/code/docs/tooling-and-profiling.md | Nsight/Nsys profiler commands and key metrics |

## Reference figures (the numbers the lessons quote)

The before/after in `TUNING.md` is representative: baseline aggregate ~30 tok/s (single stream, stock,
from the M4 baseline) vs tuned aggregate ~64 tok/s with `OLLAMA_NUM_PARALLEL=4` plus flash attention
and a q8_0 KV cache. The ~2x aggregate gain reflects concurrent batching amortizing the shared weight
read on a bandwidth-bound card (not a 4x scaling, which the bandwidth ceiling forbids). All hardware
figures are labeled representative; the reader measures their own with `bench.py`/`loadbench.py` and
records them. The `check_tuning.py` gate asserts the tuned number is at least the baseline (a proven,
non-regressing change), not a specific value.
