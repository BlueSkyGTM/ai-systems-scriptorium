# Reading Loss Curves

"Loss went down" ends most fine-tuning tutorials. It is not a verdict; it is the start of a question. The question is: which loss, and compared to what?

A training loss that keeps falling while validation loss rises is a model memorizing your training set and failing on everything else. The difference between that run and a healthy one shows up in the loss curves, not in the final training loss. Reading that difference is what this lesson builds.

## The Divergence Pattern

A healthy run has both losses decreasing together, with validation loss staying close to (and slightly above) training loss throughout. Some gap between them is normal. The signal is the *rate* at which that gap widens.

An overfit run has a signature: training loss continues dropping after a certain epoch, while validation loss plateaus or turns upward. The model is fitting the training data more precisely while its performance on held-out data gets worse. Every checkpoint after that turning point is moving in the wrong direction. The one to promote is the checkpoint at peak validation performance.

The verified trajectory from `trainer.py` (torch 2.12.1+cpu, seed=7, 16-sample training set, patience=3):

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
Best epoch: 4  (valid_loss=1.5141)
```

Training loss falls monotonically from 1.52 to 0.09: classic memorization. Validation loss improves through epoch 4, then climbs to 1.54 by epoch 7. The run at epoch 7 looks better by training loss and would fool anyone reading only that column.

For comparison, a clean teaching illustration of the same pattern without noise:

```
Epoch    train_loss    valid_loss
1        1.84          1.92
2        1.41          1.47
3        1.12          1.18    <-- valid turns; train keeps dropping
4        0.89          1.22
5        0.71          1.38
6        0.58          1.51    <-- best checkpoint was epoch 3
```

Both tables tell the same story. In the first, the turn is at epoch 4. In the second, it is at epoch 3. The shape is the pattern; the exact numbers follow from the data and the hyperparameters.

## The Generalization Gap

The gap between `train_loss` and `valid_loss` is the generalization gap. Some gap exists in every healthy run: the model has seen the training examples repeatedly and not the validation examples at all. That asymmetry produces a small, stable offset.

The signal is not the presence of a gap; it is the rate at which the gap grows. A gap that stays narrow and roughly constant means the model is generalizing. A gap that widens epoch-over-epoch means the model is overfitting. The turning point in the verified run above is the epoch where the gap stops narrowing and starts to grow.

Azure AI Foundry's fine-tuning pipeline logs four metrics to `results.csv` and visualizes them in the portal: `train_loss`, `full_valid_loss`, `train_mean_token_accuracy`, and `full_valid_mean_token_accuracy`. The documentation states directly: "Divergence between training and validation may indicate overfitting; try fewer epochs or a smaller LR." ([Azure AI Foundry fine-tuning, analyze your customized model](https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning#analyze-your-fine-tuned-model).) These are not Azure-specific metrics. They are the same four signals you would log yourself in a local MLflow run. The portal makes them visible without extra code.

## Token Accuracy as a Companion, Not a Substitute

`train_mean_token_accuracy` and `full_valid_mean_token_accuracy` measure the fraction of output tokens the model predicted correctly. For instruction-tuned language models, this is an informative companion metric, not a replacement for loss.

The reason: accuracy close to 100% is not a sign of strength. On short completions, a model can reach near-perfect accuracy by memorizing the expected token sequence verbatim. Azure Databricks documents this directly: "Accuracy close to 100% might demonstrate overfitting." ([Azure Databricks fine-tuning run tutorial, step 5 view metrics and outputs](https://learn.microsoft.com/azure/databricks/large-language-models/foundation-model-training/fine-tune-run-tutorial#step-5-view-metrics-and-outputs).)

If accuracy climbs toward 100% while `valid_loss` rises, the signals agree. Track both; trust the loss.

## LR and Curve Shape

Loss curves carry a second diagnostic: learning rate health. A learning rate that is too high produces a jagged, spiking curve as the optimizer repeatedly overshoots and the loss jumps. A learning rate that is too low produces loss that barely moves, a flat line that plateaus far above the model's capability.

Per-batch logging is what makes this shape visible. Epoch-level logging averages out the noise; you see that loss decreased but not how it got there. The curve shape, the rhythm of loss across individual batches, is where learning rate problems announce themselves.

Learning rate schedules (linear warmup, cosine decay) address both extremes: warmup at the start prevents early instability; decay at the end allows fine-grained convergence. Reading the curve is how you confirm the schedule is working.

## The Promotion Decision

The through-line from this lesson forward: every checkpoint promotion decision is grounded in `valid_loss`, not in how low training loss got. A checkpoint looks good only if its validation metric beats the alternatives. The eval gate in Module 5 formalizes this as a script that reads validation metrics for a candidate checkpoint and exits non-zero if it does not beat the baseline. The discipline starts here, at the curve.

A model whose training loss impresses you is not a good model. It is the start of a question.

## Core Concepts

- The overfitting signal is divergence: training loss continues dropping while validation loss plateaus or rises. The checkpoint at peak validation is the one to promote; every checkpoint after that point moves in the wrong direction.
- The generalization gap (train vs. val loss offset) is expected in every run; the signal is the rate at which it widens, not the gap's existence.
- Token accuracy near 100% on short completions is an overfit signal, not strength; it is a companion to loss, not a substitute (per both Azure AI Foundry and Azure Databricks documentation).
- Loss curve shape diagnoses learning rate problems: jagged and spiking means too high; slow and flat means too low. Per-batch logging is what makes the shape visible.
- "Loss went down" is the start of a question (which loss, versus what), not a verdict.

<div class="claude-handoff" data-exercise="exercises/module2/reading-loss-curves/">

**Build It in Claude Code**: Add a per-epoch logging loop to `trainer.py` that records both `train_loss` and `valid_loss` to a list or CSV, then tabulate the results and identify the epoch where `valid_loss` turns upward. Using the overfit demo setup from Module 2 (tiny training set, no regularization, enough epochs to diverge), confirm that the epoch at which you would promote the checkpoint is before the final epoch, then write one sentence explaining why you would reject the final-epoch checkpoint even though its training loss is the lowest in the run.

</div>
