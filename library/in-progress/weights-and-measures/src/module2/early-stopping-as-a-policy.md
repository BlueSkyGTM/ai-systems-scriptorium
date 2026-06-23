# Early Stopping as a Policy

The training loop does not know when to stop; you have to tell it. The usual framing calls
patience a hyperparameter and leaves it at that. That framing is imprecise enough to cause
real mistakes. Patience is not a knob like learning rate: it governs a promotion decision,
and promotion decisions need to be auditable.

The policy is one sentence: save the checkpoint with the best `valid_loss`; if `valid_loss`
has not improved for N consecutive epochs, stop and restore the best checkpoint. Everything
else follows from that sentence.

## Why "Policy" and Not "Hyperparameter"

A hyperparameter is tuned to maximize a metric. A policy is a rule you commit to before
training starts and defend afterward. The difference matters when a model misbehaves in
production and someone asks why you shipped the epoch-4 checkpoint instead of epoch-7.

"The checkpoint with the best validation loss" is a defensible answer. "I stopped when the
counter hit the patience value" is not by itself; it is only defensible if the counter was
tracking the right thing: validation loss, not training loss, not wall-clock time.

The policy form makes the audit trail explicit. `valid_loss` at each epoch is logged to the
checkpoint dict. The best-epoch record is returned by `fit`. Nothing about the promotion
decision is implicit or reconstructed from memory.

## Patience: The One Real Decision

Patience (N) is the number of epochs you allow `valid_loss` to not improve before you stop.
Common values are 2-5.

Tighter patience risks premature stopping on a noisy epoch: if `valid_loss` ticks up once
due to batch variance, a patience of 1 stops the run before the model has had a chance to
recover. Looser patience burns compute chasing epochs that are making the checkpoint worse
rather than better. The loss trajectory from the verified overfit demo makes this concrete:

```
epoch  train_loss  valid_loss
-----  ----------  ----------
    1      1.5197      1.5801
    2      0.8901      1.5413
    3      0.5283      1.5205
    4      0.3126      1.5141  <-- BEST
    5      0.1922      1.5172
    6      0.1256      1.5254
    7      0.0877      1.5355

Early stop after epoch 7  (patience=3, no improvement since epoch 4)
Best epoch : 4  (valid_loss=1.5141)
Final epoch: 7
[PASS] best epoch is before final epoch; divergence confirmed.
```

Training loss fell monotonically from 1.52 to 0.09: a model memorizing 16 samples. Validation
loss improved through epoch 4 then rose for three straight epochs. Patience of 3 stopped
the run at epoch 7 and restored the epoch-4 checkpoint. The final epoch looks better by
training loss. It is worse by every metric that matters.

## The Checkpoint Dict: Save What You Will Promote

The checkpoint is not just the model weights. It is the full state needed to resume training
or to audit the promotion decision:

```python
torch.save(
    {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "valid_loss": valid_loss,
    },
    f"checkpoints/epoch_{epoch:02d}.pt",
)
```

This is the L3 FREEZE block from the catalog, verified against `exercises/spine/trainer.py`.
The `fit` function in `trainer.py` uses `best_ckpt_path` in place of the literal path string
(to avoid hardcoding a directory during verification), but the dict keys are byte-identical.

Three things in that dict earn their place:

`model_state_dict` is the weights. Without it there is nothing to restore.

`optimizer_state_dict` holds momentum buffers and adaptive learning-rate estimates. Adam
maintains a running mean and variance for each parameter gradient. If you restore model
weights without restoring the optimizer state, those buffers reset to zero, the adaptive
estimates start fresh, and the learning dynamics diverge from what they were when the
checkpoint was saved. For inference-only promotion this does not matter; for fine-tuning
resumption it does, and the cost of including optimizer state is small enough that the
right habit is to always include it.

`valid_loss` is the promotion criterion. Store it at checkpoint time so you do not have to
rerun validation to recover it. At promotion time you load the file, read `valid_loss`, and
confirm it is the epoch you intended to promote. No reconstruction required.

See: https://docs.pytorch.org/docs/2.12/generated/torch.save.html

## How `fit` Implements the Policy

The verified `fit` function in `exercises/spine/trainer.py` is the reference implementation.
Its inner loop is three steps:

1. Train one epoch via `train_one_epoch` (the five-step loop from M1).
2. Validate via `evaluate` (catalog L1: `model.eval()` + `torch.no_grad()`, both required).
3. Compare `valid_loss` to the running best; save and reset the patience counter if better,
   or increment the counter and break when patience is exhausted.

After the loop, `fit` restores the best checkpoint before returning, so the model the caller
holds is in its best-epoch state regardless of when early stopping fired.

```python
# --- checkpoint promotion: save if this epoch has the best valid_loss ---
if valid_loss < best_valid_loss:
    best_valid_loss = valid_loss
    best_epoch = epoch
    epochs_without_improvement = 0

    best_ckpt_path = os.path.join(checkpoint_dir, f"epoch_{epoch:02d}.pt")
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "valid_loss": valid_loss,
        },
        best_ckpt_path,
    )
else:
    epochs_without_improvement += 1

# --- early stopping: stop when patience is exhausted ---
if epochs_without_improvement >= patience:
    break
```

Core torch has no built-in `EarlyStopping` class. This hand-rolled counter is the pattern.
Do not reach for a torch API that does not exist.

## The Scheduler Reads the Same Signal

`ReduceLROnPlateau` from Made With ML's `train.py` watches the same metric:

```python
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=5
)
# After each epoch's validation pass:
scheduler.step(val_loss)
```

The scheduler takes the validation metric directly. When `val_loss` stops improving, the
learning rate drops; when improvement resumes, the rate holds. Early stopping and the
scheduler are watching the same number for the same reason: the validation signal is the
arbiter of what is happening to the model, not the training signal.

See: https://docs.pytorch.org/docs/2.12/generated/torch.optim.lr_scheduler.ReduceLROnPlateau.html

## Core Concepts

- Early stopping is a checkpoint-promotion policy, not a hyperparameter: "save the
  checkpoint with best `valid_loss`; stop if no improvement for N epochs; restore the
  best before returning."
- Patience N = 2-5: tighter risks premature stop on a noisy epoch; looser burns compute
  chasing a checkpoint that is already getting worse.
- The checkpoint dict must include `optimizer_state_dict`: restoring model weights without
  optimizer state resets momentum buffers and adaptive estimates, and learning dynamics
  diverge on resume.
- The `valid_loss` key in the checkpoint dict is the promotion criterion: store it at save
  time so no revalidation is needed to audit which epoch you promoted.
- Core torch has no built-in `EarlyStopping`; the hand-rolled patience counter in `fit` is
  the pattern.
- `ReduceLROnPlateau` is stepped on the same `val_loss` that drives early stopping: both
  mechanisms answer to the validation signal, not the training signal.

<div class="claude-handoff" data-exercise="exercises/module2/early-stopping-as-a-policy/">

**Build It in Claude Code**: Implement an early-stopping training loop with a patience
counter that tracks epochs without improvement in `valid_loss`, saves the best checkpoint
as a dict containing `model_state_dict`, `optimizer_state_dict`, and `valid_loss` whenever
a new best is reached, stops when patience is exhausted, and restores the best checkpoint
before exiting. Use a small training set and a noisy validation set to deliberately induce
overfitting, then confirm that the restored model's `valid_loss` matches the checkpoint's
stored `valid_loss` key and that the best epoch is before the final epoch.

</div>
