# Local Metal — Module 4 Source Provenance

Cited-resource record for Module 4 ("Unified Memory"). Per the authoring directive, every external
resource a lesson cites is captured here as tracked ore: the URL, what it grounds, the source type,
and the retrieval date. The shipped book cites the URLs; this manifest preserves the underlying fact
against link rot. Retrieved 2026-06-21 by the M4 source-fetch tier (three Haiku fetchers) and the
authoring fleet (Sonnet workers + conductor), grounded via official Ollama, llama.cpp, NVIDIA/vendor
specs, model libraries, and corroborating community benchmarks, plus a survey of the local `aipe` ore.

## Layer offload + the GPU/CPU split (Lesson 1: when-a-model-doesnt-fit)

| Fact grounded | Source | Type |
|---|---|---|
| Ollama loads as many layers as fit on the GPU and runs the rest on the CPU (partial offload); `num_gpu` sets GPU layer count | https://github.com/ollama/ollama/blob/main/docs/faq.mdx | Ollama (authoritative) |
| `ollama ps` PROCESSOR column shows the CPU/GPU split (e.g. `100% GPU`, `48%/52% CPU/GPU`) | https://github.com/ollama/ollama/blob/main/docs/faq.mdx | Ollama (authoritative) |
| Ollama's GPU-to-CPU fallback is silent (reduces GPU layers without a warning) | https://github.com/ollama/ollama/issues/14258 | GitHub (ollama issue) |
| Real 52% GPU / 48% CPU split for a 32B Q4 model on a 16 GB card | https://knightli.com/en/2026/04/19/ollama-multiple-gpu-notes/ | community (real `ollama ps`) |
| `qwen2.5-coder:32b` default Q4_K_M ~20 GB on disk | https://ollama.com/library/qwen2.5-coder/tags | Ollama library |
| RTX 4060 Ti GDDR6 bandwidth ~288 GB/s (128-bit, 18 Gbps) | https://www.techpowerup.com/review/nvidia-geforce-rtx-4060-ti-16-gb/ | TechPowerUp (corroborated by NotebookCheck) |
| DDR5-6000 dual-channel ~96 GB/s theoretical (~87 GB/s real) | https://forums.tomshardware.com/threads/how-much-bandwidth-on-ddr5-modules.3883762/ | Tom's Hardware (community) |
| 14B Q4 ~22-34 tok/s on-card; 32B Q4 partial offload ~2-3 tok/s on RTX 4060 Ti | https://modelfit.io/gpu/rtx-4060-ti/ , https://www.hardware-corner.net/gpu-llm-benchmarks/rtx-4060-ti-16gb/ | community benchmarks (representative) |

## Quantization tradeoffs (Lesson 2: quantization-tradeoffs)

| Fact grounded | Source | Type |
|---|---|---|
| Bits/weight: Q4_K_M ~4.89, Q8_0 ~8.50, F16 16.0 | https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md | llama.cpp (authoritative) |
| 32B sizes: Q4_K_M ~20 GB (Ollama), Q8_0 ~30 GB, F16 ~64 GB | https://ollama.com/library/qwen2.5-coder/tags | Ollama library |
| Q4_K_M ~98% of F16 quality (perplexity ~+1%); Q8_0 near-lossless | https://willitrunai.com/blog/quantization-guide-gguf-explained | community benchmark |
| K-quants use mixed precision in 256-weight super-blocks (more bits for attention/output, fewer for feed-forward) | https://www.promptquorum.com/local-llms/llm-quantization-explained | community deep-dive |
| Quantization depth ore (precision benchmark framework) | `vault/ai-performance-engineering/code/ch06/` | local-ore |
| Memory-transfer / bandwidth benchmark ore | `vault/ai-performance-engineering/code/ch02/` | local-ore |

## Measuring latency (Lesson 3: measure-latency)

| Fact grounded | Source | Type |
|---|---|---|
| `/api/generate` timing fields (total_duration, load_duration, prompt_eval_count/duration, eval_count, eval_duration; all nanoseconds) + sample response (290 tokens / 4.709 s ≈ 61.6 tok/s) | https://github.com/ollama/ollama/blob/main/docs/api.md | Ollama (authoritative) |
| Streaming (`"stream": true`) emits newline-delimited JSON chunks; final chunk carries the timing fields | https://docs.ollama.com/api/usage | Ollama (authoritative) |

## Recording the baseline (Lesson 4: record-the-baseline)

| Fact grounded | Source | Type |
|---|---|---|
| Representative on-card vs split tok/s on RTX 4060 Ti (14B ~22-34; 32B split ~2-3) | https://modelfit.io/gpu/rtx-4060-ti/ | community benchmark (representative) |
| tok/s formula from `/api/generate` timing fields | https://github.com/ollama/ollama/blob/main/docs/api.md | Ollama (authoritative) |

## Reference figures (the numbers the lessons quote)

The reference build is the SPEC's Ryzen 7 7700X + 64 GB DDR5-6000 + RTX 4060 Ti 16 GB. Bandwidths
(VRAM ~288 GB/s vs system RAM ~96 GB/s, ~3:1) are vendor/review-sourced; tok/s figures (14B
~22-34 on-card, 32B Q4 ~2-3 split) and the 52% GPU / 48% CPU split are labeled representative in the
lessons, grounded in published community benchmarks because no physical rig exists yet. The reader
measures their own numbers with `bench.py` and records them in `LATENCY.md`; the validator
`check_latency.py` checks completeness and that the measurements are real and positive, not their
exact values.
