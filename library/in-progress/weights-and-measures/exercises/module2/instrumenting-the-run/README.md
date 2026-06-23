# Exercise: Instrumenting the Run (Capstone)

## Goal

Instrument a complete training loop with a validation pass and early stopping, deliberately
induce overfitting, confirm the promoted checkpoint is pre-divergence, then run
`python check_loop.py --module 2 <your_loop>.py` and make it pass. This is the module's gated
deliverable: the validator exits 0, or the module is not done.

## Why

Every technique in this module is only useful if it is in the loop. A validation loss you compute
once manually is not a discipline; a loop that always computes it, always checks for improvement,
and always stops when there is none, is. This exercise closes the loop: you instrument it, you
break it on purpose by inducing overfitting, and the validator confirms that the structure is
there and in the right order. Catching overfitting before it wastes GPU time is the payoff for
every lesson in this module.

## What You Are Building

A single file, `my_loop.py`, that contains:

- `train_one_epoch(model, loader, optimizer, loss_fn, device)` with the five canonical steps from
  M1 in the required order.
- A validation pass using `model.eval()` and `torch.no_grad()`.
- An early-stopping loop tracking `best_valid_loss` with a `patience` counter.
- A `__main__` block that induces overfitting (small training set, no regularization, high epoch
  count) and asserts the best checkpoint epoch is strictly before the final epoch.

## Steps

1. Create `exercises/module2/instrumenting-the-run/my_loop.py`.

2. Write `train_one_epoch` following the canonical five-step order. The steps must appear in this
   sequence in the file:

   ```python
   optimizer.zero_grad()
   logits = model(x)
   loss = loss_fn(logits, y)
   loss.backward()
   optimizer.step()
   ```

   Include the trainable-parameter count using `requires_grad` so the M1 checks still pass:

   ```python
   trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
   ```

3. Write the validation pass. Both `model.eval()` and the `torch.no_grad()` context are required:

   ```python
   model.eval()
   with torch.no_grad():
       for x, y in val_loader:
           ...
   ```

4. Implement the early-stopping loop with `best_valid_loss`, a `patience` counter, and checkpoint
   saving. The checkpoint must include `optimizer_state_dict`:

   ```python
   torch.save({
       "epoch": epoch,
       "model_state_dict": model.state_dict(),
       "optimizer_state_dict": optimizer.state_dict(),
       "valid_loss": valid_loss,
   }, best_ckpt_path)
   ```

5. Induce overfitting in the `__main__` block. Use a training set of 16 to 32 samples and a
   validation set of 128 or more samples, no dropout, and a high `max_epochs` (20 or more). Run
   training and print the epoch table showing train loss falling while validation loss turns.

6. Assert the best checkpoint is pre-divergence:

   ```python
   assert best_epoch < total_epochs_run, (
       f"best epoch ({best_epoch}) must be before final epoch ({total_epochs_run})"
   )
   print(f"[PASS] best epoch {best_epoch} is pre-divergence")
   ```

7. Run the validator against your file:

   ```
   python exercises/spine/check_loop.py --module 2 my_loop.py
   ```

   The pass condition is:

   ```
   [PASS] my_loop.py
   ```

   The validator checks eight things: the five M1 steps in order, the trainable-parameter check,
   a `model.eval()` call, a `torch.no_grad()` or `torch.inference_mode()` context, and an early-
   stopping signal (`best` together with `valid` or `patience`). If you see `[FAIL]`, read the
   printed failure message, fix the named problem, and re-run. Do not move on until you see
   `[PASS]`.

## Pass Condition

`python exercises/spine/check_loop.py --module 2 my_loop.py` exits 0 and prints:

```
[PASS] my_loop.py
```

`python my_loop.py` also exits 0 and prints an epoch table where validation loss turns while
training loss falls, plus the pre-divergence assertion passing.

## Done When

Both of the following are true:

- `python my_loop.py` exits 0 with a visible divergence in the epoch table.
- `python exercises/spine/check_loop.py --module 2 my_loop.py` exits 0 and prints `[PASS]`.

## Estimated Time

60 to 90 minutes.

## Stretch

Run the validator's built-in self-test to confirm it is working correctly before pointing it at
your file:

```
python exercises/spine/check_loop.py --selftest
```

Expected output includes one M2 `[PASS]` case and one M2 `[FAIL]` case, confirming the validator
rejects a loop that is missing the validation pass and early-stopping signal.

Then read `exercises/spine/trainer.py`. Its `fit(...)` function is the reference implementation
of the early-stopping loop this exercise asks you to write by hand. Compare your patience counter
and best-checkpoint logic to `fit`'s. Note one structural difference and one pattern you would
adopt. Write both as comments at the top of `my_loop.py`.
