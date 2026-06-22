# Reading a Real `train.py`

You open an unfamiliar training script and it has 250 lines, three helper functions, and a
scheduler you have never seen. There is no comment explaining which line matters most. The payoff
of Module 1 is being able to walk that file and say, out loud, what every section is asserting
about data and model, and knowing the one test to run before you let it chew through a GPU for
an hour.

## What a `train.py` Is Asserting

Every training script makes a set of claims that must hold before the first epoch begins:

- Data is on the right device.
- The model has trainable parameters and is in training mode.
- Gradients are cleared before each forward pass, not accumulated from a previous batch.
- Loss flows backward and the optimizer updates weights.
- At evaluation time, the model switches mode and gradient tracking is off.

These are not aspirations; they are invariants. When one breaks, training silently produces
garbage. The script does not crash; the loss curve never moves, or moves in the wrong
direction, or produces NaN at epoch 3.

Reading a `train.py` is the practice of finding where each invariant is asserted and checking
that nothing is missing.

## Reading `made-with-ml`'s `train.py`

The made-with-ml production script (`madewithml/train.py`) is a real production training
loop: Ray distributed, BERT-based, MLflow-logged. It is more script than you will usually
write from scratch. Open it and locate two functions: `train_step` and `eval_step`. Everything
else is orchestration.

**`train_step`** handles one full pass over the training batches:

```python
def train_step(ds, batch_size, model, num_classes, loss_fn, optimizer):
    model.train()                                        # model mode: training
    loss = 0.0
    ds_generator = ds.iter_torch_batches(batch_size=batch_size, collate_fn=utils.collate_fn)
    for i, batch in enumerate(ds_generator):
        optimizer.zero_grad()                            # zero gradients
        z = model(batch)                                 # forward
        targets = F.one_hot(batch["targets"], num_classes=num_classes).float()
        J = loss_fn(z, targets)                          # loss
        J.backward()                                     # backward
        optimizer.step()                                 # update
        loss += (J.detach().item() - loss) / (i + 1)    # running mean
    return loss
```

Every invariant from the list above is present. `model.train()` sets training mode.
`optimizer.zero_grad()` runs before the forward pass: not after, not outside the loop. The
five steps are in the canonical order: zero, forward, loss, backward, step. The
`J.detach().item()` call before accumulating is deliberate: it pulls the scalar off the
computational graph so the running-mean accumulator does not hold a reference that blocks
garbage collection across hundreds of batches.

**`eval_step`** makes the invariants for inference explicit:

```python
def eval_step(ds, batch_size, model, num_classes, loss_fn):
    model.eval()                                         # model mode: eval
    loss = 0.0
    y_trues, y_preds = [], []
    ds_generator = ds.iter_torch_batches(batch_size=batch_size, collate_fn=utils.collate_fn)
    with torch.inference_mode():                         # no gradient tracking
        for i, batch in enumerate(ds_generator):
            z = model(batch)
            targets = F.one_hot(batch["targets"], num_classes=num_classes).float()
            J = loss_fn(z, targets).item()
            loss += (J - loss) / (i + 1)
            y_trues.extend(batch["targets"].cpu().numpy())
            y_preds.extend(torch.argmax(z, dim=1).cpu().numpy())
    return loss, np.vstack(y_trues), np.vstack(y_preds)
```

Two lines do the verification work: `model.eval()` disables dropout and switches BatchNorm to
use running statistics instead of batch statistics. `torch.inference_mode()` is a stronger
form of `torch.no_grad()`: it disables gradient tracking entirely and signals to PyTorch that
no tensor produced inside the block will participate in a backward pass. Omit `model.eval()`
and dropout stays active at evaluation time, so each inference call returns a different result.
Omit `torch.inference_mode()` and every forward pass builds a computational graph that is
immediately discarded, wasting memory for the entire validation set.

The `train_loop_per_worker` function in the same file shows the orchestration layer: it calls
`train_step` and `eval_step` per epoch, feeds `val_loss` to `ReduceLROnPlateau`, and hands
checkpoint artifacts to Ray's `train.report`. Those are production wiring details. The
invariants are in `train_step` and `eval_step`.

## The Two-Batch Smoke Test

Before running a full training loop, run two batches and assert the loop is wired. This is
the test that catches the majority of training bugs in under a minute, before a GPU job runs
for an hour.

Copy `smoke_two_batches` verbatim from `trainer.py` (conductor-verified on torch 2.x CPU):

```python
def smoke_two_batches(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device | str,
) -> list[float]:
    """Run exactly two training batches and assert the loop is wired correctly.

    Asserts:
      - loss decreased batch-over-batch (gradient signal is flowing)
      - at least one parameter has requires_grad=True (something is trainable)

    Returns the two batch losses so the caller can inspect them.

    Run this before scaling to hours of GPU. It catches:
      - a broken zero_grad/backward/step hookup (loss won't decrease)
      - a frozen model passed to a training loop (no trainable params)
    """
    # trainable-parameter check: count before the loop so it's visible in check_loop.py
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

    model.train()
    losses: list[float] = []

    for i, (x, y) in enumerate(loader):
        if i == 2:
            break
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    assert losses[1] < losses[0], (
        f"loss did not decrease over two batches ({losses[0]:.4f} -> {losses[1]:.4f}); "
        "check zero_grad / backward / optimizer.step order"
    )
    assert trainable > 0, "no trainable params: check requires_grad or model freeze state"
    return losses
```

