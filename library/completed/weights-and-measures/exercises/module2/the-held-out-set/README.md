# Exercise: The Held-Out Set

## Goal

Split a dataset into non-overlapping train and validation sets, write the validation loop with
`model.eval()` and `torch.no_grad()` both present, and confirm the validation loss is stable
across two consecutive runs on the same data.

## Why

Training loss tells you whether gradients are flowing. It cannot tell you whether the model is
learning the pattern or memorizing the examples. The held-out validation set is the only signal
that can answer that question, but only if it is truly held out: any overlap between train and
validation invalidates the measurement silently, and the val loss will look better than it is. You
will not catch the leak at training time. This exercise builds the split-first, eval-mode discipline
before anything depends on it.

## Steps

1. Create `exercises/module2/the-held-out-set/val_loop.py`.

2. Build a synthetic dataset of 200 samples with `torch.utils.data.TensorDataset`. Use
   `torch.manual_seed(0)` for reproducibility.

3. Split it 80/20 into train and validation with no overlap. The split happens on indices, before
   any preprocessing:

   ```python
   n_total = len(dataset)
   n_val = n_total // 5          # 20 %
   n_train = n_total - n_val
   train_ds, val_ds = torch.utils.data.random_split(
       dataset, [n_train, n_val],
       generator=torch.Generator().manual_seed(0),
   )
   ```

   Print both lengths and assert they sum to `n_total`.

4. Wrap each split in a `DataLoader`. Use `shuffle=True` for training, `shuffle=False` for
   validation.

5. Write `validate(model, loader, loss_fn, device)` that returns the mean loss over the validation
   loader. Both conditions are required:

   ```python
   def validate(model, loader, loss_fn, device):
       model.eval()
       total_loss = 0.0
       with torch.no_grad():
           for x, y in loader:
               x, y = x.to(device), y.to(device)
               logits = model(x)
               total_loss += loss_fn(logits, y).item()
       return total_loss / len(loader)
   ```

   `model.eval()` disables Dropout and switches BatchNorm to running statistics. `torch.no_grad()`
   disables gradient tracking. Omitting either produces validation numbers that do not match
   inference-time behavior.

6. Call `validate` twice on the same validation loader without any training step in between. Print
   both results. They must match to four decimal places.

7. Add an assertion:

   ```python
   assert abs(val1 - val2) < 1e-4, f"val loss not stable: {val1:.6f} vs {val2:.6f}"
   print("stability assertion passed")
   ```

## Done When

`python val_loop.py` exits 0 and prints:

- Train and validation split lengths, summing to 200.
- The validation loss from two consecutive calls.
- `stability assertion passed`.

The whole script runs in under 10 seconds on CPU.

## Estimated Time

25 to 35 minutes.

## Stretch

Add a deliberate leak: include a few training samples in your validation set and run `validate`
again. Observe whether the reported loss changes. Write a one-sentence comment explaining why a
leaky validation set produces an optimistic number.
