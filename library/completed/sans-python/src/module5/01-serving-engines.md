# Serving engines & engine selection

You spent four modules making the model *reason* well. This module is about making it *run* — fast, cheap, and under load — and the skill that decides whether you can is performance engineering, not machine learning.

That is the thesis of Module 5, and it surprises people. The hard, hireable problem in production AI is rarely "train a better model." It is "serve this model to ten thousand concurrent users at a latency they'll tolerate and a cost the business will sign off on." That is a systems problem — queueing, memory, batching, scheduling — wearing a machine-learning costume. The model is a given; the engineering is yours.

## Why this lands at the seam

This is the part of the job an AI Engineer and an MLOps engineer both reach for and neither fully owns. The AI Engineer asks "which model, which prompt, which decoding settings?" The MLOps engineer asks "how many GPUs, what autoscaling, what service-level objective (SLO)?" The serving engine is where those two questions collide into one artifact, and the platform engineer is the person who picks it, wires it, and answers for its p99. Module 5 is the seam's home turf — the infrastructure both halves *use*. Get the engine choice wrong and no amount of prompt tuning saves the latency.

## Inference infrastructure is not training infrastructure

Start by unlearning a reflex. The stack that *trains* a model — data-parallel clusters, gradient all-reduce, checkpoints measured in terabytes, jobs that run for days — has almost nothing to do with the stack that *serves* it. Training is a throughput job you run a few times; serving is a latency job you run forever. They optimize different things, fail in different ways, and run on different software.

The training rigs, the CUDA kernels, the optimizer math — that depth is real, and it lives in the antilibrary. It is not on the road to this job. What is on the road is the serving layer: the program that holds the model weights in GPU memory, accepts requests over HTTP, batches them, and streams tokens back. That program is an **inference serving engine**, and choosing one is the first real decision of the module.

## The engines you choose between

Three engines dominate self-hosted large-language-model serving, and they split by who built them and what they optimize.

**vLLM** is the general-purpose production default — open source, hardware-broad (runs on NVIDIA and AMD, and on CPU), and built around PagedAttention and continuous batching (the next lesson is its internals). When you have no special constraint, you reach for vLLM.

**Text Generation Inference (TGI)**, Hugging Face's server, was an early default and still ships, but it entered maintenance mode in December 2025 — which makes it a risky long-term bet and biases new projects toward vLLM or its prefix-cache-specialist cousin SGLang.

**TensorRT-LLM** is NVIDIA's engine. It is locked to NVIDIA hardware and wins on the newest silicon, where its compiled engines and low-precision formats (FP8, FP4) extract throughput the portable engines can't reach. You pay for that with portability: a TensorRT-LLM deployment cannot move to AMD, and the build step — compiling the model into a hardware-specific engine — is heavier.

These are *engines*. In production you rarely run an engine bare — you wrap it in a server that gives you HTTP, health checks, and batching policy. **FastAPI with Uvicorn** is the thin custom wrapper when you want full control of the request surface. **Triton Inference Server** (NVIDIA) is the heavier multi-model, multi-framework host — it serves models from TensorRT, PyTorch, ONNX, and more behind one endpoint. **BentoML** packages the model, dependencies, and serving logic into one deployable unit and leans toward developer experience. The engine does the inference; the wrapper does the operations.

## Pick by workload, not by hype

There is no "best" engine. There is the engine that fits *this* workload, and the workload has a shape: hardware, scale, latency target, and traffic pattern.

The hardware is the first forcing function. CPU-only or laptop-edge sends you to `llama.cpp`. AMD or any non-NVIDIA accelerator rules out TensorRT-LLM and leaves vLLM. The newest NVIDIA datacenter silicon makes TensorRT-LLM the throughput leader — if you can accept the lock-in.

The traffic pattern is the second. A workload with long, shared system prompts — retrieval-augmented generation, multi-turn agents — rewards an engine built around prefix caching. A workload of short, unique prompts does not, and the prefix-cache machinery is overhead you don't recoup. You measure your traffic before you choose, because the engine that wins on one shape loses on the other.

On Azure, you may not run the engine at all. **Azure Machine Learning managed online endpoints** host the model for you: you specify the virtual-machine SKU and the scale settings, and the platform provisions the compute, recovers failed nodes, and wires latency and monitoring metrics into Azure Monitor. You trade the knobs of a self-hosted engine for turnkey operations and an endpoint-versus-deployment split that makes safe rollout a first-class feature — a blue/green deployment that takes a slice of traffic before it takes all of it. For Azure's own and partner models, **Azure OpenAI** removes even the SKU choice — you pick a *deployment type* (standard pay-per-token, provisioned-throughput for guaranteed capacity and latency, or batch for discounted bulk) and the workload shape picks for you.

The decision, then, is one question asked four times — what hardware, what scale, what latency, what traffic — and the engine falls out of the answers. That discipline is the module in miniature: measure the workload, then choose; never the reverse.

## Core concepts

- The production AI problem is performance engineering, not machine learning — serving a fixed model fast, cheap, and under load is a systems problem (queueing, memory, batching), and that is the hireable skill Module 5 teaches.
- Inference infrastructure is not training infrastructure: serving is a latency job that runs forever, training is a throughput job that runs a few times; they use different software and fail in different ways.
- Three engines dominate self-hosted serving — vLLM (portable production default), TGI (early default, now maintenance-mode and a fading bet), TensorRT-LLM (NVIDIA-locked, fastest on the newest silicon) — wrapped by FastAPI/Uvicorn, Triton, or BentoML for the operational surface.
- You pick an engine by workload shape — hardware, scale, latency target, traffic pattern — not by hype; on Azure, managed online endpoints and Azure OpenAI deployment types make that choice a platform setting instead of an engine you operate.

<div class="claude-handoff" data-exercise="exercises/module5/01-serving-engines/">

**Build It in Claude Code** — stand up `module5-serving/`: a local mock serving engine behind a FastAPI endpoint, plus an `engine_selector` that takes a workload profile (hardware, scale, latency target, traffic shape) and returns a recommended engine with a reason. No GPU, no model weights — the engine is a stub that simulates token generation so the whole stack runs offline. This is the throughline every later Module 5 lesson extends.

</div>
