# Exercise: Tensors and Autograd

## Goal

Build a small verification script that creates tensors, reads their `shape`, `dtype`, and `device`,
constructs a two-parameter toy computation, calls `backward`, and confirms the gradients by hand
against the autograd engine. The script must be runnable offline, no dataset required.

## Why

Every model failure that is not a hyperparameter problem is a tensor problem: wrong dtype, wrong
device, wrong shape entering the layer. Installing the habit of checking those three properties
before trusting any tensor is what separates an engineer who debugs quickly from one who
restarts training and hopes. This exercise builds that reflex before anything more complex depends
on it.

## Steps

1. Create `exercises/module1/tensors-and-autograd/verify_tensors.py`.

2. At the top, import `torch` and print the runtime version:

   ```python
   import torch
   print("torch:", torch.__version__)
   ```

3. Create a 2x2 float tensor `x` and print its `shape`, `dtype`, and `device`. Confirm all three
   are what you expect before moving on.

4. Build a two-parameter toy: a scalar weight `w` and bias `b`, both with `requires_grad=True`.
   Compute a predicted value and a scalar loss, then call `loss.backward()`. Print `w.grad` and
   `b.grad`.

5. Verify the gradients by hand in a comment block. For a loss of the form
   `(w * x_val + b - y_true) ** 2`, the partial derivatives are derivable with the chain rule.
   Write out the calculation and confirm the printed values match.

6. Add an assertion block that fails loudly if either gradient is `None` or zero:

   ```python
   assert w.grad is not None and w.grad.abs() > 0, "w gradient is missing or zero"
   assert b.grad is not None and b.grad.abs() > 0, "b gradient is missing or zero"
   print("gradient assertions passed")
   ```

7. Add a short comment explaining what would happen if you ran a second forward-backward pass
   without calling `optimizer.zero_grad()` (or `.grad.zero_()`) first. One or two sentences.

## Done When

`python verify_tensors.py` exits 0 and prints:

- The torch version.
- The shape, dtype, and device of `x`.
- The values of `w.grad` and `b.grad`.
- The hand-derivation comment is present in the file and the numbers match what prints.
- `gradient assertions passed`.

The whole script runs in under five seconds on CPU.

## Estimated Time

20 to 30 minutes.

## Stretch

Add a device-transfer check: create `x` on CPU, call `.to("cuda")` inside a `try/except`, and
print whether CUDA is available (`torch.cuda.is_available()`). If CUDA is not present, the
`except` branch prints a message and continues rather than crashing. Confirm `.device` on the
result.
