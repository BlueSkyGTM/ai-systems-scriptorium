# Serving & Inference Optimization

> **Migrated from** `aefs-module4-infrastructure-production` (Ph17, the operate layer) + `aipe-module4-
> inference-serving-chapters` (ch15–20, the measure layer). **Layer them** — same topics, two depths.

The deploy spine:

- **Managed platforms / inference economics → serving-engine selection** — vLLM / SGLang / TensorRT-LLM /
  llama.cpp; pick by workload, not hype.
- **vLLM internals** — paged-attention, continuous batching, chunked prefill (measured: continuous batching
  ~4.16×).
- **Speculative decoding (EAGLE-3) → production quantization** — AWQ / GPTQ / FP8 / NVFP4.
- **Disaggregated prefill/decode → KV-cache management** — LMCache, NVLink KV pooling (measured ~6.11×).
- **Prefix caching (RadixAttention) → multi-region KV locality.**

The `aipe` depth layer measures, profiles, and attributes the same operations (tensor-core decode ~15.65×) —
flash-attention, block-sparse, tensor-core kernels, regional compilation, roofline profiling.

**Inbound:** M1 Docker/Linux/terminal (ops substrate), M1 Rust async (serving layer), M2 production LLM app.
**Relocated artifact:** the speculative-decoding inference server (14) is built here.
