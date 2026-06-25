# Exercise: The Module and the Loop

## Goal

Define a small `nn.Module`, write the five-step training loop, print the trainable and total
parameter counts, and add per-batch loss logging. The loop must follow the canonical step order
and produce a readable loss trajectory.

## Why

The training loop is the seam every fine-tuning job modifies. You cannot insert a LoRA adapter in
M4 or attach an eval gate in M5 until you can write the loop from scratch and read what it says.
The parameter count is not a nicety: knowing how many parameters are trainable is the precondition
for verifying that a freeze or an adapter did what you intended.

## Steps

1. Create `exercises/module1/the-module-and-the-loop/train_loop.py`.

2. Define `TinyClassifier(nn.Module)` with an `__init__(self, in_dim, n_classes)` that registers
   a single `nn.Linear(in_dim, n_classes)` layer, and a `forward(self, x)` that returns
   `self.linear(x)`.

3. After instantiating the model, compute and print both counts:

   ```python
   total     = sum(p.numel() for p in model.parameters())
   trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
   print(f"params: total={total}, trainable={trainable}")
   ```

   Verify by hand that the printed total matches what you calculate from `in_dim` and `n_classes`
   (weights plus biases). Add the calculation as a comment.

4. Build a small synthetic dataset with `torch.utils.data.TensorDataset` and wrap it in a
   `DataLoader`. Use `torch.randn` for features and `torch.randint` for labels.

5. Write `train_one_epoch(model, loader, optimizer, loss_fn, device)` with the five steps in
   this exact order:

   ```
   1. device transfer: inputs and labels to the target device
   2. zero_grad:       clear gradients before the forward pass
   3. forward:         logits = model(inputs)
   4. loss:            loss = loss_fn(logits, labels)
   5. backward + step: loss.backward(); optimizer.step()
   ```

   On every batch, print the batch index and `loss.item()`. Return the mean loss over all batches.

6. In a `__main__` block, instantiate the model, an `nn.CrossEntropyLoss`, and an
   `torch.optim.Adam` optimizer. Run five epochs and print the per-epoch mean loss. Verify the
   mean loss trends downward across the five epochs.

## Done When

`python train_loop.py` exits 0 and prints:

- The param counts (total and trainable), matching your hand calculation.
- Per-batch loss for every batch in every epoch.
- Per-epoch mean loss for five epochs, trending downward.

The whole run completes in under 30 seconds on CPU.

## Estimated Time

30 to 45 minutes.

## Stretch

Add a `model.eval()` + `torch.no_grad()` pass after each epoch that runs the same loader and
prints validation loss. Note in a comment why `no_grad()` matters here and what would go wrong
if you forgot `model.eval()` when dropout or batch normalization is present.
