# The production performance checklist

The previous lesson taught you to measure before you optimize. This one is what you reach for once the measurement points somewhere — a prioritized list of the checks that actually move production inference, and the hardware facts you need to reason about them. The source is a 200-plus-item reference checklist from the performance-engineering literature. Reproducing 200 items would be its own kind of clutter; most of them are training- and kernel-deep and live in the antilibrary. What follows is the load-bearing subset — the roughly two dozen an AI Platform Engineer runs against a serving stack before it ships, in the order the evidence says to run them.

## Read it in priority order, not top to bottom

A checklist is dangerous when you treat it as a to-do list and start at item one. The reference is explicit about the order: apply the 80/20 rule, find the top contributors to runtime and cost, and optimize those deeply rather than micro-tuning a kernel that owns one percent of the time. So this list is grouped by the bound it serves, and you enter it from the bound your profiling named. Memory-bound decode? Start with the memory section. GPU at 50% utilization? You have a feeding problem — start with I/O and hosting, not kernels. The checklist is an index keyed by your measurement, not a sequence you grind through.

One discipline sits above all the items and never bends: **profile before and after every change, and keep the wins from eroding.** Lock versions, configs, and benchmarks in source control so a regression is traceable to the change that caused it. Bring a performance benchmark into CI so a driver bump or a code change that quietly drops Tensor Core usage gets caught by the pipeline, not by a customer. A speedup you do not guard regresses silently the first time someone touches the stack.

## Hardware and topology: the ceiling no software tweak outruns

Before the software checks, the facts that set the ceiling. The reference is blunt: your hardware, interconnects, and data paths cap performance and cost-efficiency, and no software tweak can outrun a starved GPU. The platform engineer has to reason about three of them.