The design is intentional: two batches of identical data (same samples, two copies), so the
gradient from batch 1 is guaranteed to lower the loss on batch 2. With a fully random
shuffled loader, one optimizer step does not reliably reduce loss on a different mini-batch.
The assertion holds when you control the data; it fires spuriously when you do not.

On a linearly-separable 4-class synthetic dataset, the verified result is:

```
smoke_two_batches: 1.4134 -> 1.1398  [PASS]
```

Both asserts hold. The function returns the two losses so you can read them.

## The Verify Checklist

The smoke test is the first gate. Three more checks close the verification loop.

**Overfit one batch.** Take 8 to 32 samples. Train for 100 or more iterations on that one
batch. Loss should go to approximately zero. If it does not, the loss function, the backward
pass, or the optimizer call is broken. This catches the hookup problems the two-batch smoke
might miss on stiff problems.

**Silent failures to name before you trust a loop:**

- Missing `optimizer.zero_grad()`: gradients accumulate across batches by default. The model
  does update, but in the wrong direction. Loss decreases erratically or not at all.
- Missing `model.eval()` at test time: dropout keeps firing, BatchNorm uses batch statistics
  instead of running statistics. Eval loss varies across calls on the same batch.
- CPU/CUDA device mismatch: a tensor on CPU running into a model on CUDA raises `RuntimeError`
  immediately. Check `.device` on both before the forward pass if you hit this.
- Missing `torch.no_grad()` or `torch.inference_mode()` at inference: forward passes build
  graphs that are immediately discarded, wasting memory on every call.

**NaN and Inf causes, in order of likelihood:**

- Learning rate too high: loss spikes then explodes. Halve the rate and rerun the smoke test.
- `log(0)` in cross-entropy: a predicted probability of exactly zero produces negative
  infinity. Check that `CrossEntropyLoss` receives raw logits, not softmax outputs (it applies
  its own log-softmax internally). Passing softmax outputs to `CrossEntropyLoss` computes
  `log(softmax(x))`, which can produce large negative values and numeric instability.
- Division by zero in BatchNorm: a batch of size 1 has zero variance. BatchNorm divides by
  standard deviation, which is zero, which produces NaN. Drop the last batch if it is smaller
  than 2 samples (`drop_last=True` on the `DataLoader`).

## The 10-Epoch Trajectory

The smoke test clears. Now run a real training loop: Adam at `lr=1e-2`, 4-class separable
data, 10 epochs. The verified loss trajectory on the conductor's run:

```
epoch  mean_loss
-----  ---------
   1   1.1953
   2   0.5941
   3   0.3325
   4   0.2097
   5   0.1454
   6   0.1087
   7   0.0866
   8   0.0720
   9   0.0616
  10   0.0534
```

Loss drops fast in the first few epochs and slows as the model approaches the optimum. That
shape is the signal that the loop is wired correctly and the data is learnable. A flat line
means the learning rate is too low or gradients are not flowing. A spike to NaN means the
learning rate is too high or there is a numerical fault in the loss.

## Core Concepts

- Every `train.py` asserts five invariants: data on the right device, model in training mode,
  gradients zeroed before each forward pass, loss computed and propagated backward, optimizer
  stepping after backward. Read the file as a checklist against these five, not as a sequence
  of commands to accept on trust.
- `eval_step` requires both `model.eval()` and `torch.inference_mode()`: the first switches
  dropout and BatchNorm to inference behavior; the second disables graph construction.
  Omitting either produces validation numbers that do not reflect inference-time behavior.
- The two-batch smoke test (`smoke_two_batches`) runs in under a minute and catches the
  majority of training loop bugs: a frozen model, a missing `zero_grad`, a broken backward
  hookup. Run it before scaling to GPU hours.
- The four silent failures to name before trusting a loop: missing `zero_grad` (gradient
  accumulation), missing `model.eval()` at test, CPU/CUDA device mismatch, and missing
  `inference_mode` at inference.
- NaN during training has three common causes: learning rate too high, logits processed
  through softmax before `CrossEntropyLoss`, or batch size of 1 triggering BatchNorm division
  by zero.
- Debugging is verification: you are checking whether the loop satisfies known invariants, not
  guessing at what might be wrong. The invariants are checkable in a deterministic order.

<div class="claude-handoff" data-exercise="exercises/module1/reading-a-real-train-py/">

**Build It in Claude Code**: Take the `train_one_epoch` loop from `trainer.py` and introduce a deliberate bug: remove `optimizer.zero_grad()` from inside the loop. Add `smoke_two_batches` to the file, wire it up to run against your broken loop, and observe the assertion fire. Then work through the verify checklist: note which silent-failure category the bug falls into, restore `zero_grad`, rerun the smoke to confirm it passes (`1.4134 -> 1.1398`), and write a one-paragraph explanation of why gradient accumulation causes the loss-decrease assertion to fail.

</div>
