# Module 5 — Deploy & Performance Engineering

The densest concentration of the seam: the infrastructure MLOps engineers and app devs *use* — serving
engines, GPU scheduling, gateways, observability, finops, inference performance. **Built, not described** —
every concept has a hands-on counterpart. Core thesis: **performance engineering > machine learning.**

Chapters:

1. **Serving & Inference Optimization** — engine selection, vLLM internals, speculative decoding,
   quantization, disaggregation, KV-cache management.
2. **Metrics, Observability & Rollout** — the eval thread's outer loop: inference metrics, load testing,
   shadow/canary/A-B, AI gateways, SRE-for-AI.
3. **Operations: Security, Compliance, FinOps** — secrets, compliance (SOC2/HIPAA/EU-AI-Act), token finops,
   cost optimization.
4. **Performance Engineering Depth** — profiling, roofline, NVLink topology, the 200-item checklist.
5. **Rust (entry)** — the ownership on-ramp + async serving, at the serving layer.

roadmap.sh MLOps front-loads data engineering + model training; **Northstar is inference-centric and defers
ops to here** (deviation D2). Model-centric MLOps (training pipelines) and `aipe` training/CUDA are in the
[Antilibrary](../antilibrary.md). Relocated Deploy artifacts (11 observability, 13 MCP governance, 14
inference server, 07 fine-tune pipeline) live here.
