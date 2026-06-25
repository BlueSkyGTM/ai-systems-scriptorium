# Loss Curves and the Overfitting Signal

Loss went down. That sentence ends most fine-tuning tutorials. It is not a verdict; it is the
beginning of a question. The question is: which loss, and compared to what?

A training loss that goes down while validation loss goes up is a model memorizing your
training data and failing on everything else. A training loss that goes down while validation
loss tracks closely is a model learning. The difference between those two scenarios is the
difference between a checkpoint worth deploying and one that will embarrass you in production.
Reading that difference off a loss curve is the first skill this lesson builds.

## The Two Losses You Must Track

Every training run produces at least two scalar signals: training loss (computed on each batch
of training data during the forward pass) and validation loss (computed on a held-out set,
with gradients disabled, at the end of each epoch). Both matter. Tracking only training loss is
a known failure mode.

Azure AI Foundry's fine-tuning run logs four metrics by default to `results.csv` and
visualizes them in the portal [MS-Learn: Azure AI Foundry fine-tuning, analyze your customized
model]:

| Metric | What it measures |
|---|---|
| `train_loss` | Loss per training step (forward + backward on one batch) |
| `full_valid_loss` | Validation loss computed at end of each epoch |
| `train_mean_token_accuracy` | Token-level accuracy on training batches |
| `full_valid_mean_token_accuracy` | Token-level accuracy on validation set per epoch |

These are not Azure-specific inventions. They are the same four signals you would log yourself
with MLflow in a local training loop. The portal just makes them visible without extra code.

## Reading the Divergence Pattern

A healthy run looks like this: both losses decrease together, validation loss staying close to
(slightly above) training loss across all epochs. The gap between them is the generalization
gap; some gap is normal.

An overfit run has a signature: training loss continues to decrease after a certain epoch while
validation loss plateaus or starts rising. The model is fitting the training data increasingly
well while its performance on held-out data gets worse. The checkpoint at peak validation
performance is the one to promote; every checkpoint after that point is moving in the wrong
direction.

```
Epoch    train_loss    valid_loss
1        1.84          1.92
2        1.41          1.47
3        1.12          1.18
4        0.89          1.22    <-- valid_loss turns around; training continues to drop
5        0.71          1.38    <-- overfit; training loss looks great, validation is worse
6        0.58          1.51    <-- best checkpoint was epoch 3
```

The checkpoint at epoch 3 is the one to save and evaluate. The run at epoch 6 looks better by
training loss and would fool anyone reading only that column.

## Token Accuracy Is Not a Substitute for Loss

Token accuracy (`train_mean_token_accuracy`, `full_valid_mean_token_accuracy`) measures what
fraction of output tokens the model predicted correctly. For instruction-tuned language models,
this is an informative companion metric, not a replacement for loss.

The reason: accuracy close to 100% is not a sign of a great model; it is often a sign of
overfitting, particularly on short completions where the model has memorized the expected
tokens verbatim [MS-Learn: Azure Databricks fine-tuning, step 5 view metrics and outputs,
TokenAccuracy]. Track accuracy alongside loss. If accuracy climbs toward 100% while validation
loss is rising, the signals agree: the model is overfitting.

## Early Stopping as a Policy Decision

Early stopping halts training when validation loss has not improved for a specified number of
epochs (the patience). It is often described as a hyperparameter, which obscures its nature:
it is a policy about which checkpoint to prefer.

The policy version of that decision is explicit and auditable: "I will evaluate each checkpoint
against the validation set and save only the one with the best `full_valid_loss`. If validation
loss has not improved for N consecutive epochs, I will stop and save the best checkpoint seen
so far." That is the production behavior, whether you implement it as an early-stopping callback
or as a manual checkpoint-promotion step after the run.

The patience value (N) is the only real decision. Common values are 2-5 epochs. Tighter
patience saves compute at the risk of stopping before the model has had time to recover from
a noisy epoch; looser patience burns compute chasing diminishing returns.

## Checkpointing: Save What You Will Promote

PyTorch checkpoints are serialized model state dicts:

```python
import torch

# Save a checkpoint
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "valid_loss": valid_loss,
}, f"checkpoints/epoch_{epoch:02d}.pt")

# Load it
checkpoint = torch.load("checkpoints/epoch_03.pt", weights_only=True)
model.load_state_dict(checkpoint["model_state_dict"])
```

Save the optimizer state alongside the model. If you resume training from a checkpoint without
restoring the optimizer state, the optimizer's momentum and adaptive learning rate estimates
reset, and the learning dynamics diverge from what the model was trained on.

The `valid_loss` key in the checkpoint dict is not cosmetic. It is the criterion you will use
later to decide which checkpoint to promote to the eval gate. Store it at checkpoint time so
you do not have to rerun validation to recover it.

