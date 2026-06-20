# Module 5: Deploy & Performance Engineering

The densest concentration of the seam: the infrastructure MLOps engineers and app devs *use*; serving
engines, GPU scheduling, gateways, observability, FinOps, inference performance. **Built, not described.**
Core thesis: **performance engineering > machine learning.** This is the hiring separator; the step that
turns "can call an API" into "can run it in production." The throughline artifact is `module5-serving/`: a
production serving + observability + ops stack each lesson extends, and the Module 6 artifacts later deploy onto.

The fifteen lessons, six chapters:

**Serving & inference optimization (01–03)**; serving engines and engine selection (vLLM/TGI/TensorRT-LLM,
wrapped by FastAPI/Triton/BentoML); inside the engine (continuous batching, paged KV-cache); the optimization
levers (quantization, speculative decoding, disaggregation).

**Metrics, observability & rollout (04–06)**; inference metrics & load testing (TTFT/TPOT/throughput/p99);
safe rollout (shadow/canary/A-B + AI gateways); the **outer loop** of the eval thread; observability &
SRE-for-AI (OpenTelemetry GenAI, Prometheus/Grafana, drift).

**Operations (07–08)**; security & compliance for AI ops (secrets, access, SOC 2 / HIPAA / EU AI Act as
operational requirements); token FinOps & cost optimization (the platform-scale read of Module 4's budget
governor).

**Performance engineering depth (09–10)**; measure before you optimize (profiling, roofline, attribution —
the thesis core); the production performance checklist (topology awareness, the reference distilled).

**Data, experiments & the model lifecycle [lite] (11–13)**; the MLOps-native skills the hiring bar rewards,
brought back at *literacy depth*: data ingestion at production scale (**Docling**, the RAG front door);
experiment tracking & the LLMOps outer loop (MLflow); fine-tuning in proportion (LoRA/QLoRA literacy; when to
fine-tune vs RAG vs prompt). The deep model-training build is out of scope (deferred to a
focused companion).

**Rust (entry) (14–15)**; the second compiled language enters at point-of-use: Rust break-in (ownership,
borrowing) and async Rust for serving (tokio, an inference proxy on the hot path), with Python still the
control plane.

roadmap.sh MLOps front-loads data engineering + model training; this course is **inference-centric** and keeps
model-centric depth at literacy level (deviation D2). **→ The platform the Module 6 artifacts deploy onto.**
