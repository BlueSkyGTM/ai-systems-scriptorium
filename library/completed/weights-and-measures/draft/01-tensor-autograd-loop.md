# Tensors, Autograd, and the Training Loop

Every fine-tuning script you will ever read is a thin wrapper around four operations: create a
tensor, run it forward through a model, compute a loss, call `loss.backward()`. The rest is
bookkeeping. This lesson puts those four operations under a microscope, not because the
operations are complex but because the engineer who understands what each one does can debug
any training script that breaks — and every training script eventually breaks.

The goal is not fluency in every PyTorch API. The goal is the ability to read a `train.py`,
understand what each section is asserting about your data and your model, and verify that the
assertions hold before a long training run burns your compute budget.

## Tensors Are Not Arrays

A PyTorch tensor is a multidimensional array with two properties a NumPy array lacks: a
`device` attribute (CPU or a specific GPU) and a `requires_grad` flag. Both matter in
practice.

Device placement is explicit. A tensor created on CPU and a tensor sitting on `cuda:0` cannot
be added together; PyTorch will raise a `RuntimeError` rather than silently do something wrong.
The discipline this enforces is good: you always know where your data lives [MS-Learn: Azure ML
PyTorch training, device and compute configuration].

```python
import torch

x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])   # CPU, dtype=float32
x_gpu = x.to("cuda:0")                         # explicit device transfer

print(x.device)       # cpu
print(x_gpu.device)   # cuda:0
print(x.shape)        # torch.Size([2, 2])
print(x.dtype)        # torch.float32
```

The three attributes to check on any tensor entering your model: `shape`, `dtype`, and
`device`. If any of the three is wrong, the model will either error immediately or, worse, silently
produce garbage. Checking them is not optional ceremony; it is the first line of debugging.

### Dtype Discipline

Float32 is the default training dtype. Float16 and BFloat16 appear in mixed-precision runs
(covered in M4). The trap is integer dtypes: labels for a classification task are usually
`torch.long` (int64), not float. Passing float labels to `nn.CrossEntropyLoss` raises an
error; passing long features to a linear layer also raises an error. Every tensor has a dtype
and the dtype must match what the next operation expects.

## Autograd: The Bookkeeping You Do Not Write

Backpropagation in PyTorch is not implemented by the engineer. It is generated automatically
by the autograd engine, which records every operation applied to tensors that have
`requires_grad=True` and uses that record to compute gradients on demand.

The mechanism is a directed acyclic graph built at runtime. Each forward operation adds a node.
`loss.backward()` traverses the graph in reverse, applying the chain rule at each node, and
deposits the result into each leaf tensor's `.grad` attribute.

```python
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(0.5, requires_grad=True)

x = torch.tensor(3.0)
y_true = torch.tensor(7.0)

y_pred = w * x + b            # forward pass: y_pred = 6.5
loss = (y_pred - y_true) ** 2 # scalar loss: (6.5 - 7)^2 = 0.25

loss.backward()               # backward pass: fills w.grad, b.grad

print(w.grad)  # d(loss)/dw = 2*(y_pred - y_true)*x = 2*(-0.5)*3 = -3.0
print(b.grad)  # d(loss)/db = 2*(y_pred - y_true)*1 = 2*(-0.5)*1 = -1.0
```

Verify the gradients by hand on a toy example before trusting the engine on a large model.
The exercise accompanying this lesson asks you to do exactly that.

### Gradient Accumulation and Zero

The `.grad` attribute accumulates. If you call `loss.backward()` twice without zeroing
gradients between steps, the second backward adds to the first. This is occasionally
intentional (gradient accumulation across micro-batches), but almost always a bug when it
is not intended.

The training loop must call `optimizer.zero_grad()` before each forward pass, or the
gradients from the previous batch corrupt the current one. No amount of hyperparameter tuning
fixes accumulated garbage gradients.

## `nn.Module`: the Model Contract

PyTorch models are subclasses of `nn.Module`. The contract is minimal: implement `__init__`
(define layers, register parameters) and `forward` (define the computation). The base class
handles parameter registration, device movement (`.to(device)`), and the serialization
`state_dict()` that checkpointing depends on.

```python
import torch.nn as nn

class TinyClassifier(nn.Module):
    def __init__(self, input_dim: int, num_classes: int):
        super().__init__()
        self.linear = nn.Linear(input_dim, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)   # shape: [batch, num_classes]

model = TinyClassifier(input_dim=128, num_classes=4)
print(sum(p.numel() for p in model.parameters()))  # 516 parameters
```