## Learning Rate and the Loss Curve Shape

A learning rate that is too high produces a jagged, erratic loss curve; a learning rate that
is too low produces loss that barely moves. The curve shape is the first diagnostic for
learning rate problems, which is why you need to log loss every batch, not just every epoch.

The canonical sign of a learning rate that is too high is a loss that decreases initially and
then spikes: the optimizer overshoots a minimum and the gradients explode. The canonical sign
of a learning rate that is too low is a loss that decreases very slowly and plateaus well above
what the model is capable of.

Learning rate schedules (linear warmup, cosine decay) exist because neither extreme is where
you want to spend the whole run. Warmup at the start prevents early instability; decay at the
end allows fine-grained convergence. Both appear in the training loops this book builds; the
loss curve is how you confirm they are working.

## The Validation Loop

The validation loop is structurally identical to the training loop with two differences:
`model.eval()` and `torch.no_grad()`.

```python
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    loss_fn: nn.Module,
    device: torch.device,
) -> tuple[float, float]:
    model.eval()
    total_loss = 0.0
    correct_tokens = 0
    total_tokens = 0

    with torch.no_grad():
        for batch_inputs, batch_labels in loader:
            batch_inputs = batch_inputs.to(device)
            batch_labels = batch_labels.to(device)

            logits = model(batch_inputs)
            loss = loss_fn(logits, batch_labels)
            total_loss += loss.item()

            preds = logits.argmax(dim=-1)
            correct_tokens += (preds == batch_labels).sum().item()
            total_tokens += batch_labels.numel()

    avg_loss = total_loss / len(loader)
    token_acc = correct_tokens / total_tokens
    return avg_loss, token_acc
```

`model.eval()` disables dropout and batch normalization layers that behave differently during
training. `torch.no_grad()` disables gradient tracking, which saves memory and speeds up the
forward pass. Omitting either produces validation numbers that are not comparable to what you
would see at inference time.

Call `evaluate()` at the end of every epoch. Log the results. Decide on checkpoint promotion
based on the logged `valid_loss`.

## From Loss Curves to a Promotion Decision

The through-line from this lesson to the rest of the book: every checkpoint promotion decision
is grounded in validation metrics, not in how low the training loss got. The eval gate in M5
formalizes this: it is a script that reads the validation metrics for a candidate checkpoint
and exits non-zero if the checkpoint does not beat the baseline. The discipline starts here.

If your loss curves are not telling a clear story, the next steps in order are:

1. Verify the train/validation split is correct and the sets do not overlap.
2. Check that `model.eval()` and `torch.no_grad()` are present in the validation loop.
3. Reduce the learning rate and rerun.
4. Reduce the number of epochs.
5. Check that the dataset is not too small to produce a stable validation signal.

The order matters. Most "the model won't converge" problems are actually data or eval-loop
bugs, not hyperparameter problems. Fix the plumbing before tuning the knobs.

## Core Concepts

- Tracking only training loss is a known failure mode: overfitting shows up as training loss
  decreasing while validation loss plateaus or rises, and these diverge at the checkpoint worth
  promoting.
- Azure AI Foundry logs four metrics per fine-tuning run (`train_loss`, `full_valid_loss`,
  `train_mean_token_accuracy`, `full_valid_mean_token_accuracy`); the same four signals belong
  in any local MLflow run [MS-Learn: Azure AI Foundry fine-tuning metrics].
- Token accuracy near 100% is a sign of overfitting on short completions, not a sign of a
  production-ready model; it is a companion metric to loss, not a substitute.
- Early stopping is a policy about checkpoint promotion: save the checkpoint with best
  validation loss, stop when patience epochs have elapsed without improvement.
- The checkpoint dict must include optimizer state; restoring model weights without optimizer
  state resets learning dynamics mid-run.
- `model.eval()` and `torch.no_grad()` are both required in the validation loop; omitting
  either produces metrics that do not reflect inference-time behavior.
- Loss curve shape diagnoses learning rate problems: jagged and spiking means too high; slow
  and plateauing means too low; use per-batch logging to see the shape.

<div class="claude-handoff" data-exercise="draft/exercises/02-loss-curves-overfit/">

**Build It in Claude Code**: Extend the training loop from Lesson 1 to add a full validation
loop (`model.eval()`, `torch.no_grad()`), per-epoch MLflow logging of both train loss and
valid loss, and a checkpoint-saving policy that keeps only the best checkpoint by validation
loss. Then deliberately induce overfitting (remove regularization, increase epochs, tiny
training set) and produce a loss-curve plot showing the divergence pattern. Confirm the saved
checkpoint is from the epoch before divergence, not the final epoch.

</div>
