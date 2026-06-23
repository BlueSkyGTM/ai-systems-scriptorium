# Module 4: Adapters and the Fine-Tune Build

M1 built the training loop. M2 decided when to stop. M3 cleaned the data before the loop ran.
This module fine-tunes a model without touching the base weights.

The default assumption is wrong. When you have a good pre-trained model, full fine-tuning updates
every weight at four times the model's memory cost, writes a full-size checkpoint per task, and
risks overwriting the broad knowledge the base carries. Adapters flip this default: freeze the
base, train a small delta, ship one adapter file per task. The swap is not retraining. It is
loading a thin file that patches the frozen model for a specific behavior.

The thesis of this module: the cheapest fine-tune updates the fewest weights that still move
the metric.

## Four Lessons

1. **Why Adapters** (`why-adapters`): the memory, storage, and forgetting costs of updating every
   weight; the adapter idea: freeze the base, train a small delta; one adapter per task, swap not
   retrain.

2. **LoRA from the Inside** (`lora-from-the-inside`): the low-rank decomposition
   `dW = (alpha/r) * B * A`, which layers get adapters, how to implement `LoRALinear` in pure
   torch, and how to read the trainable-vs-total ratio to confirm the freeze.

3. **Quantization and Mixed Precision** (`quantization-and-mixed-precision`): QLoRA (quantize the
   frozen base to 4-bit, train adapters in bf16) as a memory lever; AMP (`autocast` +
   `GradScaler`) and `torch.compile` for single-GPU efficiency; the byte-cost math.

4. **The Fine-Tune Build** (`the-fine-tune-build`): the complete build: wrap the model with LoRA,
   train only the adapter via the `fit()` loop from M2, save the checkpoint, call `merge()` to
   fold the adapter back into a plain linear for inference, and confirm trainable << total. `peft`
   as the production path.

## What This Module Feeds Forward

The trained adapter checkpoint produced in L4 is what M5 runs the eval gate on. M5 asks: is this
adapter actually better? The answer requires a metric, not a loss curve. M6 wraps the full
pipeline (curate, train, eval) into a portfolio artifact. The adapter produced here is the thing
M6 makes reproducible.
