# Quantization and Mixed Precision

Precision is a memory dial. Turn it down where the gradient can tolerate it,
keep it up where the loss is computed, and a model that would not fit in VRAM
suddenly does. This lesson explains the two levers, shows the reference patterns,
and gives you the math to know exactly what you are trading.

## Memory Per Element: The Math Behind the Dial

Every parameter in a model costs bytes. The cost per element by dtype:

| dtype | bits | bytes per element |
|-------|------|-------------------|
| fp32 | 32 | 4 |
| fp16 / bf16 | 16 | 2 |
| int4 (nf4) | 4 | 0.5 |

A 7B-parameter model in fp32 requires roughly 28 GB of memory for weights alone.
The same model in int4 requires around 3.5 GB. That is the QLoRA bargain: quantize
the frozen base to 4-bit, and a model that needed a large multi-GPU rig fits on a
single consumer card.

The cost of int4 is that you cannot run gradients through 4-bit weights directly.
QLoRA sidesteps this by never trying: the base is frozen, so it never receives a
gradient. Only the adapter parameters train, and those stay in bf16.

## QLoRA: The Frozen Base Shrinks, the Adapter Stays Full

QLoRA stacks two ideas from the previous lessons: the LoRA freeze pattern from L2,
and 4-bit quantization of the frozen portion. The adapter parameters remain in bf16
and receive gradients normally. The only new ingredient is the quantization config.

The reference config, from the `peft` + `bitsandbytes` library:

```python
# REFERENCE ONLY: peft + bitsandbytes required; not run in this book.
# Run this pattern on a GPU-backed environment with the libraries installed.
from transformers import AutoModelForCausalLM
import torch
from peft import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B",
    quantization_config=bnb_config,
    device_map="auto",
)
```

Source: https://huggingface.co/docs/peft/en/task_guides/lora_based_methods/qlora

Three parameters do the work:

- `load_in_4bit=True` quantizes the base weights to 4-bit on load.
- `bnb_4bit_quant_type="nf4"` selects the Normal Float 4 quantization scheme,
  which distributes quantization levels to match the expected normal distribution
  of model weights and loses less information than a uniform int4 grid.
- `bnb_4bit_compute_dtype=torch.bfloat16` sets the dtype for the dequantized
  compute that happens during the forward pass. The weight is stored in 4-bit,
  dequantized to bf16 for the matrix multiply, then the result is passed forward.

The adapter you attach on top of this config trains exactly as in L2. The only
difference is that the frozen base lives in 4-bit rather than fp32.

## AMP: Running the Forward in Lower Precision

Automatic Mixed Precision (AMP) is a different lever. Where QLoRA quantizes stored
weights, AMP changes the dtype of the forward computation at runtime. The forward
pass runs in fp16 or bf16; the loss and the backward pass stay in fp32 where
numerical accuracy matters most.

