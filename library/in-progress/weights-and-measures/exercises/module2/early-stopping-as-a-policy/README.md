# Exercise: Early Stopping as a Policy

## Goal

Implement an early-stopping training loop with a patience counter, save the best checkpoint by
validation loss with optimizer state included, restore the best checkpoint after training, and
confirm the restored model matches the best-epoch validation loss, not the final epoch's.

## Why

Early stopping is not a slider you turn down when overfitting looks bad. It is a checkpoint-
promotion policy with an auditable criterion: the checkpoint with the best validation loss is the
one you ship; if N consecutive epochs show no improvement, you stop. The "N consecutive epochs"
is the patience parameter, and the right range is 2 to 5. Tighter than 2 risks stopping at a
temporary plateau before the model has recovered. Looser than 5 wastes compute and may never
stop on a run that plateaus without diverging. The policy is only trustworthy if you can verify
it: the restored model's validation loss must match the recorded best, not drift because you
forgot to save optimizer state.

## Steps

1. Create `exercises/module2/early-stopping-as-a-policy/early_stop.py`.

2. Build a synthetic dataset with a deliberate size imbalance: a small training set (around 32
   samples) and a larger validation set (around 128 samples) so overfitting appears within
   10 to 15 epochs. Use `torch.manual_seed(1)` for reproducibility.

3. Write `train_one_epoch(model, loader, optimizer, loss_fn, device)` following the five-step
   canonical order from M1.

4. Write `validate(model, loader, loss_fn, device)` returning mean validation loss, with
   `model.eval()` and `torch.no_grad()` both present.

5. Implement the early-stopping loop. The policy in plain terms: track the best validation loss
   seen so far; when a new epoch improves it, save a checkpoint and reset the patience counter;
   when it does not, increment the counter; when the counter reaches `patience`, stop:

   ```python
   best_valid_loss = float("inf")
   patience = 3
   epochs_without_improvement = 0
   best_ckpt = "checkpoints/best.pt"

   for epoch in range(1, max_epochs + 1):
       train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)
       valid_loss = validate(model, val_loader, loss_fn, device)

       if valid_loss < best_valid_loss:
           best_valid_loss = valid_loss
           epochs_without_improvement = 0
           torch.save({
               "epoch": epoch,
               "model_state_dict": model.state_dict(),
               "optimizer_state_dict": optimizer.state_dict(),
               "valid_loss": valid_loss,
           }, best_ckpt)
       else:
           epochs_without_improvement += 1

       if epochs_without_improvement >= patience:
           print(f"Early stop at epoch {epoch}  (no improvement for {patience} epochs)")
           break
   ```

   Print the epoch number, train loss, and validation loss on each iteration so the trajectory is
   visible.

6. After the loop, restore the best checkpoint:

   ```python
   ckpt = torch.load(best_ckpt, weights_only=True)
   model.load_state_dict(ckpt["model_state_dict"])
   restored_valid_loss = validate(model, val_loader, loss_fn, device)
   ```

7. Assert the restored model matches the recorded best:

   ```python
   assert abs(restored_valid_loss - ckpt["valid_loss"]) < 1e-4, (
       f"restored loss {restored_valid_loss:.6f} does not match saved best "
       f"{ckpt['valid_loss']:.6f}"
   )
   print(f"Best epoch    : {ckpt['epoch']}")
   print(f"Best val loss : {ckpt['valid_loss']:.4f}")
   print(f"Restored loss : {restored_valid_loss:.4f}")
   print("early-stopping assertions passed")
   ```

## Done When

`python early_stop.py` exits 0 and prints:

- The per-epoch loss trajectory.
- The early-stop message naming the stopping epoch and the patience count.
- The best epoch and its validation loss.
- `early-stopping assertions passed`.

The best epoch must be earlier than the final epoch run.

## Estimated Time

40 to 55 minutes.

## Stretch

Add a second run with `patience=1` on the same data and compare which epoch it stops at versus
`patience=3`. Print both stopping epochs and the best validation loss each produced. Write a
two-sentence comment on the trade-off between a tight and a loose patience value.
