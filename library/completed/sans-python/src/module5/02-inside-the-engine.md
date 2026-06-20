# Inside the Engine: Continuous Batching & Paged KV-Cache

A web server treats every request the same: take it, do the work, return the answer, move on. Run a language model that way and you will waste most of your GPU. An inference engine is not a REST server with a model bolted on — it is a different machine, built around two facts about how a transformer generates text, and this lesson is what lives below the API you've been calling.

## Why a Seam Engineer Opens the Box

In Module 3 you learned to order a prompt "static content first, dynamic content last" so the **key-value cache** — the KV cache, the engine's memory of every token it has already processed — could be reused across turns. That lesson promised the serving layer would show you *how* it implements that cache below the API. This is where the promise comes due. The AI Engineer treats the engine as a black box that returns tokens; the platform engineer has to size its memory, read its throughput, and explain its tail latency to whoever pays the GPU bill. You cannot tune what you don't understand, and the two mechanisms below are where every serving-cost decision starts.

## A Language Model Request Is Two Phases, Not One

Generating a response is not one operation. It is two, and they stress the hardware in opposite directions.

**Prefill** reads the whole prompt at once and computes the KV cache for every input token in a single parallel pass. It is compute-bound — the GPU's math units are the bottleneck — and it produces the first output token. The time to that token is the metric users feel as "did it hang?": **time to first token**, or TTFT.

**Decode** then generates the rest, one token at a time, each new token attending to every previous token's cached keys and values. Decode is memory-bound — the bottleneck is moving the growing KV cache through memory, not arithmetic — and its pace is the **time per output token**, TPOT, the metric users feel as "how fast does it type?"

One request, two regimes. A naive server runs them back to back per request and lets the GPU idle through the slow decode phase of one request while others wait in line. That idle time is the whole problem.

## Continuous Batching: Never Let the GPU Idle

Static batching — the web-server reflex — collects N requests, runs them as a group, and returns when the *slowest* finishes. With language models that is ruinous: one request generating 800 tokens holds the entire batch hostage while seven requests that finished at 20 tokens sit done but un-returned, their GPU slots dead.

**Continuous batching** fixes this at the granularity of a single decode step. The engine's scheduler revisits the batch *between every token*: a sequence that emitted its stop token leaves immediately and frees its slot; a newly arrived request joins the batch on the next step instead of waiting for the current one to drain. The batch is a living set, not a fixed group — sequences flow in and out continuously, and the GPU stays saturated. The measured effect is large: in one reference microbenchmark the per-iteration cost dropped from roughly 53 ms to 13 ms — about a 4.16x gain attributable to the scheduling change alone. Treat that number as an illustration of the mechanism, not a figure to quote back; your own gain depends on prompt and output lengths, and you measure it on your traffic.

One sharp edge follows from the two phases: a long prompt's prefill can stall the decode steps of everyone else in the batch, spiking their TPOT. Engines answer with **chunked prefill** — slicing a long prompt into fixed-size chunks so decode tokens interleave and never starve — which is why a production engine's scheduler is the component you tune.

## Paged Attention: Stop Wasting the Memory You Bought

The KV cache is the engine's dominant memory consumer, and the naive way to store it wastes most of what you paid for. The reflex is to reserve a contiguous block per request sized to the *maximum* possible length. A request that could generate 4,000 tokens but stops at 200 holds 4,000 tokens' worth of GPU memory and uses 200. Across a batch, that internal fragmentation and over-reservation strands the majority of your KV memory — by vLLM's own accounting, classic-allocator waste runs 60–80%.

**PagedAttention** borrows the fix from how an operating system manages RAM. It splits the KV cache into fixed-size **blocks** and keeps a per-request **block table** mapping the sequence's logical positions to physical blocks scattered anywhere in memory — exactly virtual memory's page table. A sequence grows by grabbing one more block, not by pre-reserving a worst-case slab. Waste falls to under 4% — it now happens only in a sequence's last partial block — and the memory you bought goes to serving requests instead of sitting reserved-but-empty.

The block table buys a second win for free. Two requests that share a prefix — the same long system prompt, the same retrieved document — can point their block tables at the *same physical blocks* for the shared span. The engine computes that prefix's KV once and shares it, instead of recomputing it per request. This is the serving-layer mechanism behind the "static content first" rule from Module 3: your prompt ordering decides whether the engine can share blocks or has to recompute. The cache you optimized for at the agent level is this block table, here, below the API.

## The Cache Is the Cost

Two consequences a platform engineer carries from this lesson. First, **the KV cache, not the model weights, often dominates serving memory at production batch sizes** — a 7-billion-parameter model quantized to 4 bits may be roughly 4 GB of weights and 10–30 GB of KV cache under load, which is why "the model fits" is the wrong question and "the model *plus its cache at my batch size* fits" is the right one. Second, the metrics that matter — TTFT, TPOT, throughput — are properties of the scheduler and the allocator, not of the model. Managed platforms hide this: an Azure OpenAI provisioned deployment exposes the result as a utilization metric in Azure Monitor and returns HTTP 429 once utilization passes 100% — the same KV-and-scheduler ceiling, surfaced as a quota signal instead of an out-of-memory error.

A REST server scales by adding stateless replicas. An inference engine scales by packing more sequences into a batch and more blocks into memory without missing a latency target — a different machine, solving a different problem, and now not a black box.

## Core Concepts

- A language-model request is two phases with opposite bottlenecks: prefill is compute-bound and sets TTFT (time to first token); decode is memory-bound and sets TPOT (time per output token) — the engine is built to keep both busy.
- Continuous batching schedules the batch between every decode token, so finished sequences leave and new ones join without waiting for the slowest request — a large throughput gain over static batching (several-fold in one reference benchmark) from the scheduling change alone.
- PagedAttention stores the KV (key-value) cache in fixed-size blocks with a per-request block table, like an OS page table — cutting fragmentation from 60–80% to under 4% and letting requests share physical blocks for a common prefix (the serving-layer payoff of "static content first").
- At production batch sizes the KV cache, not the model weights, usually dominates GPU memory; the metrics that decide a deployment — TTFT, TPOT, throughput — belong to the scheduler and allocator, not the model.

<div class="claude-handoff" data-exercise="exercises/module5/02-inside-the-engine/">

**Build It in Claude Code** — Replace the naive request handler in `module5-serving/` with a continuous-batching scheduler and a paged KV-cache allocator, both simulated (no GPU, no real attention math). Model prefill and decode as separate timed phases, let sequences join and leave the batch between decode steps, allocate the KV cache in fixed blocks with a block table, and measure simulated TTFT and throughput against the static-batching baseline to show the gain.

</div>
