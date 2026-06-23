# Why Adapters

Full fine-tuning costs more memory than most people expect, and for most tasks, it costs more than the task is worth.

That gap between what full fine-tuning requires and what the task actually demands is where adapters live.

## The Memory Bill for Full Fine-Tuning

When you update every weight in a model, the memory bill arrives in four line items.

The first is the parameters themselves. A 7B-parameter model in `float32` costs 4 bytes per parameter: 28 GB before a single gradient fires.

The second is the gradients. The backward pass produces one gradient tensor per parameter, the same shape as the weights. That is another 28 GB.

The third is the optimizer state. Adam is the standard choice, and it keeps two running statistics for every parameter: a first moment (a moving average of the gradient) and a second moment (a moving average of the squared gradient). Those are two more copies of the parameter tensor: 56 GB.

Add them up: parameters plus gradients plus Adam's two state buffers is roughly 4x the model's weight memory. A 7B model at `float32` needs around 112 GB just to run the optimizer step. The forward pass has not been counted yet.

The fourth is the activation cache. The backward pass reuses activations from the forward pass to compute gradients. A naive implementation caches every intermediate tensor for every layer. For a large model on a long sequence, that activation cache can easily match or exceed the weight memory on its own.

Three levers exist to reduce peak memory without abandoning full fine-tuning entirely. Gradient checkpointing recomputes activations on the backward pass rather than caching them; the activation footprint drops to roughly O(sqrt(layers)) at the cost of a second forward pass. Gradient accumulation trains on smaller micro-batches and sums gradients before the optimizer step, reducing the per-step activation memory. Optimizer-state offload moves Adam's first and second moments to CPU RAM, trading memory for a transfer latency penalty on each step. None of these change the fundamental cost: you are still updating every weight in the model, and you are still writing a full-size checkpoint each time.

That checkpoint is its own problem. A fine-tuned 7B model at `float32` produces a 28 GB checkpoint file. If you are tuning one model for ten different tasks, you are writing ten copies of those 28 GB. Serving them means loading and swapping full model copies. Storage and serving costs scale linearly with task count.

## The Forgetting Risk

There is a fifth cost that does not appear in any memory profiler: catastrophic forgetting. When you update every weight for Task A, the model forgets what it knew for Task B. For a general-purpose base model, that erosion of broad capability is often the thing you wanted to preserve. Full fine-tuning has no mechanism to protect it; the optimizer's only job is to minimize the loss on Task A's training data.

## The Adapter Idea

Adapters reframe the problem. Instead of asking "how do we update all the weights cheaply?", they ask which weights actually need to move.

The answer, empirically, is a small fraction. The base model's weights encode a large, general representation; the task-specific adaptation lives in a small delta on top of that representation. Adapters exploit this by freezing the base model entirely and training only a small set of new parameters attached to specific layers.

The memory consequences are direct. No gradients flow through the frozen base parameters; the backward pass skips them entirely. Adam's optimizer state covers only the adapter parameters, not the full model. The activation cache is the same as any inference pass through the frozen layers, plus the small adapter layers. In practice, training a LoRA adapter on a 7B model can run in a fraction of the VRAM a full fine-tune would need.

The checkpoint consequence is equally direct. The trained adapter is the delta, not the full model. From the HF `peft` docs at https://huggingface.co/docs/peft/en/quicktour, a LoRA adapter on a 350M-parameter model produces a checkpoint of roughly 6-7 MB. The base model is shared; only the small adapter ships per task. Serving ten tasks means loading one base model and swapping ten small adapter files, not ten full-size checkpoints.

Catastrophic forgetting is structurally avoided. The base weights never change; they cannot be overwritten by the task gradient. The task-specific knowledge lives entirely in the adapter, separate from the base representation.

## The Cost Principle

The cheapest fine-tune updates the fewest weights that still move the metric. Full fine-tuning updates every weight because the default loop touches everything. Adapters are the mechanism for making "fewest weights" a deliberate choice rather than an accident of which loop you reached for.

This is not a frugality argument; it is a precision argument. Surgical updates to the weights that matter most for the task produce better-isolated, more-reusable models than wholesale updates that overwrite the base representation along with the task signal.

## Core Concepts

- A full fine-tune in `float32` costs roughly 4x the model's weight memory: parameters plus gradients plus Adam's two optimizer-state buffers; the activation cache adds more on top, and the result is one full-size checkpoint per task.
- Three memory levers reduce the peak cost without changing the fundamental price: gradient checkpointing recomputes activations rather than caching them (~O(sqrt(layers)) peak), gradient accumulation reduces per-step activation memory, and optimizer-state offload moves Adam's moments to CPU RAM.
- Catastrophic forgetting is a structural risk in full fine-tuning: the optimizer updates every weight for Task A and erodes what the model knew before, with no mechanism to protect the base representation.
- Adapters freeze the base model and train only a small delta: one small adapter file per task (a few MB), swapped at serving time; no gradients through the base, Adam state only over the adapter, base knowledge structurally preserved.
- The principle that unifies both: the cheapest fine-tune updates the fewest weights that still move the metric.

<div class="claude-handoff" data-exercise="exercises/module4/why-adapters/">

**Build It in Claude Code**: For a model of your choice (e.g., 350M or 7B parameters), compute the full fine-tune memory estimate in `float32`: parameter bytes (4 bytes per param), gradient bytes (same), and Adam's two optimizer-state buffers (8 bytes per param total); sum them to get the optimizer-step floor before any activation cache. Then estimate the adapter fine-tune: pick a LoRA rank (e.g., r=8, targeting `q_proj` and `v_proj` in each transformer block), compute how many adapter parameters that adds, and apply the same four-term formula to the adapter parameters only. Print both totals and the ratio; write a two-sentence argument, in code comments, for why the ratio is the right way to report the savings rather than the raw byte difference.

</div>
