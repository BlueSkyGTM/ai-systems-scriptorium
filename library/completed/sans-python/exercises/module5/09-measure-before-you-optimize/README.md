# Exercise 09 — Measure Before You Optimize: Profile, Attribute, Fix

## Goal

Instrument `module5-serving/` with phase timers, run a profiling pass against a synthetic load, attribute the dominant cost from the timeline alone, apply the one fix that targets the real limiter, measure the before/after delta in throughput and latency, and then prove that a *wrong* fix — optimizing a path that was never the bottleneck — buys nothing.

## Why

An optimization applied to the wrong bound is negative work: added complexity, no speedup. The Production AI Engineer earns the right to change code by profiling first — naming the limiter from evidence, not the reflex. This exercise makes that discipline runnable: the bottleneck is planted, and you must find it from the profile before you touch it.

## Steps

1. **Phase timers.** Add `module5-serving/profiling/phases.py` with a lightweight phase-timer context manager (stdlib `time.perf_counter()` — no external profiler, no GPU). Wrap the serving path so every request records named spans: `input_staging`, `queue_wait`, `prefill`, `decode`. Emit a per-phase breakdown (total time, share of wall-clock) the way an Nsight Systems timeline names phases — this is your "systems-level" view.

2. **Plant a bottleneck.** Make the mock serving layer drain its request queue one request at a time — a serialized handoff that holds each request in `queue_wait` while the "GPU" (the mock engine) sits idle. The decode path itself is already fast; the time is lost upstream. Do not label the bottleneck in the output — it must be discoverable only from the phase breakdown.

3. **Profiling pass.** Add `module5-serving/profiling/run_profile.py` that drives the endpoint with a synthetic load (a batch of concurrent requests with varied prompt/output lengths, fixed seed so runs are aligned) and prints the phase breakdown plus throughput (tokens/sec) and latency (p50/p99 end-to-end). Warm up first, then measure the steady state — discard the first iteration so compile/cache-fill noise never lands in the number.

4. **Attribute from the timeline.** From the breakdown alone, identify which phase owns the wall-clock. Write the attribution as a one-line claim in the script output: e.g. `LIMITER: queue_wait owns 78% of wall-clock — feeding problem, not a kernel problem.` The point is that the profile, not a guess, names the bound.

5. **The right fix.** Replace the serialized drain with continuous-style batching (process ready requests together instead of one at a time). Re-run the *same* aligned load. Print the before/after delta in both throughput and latency, side by side. Throughput should rise and tail latency should fall because the queue stops starving the engine.

6. **The wrong fix.** Take a non-bottleneck path — the already-idle decode/compute step — and "optimize" it (e.g. simulate a quantization speedup that lowers per-token decode cost). Re-run the same load. Show that end-to-end throughput and latency barely move, because decode was never the limiter. Print both deltas together so the contrast is undeniable: the right fix moved the number, the wrong fix did not.

## Done when

- The profiling run prints a per-phase breakdown (`input_staging`, `queue_wait`, `prefill`, `decode`) with each phase's share of wall-clock, against an aligned, warmed-up, steady-state synthetic load.
- The script names the limiter from the breakdown alone — the planted bottleneck is attributed, not labeled in advance.
- The right fix (batching the serialized drain) shows a measured throughput gain and tail-latency drop on the same load.
- The wrong fix (speeding up the idle decode path) shows a near-zero end-to-end delta, proving an optimization off the bottleneck buys nothing.
- It runs locally — no GPU, no cloud, no real model. Every number is simulated by the latency model, but the systems behavior (queue starvation, the gain from batching) is real.

## Stretch

Add a second planted bottleneck in a different phase (e.g. an `input_staging` stall that mimics a slow CPU tokenizer), gate it behind a flag, and show that the *same* batching fix that won against the queue bottleneck does nothing against the staging bottleneck — reinforcing that the fix must match the bound the profile named, not the last fix that worked.
