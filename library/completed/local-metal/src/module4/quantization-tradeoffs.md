# Quantization Tradeoffs

Module 3 read a quant tag at face value and asked only one question: does it fit the card? This lesson is the reasoning under that tag. The choice of quantization is the single lever that decides whether a model fits in VRAM at all, and making that choice deliberately is what keeps you off the system bus.

## Step 1: Bits per Weight

A model's on-disk size follows a simple rule: multiply the parameter count by the bits per weight, then divide by eight to convert to bytes. The bits-per-weight value is determined by the quantization scheme.

According to the llama.cpp quantization table, the common schemes land at roughly:

| Scheme | Bits per Weight |
|--------|----------------|
| Q4_K_M | 4.9 |
| Q8_0 | 8.5 |
| F16 | 16.0 |

For a 32B model, those figures produce:

| Scheme | Estimated Size |
|--------|---------------|
| Q4_K_M | ~20 GB |
| Q8_0 | ~34 GB |
| F16 | ~64 GB |

Ollama lists the Q4_K_M variant of `qwen2.5-coder:32b` at 20 GB, which confirms the estimate. Lower bit depth, smaller file, and more of it fits on the card.

## Step 2: The Quality Cost

Fewer bits per weight means coarser weight representation and some quality loss. The standard measure is perplexity: a lower perplexity means the model is more confident and more accurate on held-out text. Q4_K_M lands around 1% higher perplexity than F16, meaning it delivers roughly 98% of the quality at about a quarter of the size. Q8_0 is near-lossless.

The practical reading: Q4_K_M is the standard sweet spot for local serving. The difference from full precision shows up as occasional wording variation, not factual errors. For a coding or chat use case, it is rarely perceptible.

Why does Q4_K_M hold quality so well for a four-bit scheme? K-quants use mixed precision inside a fixed-size super-block. Attention and output layers, which are more sensitive to rounding, get more bits; feed-forward layers, which are more redundant, get fewer. That structure is what makes K-quants outperform a naive flat four-bit quantization at the same average bit depth.

## Step 3: Choosing the Level for Your Card

The decision rule is: pick the highest quantization that still fits the model fully in VRAM with room for context.

On the 16 GB RTX 4060 Ti, consider two models:

- A 14B model at Q4_K_M is roughly 9 GB on disk and loads to about 10 to 12 GB in VRAM. That leaves several gigabytes for the KV cache. Q8_0 for the same 14B model would cost about 16 GB, consuming the entire card before a single token of context fits.
- A 32B model at Q4_K_M is roughly 20 GB. It exceeds the 16 GB card outright, which is exactly why it spilled in the previous lesson. Q8_0 would reach 34 GB, and F16 would reach 64 GB; neither fits at all.

Quantization is how you slide a large model down to a size the card can hold. You work from the best quality downward until the model fits with context headroom remaining. When you reach the lowest reasonable scheme and the model still does not fit, you face a genuine choice: accept the GPU/CPU split and pay the speed penalty, or switch to a smaller model that fits entirely on the card.

## Step 4: The Deeper Tuning Is Later

Choosing a model and quant that fit on the card is a one-time decision per model; it is not the last word on performance. KV-cache quantization, layer offload tuning, and profiling tokens per second under realistic load are Module 7. The goal here is to enter that module with a model that fits, so the profiling numbers reflect GPU throughput rather than system-bus drag.

Once you know how to read a quant tag, size a model, and apply the highest-that-fits rule, the mechanical part of the decision is fast. The rest is measuring what the choice actually costs in tokens per second.

## Core Concepts

- A model's on-disk size equals its parameter count times bits-per-weight divided by eight; Q4_K_M at 4.9 bits/weight, Q8_0 at 8.5, and F16 at 16 set the three common anchors.
- Lower bit depth degrades quality, measured as perplexity; Q4_K_M lands around 1% higher perplexity than F16 (roughly 98% of the quality) while K-quants' mixed-precision super-blocks hold quality better than flat four-bit schemes.
- Q4_K_M is the standard sweet spot for local serving: near-indistinguishable output, a quarter of the full-precision size, and the default that Ollama pulls when no tag is specified.
- The selection rule is highest-that-fits: start from the best quantization and step down until the model fits in VRAM with context headroom; when none fit, either accept the split or choose a smaller model.

<div class="claude-handoff" data-exercise="exercises/module4/quantization-tradeoffs/">

**Build It in Claude Code**: Create `exercises/module4/quantization-tradeoffs/vram_fit.py`, a stdlib-only planner that estimates a model's VRAM footprint from its parameter count and bits-per-weight, then prints whether it FITS or SPILLS against your card's VRAM budget.

</div>

<!-- SOURCES: https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md | https://ollama.com/library/qwen2.5-coder/tags | https://willitrunai.com/blog/quantization-guide-gguf-explained | https://www.promptquorum.com/local-llms/llm-quantization-explained -->
