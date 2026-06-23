# Fitting Catalog: Weights and Measures M2 Reference Ingredient

Distilled 2026-06-21 (Haiku fetch tier) from the in-book draft `draft/02-loss-curves-overfit.md`
(M2's primary, already-dense input) + `aefs` Phase 03 (`07-regularization`, `13-debugging-neural-networks`)
+ `made-with-ml` `train.py` + live MS-Learn / PyTorch docs. The **schema the M2 authors fill**: author
against this + the draft, not the raw vault.

**Grounding rule (carries from M1):** real PyTorch only. The `aefs` from-scratch debugger code is
conceptual scaffolding for the *checks* it teaches (overfit-one-batch, loss-health states), not code
the reader copies verbatim into a torch run. Every canonical code block is Sonnet-frozen (written +
RUN) before authoring; `[FREEZE]` marks a block the spine-engineer must verify.

**Doc version:** PyTorch 2.12. Core `torch` has **NO built-in `EarlyStopping`**; it is a hand-rolled
pattern (counter + best-metric tracking). Do not invent a torch API for it.

---

## Doc anchors (cite these; real URLs)

| Topic | URL | Facts |
|---|---|---|
| Azure AI Foundry fine-tune metrics | https://learn.microsoft.com/azure/ai-foundry/openai/how-to/fine-tuning#analyze-your-fine-tuned-model | `results.csv` logs `train_loss`, `valid_loss`, `full_valid_loss` (end-of-epoch), `train_mean_token_accuracy`, `full_valid_mean_token_accuracy`. "Divergence between training and validation may indicate overfitting; try fewer epochs or a smaller LR." |
| Azure Databricks token accuracy | https://learn.microsoft.com/azure/databricks/large-language-models/foundation-model-training/fine-tune-run-tutorial#step-5-view-metrics-and-outputs | "Accuracy close to 100% might demonstrate overfitting." Eval loss can mislead on instruction tasks; use it as one signal. |
| no_grad vs inference_mode | https://docs.pytorch.org/docs/2.12/generated/torch.no_grad.html | both disable grad; `inference_mode` is stricter/faster. Orthogonal to `eval()`. |
| Module.eval()/train() | https://docs.pytorch.org/docs/2.12/generated/torch.nn.Module.html | `eval()` = `train(False)`; switches Dropout off and BatchNorm to running stats; does NOT disable grad. |
| lr_scheduler | https://docs.pytorch.org/docs/2.12/generated/torch.optim.lr_scheduler.ReduceLROnPlateau.html | `LinearLR(start_factor,...)` warmup; `CosineAnnealingLR(T_max, eta_min)` decay; `ReduceLROnPlateau(mode="min", factor, patience)` stepped as `scheduler.step(val_loss)` (takes the metric, not blind per-epoch). |
| checkpoint | https://docs.pytorch.org/docs/2.12/generated/torch.save.html | save a dict with `model.state_dict()` AND `optimizer.state_dict()`; optimizer state holds momentum/adaptive estimates, so resume without it diverges. |

---

## L1: `the-held-out-set`

**Thesis:** two scalar signals are mandatory: `train_loss` (per batch, grad on) and `valid_loss`
(held-out, grad off, end of epoch). Tracking only train loss is a known failure mode.

**Facts:** the leak (any train/val overlap invalidates the val signal; split first, preprocess
second). The validation loop needs BOTH `model.eval()` (Dropout off, BatchNorm running stats) AND
`torch.no_grad()`/`inference_mode()` (grad off); omitting either makes the numbers not match inference.

**Canonical code [FREEZE]**: the validation loop (verbatim from `draft/02` L136-163; the spine-engineer
folds this into `trainer.py` as `evaluate(...)` returning `(avg_loss, token_acc)`):
```python
def evaluate(model, loader, loss_fn, device):
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

---

## L2: `reading-loss-curves`

**Thesis:** the divergence pattern is the overfitting signal: train loss keeps dropping while
validation loss plateaus or rises; the checkpoint at peak validation is the one to promote.

**Canonical data [FREEZE]**: the worked epoch table (verbatim from `draft/02`; best = epoch 3):
```
Epoch    train_loss    valid_loss
1        1.84          1.92
2        1.41          1.47
3        1.12          1.18    <-- valid turns; train keeps dropping
4        0.89          1.22
5        0.71          1.38
6        0.58          1.51    <-- best checkpoint was epoch 3
```

**Facts:** the generalization gap (some gap is normal; the *rate* of divergence is the signal). Token
accuracy is a companion not a substitute; near-100% on short completions is an overfit signal, not
strength (MS-Learn confirms). LR vs curve shape: jagged/spiking = LR too high (overshoot); slow/flat =
LR too low. Per-batch logging is what makes the shape visible.

---

## L3: `early-stopping-as-a-policy`

**Thesis:** early stopping is an auditable checkpoint-promotion policy, not a hyperparameter: "save
the checkpoint with best `valid_loss`; if no improvement for N epochs, stop and promote the best."
Patience N = 2-5 (tighter risks premature stop; looser burns compute).

**Canonical code [FREEZE]**: the checkpoint dict (verbatim from `draft/02`; the `valid_loss` key is the
promotion criterion, optimizer state is mandatory for resume):
```python
torch.save({
    "epoch": epoch,
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "valid_loss": valid_loss,
}, f"checkpoints/epoch_{epoch:02d}.pt")
```

**Real scheduler reference (mwml `train.py`):** `ReduceLROnPlateau(optimizer, mode="min", factor=...,
patience=...)` then `scheduler.step(val_loss)`; the scheduler is driven by the validation metric, the
same signal early stopping watches.

---

## L4: `instrumenting-the-run` (capstone)

**Thesis:** instrument a run to catch overfitting before it wastes GPU; deliberately induce it (tiny
train set, no regularization, too many epochs) and confirm the saved checkpoint is pre-divergence.

**Facts (the verify checklist, from `aefs 13`):**
- Overfit-one-batch: train on one batch for ~100-200 steps; loss must fall to ~0. Fails => the loop or
  loss is broken. This is the gate before a full run.
- Loss-health states: `NAN_OR_INF` (LR too high; log(0); div-by-zero), `NOT_DECREASING` (LR too low or
  data bug), `OSCILLATING` (LR unstable or batch too small).
- Debug order (from `draft/02`): fix the plumbing (split, eval loop, gradients) before the knobs (LR,
  epochs, model size). Most "won't converge" bugs are data/eval-loop bugs, not hyperparameters.

**Conceptual scaffold (aefs `13`, explain don't hand to reader as torch):** `overfit_one_batch(...)`
and `NetworkDebugger.check_loss_health()` show the checks; the reader implements the equivalent against
the real spine.

---

## Throughline (the spine-engineer builds + freezes these)

- `exercises/spine/trainer.py` gains: `evaluate(model, loader, loss_fn, device) -> (loss, acc)` and
  `fit(model, train_loader, val_loader, optimizer, loss_fn, device, max_epochs, patience)`: per-epoch
  train + validate, track best `valid_loss`, early-stop on patience, return the best-epoch record. M1's
  `train_one_epoch` + `smoke_two_batches` stay byte-identical.
- `exercises/spine/check_loop.py` gains `--module 2`: on top of M1 checks, require a `model.eval()`
  call, a `no_grad`/`inference_mode` context, and an early-stop signal (`best` + `valid`/`patience`).
  No flag = M1 behavior, byte-identical. `--selftest` covers both modules with good + bad cases.
- Verify on torch-CPU: the `fit` early-stop demo must show a divergence (val turning up) and stop at /
  restore the best epoch; capture the real trajectory in `FREEZE-VERIFIED.md`.
