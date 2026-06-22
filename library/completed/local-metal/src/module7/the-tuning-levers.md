# The Tuning Levers

You profiled the rig and you know where the time goes. Now you can tune deliberately. There are only four levers worth pulling on one consumer card; each has a real tradeoff, and knowing the tradeoff is what keeps you from chasing a forum number that doesn't apply to your setup.

## Step 1: Flash Attention

Flash attention rewrites the attention computation to process data in tiles that fit inside on-chip SRAM, rather than reading and writing the full attention matrix through VRAM on every step. The practical effect on a single card: a modest speedup on long sequences and a smaller attention memory footprint. On a bandwidth-constrained GPU like the 4060 Ti, gains depend on sequence length; short prompts see less benefit than long-context workloads. (Flash attention papers report large throughput improvements on server hardware; treat single-card numbers as representative, not guaranteed.)

Enable it by setting the environment variable before Ollama starts:

```
OLLAMA_FLASH_ATTENTION=1
```

The other reason to enable it is not speed at all: flash attention is a prerequisite for KV-cache quantization in Step 2. Enable it first, before touching the cache type, or the cache flag has no effect.

## Step 2: KV-Cache Quantization

The KV cache holds the attention keys and values for every token in the context window. In the default configuration it lives in VRAM at f16 precision. You can halve or quarter that footprint by switching the cache type:

```
OLLAMA_KV_CACHE_TYPE=q8_0   # ~half the KV-cache VRAM; minimal quality cost
OLLAMA_KV_CACHE_TYPE=q4_0   # ~quarter the KV-cache VRAM; noticeable quality cost
```

The f16 default is the zero-cost baseline. `q8_0` is the practical choice: the precision loss is minimal in most workloads and the VRAM savings are meaningful. `q4_0` is available if you need to push further, but the quality degradation is real and worth measuring before committing.

What this lever actually buys is not speed; it is context. Freed KV-cache VRAM lets you extend the context window, or hold more parallel requests, within the same memory budget. If your bottleneck is context length rather than tokens per second, this is the most direct fix.

Requires flash attention to be enabled (Step 1).

## Step 3: Request Parallelism

By default Ollama queues requests and processes them one at a time. Setting `OLLAMA_NUM_PARALLEL` to a value greater than one lets the model serve multiple concurrent requests in the same forward pass:

```
OLLAMA_NUM_PARALLEL=2
```

The gain here is aggregate throughput, not single-request latency. When several requests arrive together, one weight read can serve them all; the GPU stops idling between requests. Under genuine concurrent load, this is the most impactful lever in the set.

The cost is proportional: each additional parallel slot needs its own KV-cache allocation in VRAM. If `num_ctx` is 4096 tokens per request and you set `OLLAMA_NUM_PARALLEL=2`, you are holding two full KV caches simultaneously. The headroom fills fast, so this lever and context sizing are directly connected.

One important nuance: if you are the only user, single-stream tokens per second does not improve. This lever only pays off when you have actual concurrent load to serve, which is exactly what the next lesson measures.

## Step 4: Context Sizing and Keep-Alive

KV-cache VRAM scales linearly with context length. Every token in the window needs a key-value entry for every layer and every head; double the context, roughly double the cache. Set `num_ctx` in your model configuration, or the global default via:

```
OLLAMA_CONTEXT_LENGTH=4096
```

Size it to what your actual workload needs, not to the model's theoretical maximum. A context window you do not use is VRAM you cannot spend on parallelism or a larger model.

`OLLAMA_KEEP_ALIVE` controls how long a loaded model stays resident in VRAM after its last request. The default is five minutes. Longer keep-alive eliminates reload latency between requests; shorter keep-alive frees VRAM sooner for other uses. On a dedicated inference host, a longer window is almost always the right call. On a workstation where you share the GPU with other tasks, a shorter window keeps VRAM available between sessions.

## Step 5: The One-at-a-Time Discipline

Every lever here interacts with at least one other. Parallelism and context both eat KV-cache VRAM; KV-cache quantization and context sizing both affect output quality; flash attention is a prerequisite for cache quantization. The temptation is to apply all of them at once and measure the total effect.

That approach tells you nothing. If throughput goes up, you do not know which lever caused it. If quality drops, you do not know which one to roll back.

The discipline is simple: change one setting, restart Ollama, run the same prompt sequence, record the metric, and compare to baseline. Keep the setting only if the number improved and quality held. Then move to the next lever. A tuning session that takes ninety minutes with this discipline is more useful than one that takes ten minutes without it.

The before-and-after you are building toward, `TUNING.md`, is the record of that sequence: one lever, one measurement, one decision, repeated four times. That document is what makes the tuning reproducible and reviewable.

A tuned rig with documented numbers is a claim a reviewer can reproduce; an untuned rig with a forum setting applied is just a guess that happened to persist. The next lesson puts all four levers under concurrent load so you can see which ones actually change the throughput curve.

## Core Concepts

- Flash attention reduces attention-step VRAM and gives a modest single-stream speedup on long sequences; enable it first because KV-cache quantization requires it.
- KV-cache quantization (`q8_0` or `q4_0`) trades precision for VRAM, primarily extending your context budget rather than increasing tokens per second.
- `OLLAMA_NUM_PARALLEL` raises aggregate throughput under concurrent load at the cost of proportionally more KV-cache VRAM; it does not speed up a single isolated request.
- Change one lever at a time, measure against a fixed baseline, and keep only what the numbers confirm.

<div class="claude-handoff" data-exercise="exercises/module7/the-tuning-levers/">

**Build It in Claude Code**: Write a one-page tuning plan: for each lever (flash attention, KV-cache type, num_parallel, context length), record the value to try, the metric it should move, and its VRAM cost; decide the order to apply them.

</div>

<!-- SOURCES: https://github.com/ollama/ollama/blob/main/docs/faq.mdx | https://github.com/ollama/ollama/blob/main/envconfig/config.go | https://docs.ollama.com/faq | https://github.com/dao-ailab/flash-attention -->
