# Tensors and Autograd

Before you can read a `train.py` or debug one that breaks, you need to trust the two primitives
underneath it: the tensor and the autograd engine. Most engineers treat them as a black box and
pay for it later, when a gradient is silently wrong and the model trains for hours before the
loss stops moving. This lesson puts both under a microscope.

## Tensors: Three Attributes That Cannot Be Wrong

A PyTorch tensor is a multidimensional array with two properties a NumPy array lacks: a `device`
attribute (CPU or a specific GPU) and a `requires_grad` flag. Three attributes determine whether
a tensor is compatible with the next operation in your pipeline:

```python
import torch

x = torch.tensor([[1., 2.], [3., 4.]])      # cpu, float32
print(x.shape, x.dtype, x.device)            # torch.Size([2, 2]) torch.float32 cpu
```

Real output, captured on torch 2.x:

```
torch.Size([2, 2]) torch.float32 cpu
```

Check `shape`, `dtype`, and `device` on every tensor entering a model. If any of the three is
wrong, PyTorch raises rather than silently producing garbage. That is the behavior you want: an
error you can read beats a loss curve that does not converge and gives you no clue why.

See the [PyTorch tensor reference](https://docs.pytorch.org/docs/stable/tensors.html) for the
full attribute table.

### Device Placement Is Explicit

A tensor on CPU and a tensor on `cuda:0` cannot be added together. PyTorch raises a
`RuntimeError` at the point of the operation, not at the end of the batch. Move tensors to the
right device with `.to(device)` before they enter any computation, and the error surface becomes
small and local instead of large and mysterious.

### Dtype Discipline

`float32` is the default training dtype. The trap is labels: classification targets are
`torch.long` (int64), not float. Pass float labels into `nn.CrossEntropyLoss` and it raises.
Pass integer features into a linear layer and it also raises. The dtype must match what the
next operation expects; no implicit cast saves you.

## Autograd: The Bookkeeping You Do Not Write

Backpropagation in PyTorch is generated automatically. Set `requires_grad=True` on a leaf tensor
and the autograd engine records every operation applied to it. Call `loss.backward()` and the
engine traverses that record in reverse, applying the chain rule at each step, depositing
results into each leaf's `.grad` attribute.

You do not implement this graph. The [autograd documentation](https://docs.pytorch.org/docs/stable/autograd.html)
describes it as a directed acyclic graph built at runtime: each forward operation adds a node,
`backward()` reverse-traverses the nodes.

What you do is verify it.

### The Two-Parameter Toy

Build the smallest possible example, derive the gradients by hand, and confirm the engine
agrees. Use `w * 3 + b` with a squared error loss:

```python
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(0.5, requires_grad=True)
y_pred = w * 3.0 + b                          # 6.5
loss = (y_pred - 7.0) ** 2                    # 0.25
loss.backward()
print(w.grad, b.grad)                         # tensor(-3.) tensor(-1.)
```

Real output:

```
tensor(-3.) tensor(-1.)
```

The hand-derivation: `y_pred = 2*3 + 0.5 = 6.5`; `loss = (6.5 - 7)^2 = 0.25`. Differentiating
with respect to `w`: `d(loss)/dw = 2*(y_pred - y_true)*3 = 2*(-0.5)*3 = -3.0`. With respect to
`b`: `d(loss)/db = 2*(y_pred - y_true)*1 = 2*(-0.5)*1 = -1.0`. The engine reports the same
numbers. If it did not, you would know something was wrong before running a real model for an
hour on GPU.

The through-line question for this book begins here: *how do I know this is doing what I think?*
The answer, at the level of gradients, is: compute by hand on a toy and check the engine. Do it
once and you trust the engine for the rest of the course. Skip it and every gradient is an act
of faith.

### Under the Hood (Conceptual Only)

The [aefs from-scratch source](https://github.com/karpathy/micrograd) shows what autograd is
doing: a `Value` class where each operation attaches a `_backward` closure, and a
reverse-topological-sort `backward()` that fires each closure in turn. You do not write this
class; PyTorch's C++ engine does the equivalent at high speed. The from-scratch version earns
its place as explanation, not as code you ship.

## Gradient Accumulation and `zero_grad`

The `.grad` attribute accumulates across `backward()` calls. Call it twice without zeroing and
the second backward adds its gradients to the first. Occasionally this is intentional: gradient
accumulation across micro-batches lets you simulate a larger batch on limited GPU memory. Almost
always, though, accumulated gradients from a prior batch corrupting the current update is a bug,
not a feature.

The fix is mandatory:

```python
optimizer.zero_grad()   # call this before every forward pass
```

No amount of learning-rate tuning recovers a loop that skips this step. The optimizer is moving
in the direction of the sum of all gradients ever computed, not the gradient of this batch.

## Core Concepts

- A PyTorch tensor carries `shape`, `dtype`, and `device`; mismatches raise a `RuntimeError`
  rather than silently corrupting results, so check all three before trusting any tensor.
- Autograd builds a directed acyclic graph at runtime; `loss.backward()` traverses it in reverse
  and deposits gradients into `.grad` on every leaf with `requires_grad=True`.
- Verify gradients by hand on a minimal toy before trusting the engine on a large model: derive
  on paper, confirm the engine matches, and the rest of the course runs on solid ground.
- Labels for classification are `torch.long`, not float; dtype mismatches raise at the point of
  the operation, not silently at training end.
- Device placement is explicit: `.to(device)` moves a tensor; mixing CPU and CUDA tensors in one
  operation raises immediately.
- Gradients accumulate across `backward()` calls; `optimizer.zero_grad()` before every forward
  pass is not optional, it is the correctness condition for the update.

<div class="claude-handoff" data-exercise="exercises/module1/tensors-and-autograd/">

**Build It in Claude Code**: Create a few tensors with different shapes and dtypes, print their
`shape`, `dtype`, and `device` to confirm the values, then build the two-parameter toy
(`w = 2.0`, `b = 0.5`, input `3.0`, target `7.0`), call `loss.backward()`, and verify `w.grad`
and `b.grad` against your hand-derivation. If the engine and your paper agree, you are done.

</div>
