# Module 5 Serving Stack — the `module5-serving/` substrate

This is the starter every Module 5 exercise builds on. Lesson 01 seeds it; copy it to `module5-serving/`
and extend it lesson by lesson into a production serving + observability + ops stack — the same artifact the
Module 6 deployment exercises later run on top of. It is deliberately minimal: a starter, not a finished
system.

## What lesson 01 seeds

```
_serving/
├── README.md           (you are here)
├── app.py              FastAPI app: one /generate endpoint over a mock engine, streams tokens
├── engine.py           MockEngine — simulates token generation with a latency model (no GPU, no weights)
├── engine_selector.py  takes a WorkloadProfile, returns a recommended engine + reason
└── profiles.py         a few WorkloadProfile fixtures (edge-CPU, AMD-datacenter, NVIDIA-newest, RAG-heavy)
```

## Design

- **No GPU, no cloud, no model weights.** The engine is a stub. It does not run attention; it *simulates*
  token generation with a latency model — a fixed prefill cost plus a per-token decode cost — so the whole
  stack runs offline on any laptop. Every later exercise measures *simulated* TTFT, TPOT, and throughput,
  never real inference. The point is the systems behavior, which the simulation reproduces faithfully; the
  GPU math is on the *Avec Python* path and out of scope here.
- **Control plane is Python.** The FastAPI app, the selector, and the latency model are plain Python. This is
  the everything-as-code stance the module teaches — you own the request surface and the scheduling policy.
- **The engine is swappable.** `engine.py` exposes the same interface a real vLLM/TGI/TensorRT-LLM client
  would: submit a request, get streamed tokens, read metrics. Swap the mock for a real engine later and the
  app, the scheduler, and the metrics layer don't change shape.

## Run it

```bash
uvicorn app:app --reload
# then, in another shell:
curl -N -X POST localhost:8000/generate -d '{"prompt": "hello", "max_tokens": 32}'
```

The endpoint streams simulated tokens with a realistic TTFT pause before the first one. `engine_selector.py`
can be run standalone against the fixtures in `profiles.py` to print an engine recommendation per workload.

## What later lessons add (on top of this, not instead of it)

This substrate is the floor. Each Module 5 lesson bolts one layer on:

- **Lesson 02** — a continuous-batching scheduler and a paged KV-cache allocator (both simulated) replace the
  naive one-request-at-a-time handler; measure the throughput gain over static batching.
- **Lesson 03** — an optimization layer simulating quantization, speculative decoding, and disaggregated
  prefill/decode, each with the regime where it turns net-negative.
- **Later (Metrics, Rollout, Ops chapters)** — TTFT/TPOT/p99 instrumentation and load testing, shadow/canary
  rollout behind an AI gateway, OpenTelemetry traces and dashboards, token FinOps and quotas, the Docling
  ingestion front door, and a Rust async proxy in front of the engine.

Keep the stack coherent as it grows: every layer is something the next lesson assumes is already there. By
the end of the module, `module5-serving/` is a serving platform you could point a real engine at — and the
Module 6 artifacts deploy onto exactly this shape.
