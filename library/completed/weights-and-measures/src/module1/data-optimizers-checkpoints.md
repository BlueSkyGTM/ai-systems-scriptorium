# DataLoaders, Optimizers, and Checkpoints

A checkpoint you have not reloaded and verified is a checkpoint you do not have. That
sentence sounds obvious until you lose four GPU-hours because a save path was wrong, the
weights never wrote to disk, and you found out at inference time. This lesson wires the
three pieces that turn a training loop into a recoverable process: `DataLoader` for
organized data delivery, an optimizer and schedule for controlled updates, and `state_dict`
for a checkpoint that actually loads.

## Feeding the Loop: `DataLoader`

`torch.utils.data.DataLoader` wraps a `Dataset` and delivers batches. The four parameters
that matter for a training run:

`batch_size` controls gradient quality and memory together. A larger batch smooths the
gradient estimate but costs more GPU memory per step. There is no universal right number;
the profiler (M4) shows you where the tradeoff lands for your data.

`shuffle=True` on training data, never on validation. Shuffling exposes the model to
different sequences each epoch and prevents it from memorizing order. Shuffling validation
data corrupts epoch-level metrics because the batches change between runs.

`pin_memory=True` allocates tensors in pinned (page-locked) CPU memory, which speeds the
transfer to GPU. Use it when the bottleneck is data loading. The profiler shows the
bottleneck; a blog post does not.

`num_workers` sets how many background processes load data in parallel. The right value
comes from the profiler in M4, not a blog post. It is worth knowing the platform rule now,
because getting it wrong on Windows raises a hard error:

```python
from torch.utils.data import DataLoader

# Linux / Azure ML AmlCompute: num_workers=2 is fine at module level
train_loader = DataLoader(train_ds, batch_size=64, shuffle=True, num_workers=2, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=256, shuffle=False)
```

On Windows, `num_workers > 0` triggers Python's `spawn` multiprocessing mode. The spawned
workers re-import the module, which means any DataLoader call at module scope fires again
inside each worker, which spawns more workers, which raises a `RuntimeError`. The fix is
one guard:

```python
# Windows local dev: wrap the entry point
if __name__ == "__main__":
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True,
                              num_workers=2, pin_memory=True)
```

For local development on Windows, `num_workers=0` (single-process) is simpler and always
safe. On Azure ML `AmlCompute` (Linux), `num_workers=2` is the correct starting point.
The platform difference is not a bug in your code; it is a spawn-mode detail that the
FREEZE-VERIFIED.md for this module confirms.

See: https://docs.pytorch.org/docs/stable/data.html

## The Optimizer: Adam Out of the Box

`torch.optim.Adam` is the right default for most problems. Its hyperparameters:

- `lr=1e-3`: the learning rate. The most important knob.
- `betas=(0.9, 0.999)`: exponential decay rates for the first and second gradient moments.
- `eps=1e-8`: numerical stability term, added to the denominator.

These defaults are fine untuned for the majority of training runs. Do not reach for a
custom epsilon or a different beta until the profiler and the loss curve give you a reason.

```python
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
```

See: https://docs.pytorch.org/docs/stable/optim.html

## Learning Rate Schedule: `StepLR`

A fixed learning rate that worked at epoch 1 is often too large at epoch 30. A schedule
decays the rate on a rule so updates stay large early (fast learning) and small late
(fine convergence).

`StepLR` is the simplest schedule: every `step_size` epochs, multiply the learning rate by
`gamma`.

```python
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
```

With `step_size=10` and `gamma=0.1`, the rate drops by 10x every ten epochs. Call
`scheduler.step()` once per epoch, after validation.

The real alternative from production practice: `ReduceLROnPlateau(mode="min")`, stepped on
`val_loss`. Made With ML's training pipeline uses this pattern because it reacts to actual
model behavior instead of a fixed cadence. When `val_loss` stops improving, the rate
drops; when it resumes improving, it holds. The tradeoff is that you need a validation
metric to step on.