**Memory bandwidth is the decode budget.** Autoregressive decode is memory-bound (lesson 09), so the number that bounds your single-stream latency is how fast the GPU moves bytes from HBM (high-bandwidth memory, the GPU's on-package DRAM), not its peak FLOPs. When you size a serving box, the HBM bandwidth and capacity are the spec to read first for decode-heavy workloads — capacity sets how much KV cache and how many concurrent sequences you hold, bandwidth sets how fast you can decode them.

**NVLink (NVIDIA's high-bandwidth GPU-to-GPU interconnect) is why multi-GPU serving scales — or doesn't.** NVSwitch is the fabric that connects many NVLink links together. The reference's headline figure: the fifth generation of NVLink provides up to 1.8 TB/s bidirectional bandwidth per GPU — over 14x a PCIe Gen5 link — which is what lets a model sharded across GPUs behave almost like one. The serving consequence is concrete: in the serving chapters' benchmark runs, a KV cache (key-value cache) pooled across GPUs over NVLink showed a 6.11x latency improvement over the local-only path. That win exists *because* the fabric is fast enough to make remote memory nearly local. On a PCIe-only box, the same pooling would be a bottleneck, not a speedup.

**Topology awareness is placement, not just hardware.** Owning fast links is not enough; you have to keep tightly-coupled work on them. Large nodes expose multiple NVLink "islands," and the reference's rule is to place the shards of one model within a single high-bandwidth domain and avoid crossing islands or domains for coupled work. Read the actual layout of your box with `nvidia-smi topo -m` before you pin anything — the diagram, not the assumption, tells you which GPUs share a fast link. In the serving chapters' benchmark runs, a topology-aware routing policy beat uniform placement by 5.07x on a mixture-of-experts target; same GPUs, same model, better placement.

On Azure, this reasoning maps to SKU choice rather than rack design: the ND-series and NC-series GPU virtual machines differ in GPU generation, HBM, and whether they expose NVLink/NVSwitch across the GPUs in the VM, which is exactly what decides whether multi-GPU pooling helps you. (The Azure ND-series GB200/GB300 v6 and H100/H200 v5 sizes, for instance, expose NVLink across the GPUs inside the VM.) Pick the SKU from the bound you measured, not the headline FLOPs (floating-point operations per second).

## The curated checklist

Grouped by bound. Enter from the one your profiling named.

**Goodput and the metric you optimize for.** Optimize for *goodput* — useful work per dollar and per watt — not raw FLOPs; a box at peak FLOPs serving garbage tokens is not winning. Track time-to-first-token and time-per-output-token next to throughput and the cost per token, because these are the latency budget a serving SLA is written against, and an optimization that helps one while hurting another is a regression. Compute throughput-per-dollar across instance types before you scale — second-best hardware at a fraction of the cost often wins on price-performance.

**Memory-bound (decode, KV cache) — the first place to look for serving.**
- Quantize weights and the KV cache where accuracy allows; lower precision (FP8, and the AWQ/GPTQ/SmoothQuant family) cuts the bytes a memory-bound path must move.
- Pool the KV cache over NVLink when the fabric supports it; keep hot weights, activations, and KV in HBM and spill only cold data to slower tiers.
- Manage the cache: paged/block-wise allocation and sound eviction-and-promotion policies keep decode latency inside budget instead of fragmenting memory.
- Watch for out-of-memory drift; nearing OOM (out-of-memory) makes the framework swap tensors to host and collapses throughput, and memory that climbs each iteration is a leak, not a workload.

**Compute-bound (prefill, large batches).**
- Use the better attention kernel and precision mode for the hardware — Flash-style attention, BF16/TF32 on Tensor Cores — to do the same math faster.
- Exploit structured sparsity (2:4 pruning) where accuracy survives it, for sparse Tensor Core paths.
- Capture steady-state decode with CUDA Graphs / regional compilation to cut per-launch overhead on the repeated path — but audit that the capture is steady-state-only so you are not timing warmup.

**Scheduling and batching — the cheapest serving wins, often mistaken for kernel problems.**
- Use continuous batching so decode throughput stays high instead of draining the queue one request at a time; this was a 4.16x target in the serving chapters' benchmark runs and is usually the first scheduling fix.
- Cut scheduler and runtime coordination overhead; in the same runs, a runtime-scheduler fix showed 1.78x with no model change.
- Disaggregate prefill and decode when one is starving the other, so a long prefill does not block decode and wreck time-to-first-token.

**I/O-bound (GPU under-fed — suspect this first when utilization is low).**
- Load and preprocess data in parallel; the default one-or-two loader workers is often the hidden bottleneck.
- Pin host memory and overlap host-to-device copies with compute via separate streams so the GPU never waits on the next batch.
- Store models and data on fast NVMe and write checkpoints and logs asynchronously so disk never stalls the serving loop.

**Host, OS, and scheduling — the quiet throughput drains.**
- Set NUMA affinity: pin each GPU's process and memory to the nearest CPU node, or cross-NUMA traffic can halve effective bandwidth.
- Enable GPU persistence mode so the driver stays warm and jobs don't pay re-init latency.
- Use MIG (Multi-Instance GPU) to partition a large GPU for many small inference jobs, and MPS (Multi-Process Service) when several processes share a GPU none of them saturates — but never MIG for a single tightly-coupled multi-GPU job.
- Keep the driver and CUDA stack consistent across nodes, and keep ECC on for reliability; its cost is a few percent and it catches the silent corruption that kills a long run.

**Telemetry — so the wins survive contact with production.**
- Export per-GPU metrics (DCGM to Prometheus/Grafana) and watch for utilization drops, throttling, and ECC errors; alert on anomalies instead of finding them in the postmortem. On Azure, Azure Monitor and Application Insights are the equivalent sinks for this telemetry.

## Run it honestly: partial beats fake-green

The reference's operator playbook ends on a discipline more important than any single item, and it is the one to carry: keep capability-limited outcomes *truthful*. When a check can't run on your hardware — no NVLink to pool across, no multi-GPU to disaggregate — mark it skipped or partial, never fake-green. When a check fails, root-cause it in the most local correct place, fix it there, re-run that one target, and only then move on — do not paper over a failure to keep the list moving. And do not disable the profiler to make a run pass; a green checklist that turned off its own measurement is worth nothing.

That honesty is the whole value of the artifact. A checklist exists to produce a findings document a teammate can trust — what is green, what is partial because your hardware can't exercise it, what is an open finding ranked by impact. The platform engineer who hands over *that* is worth more than the one who hands over a wall of checkmarks, because the first one told you where the bodies are and the second one hid them.

## Core concepts

- A 200-item checklist is an index keyed by measurement, not a top-to-bottom to-do list: enter it from the bound your profiling named and apply the 80/20 rule — optimize the top runtime contributors deeply, skip the one-percent items.
- Hardware sets the ceiling no software outruns: HBM bandwidth bounds memory-bound decode, NVLink (up to 1.8 TB/s/GPU on NVLink 5) is what makes multi-GPU KV pooling a 6.11x win instead of a bottleneck, and topology-aware placement — read with `nvidia-smi topo -m` — keeps coupled shards on the fast fabric.
- Optimize for goodput (useful work per dollar and watt) tracked as TTFT, TPOT, throughput, and cost-per-token together, and guard every win with version control and a CI performance benchmark so it cannot regress silently.
- Run the checklist honestly: mark hardware-limited checks skipped or partial rather than fake-green, root-cause failures in the most local place, never disable the profiler — the deliverable is a trustworthy findings doc, not a wall of checkmarks.

<div class="claude-handoff" data-exercise="exercises/module5/10-the-performance-checklist/">

**Build it in Claude Code** — turn this lesson into a runnable audit against the `module5-serving/` stack. Encode the curated checklist as a script that probes the stack and the host (`nvidia-smi topo -m` where a GPU exists, batching/cache config, telemetry presence, version pinning), classifies each item green / partial / skipped / open-finding with a reason, and emits a prioritized findings document ranked by impact. Mark hardware you don't have as skipped, never fake-green; produce the doc a teammate could act on cold. Open the repo and run the exercise for this lesson.

</div>
