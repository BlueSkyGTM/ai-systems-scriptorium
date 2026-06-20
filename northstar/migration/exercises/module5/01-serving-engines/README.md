# Exercise 01 — Serving Engines & Engine Selection

## Goal

Stand up `module5-serving/` from the `_serving/` starter: a local mock inference engine behind a FastAPI `/generate` endpoint that streams simulated tokens, plus an `engine_selector` that turns a workload profile into a recommended serving engine with a reason. No GPU, no model weights — everything runs offline.

## Why

The first real decision of production serving is which engine to run, and it is made by workload shape — hardware, scale, latency, traffic — not by hype. This exercise builds the substrate every later Module 5 lesson extends, and encodes the selection logic as code you can diff instead of a vibe you defend in a meeting.

## Steps

1. **Create the artifact.** Make `module5-serving/` and copy the `_serving/` starter into it. All Module 5 exercises extend this directory.

2. **Mock engine.** Implement `engine.py` with a `MockEngine` that simulates generation — never runs a real model. Give it a latency model: a fixed `prefill_ms` (a function of prompt length) plus a per-token `decode_ms`. `generate(prompt, max_tokens)` yields one simulated token at a time, sleeping the decode interval between tokens and the prefill interval before the first, so a caller observes a realistic time to first token (TTFT). Expose a metrics hook that records TTFT and total tokens per request.

3. **FastAPI surface.** Implement `app.py` with a single `POST /generate` endpoint that streams the engine's tokens back (a streaming response). Add a `GET /healthz`. Keep the control plane plain Python — no agent or serving framework beyond FastAPI/Uvicorn.

4. **Engine selector.** Implement `engine_selector.py`: a `WorkloadProfile` (hardware, scale, latency target, traffic shape) and a `select_engine(profile) -> (engine, reason)` that applies the lesson's forcing functions — CPU/edge → `llama.cpp`; AMD/non-NVIDIA → vLLM (TensorRT-LLM ruled out); newest NVIDIA + throughput-first → TensorRT-LLM; prefix-heavy RAG/agent traffic → a prefix-cache specialist; otherwise → vLLM as the default. Return the reason string, not just the name.

5. **Profiles + run.** Fill `profiles.py` with the four fixtures (edge-CPU, AMD-datacenter, NVIDIA-newest throughput, RAG-heavy) and print the recommendation for each. Start the server and stream a generation to see the simulated TTFT pause.

## Done when

- `module5-serving/` exists with `app.py`, `engine.py`, `engine_selector.py`, and `profiles.py`.
- `uvicorn app:app` serves `POST /generate`, which streams simulated tokens with a visible TTFT delay before the first token, and `GET /healthz` returns ok.
- `python engine_selector.py` prints a recommended engine **and a reason** for each of the four profiles, and the AMD profile never returns TensorRT-LLM.
- Nothing imports a real model or requires a GPU — the engine is a stub and the stack runs on a laptop.

## Stretch

Add a `--traffic` flag that fires N concurrent simulated requests at `/generate` and reports aggregate throughput (tokens/sec) and the per-request TTFT distribution (p50/p99). This becomes the load-generation seed the metrics lesson builds on.
