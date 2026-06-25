# Exercise: Reading Loss Curves

## Goal

Train a small model for several epochs, log train and validation loss after each epoch, tabulate
the trajectory, identify the divergence epoch, and name the checkpoint you would promote.

## Why

A training run that shows falling loss is not evidence of a well-trained model. It is a question
waiting to be answered: is the validation loss following the training loss down, or is it turning
while training keeps dropping? The divergence epoch is where the model crosses from learning to
memorizing. Recognizing that crossing from a table, before you have a plot, is the skill. You need
it when a run finishes on a remote machine, when a plot is not available, and when someone hands
you a CSV and asks whether the checkpoint they promoted was the right one.

## Steps

1. Create `exercises/module2/reading-loss-curves/curve_log.py`.

2. Build a small model and a synthetic dataset. Use a large model relative to the dataset size so
   overfitting is visible within 8 to 10 epochs: for example, a two-layer MLP on 64 training
   samples with no dropout.

3. Create non-overlapping train and validation splits. Keep the validation set separate from any
   data the model sees during the training loop.

4. Write a training loop that runs for a fixed number of epochs. After each epoch, compute and
   store both the train loss (mean over training batches) and the validation loss (mean over
   validation batches with `model.eval()` and `torch.no_grad()`).

5. After training, print the epoch table with this format:

   ```
   Epoch    train_loss    valid_loss
       1        1.84          1.92
       2        1.41          1.47
       3        1.12          1.18
       4        0.89          1.22
       5        0.71          1.38
       6        0.58          1.51
   ```

   The exact numbers will differ; what must be visible is that validation loss turns while training
   loss continues to fall.

6. Add a detection block that finds the divergence epoch (the first epoch where validation loss
   is higher than the previous epoch's validation loss) and the best-checkpoint epoch (the epoch
   with the lowest validation loss):

   ```python
   best_epoch = min(range(len(val_losses)), key=lambda i: val_losses[i]) + 1
   divergence_epoch = next(
       (i + 2 for i in range(len(val_losses) - 1) if val_losses[i + 1] > val_losses[i]),
       None,
   )
   print(f"Best checkpoint : epoch {best_epoch}  (val_loss={val_losses[best_epoch-1]:.4f})")
   print(f"Divergence epoch: epoch {divergence_epoch}")
   ```

7. Assert that the best checkpoint epoch is before the divergence epoch:

   ```python
   assert divergence_epoch is not None, "no divergence observed; run more epochs or increase model size"
   assert best_epoch < divergence_epoch, (
       f"best checkpoint ({best_epoch}) is not before divergence ({divergence_epoch})"
   )
   print("curve assertions passed")
   ```

## Done When

`python curve_log.py` exits 0 and prints:

- The epoch table showing validation loss turning while training loss falls.
- The identified best-checkpoint epoch and divergence epoch.
- `curve assertions passed`.

The whole run completes in under 60 seconds on CPU.

## Estimated Time

35 to 50 minutes.

## Stretch

Plot the two curves with `matplotlib` if it is available, saving to `curve.png`. Mark the best
checkpoint epoch with a vertical line. If `matplotlib` is not installed, print a note and
continue rather than crashing: wrap the import in a `try/except ImportError` block.
