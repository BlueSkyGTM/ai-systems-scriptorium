# Where the Time Goes

Tuning without profiling is guessing. Before you change a single setting, you need to see where
the time actually goes, because the answer is not where most people expect it.

## Step 1: The Two Numbers a GPU Reports

`nvidia-smi` has a streaming mode that prints per-second device metrics to the terminal:

```bash
nvidia-smi dmon -s um
```

The `-s` flag selects metric groups. `u` requests utilization; `m` requests memory utilization.
Two columns matter here.

`sm%` is streaming-multiprocessor utilization: the fraction of the GPU's compute cores that are
doing math. `mem%` is memory utilization: how hard the memory subsystem is working to move data
between VRAM and the compute units. Together they tell you whether the GPU is constrained by how
fast it can compute or by how fast it can read.

Start `nvidia-smi dmon -s um` in one terminal, then send a long generation (a few hundred tokens)
in another. What you should see looks roughly like this:

```
# gpu   sm%  mem%
    0    42    81
    0    38    84
    0    45    79
    0    40    83
    0    36    86
```

The exact numbers vary by model size, quantization, and batch size. The shape is what to read.

## Step 2: The Bandwidth-Bound Signature

That output is not a problem. It is the signature of memory-bandwidth-bound inference, and it is
exactly what local LLM serving looks like.

Here is why. When the model generates a token, it reads the full set of model weights from VRAM
once per token, feeds them to the arithmetic units, and performs a matrix-by-vector
multiplication. The computation itself is small, because you are generating one token, not running
a training batch of thousands. The GPU finishes the math fast and then waits while the memory
subsystem loads the next round of weights. The bottleneck is the transfer, not the multiplication.

The signature of that bottleneck is `mem%` in the 70 to 90 range while `sm%` stays well below
100, often 30 to 60 percent. The compute cores are idle a significant fraction of the time, not
because they are misconfigured, but because they are waiting on memory. This is the normal,
expected shape of transformer inference at token-generation time.

Module 4 put numbers on the gap: the RTX 4060 Ti's GDDR6 delivers roughly 288 GB/s, while
DDR5-6000 system RAM delivers roughly 96 GB/s. The 3:1 ratio is why layers stranded in system
RAM generate tokens so much more slowly. It is also why, once the model is fully on-card, the
memory bus, not the compute units, remains the limiting factor.

## Step 3: What This Tells You About Tuning

Because you are bandwidth-bound, the wins are not where a forum post usually points. Higher clock
speeds on the compute cores do not help when the cores are already waiting on the bus. More shader
parallelism does not help when the work per token is a single matrix-by-vector pass.

What does help is moving less data or moving it better. Three levers directly attack the bandwidth
problem:

- **Quantization** shrinks the weights. A Q4_K_M model loads roughly half the bytes per token
  compared to a Q8 model, so each token reads half the VRAM.
- **KV-cache quantization** shrinks the attention cache that grows with context length. On long
  contexts, the KV cache can consume as much bandwidth as the weights.
- **Request batching** lets one weight read serve several concurrent token positions at once,
  amortizing the memory cost across multiple requests.

The next lesson covers each lever and the tradeoff it actually carries. The point here is that
profiling first shows you which problem to solve: if `sm%` is the ceiling, you have a compute
problem; if `mem%` is the ceiling and `sm%` is not, you have a bandwidth problem, and you need
bandwidth solutions.

## Step 4: Watch VRAM Headroom

While `nvidia-smi dmon` runs in one terminal, open a second watcher in another:

```bash
nvidia-smi
```

Or add memory usage to the stream by running `nvidia-smi dmon -s um` alongside a standard
`nvidia-smi` refresh. The field to watch is the used/total VRAM figure, for example
`12850 MiB / 16384 MiB`.

This matters because of the cliff from Module 4. If VRAM usage climbs past roughly 95 percent,
Ollama starts offloading layers to system RAM, and the bandwidth drop is immediate and severe: a
model that was doing 25 tokens per second on-card can fall to 3 tokens per second when even a
handful of layers spill over. The clip does not come with a warning. You see it in the slowdown,
and then you confirm it with `ollama ps`.

Keep headroom. A KV cache grows with context length, so a model comfortably on-card at a short
prompt can tip over the edge on a long conversation. Knowing your baseline headroom, from the
profiling run, tells you how much margin you have before that happens.

Once you can read `sm%`, `mem%`, and VRAM headroom under a real generation load, you know the
actual shape of your workload. Everything in the next lesson follows from that shape.

## Core Concepts

- Profile before you tune: `sm%` and `mem%` from `nvidia-smi dmon -s um` tell you whether you
  are constrained by compute or by memory bandwidth; guessing the constraint without measuring it
  leads to tuning the wrong lever.
- The bandwidth-bound signature is high `mem%` (roughly 70 to 90 percent) with `sm%` well below
  100 (often 30 to 60 percent); this is normal for token generation, not a misconfiguration.
- Because token generation reads the full model weights from VRAM for every token while doing only
  a small matrix-by-vector computation, the wins come from moving less data (quantization,
  KV-cache quantization, batching), not from chasing compute utilization.
- VRAM headroom matters during profiling: if usage climbs past roughly 95 percent, layers spill to
  system RAM and throughput drops severely, confirming the cliff first established in Module 4.

<div class="claude-handoff" data-exercise="exercises/module7/where-the-time-goes/">

**Build It in Claude Code**: Run `nvidia-smi dmon -s um` while generating, and record the peak `sm%` and `mem%` plus a one-line verdict on whether your workload is memory-bandwidth-bound.

</div>

<!-- SOURCES: https://docs.nvidia.com/deploy/nvidia-smi/index.html | https://www.baseten.co/blog/llm-transformer-inference-guide/ | https://www.hardware-corner.net/gpu-ranking-local-llm/ -->
