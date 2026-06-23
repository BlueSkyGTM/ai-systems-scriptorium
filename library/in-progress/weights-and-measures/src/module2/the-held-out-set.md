# The Held-Out Set

Training loss went down. You saw it happen, batch by batch. That number is not the verdict.

It tells you how well the model performed on the same data it learned from: a closed loop, the
worst possible test of generalization. The question worth asking is whether the model improved on
data it never touched during training. Without a second signal, you cannot answer it; you are
flying with one instrument.

## Two Signals, Not One

Every training run needs two scalar signals tracked from the start:

- `train_loss`: computed per batch, gradients on. This is what the optimizer is minimizing.
- `valid_loss`: computed on the held-out set, gradients off, once per epoch. This is what you
  actually care about.

Azure AI Foundry's fine-tuning infrastructure logs both by default. From
[learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning#analyze-your-fine-tuned-model),
the `results.csv` for a fine-tuning run includes `train_loss`, `full_valid_loss`,
`train_mean_token_accuracy`, and `full_valid_mean_token_accuracy`. The portal notes directly:
"Divergence between training and validation may indicate overfitting; try fewer epochs or a
smaller LR."

This is not an Azure-specific invention. It is the exact two-signal contract you build yourself
in any local loop. The production infrastructure just makes visible what you would log with
`print` or MLflow in your own trainer.

Tracking only `train_loss` is a known failure mode. A model that memorizes its training set can
drive `train_loss` to near zero while `valid_loss` climbs. The training-only view looks like
success; the two-signal view shows a model that is getting worse at the thing that matters.

## The Leak That Kills the Signal

A validation set is only valid if it has never touched the training pipeline. One overlap
invalidates it: a preprocessed sample in both splits, a normalization mean computed across the
full dataset before splitting, any augmentation seeded from the combined pool. The model has
seen that data in some form; the measured `valid_loss` is not a held-out number anymore.

The rule is simple: split first, preprocess second. Generate your train and validation indices
from the raw data before any transformation runs. Fit scalers, tokenizers, and statistics on
the training split only. Apply them to the validation split without refitting.

A `valid_loss` computed on a contaminated set is not a validation number. It is a slightly
noisier version of `train_loss`, and it will give you false confidence at exactly the moment
you need real signal.

## The Validation Loop

The validation loop looks like the training loop with two structural changes: `model.eval()` and
`torch.no_grad()`. Both are required. Omitting either produces numbers that do not match what the
model will do at inference time.

Copy `evaluate` verbatim from `exercises/spine/trainer.py`:

```python
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    loss_fn: nn.Module,
    device: torch.device | str,
) -> tuple[float, float]:
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            total_loss += loss_fn(logits, y).item()
            correct += (logits.argmax(dim=-1) == y).sum().item()
            total += y.numel()
    return total_loss / len(loader), correct / total
```

Conductor-verified output on a 32-sample held-out set, torch 2.12.1+cpu:

```
evaluate => avg_loss=1.3588, token_acc=0.3750
evaluate FREEZE check: PASS
```

## What Each Call Does

`model.eval()` is a mode switch. It tells every layer in the model to behave as it would at
inference time: Dropout passes inputs through unchanged instead of masking them; BatchNorm uses
its running statistics instead of batch statistics. The PyTorch docs for
[torch.nn.Module.eval](https://docs.pytorch.org/docs/2.12/generated/torch.nn.Module.html) confirm:
`eval()` is equivalent to `train(False)`. It does not disable gradient tracking.

`torch.no_grad()` disables gradient tracking for every operation inside the context. The autograd
engine stops building the computation graph; no `.grad` values accumulate. The PyTorch docs for
[torch.no_grad](https://docs.pytorch.org/docs/2.12/generated/torch.no_grad.html) note that
`torch.inference_mode()` is the stricter and faster option when you will never need gradients
from the forward pass: it additionally prevents tensors created inside the block from
participating in future gradient computations. Either satisfies the requirement; neither replaces
`model.eval()`.

These two calls are orthogonal. `model.eval()` changes layer behavior; `torch.no_grad()` changes
the autograd engine's recording. You need both because each does something the other cannot.
Omit `model.eval()` and Dropout will randomly zero activations during validation: your
`valid_loss` will vary run to run for a reason that has nothing to do with generalization. Omit
`torch.no_grad()` and the forward pass builds a graph you never use, burning memory and time, and
the behavior of certain layers diverges from their inference-time form.

Call `evaluate` at the end of every training epoch. The `train_loss` from that epoch's batches
and the `valid_loss` from this call are the two numbers that tell you whether the model is
learning or memorizing.

## A Validation Number You Cannot Trust Is Not a Number

There is a version of this setup that looks correct but is not: the validation loop runs, a
number prints, the curve looks clean. If the split was contaminated, or if `model.eval()` was
missing, or if `torch.no_grad()` was missing, that number is not a held-out measurement. It is
noise labeled as signal.

The discipline is cheap at the start and expensive to retrofit. Split before preprocessing. Put
both calls in the loop before you run a single epoch. The validation number you log is only worth
logging if it measures what you think it measures, and the only way to know it does is to build
the loop correctly from the beginning.

## Core Concepts

- Two signals are mandatory from the first training run: `train_loss` per batch with gradients on,
  and `valid_loss` on a held-out set with gradients off, once per epoch. Tracking only `train_loss`
  is a known failure mode; the divergence between them is the overfit signal.
- The validation set is only valid if it never touched the training pipeline. Split first,
  preprocess second: fit scalers and statistics on the training split only, never on the full dataset
  before splitting.
- `model.eval()` and `torch.no_grad()` are both required in the validation loop and do different
  things. `model.eval()` switches Dropout off and BatchNorm to running statistics; `torch.no_grad()`
  stops the autograd engine from building a graph. Omitting either produces validation numbers that
  do not reflect inference-time behavior.
- `torch.inference_mode()` is a stricter, faster alternative to `torch.no_grad()` for pure
  inference passes; it is orthogonal to `model.eval()` and satisfies the same requirement.
- A `valid_loss` computed on a contaminated split is a noisier version of `train_loss`, not a
  held-out measurement. A validation number you cannot trust is not a number.

<div class="claude-handoff" data-exercise="exercises/module2/the-held-out-set/">

**Build It in Claude Code**: Take a small synthetic dataset (e.g., 200 labeled samples) and split
it into train and validation sets with no overlap: generate the split indices first, then apply
any preprocessing using statistics computed on the training split only. Write the validation loop
with `model.eval()` and `torch.no_grad()` as shown in this lesson, calling `evaluate` at the end
of each epoch. Run two full training cycles from the same random seed and confirm that the
reported `valid_loss` is identical across both runs: a number that changes between otherwise
identical validation passes is a sign that a stateful layer is still in training mode.

</div>
