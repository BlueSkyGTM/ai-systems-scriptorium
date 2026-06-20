# Measure before you optimize: profiling & roofline

Chapter 1 handed you the levers — continuous batching, quantization, paged attention, disaggregated prefill and decode. This lesson is the discipline that decides which lever to pull. An optimization applied to the wrong bottleneck is not a small win; it is negative work — added complexity, no speedup, and a slower path to the fix that would have mattered. The serving lessons taught you the moves. This one teaches you to earn the right to make one.

## Optimization without measurement is guessing with a budget

Here is the thesis of the whole module, stated as a working rule: you do not get to optimize a system you have not profiled. The reflex — "decode feels slow, let me quantize" — is the expensive reflex. Quantization helps a workload bound by memory bandwidth or weight size. If your decode is actually stalling on a scheduler that drains the queue one request at a time, you can quantize to four bits and watch the latency sit exactly where it was, because you spent your effort on a part of the system that was never the limiter.

The reference checklist behind this chapter states it flatly: *profile before and after.* Tweaks made on theory might not help — or even hurt — in practice. It gives the case that should haunt you: enable activation checkpointing on a workload that is not memory-limited, and you trade compute you needed for memory you had to spare, and the job gets *slower*. The optimization was real. The application was a guess. That is the difference this lesson exists to remove.

This is also the seam's sharpest edge. The machine-learning instinct is to reach for a better model, a bigger model, a fine-tune. The platform-engineering instinct is to ask where the time actually goes — and the answer, more often than the ML instinct expects, is a queue, a copy, or a CPU thread starving the GPU. Knowing whether you need a kernel change or a trip to the store for more memory bandwidth is a deployable, demonstrable skill. It is the one that separates the engineer who ships a 4x speedup from the one who ships a clever change nobody can measure.

## The four bounds: name the limiter before you touch it

Every inference workload is limited by one of four things at any moment, and your only job in the first profiling pass is to find out which:

