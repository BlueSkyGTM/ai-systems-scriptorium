# Exercise: Loss Curves and the Overfitting Signal

## Goal

Extend the training loop from Exercise 1 to add a full validation loop, per-epoch MLflow
logging of both losses, a best-checkpoint saving policy, and a deliberate overfitting run
that produces a loss curve showing the divergence pattern. The exercise ends when you can read
a loss curve and point to the checkpoint you should have promoted.

## Why

The Production AI Engineer does not run training and declare it done when training loss is low.
They read the validation signal, identify the checkpoint at peak validation performance, and
document why every other checkpoint was not promoted. This exercise builds that practice.
Without it, the eval gate in M5 has no foundation.

## Steps

1. Copy `m1-training-loop/` to `m1-loss-curves/` as your starting point. Add
   `matplotlib` to your dependencies (for plotting).

2. Implement `src/evaluate.py` with `evaluate(model, loader, loss_fn, device) -> tuple[float, float]`:
   - Set `model.eval()` and wrap the loop in `torch.no_grad()`.
   - Accumulate total loss and compute token accuracy (correct predictions / total samples).
   - Return `(avg_loss, token_accuracy)`.
   - Add a comment explaining why `model.eval()` and `torch.no_grad()` are both required, not
     just one of the two.

3. Extend `src/train.py` with a `train(model, train_loader, val_loader, optimizer, loss_fn, device, n_epochs, patience)` function:
   - Call `train_one_epoch` and `evaluate` each epoch.
   - Log to MLflow: `train_loss`, `valid_loss`, `valid_token_acc`, and the current epoch.
   - Implement the checkpoint-saving policy:
     - Keep track of `best_valid_loss`.
     - If current epoch's `valid_loss` is lower, save the checkpoint to
       `checkpoints/best.pt` using `torch.save` with model state, optimizer state,
       epoch number, and `valid_loss`.
     - If `valid_loss` has not improved for `patience` consecutive epochs, stop early.
   - Return the list of `(train_loss, valid_loss)` tuples for every epoch that ran.

4. Produce an overfitting run in `overfit.py`:
   - Use a training set of 64 samples and a validation set of 64 samples (tiny, so the model
     can memorize the training set).
   - Train for 20 epochs with no regularization, `lr=1e-2`.
   - Do NOT use early stopping for this run (set `patience=20`).
   - Plot training and validation loss per epoch using `matplotlib` and save the plot to
     `overfit_curve.png`. Both curves on the same axes, clearly labeled.
   - Print the epoch number and `valid_loss` value for the saved best checkpoint.

5. Confirm the policy worked in `verify.py`:
   - Load the checkpoint from `checkpoints/best.pt`.
   - Print the stored `epoch` and `valid_loss`.
   - Assert that `valid_loss` from the checkpoint is lower than the `valid_loss` from the
     final epoch of the run (the checkpoint is not the last epoch).
   - Assert that the checkpoint's model weights load cleanly into a fresh `TinyClassifier`
     instance with the same architecture.

## Done When

- `python overfit.py` runs 20 epochs, prints per-epoch train and valid loss, saves
  `checkpoints/best.pt` and `overfit_curve.png`.
- `overfit_curve.png` shows the divergence pattern: training loss continues to fall while
  validation loss rises after some epoch.
- `python verify.py` exits 0; the printed best-checkpoint epoch is not 20, and its
  `valid_loss` is lower than the epoch-20 `valid_loss`.
- MLflow shows a run with `train_loss` and `valid_loss` logged per epoch.
- The `evaluate.py` comment explains both `model.eval()` and `torch.no_grad()` correctly.

## Stretch

Add a second run in `healthy.py` using a larger dataset (1024 training samples, 256
validation) and a lower learning rate (lr=1e-3). Plot its loss curves alongside the overfitting
run's curves to show what a healthy run looks like. The healthy run should show both losses
decreasing together; the best checkpoint should be at or near the final epoch, not earlier.
This side-by-side comparison is the visual you will use to explain your training decisions in a
code review.