The PyTorch AMP recipe (https://docs.pytorch.org/tutorials/recipes/recipes/amp_recipe.html)
shows the pattern. The forward runs inside `torch.autocast`:

```python
# AMP training loop: runs on CPU (bf16) or GPU (fp16 or bf16).
# fp16 on GPU requires a GradScaler; bf16 does not.
import torch

scaler = torch.amp.GradScaler("cuda")   # remove for bf16 or CPU

for batch_inputs, batch_labels in train_loader:
    optimizer.zero_grad()

    with torch.autocast(device_type="cuda", dtype=torch.float16):
        logits = model(batch_inputs)                 # forward in fp16
        loss = loss_fn(logits.float(), batch_labels) # cast back to fp32 for loss

    scaler.scale(loss).backward()   # scale before backward to prevent underflow
    scaler.step(optimizer)
    scaler.update()
```

Source: https://docs.pytorch.org/tutorials/recipes/recipes/amp_recipe.html

The `logits.float()` cast before the loss function is not optional. Many loss
functions (cross-entropy in particular) accumulate in fp32 internally, but passing
fp16 logits can still produce underflow on extreme values. Cast explicitly; pay
one type conversion, avoid a silent numerical failure.

## Why fp16 Needs a GradScaler and bf16 Usually Does Not

The difference is in the exponent range of the two formats.

fp16 has a 5-bit exponent, giving a maximum representable value around 65,504.
Gradients during the backward pass are often very small: values below the fp16
minimum positive normal (~6e-5) flush to zero. This is gradient underflow, and it
silently stops learning. The `GradScaler` multiplies the loss by a large scale
factor before the backward pass, shifting the gradient magnitudes into the
representable range, then divides the gradients back out before the optimizer step.

bf16 has an 8-bit exponent, the same range as fp32. The mantissa is smaller (7
bits vs. 23 for fp32), so bf16 is less precise, but underflow is not the
characteristic failure mode. Most bf16 training runs omit the scaler. If you do
use a scaler with bf16, it adds overhead without benefit.

On CPU, `torch.autocast` supports bf16 but not fp16. The speedup on CPU is modest
compared to GPU (where tensor cores run fp16/bf16 much faster than fp32). Knowing
the mechanism on CPU means you apply it correctly on real hardware.

## `torch.compile`: Kernel Fusion for Throughput

`torch.compile` is a third dial. It does not change weight precision or dtype; it
fuses the graph of operations the model executes into fewer, more efficient CUDA
kernels. The interface is one line:

```python
model = torch.compile(model)
```

Three compilation modes trade compilation time for runtime throughput:

- `default`: a balanced compile; the right starting point.
- `reduce-overhead`: more aggressive graph capture, faster iteration, suited to
  fixed-shape inputs.
- `max-autotune`: exhaustive kernel search; highest throughput, longest compile
  time; use before a long training run, not for interactive work.

`torch.compile` performs best on recent NVIDIA CUDA hardware. CPU support is
experimental as of PyTorch 2.x. On a GPU, it routinely provides 10-30% throughput
gains on top of AMP, with no change to the model's math.

Source: https://docs.pytorch.org/docs/stable

## Honesty About Hardware

QLoRA's 4-bit quantization, `bitsandbytes`, and `torch.compile` deliver their
largest gains on GPU. This book's spine runs on CPU. The point of teaching these
mechanisms here is not to run them: it is to give you the math and the pattern so
you recognize what a production config is doing and can reason about it without
guessing.

When you bring a fine-tuning job to a GPU machine, the QLoRA config snippet above
is the one you reach for. The AMP loop above is the one you wrap your forward pass
in. The memory math (fp32=4B, bf16=2B, int4=0.5B) is the one you use to estimate
whether your model fits before you start the job.

The mechanisms are learnable here. The hardware to run them scales from a free-tier
Colab GPU to a dedicated instance. The reader who understands the mechanism adapts
to either.

The through-line of this module is a dial: precision is memory and speed traded
against gradient fidelity. Turn it down at the base weights where the gradient does
not flow (QLoRA). Turn it down in the forward pass where the computation is cheapest
to approximate (AMP). Leave it at fp32 where the loss is computed. Know exactly
what you are trading at each step, and the dial is yours to set.

## Core Concepts

- Memory cost per parameter scales with dtype: fp32 is 4 bytes, fp16/bf16 is 2 bytes,
  int4 is 0.5 bytes. A 7B model shrinks from 28 GB to 3.5 GB moving from fp32 to 4-bit;
  the math is the decision, not intuition.
- QLoRA quantizes the frozen base to 4-bit and keeps the trainable adapters in bf16.
  Gradients never touch the 4-bit weights because those weights are frozen; the adapter
  stays full precision and trains normally.
- AMP runs the forward pass in fp16 or bf16 and casts logits back to fp32 before the loss.
  Always cast explicitly; relying on implicit promotion misses edge cases that produce silent
  numerical failure.
- fp16 needs a `GradScaler` because its 5-bit exponent cannot represent the small gradient
  values the backward pass produces; bf16's 8-bit exponent matches fp32's range and usually
  does not need one.
- `torch.compile` fuses the operation graph into fewer kernels for throughput gains with no
  change to the model's math. It is a production-only optimization: run it on real CUDA hardware,
  not as part of learning the mechanism.
- Precision is a memory dial. Turn it down where the gradient can tolerate it, keep it up where
  the loss is computed, and know the byte cost of every setting before you choose.

<div class="claude-handoff" data-exercise="exercises/module4/quantization-and-mixed-precision/">

**Build It in Claude Code**: Compute the memory footprint of a model's weights at fp32, bf16, and int4 for a range of parameter counts (1M, 7B, 70B), print a comparison table, and confirm the 8x shrink from fp32 to int4. Then write an AMP training loop for a small `TinyClassifier` using `torch.autocast` on CPU with `dtype=torch.bfloat16`, cast logits to fp32 before the loss, run ten steps, and print the loss at each step to confirm training proceeds. Explain in a comment where you would add a `GradScaler` if you were running fp16 on GPU, and why bf16 on CPU does not need one.

</div>
