# Exercise: When a Model Doesn't Fit

## Goal

Observe a partial offload on your own rig. Read the GPU/CPU split that `ollama ps` reports for a
model that exceeds VRAM, and note the throughput it produces.

## Why

You cannot reason about the VRAM-vs-system-RAM trade until you have seen it on your own hardware.
Representative numbers from the lesson show the shape of the gap; your rig's actual split and
speed are what you will compare in the Measure Latency lesson.

## Steps

1. Pull the model:

   ```bash
   ollama pull qwen2.5-coder:32b
   ```

2. Start a generation in one terminal (a long prompt helps keep the model loaded long enough to
   read):

   ```bash
   ollama run qwen2.5-coder:32b "Explain the transformer attention mechanism in detail."
   ```

3. In a second terminal, while the generation is running:

   ```bash
   ollama ps
   ```

4. Note the PROCESSOR column. Record the GPU/CPU split you see.

5. Optionally, watch the token output in the first terminal and estimate the rough speed. You do
   not need a precise number here; the Measure Latency lesson provides `bench.py` for that.

> **Note, no rig yet:** If you do not have the hardware set up, read the representative split
> from the lesson (`52% GPU / 48% CPU` on a 16 GB card, roughly 2 to 3 tokens per second) and
> treat this step as observation rather than measurement. You will record your own numbers with
> `bench.py` in the Measure Latency lesson.

## Done When

You can state, for a model that does not fit in your VRAM, the approximate GPU/CPU split
`ollama ps` reported and explain in one sentence why the CPU-resident layers slow generation down.

## Stretch

Pull the smaller quantization of the same model:

```bash
ollama pull qwen2.5-coder:32b-instruct-q2_K
```

This tag is roughly 12 GB on disk. Run `ollama ps` again and check whether the split changed:
the model may now fit entirely on the card, or the GPU fraction may have grown. Either outcome
is informative. A tighter quant changed the split; that is the core idea of the next lesson.