- **Compute-bound** — the arithmetic units are busy; you are doing real floating-point work (FLOPs, floating-point operations) near the hardware's ceiling. Prefill on a large batch lives here.
- **Memory-bound** — the arithmetic units are *idle, waiting on data* moving to and from high-bandwidth memory (HBM, the GPU's on-package DRAM). Single-stream autoregressive decode lives here: one token at a time, reloading the model's weights and the key-value cache for each step.
- **I/O-bound** — the GPU waits on disk or the host: model load, data staging, a slow tokenizer on the CPU.
- **Communication-bound** — in a multi-GPU deployment, the GPUs wait on each other across the interconnect.

The reference puts it in one line worth memorizing: you can't optimize what you don't measure; profiling reveals whether you're compute-bound, memory-bound, I/O-bound, or network-bound, so you target the right fix. The four bounds map to four different toolboxes. Quantization and better attention kernels attack a compute or memory-traffic bound. A bigger data-loader pool or pinned host memory attacks I/O. Topology-aware placement attacks communication. Pick the toolbox before the tool, and pick it from evidence.

## The roofline: a picture of the ceiling you are under

The roofline model is the one diagram worth keeping in your head for this work. It answers the single question — *am I bandwidth-limited or compute-limited?* — by plotting two numbers against the hardware's actual ceilings.

The horizontal axis is **arithmetic intensity**: floating-point operations performed per byte moved from memory (FLOPs per byte). A kernel that reads a lot of data and does little math with it sits on the left. A kernel that loads its operands once and grinds on them sits on the right.

The vertical axis is **achieved performance** in FLOPs per second. The "roof" has two slopes. On the left, a diagonal: performance rises with intensity because you are *memory-bound* — the memory bus, not the math units, sets your speed, and every extra FLOP-per-byte buys you more. On the right, a flat ceiling: you have saturated the compute units and become *compute-bound*; more intensity buys nothing because the arithmetic, not the bus, is now the wall.

```
 performance
 (FLOPs/s)
     │            ┌──────────────  compute roof (peak FLOPs/s)
     │           ╱   compute-bound region →
     │          ╱
     │         ╱  ← memory-bound region
     │        ╱
     │       ╱  slope = memory bandwidth (bytes/s)
     │      ╱
     └─────┴────────────────────────────  arithmetic intensity
                                            (FLOPs / byte)
```

Plot your kernel as a point. Under the diagonal, your fix is to *move less data* — quantize the weights or the KV cache to shrink bytes, fuse kernels so intermediate results never round-trip through HBM, reuse a cache instead of recomputing it. Under the flat roof, data movement will not save you; you need a faster algorithm or to do less arithmetic — a sparser attention pattern, an early exit, a smaller effective computation. The same point also tells you the *ceiling itself*: if you are at the roof, you are done, and more engineering is wasted. Nsight Compute ships a roofline pane that plots this for every captured kernel and flags the limiter for you. You do not derive the model by hand at the console — you read it, and let it tell you which region you are standing in.

Why this matters for an LLM specifically: decode is structurally memory-bound. Each generated token reloads the weights and the growing KV cache to produce one token's worth of math, so arithmetic intensity is low and you sit on the diagonal — which is exactly why the chapter-1 levers that *cut bytes* (paged and pooled KV cache, quantized cache, lower precision) buy so much there, and why a faster matmul kernel often buys nothing. Prefill is the opposite: a full prompt's worth of arithmetic per byte loaded, far to the right, compute-bound. One model, two regimes, two toolboxes. The roofline is how you stop confusing them.

## Systems first, then kernels: the two-step attribution loop

Knowing the bound is half the discipline. The other half is *attribution* — pinning the lost time to a specific cause before you change code. The reference prescribes a two-step flow, and it is the right order.

**Step one — the timeline.** Capture the whole system with a timeline profiler (NVIDIA Nsight Systems is the reference's tool) and tag your phases — input staging, prefill, decode, the inter-token gaps — with named markers so the timeline reads like a story instead of a wall of kernels. The timeline answers the cheap, decisive questions first: *Is the GPU even busy?* A GPU sitting at 50% utilization is not a kernel problem; it is a feeding problem — the data, the CPU, or the queue is starving it, and no kernel rewrite will close a gap the GPU never spent computing. The reference's example is exact: utilization dips every five minutes that turn out to coincide with checkpoint saves. You would never find that by staring at a kernel. You find it by looking at when the GPU goes idle and what else happened at that instant.

**Step two — the kernel.** *Only* once the timeline names the dominant phase do you drop into a kernel profiler (Nsight Compute) on that one kernel, and read occupancy, memory throughput, and the roofline point. This is where the 80/20 rule earns its keep: if ninety percent of your time is in two kernels or one communication phase, you optimize those deeply and ignore the one-percent kernel entirely, however ugly it looks. The two-step loop exists so you never burn a kernel-profiling session on a kernel that was never the limiter.

The measured deltas from the serving chapters only mean anything inside this loop. In the reference's own benchmark runs, a tensor-core decode kernel showed a 15.65x speedup on one target; cache-aware reuse of the rotary-position and query path showed 23.53x; a smarter routing policy showed 7.07x with the underlying workload unchanged. Those are not numbers to quote at a stranger's stack. They are numbers that were *attributed* — profiled deep-dive to confirm the win came from the cache movement, the scheduling, or the decode behavior the engineer claimed it did, not from a lucky batch. Re-measure on your own hardware before you treat any published delta as a threshold. A speedup you cannot reproduce on your machine is a rumor, not a result.

## Measure honestly or don't bother

The fastest way to lie to yourself is a sloppy measurement, so the reference fences the method as hard as the optimization. Align the runs before timing — clamp the random seed, the preprocessing, the batch shapes — so the delta comes from your change and not from a different workload sneaking in. Measure the *steady state* — warm up first, run the compile and the cache-fill before you start the clock — so first-iteration noise never lands in the reported number. Track throughput and latency *together*; tokens per second next to milliseconds, because an optimization that improves one while quietly wrecking the other is a regression wearing a win's clothes. And log the environment every run — GPU, driver, toolkit, the exact command — so a number is replayable and a regression is traceable to the thing that changed.

For the AI Platform Engineer, this is the habit the title is built on: you are the person who can say *where the time goes* and prove it, before anyone spends a sprint optimizing a part of the system that was already at its roof. Measure first. The lever comes second, and only the measurement tells you which one.

## Core concepts

- Optimization without measurement is negative work: a fix applied to a part of the system that was not the bottleneck adds complexity and buys nothing, so you do not optimize a workload you have not profiled.
- Every inference workload is compute-bound, memory-bound, I/O-bound, or communication-bound at any moment; naming the bound first picks the toolbox — quantization and kernel work for compute/memory, data-loader and pinned-memory work for I/O, topology-aware placement for communication.
- The roofline plots arithmetic intensity (FLOPs per byte) against achieved performance: under the diagonal you are memory-bound and the fix is to move fewer bytes; under the flat roof you are compute-bound and the fix is less or faster arithmetic. LLM decode sits memory-bound, prefill compute-bound.
- Attribute before you change code with the two-step loop: a timeline profiler first to find the dominant phase and check the GPU is even busy, then a kernel profiler on that one phase — and measure the steady state with aligned runs so the delta is the optimization, not a lucky batch.

<div class="claude-handoff" data-exercise="exercises/module5/09-measure-before-you-optimize/">

**Build It in Claude Code** — instrument the `module5-serving/` mock serving layer with phase timers (input staging, prefill, decode, queue wait), run a profiling pass against a synthetic load, and read off which phase dominates. The layer hides a deliberate bottleneck — a serialized queue drain that starves the "GPU" while the model sits idle. Attribute it from the timeline before you touch it, apply the one fix that targets the actual limiter, and report the measured before/after delta in both throughput and latency. Then prove a *wrong* fix (quantizing the already-idle compute path) buys nothing.

</div>
