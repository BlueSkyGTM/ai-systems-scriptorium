# Exercise 04 — Inference Metrics & Load Testing

## Goal

Add a metrics middleware to `module5-serving/` that records TTFT, TPOT, and throughput per request and reports p50/p90/p99 plus goodput against a declared SLO, then write a local load-test script that drives the endpoint under varied-length prompts in steady, ramp, and spike shapes and finds the concurrency where goodput collapses.

## Why

A serving endpoint that streams beautifully for one request can fall over at fifty, and the mean latency will never show it. You measure TTFT, TPOT, and goodput under realistic concurrency so you size the fleet on evidence, not the model card — the production-performance half of the eval discipline.

## Steps

1. **Metrics middleware.** Add `module5-serving/metrics/recorder.py` with a `RequestMetrics` recorder that wraps a streaming response and captures, per request: TTFT (time from request start to first token), TPOT (mean gap between subsequent tokens), total output tokens, and end-to-end latency. Keep it stdlib — a `time.perf_counter()` around the token stream is enough. The serving endpoint stays local; mock the token stream with a generator that yields tokens on a small sleep so the numbers are real but no GPU is needed.

2. **Percentiles, not means.** Aggregate recorded requests into p50/p90/p99 for TTFT, TPOT, and end-to-end. Do not report a mean as the headline — LLM latency is right-skewed, so the percentile view is the contract.

3. **Goodput against an SLO.** Declare an SLO in config (e.g. `ttft_p99_ms`, `e2e_p99_ms`). Compute goodput as the fraction of requests that met *every* SLO constraint at once. Print throughput (total output tokens per wall-clock second) beside it so the throughput-vs-goodput trade is visible.

4. **Local load-test script.** Add `module5-serving/loadtest/run.py` that drives the endpoint at a configurable concurrency. Generate prompts with varied input length (a mean and a standard deviation) — never a single repeated prompt, or you measure one lucky point on the prefix cache. Tokenize off the request-generation path (or skip client-side tokenization entirely) so the client is not the bottleneck.

5. **Four shapes, three required.** Implement at least steady, ramp, and spike load profiles. Steady finds the sustainable goodput ceiling; ramp walks concurrency up until the percentiles break; spike jumps concurrency to test reaction. (Soak — hours at moderate load — is the stretch.)

6. **Find the cliff.** Run the ramp and print the concurrency level at which goodput drops below the SLO. That number is the deliverable — it sizes the fleet and sets the autoscaling trigger.

## Done when

- The middleware records TTFT, TPOT, throughput, and end-to-end latency per request and reports p50/p90/p99 — no mean as the headline metric.
- Goodput is computed against a multi-constraint SLO and printed beside throughput, so the trade between them is legible.
- The load-test script drives steady, ramp, and spike shapes with varied-length prompts, and prints the concurrency at which goodput collapses.
- It runs locally with a mocked token stream — no cloud endpoint, no GPU, no API key.

## Stretch

Add a soak profile (sustained moderate load over a long run) and track resident memory per N requests to surface a leak that only appears after the thousandth request. Plot TTFT p99 against concurrency so the cliff is visible, not just printed.
