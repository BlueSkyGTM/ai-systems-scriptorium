# Instrumenting the Run

A GPU job that ran for two hours and produced a checkpoint you cannot trust is not a setback;
it is a bill. The tools to avoid paying it are not expensive: one batch, 100 steps, and the
loss curve you should have been watching from minute one. That is the whole lesson.

Overfitting does not announce itself. It hides in a training loss that looks great until you
compare it to the validation loss rising beside it. The job of this module's payoff is to
instrument a run so that divergence is visible, catchable, and stopped at the right epoch
instead of the last one.

## The Overfit-One-Batch Sanity Test

Before you submit a full training run, run one batch for 100 to 200 steps and watch the loss.
It must fall to approximately zero. A single linear layer on a linearly separable batch with
no regularization will converge there in well under 200 steps. If it does not, the problem
is in the loop or the loss, not the dataset.

The `aefs` debugging framework names this check `overfit_one_batch`. The logic is the same
in any training framework:

1. Pull one batch from the training loader.
2. Repeat the five-step loop (zero, forward, loss, backward, step) for 100-200 iterations on
   that same batch.
3. Assert the final loss is near zero.

A failure here is unambiguous: the backward pass is not reaching the weights, the loss function
is receiving the wrong input shape, or the optimizer is not stepping. None of those causes live
in your data. Fix the wiring before you look anywhere else.

## The Three Loss-Health States

Once the loop clears the one-batch test, a full run can still fail in three recognizable ways.
Read the curve shape before reaching for any knob:

**`NAN_OR_INF`**: loss spikes or prints `nan` within the first few epochs. The usual causes,
in order: LR too high (gradient explodes), `log(0)` in the loss (a predicted probability of
exactly zero passed into cross-entropy), or division by zero in BatchNorm (batch size of 1).
Halve the LR and recheck. If NaN persists, confirm that `CrossEntropyLoss` is receiving raw
logits, not softmax outputs.

**`NOT_DECREASING`**: loss barely moves across epochs. LR too low is the obvious read;
a data bug is the less obvious one. Confirm the labels match the inputs (a shuffled label
array and an unshuffled input tensor is a silent failure that looks like a flat loss curve),
then raise the LR by a factor of 10 and rerun the smoke test.

**`OSCILLATING`**: loss bounces from epoch to epoch without a clear downward trend. LR is
unstable for this batch size, or the batch is too small to produce a stable gradient signal.
Reduce the LR or increase the batch size. A learning rate scheduler (warmup then cosine
decay) often converts an oscillating run into a converging one.

## Debug Order: Plumbing Before Knobs

The order in the draft is the order in practice. When a run will not converge:

1. Verify the train/validation split: no overlap; split before any preprocessing that touches
   the full dataset.
2. Confirm both `model.eval()` and `torch.no_grad()` (or `torch.inference_mode()`) are present
   in the validation loop. Either flag missing means the validation numbers do not match
   inference-time behavior.
3. Run the two-batch smoke test and the one-batch overfit test: confirm gradients are flowing
   and the loss function is receiving the right shape.
4. Only after those three pass: adjust LR, epoch count, or model size.

Most "the model won't converge" reports skip steps 1-3 and land on step 4. The fix that
lands there is a slower version of the original bug.

## Deliberately Inducing Overfitting

The clearest way to prove the instrumentation works is to make it catch something real.
The `trainer.py` overfit demo uses three levers: a tiny training set (16 samples), no
regularization, and patience=3 with max_epochs=30. The training loss memorises the 16 samples
and keeps falling; the validation loss improves through epoch 4 then rises. Early stopping
fires after epoch 7.

The verified trajectory from `FREEZE-VERIFIED.md` (real captured output):

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

Training loss at epoch 7 is 0.09: the model is nearly perfect on 16 samples. Validation
loss at epoch 7 is 1.54: worse than at epoch 4, when generalization peaked. The checkpoint
saved and restored is epoch 4. Without `fit()`'s early-stopping counter and best-epoch
tracking, you would have promoted the epoch-7 weights and deployed a model that had
memorized the training set.

The two signals that make this work are the same two this module built: a correct validation
loop (both flags), and an explicit promotion criterion stored in the checkpoint dict (`valid_loss`
at save time, not reconstructed later). Remove either and the instrument goes dark.

## What `check_loop.py --module 2` Checks

`check_loop.py` verifies structure, not behavior. With `--module 2`, it confirms the submitted
file has:

- The M1 five-step loop (zero, forward, loss, backward, step) in the canonical order.
- A trainable-parameter check (`requires_grad` plus a counting construct).
- A `model.eval()` call (validation pass present).
- A `torch.no_grad()` or `torch.inference_mode()` context (grad disabled in the val pass).
- An early-stopping signal: `best` together with `valid` or `patience`.

Missing any of those is a structural failure the checker names exactly. A loop that passes all
five checks and then shows a divergence you can read in the trajectory is a loop worth promoting
to the eval gate in M5.

The checkpoint a hiring screen sees is the one `fit()` restores: the epoch with the best
validation loss, saved before divergence, carrying both model and optimizer state. That is not
the default behavior of a training loop you write without the discipline from this module; it
is the thing this module adds.

## Core Concepts

- The overfit-one-batch sanity test (100-200 steps, one batch, loss to zero) is a gate before
  a full run, not an optional warmup: if loss does not fall to approximately zero, the loop or
  the loss function is broken, and the problem is not the data.
- Loss-health states map directly to root causes: `NAN_OR_INF` means LR too high, `log(0)`,
  or a division by zero in the loss; `NOT_DECREASING` means LR too low or a data bug;
  `OSCILLATING` means LR is unstable or the batch size is too small.
- Debug order is fixed: fix the plumbing first (split correctness, eval loop flags, gradient
  flow), then adjust the knobs (LR, epochs, model size). Most "won't converge" bugs are
  data and eval-loop bugs wearing hyperparameter masks.
- `fit(...)` catches divergence automatically when the validation pass and the early-stopping
  counter are wired together: it saves the best-epoch checkpoint and restores it before
  returning, so the promoted model is always pre-divergence.

<div class="claude-handoff" data-exercise="exercises/module2/instrumenting-the-run/">

**Build It in Claude Code**: Take the `fit(...)` function from `trainer.py` and wire it into
your own training loop: add the validation pass with both `model.eval()` and `torch.no_grad()`,
add the early-stopping counter and best-checkpoint tracking, deliberately induce overfitting
by using a tiny training set with no regularization and a high epoch ceiling, then confirm
the returned checkpoint is from an epoch before the final epoch. Run
`python check_loop.py --module 2 <your_loop>.py` and make it PASS on all five checks.

</div>
