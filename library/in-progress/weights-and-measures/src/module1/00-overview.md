# Module 1: The PyTorch Operator

The hiring screen asks for PyTorch. What the job tests is whether you can read, run, modify, and
verify a training script without reaching for a tutorial. This module builds that foundation: tensors,
autograd, `nn.Module`, the training loop, data loading, checkpointing, and the discipline to know
whether the whole thing is actually doing what you intended.

The through-line starts here. Every lesson frames its mechanics around one question you will carry
into every job that touches a training script: **how do I know this is doing what I think?** That
question is not a detour from PyTorch; it is the point of PyTorch.

## Four Lessons

1. **Tensors and Autograd** (`tensors-and-autograd`): a tensor is an array plus `device` and
   `requires_grad`; autograd is the bookkeeping you do not write. You create tensors, check their
   shape, dtype, and device, build a two-parameter toy, call `backward`, and verify the gradients by
   hand against the engine. The lesson installs the reflex: check the tensor before you trust it.

2. **The Module and the Loop** (`the-module-and-the-loop`): `nn.Module` is the model contract; the
   training loop is five steps in a fixed order. You define a small module, write the loop, log per-
   batch loss, and print trainable versus total parameter counts. That count is the precondition for
   the M4 LoRA freeze: you cannot freeze what you have not counted.

3. **Data, Optimizers, and Checkpoints** (`data-optimizers-checkpoints`): `DataLoader` batches,
   shuffles, and parallelizes; the optimizer and one schedule drive the updates; `state_dict` is the
   checkpoint artifact. You wrap a dataset, add Adam with a step schedule, save a checkpoint, reload
   it, and assert the forward pass matches. Reload-and-assert is not optional; it is the gate.

4. **Reading a Real `train.py`** (`reading-a-real-train-py`): the payoff. Take an unfamiliar
   training script, name what each section asserts, add the two-batch smoke test, then run
   `check_loop.py` against your loop and make it pass. A loop is not done because it runs; it is done
   when a validator confirms the five steps are wired in the right order with trainable-parameter
   verification present.

## What This Module Feeds Forward

The loop you build here is the scaffold every later module modifies in place. M4 inserts LoRA
adapters into it; M5 attaches the eval gate. The verify discipline is not a module-one exercise it
is the book's spine: every technique that follows is only trustworthy if you can confirm it is
doing what you think.