The parameter count check is not cosmetic. For a fine-tuning run, you compare total parameters
against trainable parameters — the ratio tells you whether your adapter (LoRA) is actually
frozen the base and training only the adapter weights. If the numbers are wrong, the freeze
did not work.

## The Training Loop

All four operations assembled into the canonical single-epoch training loop:

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device,
) -> float:
    model.train()
    total_loss = 0.0

    for batch_inputs, batch_labels in loader:
        # 1. Device transfer
        batch_inputs = batch_inputs.to(device)
        batch_labels = batch_labels.to(device)

        # 2. Zero accumulated gradients
        optimizer.zero_grad()

        # 3. Forward pass
        logits = model(batch_inputs)

        # 4. Loss
        loss = loss_fn(logits, batch_labels)

        # 5. Backward pass
        loss.backward()

        # 6. Parameter update
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(loader)
```

Each step is labeled deliberately. In a production script these labels are absent, and that is
fine once you have internalized the pattern. Until then, name what each line is doing when you
write a new loop.

### What to Log from the Loop

`loss.item()` extracts the scalar loss value from the computation graph and returns a plain
Python float. Log it per batch. Log the learning rate from the scheduler if you have one.
Log the step count. These three values, written to MLflow or printed to stdout, are the
minimum that lets you diagnose a training run that goes wrong [MS-Learn: Azure Databricks
MLflow deep learning workflow and tracking].

A training run with no per-batch logging is a black box. You find out something went wrong
at the end of the epoch, with no information about when.

## `DataLoader`: Batching Is Not Free

`torch.utils.data.DataLoader` handles batching, shuffling, and (optionally) multi-process
data loading. The parameters that matter for a fine-tuning run:

- `batch_size`: affects gradient quality and memory. Larger batches smooth gradients but
  require more GPU memory; use gradient accumulation to simulate large batches on a small GPU.
- `shuffle=True`: shuffle training data every epoch; never shuffle validation data.
- `num_workers`: number of background processes loading data. Zero means single-process,
  which is safe but slow. On a single GPU, 2-4 workers is a common starting point.
- `pin_memory=True`: allocates tensors in pinned memory for faster GPU transfer. Use it when
  your bottleneck is data loading, not when you have no idea where the bottleneck is.

The correct place to discover the right `num_workers` value is the profiler, not a blog post.
`torch.profiler` (covered in M4) shows whether your GPU is idle waiting for data or busy
computing. Set `num_workers` after you know the answer.

## Verify the Loop Before You Scale It

Before running a full training loop on real data, run it for two batches with a tiny dataset
and check three things:

1. Loss decreases from batch 1 to batch 2 (the model is learning something).
2. `model.parameters()` includes all the weights you expect to train (the right layers are
   unfrozen).
3. The tensor shapes printed inside the loop match your model's expected input dimensions.

This two-batch smoke test takes under a minute and catches the majority of bugs that would
otherwise surface after an hour of GPU time [MS-Learn: Azure Machine Learning PyTorch training
job, configure and submit].

## Core Concepts

- A PyTorch tensor carries three attributes that determine compatibility with any operation:
  `shape`, `dtype`, and `device`; mismatches raise errors rather than silently corrupt results.
- Autograd builds a computation graph at runtime; `loss.backward()` traverses it in reverse to
  deposit gradients into `.grad` on every leaf tensor with `requires_grad=True`.
- `optimizer.zero_grad()` must precede every forward pass; accumulated gradients from prior
  batches corrupt the current update.
- `nn.Module` is the model contract: `__init__` registers parameters, `forward` defines the
  computation, and `state_dict()` is the checkpoint artifact.
- The training loop is five steps in order: device transfer, zero grad, forward, loss,
  backward, optimizer step; label each step until the pattern is reflexive.
- Log `loss.item()`, the learning rate, and the step count every batch; a loop with no
  per-batch logging is a black box.
- Verify the loop for two batches on a tiny dataset before scaling; check loss decreases,
  parameter count matches expectations, and shapes are correct.

<div class="claude-handoff" data-exercise="draft/exercises/01-tensor-autograd-loop/">

**Build It in Claude Code**: Build a minimal PyTorch training loop from scratch for a toy
classification task. Implement a two-layer `nn.Module`, write the five-step training loop,
add per-batch MLflow logging of loss and learning rate, and write a smoke test that verifies
loss decreases over two batches and that all expected parameters are trainable. The loop must
run on CPU in under 30 seconds.

</div>
