# Exercise: Write a Tuning Plan

## Goal

Write a one-page tuning plan so you tune deliberately, one lever at a time, before you touch a single environment variable.

## Why

The four levers from the lesson interact: parallelism and context both eat KV-cache VRAM; KV-cache quantization depends on flash attention being enabled; more context means less headroom for more parallel slots. If you change three settings at once and something improves, you have learned nothing reproducible. A written plan forces you to commit, in advance, to what each lever should do and how you will know if it worked.

## Steps

Work through each lever in the table below. For each one, fill in four columns:

1. **Setting**: the environment variable or model parameter, and the value you will try.
2. **Expected Effect**: what the lever should change (tokens per second, context capacity, aggregate throughput, VRAM headroom).
3. **Metric to Watch**: the specific number you will record (for example: tokens/s from the Ollama API, peak VRAM from `nvidia-smi`, time-to-first-token in milliseconds).
4. **VRAM Cost**: whether this setting increases, decreases, or leaves unchanged the VRAM consumed by the running model.

### Starter Table

Fill in every cell before you run a single test.

| Lever | Setting and Value | Expected Effect | Metric to Watch | VRAM Cost |
|---|---|---|---|---|
| Flash attention | `OLLAMA_FLASH_ATTENTION=` | | | |
| KV-cache type | `OLLAMA_KV_CACHE_TYPE=` | | | |
| Request parallelism | `OLLAMA_NUM_PARALLEL=` | | | |
| Context length | `OLLAMA_CONTEXT_LENGTH=` | | | |

### Notes on Filling the Table

**Flash attention**: the expected effect is a modest speedup on long sequences, plus it unlocks the KV-cache type lever. VRAM cost is a small reduction in attention memory.

**KV-cache type**: the expected effect is extended context capacity or more parallel slots in the same VRAM budget, not raw speed. The metric to watch is peak VRAM before and after, and context length you can sustain without an out-of-memory error.

**Request parallelism**: the expected effect is higher aggregate throughput under concurrent load. Single-request latency does not improve. The metric is total tokens per second across all concurrent requests. The VRAM cost is one full KV cache per additional slot.

**Context length**: the expected effect is a smaller or larger KV-cache footprint. The metric is peak VRAM. Size it to what your actual workload needs; unused context window is VRAM you cannot spend elsewhere.

## Done When

You have a completed table with every cell filled: the exact setting, the specific effect you expect, the number you will record, and the VRAM implication. Each lever has a measurable prediction, not a hope.

## Stretch

Decide the order you will apply the levers, and write it below the table with a one-line reason for each position.

Hint: one lever must come before another for a mechanical reason, not a preference. Identify which one, and put it first.