```python
# Alternative: reactive schedule from made-with-ml
plateau_sched = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=5
)
# Called after each epoch's val_loss is known:
# plateau_sched.step(val_loss)
```

Start with `StepLR` to understand the mechanics. Graduate to `ReduceLROnPlateau` when you
have a reliable validation metric and want the schedule to respond to it.

## Checkpointing: Save the `state_dict`, Not the Model

The portable checkpoint is a dictionary, not the model object. Saving the model object
serializes the class definition alongside the weights; if your module hierarchy changes,
`torch.load` cannot reconstruct it. Saving `state_dict` saves only the weights: a plain
mapping of parameter names to tensors, loadable into any matching architecture.

The conductor-verified round-trip for this module:

```python
# Save: epoch, model weights, optimizer state
torch.save(
    {
        "epoch": ep,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
    },
    "ckpt.pt",
)

# Load: weights_only=True prevents arbitrary code execution
ckpt = torch.load("ckpt.pt", weights_only=True)
model.load_state_dict(ckpt["model"])
```

After `load_state_dict`, the verified state_dict keys for `TinyClassifier` are:

```
['linear.weight', 'linear.bias']
```

This is the FREEZE-VERIFIED output from the module's build log. Your model's keys will
differ; the point is to inspect them and confirm they match your architecture before
trusting the weights.

See: https://docs.pytorch.org/docs/stable/generated/torch.save.html

### The Verify Rule

Run a forward pass with a known input after loading. Compare the output to the output
from the same input before saving. If the outputs match, the checkpoint round-trip is
complete. If they differ, the weights did not load correctly and the checkpoint is not
what you think it is.

Reload and verify every checkpoint you intend to use for inference or fine-tuning
resumption. The cost of the check is one forward pass. The cost of skipping it is
discovering the error at deployment.

## Assembling the Pieces

One epoch, with schedule and checkpoint:

```python
for ep in range(1, num_epochs + 1):
    train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)
    scheduler.step()

    torch.save(
        {"epoch": ep, "model": model.state_dict(), "optimizer": optimizer.state_dict()},
        f"ckpt_ep{ep}.pt",
    )

# After the run: reload and verify
ckpt = torch.load("ckpt_ep10.pt", weights_only=True)
model.load_state_dict(ckpt["model"])
with torch.no_grad():
    out_reload = model(sample_input)
# Compare out_reload to out_before_save; they should match.
```

## Core Concepts

- `batch_size` sets a tradeoff between gradient quality and GPU memory; the profiler (M4)
  finds the right value for your data, not a default from a blog post.
- `shuffle=True` belongs on training data only; shuffling validation data corrupts
  epoch-level metrics.
- `num_workers > 0` on Windows requires an `if __name__ == "__main__"` guard; `num_workers=0`
  is safe for local dev, and `num_workers=2` is the correct starting point on Linux
  production (Azure ML).
- Adam's defaults (lr=1e-3, betas=(0.9, 0.999), eps=1e-8) are fine untuned for most
  problems; reach for a custom value when the loss curve and profiler give you a reason.
- Save `state_dict`, not the model object: `state_dict` is a plain weight map, portable
  across architecture refactors.
- A checkpoint you have not reloaded and run a forward pass through is a checkpoint you
  do not have.

<div class="claude-handoff" data-exercise="exercises/module1/data-optimizers-checkpoints/">

**Build It in Claude Code**: Wrap a `TensorDataset` in a `DataLoader` (batch_size=64, shuffle=True, num_workers=0), build a `TinyClassifier`, attach an Adam optimizer and a `StepLR` schedule (step_size=5, gamma=0.1), train for ten epochs calling `scheduler.step()` each epoch, save the `state_dict` checkpoint to `ckpt.pt`, reload it into a fresh model instance with `load_state_dict`, run a forward pass on the same input before and after reloading, and assert the two outputs are identical to confirm the round-trip.

</div>
