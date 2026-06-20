# VERIFY verdict — M5 L01 · Serving Engines & Engine Selection

**Verifier:** Sonnet VERIFY subagent · **Date:** 2026-06-19
**Verdict:** PASS (edited in place; all markers resolved; no FLAGs)

## Claim ledger

| Claim | Source / check | Result |
|---|---|---|
| vLLM is the general-purpose open-source production default | vLLM docs (WebFetch): "fast and easy-to-use library for LLM inference and serving," SOTA throughput | PASS |
| vLLM runs on NVIDIA and AMD (and CPU) | vLLM docs (WebFetch): "NVIDIA GPUs, AMD GPUs, and x86/ARM/PowerPC CPUs" | FIXED (added "and on CPU" — docs confirm CPU too) |
| vLLM built around PagedAttention + continuous batching | vLLM docs (WebFetch): PagedAttention + "continuous batching, chunked prefill, prefix caching" | PASS |
| TGI was an early default, now maintenance mode; biases toward vLLM/SGLang | TGI repo README (WebFetch) + Lysandre/HF announcement (WebSearch) | PASS |
| TGI entered maintenance mode "late 2025" | WebSearch: HF announcement dated **Dec 11 2025** | FIXED (tightened "late 2025" → "December 2025"; exact date confirmed) |
| TensorRT-LLM is NVIDIA-locked, wins on newest silicon, compiled kernels + low-precision | TRT-LLM docs + support matrix (WebFetch): NVIDIA-only (no AMD), Blackwell/Hopper, FP8/FP4/INT4/INT8 | PASS (added "(FP8, FP4)" + clarified build = compiling to hardware-specific engine) |
| Triton = heavier multi-model, multi-framework host | Triton repo README (WebFetch): "deploy any AI model from multiple DL/ML frameworks: TensorRT, PyTorch, ONNX, OpenVINO…" | PASS (added concrete framework list) |
| BentoML packages model+deps+serving logic into one unit; DX-leaning | BentoML docs (WebFetch): "Unified Inference Platform," build AI systems 10x faster, Python-first | PASS |
| Hardware mapping: CPU→llama.cpp, AMD→vLLM only, newest NVIDIA→TRT-LLM | aefs Ph17 L28 + TRT-LLM support matrix | PASS |
| Traffic pattern: prefix-cache rewards long shared prompts; short unique prompts don't recoup | aefs Ph17 L06 (SGLang/RadixAttention), prompt-template-as-cache-key | PASS |
| Azure ML managed online endpoints host model, provision compute, recover nodes, Azure Monitor metrics, endpoint/deployment split for safe rollout | MS Learn: "Perform safe rollout of new deployments for real-time inference" — blue/green, traffic mirroring/canary, managed online endpoints | PASS (removed "patches the host" — not asserted in the cited doc; replaced with confirmed blue/green framing) |
| Azure OpenAI deployment types: standard pay-per-token / provisioned-throughput (guaranteed capacity+latency) / batch (bulk) | MS Learn: Foundry deployment-types table (Standard pay-per-token; Provisioned per-PTU, defined latency SLA; Batch discounted async) | PASS (added "discounted" to batch — confirmed 50% discount) |

## Markers resolved
All 5 `[verify:…]` and 2 `[MS-Learn:…]` markers removed → clean student-facing prose. No markers remain (grep clean).

## Perf numbers
No standalone perf numbers in L01 (engine-selection lesson). Hardware/precision claims confirmed against vendor docs.

## "Layer two depths, don't dedup"
L01 is the aefs **operate-depth** framing (engine selection, L28). Internals/measure-depth deliberately deferred to L02. No collapse. Preserved.

## STYLE result
- H1: one. Lead: 2 sentences, thesis + seam stake, no throat-clearing — PASS.
- One `## Core concepts` (4 props) before handoff — PASS.
- claude-handoff div present, correct exercise path — PASS.
- Ending: reframe ("the module in miniature: measure the workload, then choose") — not a template, not the banned "An AI Platform Engineer who…" opener — PASS.
- Acronyms: FIXED — glossed "service-level objective (SLO)" on first use. "inference serving engine" bolded on intro. HTTP/p99/GPU standard.
- Voice: second person, present tense, blunt — PASS.

## Verdict
**PASS.** Every vendor and Azure claim independently confirmed. Two factual tightenings (TGI date; "patches the host" removed). No unverifiable claims; no FLAGs.
