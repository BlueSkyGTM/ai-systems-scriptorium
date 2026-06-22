# The Module and the Loop

Every PyTorch training script is an `nn.Module` and a five-step loop. The module contracts what
your model owns; the loop contracts what order the math runs in. Get either wrong and the model
trains, but it trains the wrong thing in the wrong direction, and nothing in the output tells you.

This lesson names what each piece asserts, shows the verified code, and introduces the
trainable-vs-total parameter check: the number you will revisit in Module 4 when you freeze a
model for LoRA and need to verify the freeze worked.

## `nn.Module`: the Model Contract

An `nn.Module` subclass is not a class with a `forward` method bolted on. It is a contract with
three parts:

- `__init__` registers parameters. Assign an `nn.Linear` (or any `nn.Module` child) to `self`
  inside `__init__`, and PyTorch tracks its weight tensors automatically. Assign a plain
  `torch.Tensor` to `self` and it is not tracked; `parameters()` will not see it.
- `forward` defines the computation. You call `model(x)`, not `model.forward(x)`. The base class
  `__call__` runs hooks, then dispatches to your `forward`.
- `state_dict()` is the checkpoint artifact. It returns an ordered dict of every registered tensor
  keyed by name. Save the `state_dict`, not the model object itself; the object carries class
  references that break across Python versions and refactors.

See the full contract at
[docs.pytorch.org/docs/stable/generated/torch.nn.Module.html](https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html).

## `TinyClassifier` and the Param Count

A single linear layer is enough to exercise the full contract. Copy `TinyClassifier` from
`trainer.py` verbatim:

```python
import torch.nn as nn

class TinyClassifier(nn.Module):
    def __init__(self, in_dim: int, n_classes: int) -> None:
        super().__init__()
        self.linear = nn.Linear(in_dim, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)  # [batch, n_classes]
```

Now count the parameters before doing anything else:

```python
model = TinyClassifier(128, 4)
total     = sum(p.numel() for p in model.parameters())
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(total, trainable)
```

The output, conductor-verified on torch 2.x CPU:

```
516 516
```

The math: `nn.Linear(128, 4)` holds a weight matrix of 128 * 4 = 512 values plus a bias of 4
values. All 516 are trainable by default because `requires_grad=True` on every `nn.Parameter`.

`516 516` is the baseline. In Module 4 you freeze the base model and add LoRA adapters. After that
freeze, `total` stays 516 but `trainable` drops to the adapter params only. If `trainable` still
reads 516 after the freeze, the freeze did not work. The param-count check is the precondition,
not a formality.

## The Five-Step Loop

The canonical training loop has five steps in a fixed order. Rearrange them and the math is wrong;
the error will not be loud.

Copy `train_one_epoch` from `trainer.py` verbatim:

```python
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    model.train()
    running = 0.0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)  # 1 device
        optimizer.zero_grad()                                   # 2 zero
        logits = model(inputs)                                  # 3 forward
        loss = loss_fn(logits, labels)                          # 4 loss
        loss.backward()                                         # 5 backward
        optimizer.step()                                        # 6 update
        running += loss.item()
    return running / len(loader)
```

What each line asserts:

**Step 1: device.** `inputs.to(device)` and `labels.to(device)` make both tensors live on the
same device as the model. A CPU tensor fed into a CUDA model raises `RuntimeError`; PyTorch will
not silently move data for you. The move is explicit by design.

**Step 2: zero.** `optimizer.zero_grad()` clears accumulated gradients from the previous batch.
Gradients accumulate by default: skip this step and batch N's gradient adds to batch N-1's. The
resulting update is wrong and nothing signals it.

**Step 3: forward.** `model(inputs)` dispatches through `nn.Module.__call__` to your `forward`
method. The autograd engine records every operation on this path, building the graph
`loss.backward()` will traverse.

**Step 4: loss.** `loss_fn(logits, labels)` produces a scalar. For classification, the standard
choice is `nn.CrossEntropyLoss`. Labels must be `torch.long`; passing float labels raises
immediately.

**Step 5: backward + step.** `loss.backward()` traverses the recorded graph and deposits
gradients into each leaf tensor's `.grad`. `optimizer.step()` reads those gradients and updates
the weights. The order is not negotiable: calling `optimizer.step()` before `backward()` updates
weights with stale gradients.

The `model.train()` call before the loop is not one of the five steps, but it is not optional
either. It switches layers like `Dropout` and `BatchNorm` from eval behavior to train behavior.
Forgetting it is a silent correctness bug that hides in aggregate metrics.

## What to Log Per Batch

`loss.item()` detaches the scalar from the computation graph and returns a plain Python float.
Log it every batch. Log the learning rate from the optimizer or scheduler. Log the global step.
Those three values are the minimum signal for diagnosing a run that degrades mid-epoch.

The production pattern comes from made-with-ml's `train_step`: accumulate a running mean rather
than summing and dividing at the end, so the per-batch metric is always current:

```python
running_loss += (loss.item() - running_loss) / (step + 1)
```

At eval, switch to `torch.inference_mode()` and call `model.eval()` before the validation loop.
`inference_mode` skips graph recording entirely; it is faster and uses less memory than
`torch.no_grad()` for pure inference passes.

A loop with no per-batch logging is a black box. You find out the epoch averaged poorly at the
end, with no information about which batch started the slide.

## Core Concepts

- `nn.Module.__init__` registers parameters by attribute assignment; `forward` defines the
  computation; `state_dict()` is the checkpoint artifact. Save the `state_dict`, not the object.
- The param-count check (`trainable == total` before any freeze) is the precondition for Module
  4's LoRA freeze: if `trainable` does not drop as expected after freezing, the freeze failed.
- The five steps are: device, zero_grad, forward, loss, backward+step. They run in exactly this
  order; rearranging any of them corrupts the update silently.
- Log `loss.item()`, learning rate, and step every batch; a loop with no per-batch logging gives
  you no diagnosis point when a run goes wrong mid-epoch.
- At eval, pair `model.eval()` with `torch.inference_mode()`: `model.eval()` switches Dropout and
  BatchNorm to inference mode; `inference_mode` skips graph recording and runs faster than
  `no_grad`.
- The verified param count for `TinyClassifier(128, 4)` is `516 516`: 512 weight values plus 4
  bias values, all trainable until a freeze changes that.

<div class="claude-handoff" data-exercise="exercises/module1/the-module-and-the-loop/">

**Build It in Claude Code**: Define a small `nn.Module` subclass (one or two linear layers) and
instantiate it. Print both `total` and `trainable` parameter counts using `model.parameters()`;
they should match before any freeze. Write the five-step `train_one_epoch` function with each step
labeled in a comment, run it for one epoch on a tiny synthetic dataset, and add per-batch logging
of `loss.item()`, the current learning rate, and the step number. Verify by running the loop and
confirming the logged loss prints every batch.

</div>
