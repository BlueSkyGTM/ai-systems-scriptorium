# A 14B Model on the Card

The runtime is installed and listening. The question now is whether the first model you pull
will actually serve fast, or whether it will quietly overflow into system RAM and crawl.

## Step 1: Pull the Model

Pull the default coding model for this build:

```bash
ollama pull qwen2.5-coder:14b
```

Ollama downloads the GGUF file, which is 9.0 GB on disk at the default tag. Confirm it arrived:

```bash
ollama list
```

What you should see:

```
NAME                      ID              SIZE    MODIFIED
qwen2.5-coder:14b         ...             9.0 GB  a few seconds ago
```

The SIZE column is disk size, not VRAM cost. That distinction matters: the two numbers are not
the same, and mixing them up is how a model ends up spilling.

## Step 2: Read the Tag

The default tag Ollama pulls is `Q4_K_M`. That string encodes the quantization scheme used to
compress the model weights. The short reading: `Q4` means four-bit weight quantization; `K_M`
is the variant within the GGUF "K-quant" family, where the quantizer uses block-wise scaling
to preserve more accuracy than a flat four-bit scheme would.

The published tags for `qwen2.5-coder:14b` span a range of sizes:

| Tag | Approximate Size |
|-----|-----------------|
| Q2_K | 5.8 GB |
| Q3_K_M | 7.3 GB |
| Q4_K_M | 9.0 GB |
| Q8_0 | 16 GB |
| FP16 | 30 GB |

Four-bit roughly halves the disk size versus eight-bit, because each weight takes half the bits.
That is why `Q4_K_M` fits a 16 GB card with room to spare, while `Q8_0` would consume the
entire card before a single token of context or any compute buffers. The deep tradeoff between
quantization level and output quality gets its own treatment in Modules 4 and 7; here the only
question is whether the tag fits the card.

## Step 3: Understand the Headroom

The 9.0 GB of weights on disk is not the VRAM cost at runtime. Loading and serving the model
also requires a KV cache for in-context attention and compute buffers for the forward pass.
The realistic loaded footprint for `qwen2.5-coder:14b` at Q4_K_M is roughly 10 to 12 GB,
depending on context length. On a 16 GB card, that leaves several GB of headroom for the
context window you will actually use.

Treat any specific number here as approximate: the exact figure shifts with context length
and Ollama version. The invariant is the inequality: weights + KV cache + buffers must
be less than total VRAM. On a 16 GB card at Q4_K_M, they are.

## Step 4: Prove Zero Overflow

Two checks confirm the model is running entirely on the GPU.

First, while the model is loaded, run:

```bash
ollama ps
```

What you should see:

```
NAME                 ID        SIZE    PROCESSOR    UNTIL
qwen2.5-coder:14b   ...        ...     100% GPU     4 minutes from now
```

The PROCESSOR column is the verdict. `100% GPU` means the entire model is resident in VRAM.
A reading like `30% CPU 70% GPU` means part of the model spilled into system RAM and is
serving across the system bus, which is roughly 10 to 50 times slower per token. If you see
a CPU split, drop to a smaller tag (for example, `qwen2.5-coder:7b`) and re-pull.

Second, run:

```bash
nvidia-smi
```

What you should see in the Memory-Usage column while the model is loaded:

```
|  0%   52C    P0             65W / 165W  |   11254MiB / 16380MiB  |     15%      Default |
```

The reference build shows roughly `11254MiB / 16380MiB`: the model, its KV cache, and buffers
together, comfortably under the 16380 MiB the card reports as usable. Your number will be close
but not identical; any reading below about 14000 MiB leaves enough headroom for the default
context window.

## Step 5: Know the Swap-ins

`qwen2.5-coder:14b` is the default for this build because it is a current coding model with
strong benchmark results at the Q4 size. Two alternatives swap in cleanly on a 16 GB card:

- `codellama:13b` (approximately 7.4 GB at the default tag) leaves more headroom if you need
  a larger context window or want to run a second lightweight model simultaneously.
- The `deepseek-coder` family is worth knowing, though the naming is non-obvious: there is no
  `deepseek-coder:14b`. The closest peer is `deepseek-coder-v2:16b` at roughly 8.9 GB, similar
  VRAM cost to the Qwen model.

Either alternative fits the card at their default tags. The reasoning that keeps a model on the
card does not change: check the tag size, load it, read `ollama ps`, confirm `100% GPU`.

Once `100% GPU` is yours, the card is doing real work at inference speed, not a throttled crawl
that only looks like local AI. The VRAM budget you leave unspent is not waste; it is the context
headroom that lets the model hold a full conversation.

## Core Concepts

- A quantization tag like `Q4_K_M` means four-bit K-quant weight compression; lower bit depth
  shrinks the model so it fits tighter VRAM budgets, at a quality tradeoff covered in later modules.
- The fits-on-card invariant is non-negotiable: weights plus KV cache plus compute buffers must
  stay below total VRAM, or every generated token pays a system-bus penalty.
- `ollama ps` with `100% GPU` in the PROCESSOR column is the proof of zero overflow; any CPU
  fraction in that column means the model has spilled and must be replaced with a smaller tag.
- The VRAM footprint at runtime is larger than the on-disk size; budget roughly 10 to 12 GB of
  VRAM for a 9.0 GB Q4_K_M model, not 9.0 GB.

<div class="claude-handoff" data-exercise="exercises/module3/a-14b-model-on-card/">

**Build It in Claude Code**: Create `exercises/module3/a-14b-model-on-card/MODELS.md` with the `## Serving Layer` and `## Models` sections, recording `qwen2.5-coder:14b`, its quantization, and its VRAM used against your 16 GB total. The next lesson finalizes this file and adds the validator.

</div>

<!-- SOURCES: https://ollama.com/library/qwen2.5-coder:14b | https://ollama.com/library/qwen2.5-coder/tags | https://huggingface.co/bartowski/Qwen2.5-Coder-14B-Instruct-GGUF | https://github.com/ollama/ollama/issues/10445 | https://github.com/ollama/ollama/issues/9704 | https://ollama.com/library/codellama -->
