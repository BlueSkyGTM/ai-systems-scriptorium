# The Optimization Levers: Quantization, Speculative Decoding, Disaggregation

The engine is running and the batch is full. Latency is still too high or the GPU bill is still too large, and now you reach past the defaults for the levers that trade one resource for another. There are three big ones, each buys a different thing, and each can quietly cost you something you weren't watching.

## Why This Is a Decision Lesson, Not a Recipe

Every lever here is a trade, and the seam is exactly where the trade gets adjudicated. The AI Engineer guards output quality — does the model still answer well? The MLOps engineer guards the service-level objective (SLO) and the bill — is it faster, is it cheaper? A platform engineer pulls a lever only when *both* hold, and the failure mode of every one of these techniques is the same: a real win on the metric you watched, paid for with a regression on the metric you didn't. So the rule that governs all three comes first: **measure on your own traffic before and after, or you are gambling.** None of these is free, and none is universal.

## Quantization: Smaller Weights, Watch the Cache and the Calibration

**Quantization** stores the model's weights in fewer bits — 16-bit down to 8, 4, even lower — so the model takes less memory and moves through it faster. Since decode is memory-bound, less memory traffic means faster tokens, and a smaller model fits cheaper hardware. That is the win, and it is large.

The format is not a free choice; it is a function of your hardware, engine, and workload. The current landscape sorts roughly into GGUF k-quants for CPU and edge serving, AWQ as the datacenter GPU default for 4-bit, GPTQ where you serve many fine-tuned adapters, and FP8 as the near-lossless middle ground on recent NVIDIA silicon.

Two traps swallow teams who treat quantization as a checkbox. The first is **calibration mismatch**: 4-bit methods choose which weights to protect using a small sample dataset, and if that sample doesn't match your production domain, the method protects the wrong weights and your accuracy quietly drops on the work you do. The second is the one nobody budgets for — **quantizing weights is not quantizing the cache.** Shrink a model to 4 GB and forget that the KV cache is still 10–30 GB at production batch, and you've optimized the small number while the large one runs you out of memory.

## Speculative Decoding: Guess Ahead, but Only If the Guesses Land

Decode is slow because it is sequential — one forward pass per token. **Speculative decoding** breaks the sequence by having a small, fast *draft* model propose several tokens at once, then verifying all of them in a single forward pass of the full *target* model. Accepted guesses are free tokens; the target model produces several tokens for the cost of one pass. The newest draft methods (EAGLE-3 and its kin) train the draft on the target's hidden states rather than raw text, which lifts acceptance rates on general chat into the rough range of 0.6–0.8.

Here the trap is built into the mechanism, and it is the cleanest example in the lesson of why you measure. Every *rejected* draft costs you a second target pass — you ran the draft model *and* the target, and threw the draft away. When acceptance is low and the system is already compute-bound — high concurrency, below an acceptance rate of roughly 0.55 — speculative decoding goes net negative: you've added work, not removed it. And domain-specific traffic tends to drop acceptance unless you train a draft head on your own data, so the technique that wins on a general-chat benchmark can lose on your production prompts. Watch p99 of the per-token latency, not the mean — the mean improves while the tail, fed by those two-pass rejections, can get worse.

## Disaggregation: Stop Buying the Wrong Resource for Each Phase

The last lever comes straight from the two-phase split in the previous lesson. Prefill is compute-bound; decode is memory-bound. Run them on the same GPU and you are forever buying the wrong resource for one of them — a GPU sized for prefill's compute sits underused during decode, and one sized for decode's memory bandwidth is starved during prefill. Worse, a request's prefill and decode contend on the same device, so neither time-to-first-token nor per-token latency can be tuned without hurting the other. Colocating the two phases is estimated to waste on the order of 20–40% of GPU time.

**Disaggregated prefill/decode** splits the two phases onto separate GPU pools, each sized for its own bottleneck, and ships the KV cache from the prefill pool to the decode pool over a fast interconnect. You can now scale prefill and decode independently and match each pool to its workload. The catch is the handoff: transferring the KV cache between pools is a tax — tens of milliseconds for a multi-thousand-token prompt, and more on slower fabrics — so short prompts don't earn the split, and disaggregation pays off mainly at scale, on long prompts, with a fast fabric between the pools.

## The Lever You Don't Have to Pull

Self-hosting is what puts these levers in your hands; a managed platform takes most of them away and hands back a single dial. On Azure OpenAI you don't choose AWQ versus FP8 or tune a draft model — you size a **provisioned-throughput** deployment in units of capacity (PTUs), benchmark your real traffic against it, and the platform owns the quantization, batching, and scheduling underneath. That is itself a decision on the seam: pull the levers yourself and own the trade-offs, or rent a tuned engine and own only the capacity number. Both are defensible; pretending the managed path has no trade is not.

Reach for these in order of blast radius. Quantization is a config change you can validate offline against an eval set. Speculative decoding is a config change you must validate against live traffic. Disaggregation is an architecture change you justify only at scale. Pull the cheap, reversible lever first, measure, and stop the moment the SLO and the eval both clear — the most expensive optimization is the one that bought a number you weren't grading.

## Core Concepts

- Every serving optimization is a trade, and each fails the same way — a win on the watched metric paid for by a regression on the unwatched one — so measure on your own traffic before and after; none is free or universal.
- Quantization shrinks weights to fewer bits for less memory traffic and faster decode, but the format depends on hardware/engine/workload, and two traps bite: calibration data must match your domain, and quantizing weights does nothing for the 10–30 GB KV cache.
- Speculative decoding uses a fast draft model to propose tokens the target verifies in one pass; it is net-negative below roughly 0.55 acceptance because every rejected draft costs a second pass, so gate it on p99 per-token latency, not the mean.
- Disaggregating prefill (compute-bound) from decode (memory-bound) onto separate GPU pools recovers the 20–40% wasted by colocation, but the KV-cache transfer is a tax that only pays off at scale on long prompts — pull levers in order of blast radius: config, then live-traffic config, then architecture.

<div class="claude-handoff" data-exercise="exercises/module5/03-optimization-levers/">

**Build It in Claude Code** — add an optimization layer to `module5-serving/` that simulates all three levers: a `quantization` setting that lowers per-token decode time but also lowers a simulated quality score, a `speculative_decoding` mode with a tunable acceptance rate that goes net-negative below a threshold, and a `disaggregated` mode that splits prefill and decode and charges a KV-transfer tax. Run the same simulated workload through each lever, print TTFT/TPOT/throughput and the quality score before and after, and show the regime where each lever turns net-negative.

</div>
