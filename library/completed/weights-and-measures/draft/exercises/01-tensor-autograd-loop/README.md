# Exercise: Tensors, Autograd, and the Training Loop

## Goal

Build a minimal but complete PyTorch training loop for a toy multiclass classification task.
The loop must be correct (five steps in order, gradients zeroed, per-batch logging) and
verifiable (a smoke test that proves it learns and that the right parameters are training).

## Why

The training loop is the seam every fine-tuning script modifies. You do not get to adapt
a LoRA trainer or attach an eval gate until you can write and verify the loop from scratch.
This exercise builds that base; every later module modifies it without replacing it.

## Steps

1. Create a project directory `m1-training-loop/` with a `src/` package. Add `torch` and
   `mlflow` to your dependencies.

2. Implement `src/model.py` with a `TinyClassifier(nn.Module)`:
   - `__init__(self, input_dim, hidden_dim, num_classes)`: two `nn.Linear` layers with a
     `nn.ReLU` between them.
   - `forward(self, x)`: apply layers in order; return logits of shape `[batch, num_classes]`.
   - After instantiation, print `sum(p.numel() for p in model.parameters())` and confirm the
     count matches what you calculate by hand from the dimensions you chose.

3. Implement `src/data.py` with a `make_toy_dataset(n_samples, input_dim, num_classes)`:
   - Generate random float features with `torch.randn` and random integer labels with
     `torch.randint`.
   - Return a `torch.utils.data.TensorDataset` wrapping both tensors.
   - Keep `n_samples` small (128 is enough); the point is a fast loop, not a real dataset.

4. Implement `src/train.py` with `train_one_epoch(model, loader, optimizer, loss_fn, device)`:
   - Write the five-step loop explicitly: device transfer, `zero_grad`, forward, loss,
     `backward`, `optimizer.step`.
   - Log `loss.item()` and the current learning rate to MLflow on every batch.
   - Return the average loss across all batches.
   - Do NOT use a scheduler in this lesson; keep the learning rate constant so the curve is
     easy to read.

5. Write `smoke.py` at the project root:
   - Instantiate model, dataset, loader, optimizer (`torch.optim.Adam`, lr=1e-3), and loss
     (`nn.CrossEntropyLoss`).
   - Run two epochs with a batch size of 16.
   - Assert that epoch-2 average loss is lower than epoch-1 average loss.
   - Assert that all parameters in the model have `requires_grad=True` (none are frozen).
   - Print a per-epoch summary: epoch number, average loss. The test must complete in under
     30 seconds on CPU.

6. Verify gradients by hand on a two-sample batch before running the full loop:
   - Pick `input_dim=2`, `hidden_dim=4`, `num_classes=2`.
   - Run one forward and backward pass.
   - Print `model.linear1.weight.grad` and confirm it is non-zero and not `None`.
   - Add a comment in the code explaining what would happen if you forgot `zero_grad()` before
     the second batch.

## Done When

- `python smoke.py` exits 0, prints per-epoch loss for two epochs, and epoch 2 is lower.
- All parameter `requires_grad` assertions pass.
- MLflow logs appear locally (`mlflow ui` shows a run with `loss` and `lr` logged per batch).
- The two-sample gradient check prints non-zero gradients and the `zero_grad` comment is
  present.
- The whole run completes under 30 seconds on CPU.

## Stretch

Add a `--device cuda` flag to `smoke.py` that moves the model and data to GPU when available.
Confirm the same assertions pass. Add a check that prints the device of the first parameter
(`next(model.parameters()).device`) so you can verify the transfer actually happened.
