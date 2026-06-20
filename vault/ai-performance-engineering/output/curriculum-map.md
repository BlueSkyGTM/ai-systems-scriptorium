# AI Performance Engineering — Curriculum Map

> Inference-serving subset of an O'Reilly GPU-performance book. Maps to Module 4. Training/CUDA chapters are antilibrary.

## Overview

| Module 4 Section | Source | Output file |
|---|---|---|
| Inference Serving Chapters | `code/ch15–ch20` READMEs | `output/content/module4-inference-serving-chapters.md` |
| Inference Reference Docs | `docs/*.md` | `output/content/module4-inference-reference-docs.md` |
| Production Checklist (Full Sweep) | `code/FULL_SWEEP.md` | `output/content/module4-full-sweep-checklist.md` |
| Antilibrary (Training / CUDA / Kernels) | `code/ch01–ch14` | `output/antilibrary.md` |

## Routing Notes

- **KEEP = ch15–20** (inference serving: disaggregation, KV management, prefill/decode routing, attention/decoding, adaptive precision, case studies). All kept content maps to Module 4 sections.
- **ANTILIBRARY = ch01–14** (training, CUDA, kernels). Routed to `output/antilibrary.md`. These chapters cover training performance, CUDA kernel authoring, and low-level GPU programming — outside the inference-serving seam.
- Students **deploy and benchmark** inference servers (vLLM, SGLang, TensorRT-LLM); they do **not** write GPU kernels.
- Focus metrics: cost/token, throughput/dollar, latency, KV cache efficiency.
- Core topics within kept chapters: paged attention, KV cache management, prefill/decode disaggregation, continuous batching, speculative decoding, adaptive precision, and inference profiling.
- **No visuals**: no image references and no Mermaid diagrams in kept content. Structured markdown and tables only.
- Be faithful to source material. No opinions.
