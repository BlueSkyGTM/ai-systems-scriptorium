# Exercise: Data, Optimizers, and Checkpoints

## Goal

Wrap a dataset in a `DataLoader`, add an Adam optimizer with a `StepLR` schedule, save a
checkpoint using `state_dict`, reload it into a fresh model, and assert the reloaded model
produces identical outputs. The checkpoint round-trip must be verified, not assumed.

## Why

A checkpoint that has not been reloaded and tested is not a checkpoint; it is a file that might
be one. The reload-and-assert discipline here is the same gate that M5 applies to eval artifacts:
you do not trust a saved state until a forward pass confirms it. The DataLoader and optimizer
setup is also the direct scaffold that `train_one_epoch` in later modules extends.

## Steps

1. Create `exercises/module1/data-optimizers-checkpoints/checkpoint_loop.py`.

2. Build a synthetic `TensorDataset` with at least 256 samples and wrap it in two DataLoaders:
   a training loader with `batch_size=64, shuffle=True, num_workers=0` and a validation loader
   with `batch_size=256, shuffle=False`. Print the number of batches in each.

3. Instantiate `TinyClassifier` (copy or import the definition from the previous exercise),
   an `nn.CrossEntropyLoss`, an `torch.optim.Adam` optimizer (`lr=1e-3`), and a
   `torch.optim.lr_scheduler.StepLR` scheduler (`step_size=2, gamma=0.5`).

4. Write a training loop for five epochs. After each epoch, call `scheduler.step()` and print
   the current learning rate:

   ```python
   current_lr = scheduler.get_last_lr()[0]
   print(f"epoch {ep}: mean_loss={mean_loss:.4f}, lr={current_lr:.6f}")
   ```

5. After epoch 3, save a checkpoint:

   ```python
   torch.save({
       "epoch": 3,
       "model": model.state_dict(),
       "optimizer": optimizer.state_dict(),
   }, "ckpt.pt")
   print("checkpoint saved: ckpt.pt")
   ```

6. Load the checkpoint into a second freshly instantiated model and assert its output on a fixed
   input batch matches the original:

   ```python
   ckpt = torch.load("ckpt.pt", weights_only=True)
   model2 = TinyClassifier(in_dim, n_classes)
   model2.load_state_dict(ckpt["model"])
   model2.eval()

   with torch.no_grad():
       out_original = model(fixed_batch)
       out_reloaded = model2(fixed_batch)

   assert torch.allclose(out_original, out_reloaded), "reloaded model output does not match"
   print("checkpoint reload assertion passed")
   ```

   `fixed_batch` is a tensor you create before training and hold constant across both calls.

## Done When

`python checkpoint_loop.py` exits 0 and prints:

- The number of batches in each DataLoader.
- Per-epoch loss and learning rate for five epochs, with the learning rate stepping at epoch 3
  (and again at epoch 5, if the schedule fires).
- `checkpoint saved: ckpt.pt`.
- `checkpoint reload assertion passed`.

The file `ckpt.pt` exists in the exercise directory after the run. The whole script runs in under
60 seconds on CPU.

## Estimated Time

30 to 45 minutes.

## Stretch

Replace `StepLR` with `torch.optim.lr_scheduler.ReduceLROnPlateau(mode="min")`. Step it on
validation loss instead of per epoch, and print when the learning rate actually decreases. Add a
comment explaining when you would prefer `ReduceLROnPlateau` over `StepLR`.
