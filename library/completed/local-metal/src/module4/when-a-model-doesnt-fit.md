# When a Model Doesn't Fit

Module 3 ended with a rule: if `ollama ps` reads `100% GPU`, the model is on the card and you
are done. This lesson is the deliberate break from that rule, and what you see when you break it.

## Step 1: What Ollama Does

When a model's memory footprint exceeds available VRAM, Ollama does not refuse to load it. It
loads as many transformer layers as fit onto the GPU and runs the remainder on the CPU from
system RAM. This is called partial layer offload. The parameter that controls it is `num_gpu`,
which sets the number of layers to place on the GPU; Ollama sets it automatically based on what
fits, but you can also set it explicitly in a Modelfile.

Pull a model that will not fit in 16 GB of VRAM:

```bash
ollama pull qwen2.5-coder:32b
```

The default tag is `Q4_K_M`, which is roughly 20 GB on disk. That exceeds the card's 16 GB
before a KV cache or compute buffers are added. Ollama downloads it without complaint and loads
what it can.

## Step 2: Read the Split

Once the model is loaded and serving, run:

```bash
ollama ps
```

What you should see is different from Module 3. Instead of `100% GPU`, the PROCESSOR column now
reports a split:

```
NAME                      ID        SIZE    PROCESSOR          UNTIL
qwen2.5-coder:32b         ...        ...     52% GPU / 48% CPU  4 minutes from now
```

The split above is representative; your rig's actual numbers depend on VRAM headroom at the
moment Ollama loads the model and the context length in use. What matters is the shape: part of
the model is on the card, part is in system RAM, and you can see exactly how much is where.

One detail worth knowing: Ollama's fallback is silent. When a model exceeds VRAM, Ollama reduces
GPU layers automatically without logging a warning or returning an error. `ollama ps` is the only
reliable way to see whether a split happened. Do not assume `100% GPU` unless you read it.

## Step 3: Why the Split Is Slow

Token generation is memory-bandwidth-bound. The bottleneck is not compute but how fast the
hardware can stream weights from memory to the arithmetic units. The two halves of the budget run
at very different speeds.

The RTX 4060 Ti's GDDR6 delivers roughly 288 GB/s. The rig's dual-channel DDR5-6000 system RAM
delivers roughly 96 GB/s. That is approximately a 3:1 gap in bandwidth, and the layers stranded
in system RAM generate tokens at the slower rate, dragging the whole model's output down.

In practice, a 32B Q4_K_M model that splits across this card drops to roughly 2 to 3 tokens per
second. The 14B Q4_K_M model from Module 3, which stays fully on-card, runs at roughly 22 to 34
tokens per second. Both numbers are representative; you will measure your own rig in the Measure
Latency lesson. The point is the order of magnitude: one split model is not a slower version of
the same experience, it is a categorically different one.

## Step 4: The Unified Memory Budget

The rig does not have one memory budget; it has two, joined. VRAM and system RAM together form
the pool Ollama spans when a model is too large for the fast half alone. The module overview calls
this "unified memory," not because the hardware shares silicon (the GPU and host RAM are
separate), but because Ollama treats both as one budget it can allocate across.

The two halves are not equal. Fitting the entire model on the fast half, VRAM, is worth roughly
ten times the throughput of splitting it. Spilling onto the slow half is a deliberate trade, not
an accident, and the only reason to make it is when the larger model's quality is worth the
speed. Knowing the exact cost of that trade is what the rest of this module measures.

The next lesson examines quantization: the variable that decides how much of a given model fits
the fast half in the first place. A tighter quant can pull a model that currently splits fully
onto the card, sometimes at surprisingly little quality cost.

## Core Concepts

- When a model exceeds VRAM, Ollama loads as many layers as fit on the GPU and runs the rest on
  the CPU from system RAM; this is partial layer offload, controlled by the `num_gpu` parameter.
- The `ollama ps` PROCESSOR column shows the GPU/CPU split; Ollama's fallback is silent, so
  reading this column is the only reliable way to confirm whether a split occurred.
- Token generation is memory-bandwidth-bound: the RTX 4060 Ti's VRAM runs at roughly 288 GB/s
  versus roughly 96 GB/s for DDR5-6000 system RAM, a 3:1 gap that makes CPU-resident layers far
  slower to serve.
- VRAM and system RAM form one combined pool Ollama can span, but the two halves are not equal;
  fitting the model on the fast half is worth roughly an order of magnitude in throughput.

<div class="claude-handoff" data-exercise="exercises/module4/when-a-model-doesnt-fit/">

**Build It in Claude Code**: Pull a model larger than your VRAM (for example `qwen2.5-coder:32b`), run `ollama ps` during a generation, and record the GPU/CPU split you observe along with a one-line explanation of why the CPU-resident layers slow generation down.

</div>

<!-- SOURCES: https://github.com/ollama/ollama/blob/main/docs/faq.mdx | https://github.com/ollama/ollama/issues/14258 | https://ollama.com/library/qwen2.5-coder/tags | https://knightli.com/en/2026/04/19/ollama-multiple-gpu-notes/ | https://www.techpowerup.com/review/nvidia-geforce-rtx-4060-ti-16-gb/ | https://modelfit.io/gpu/rtx-4060-ti/ -->
