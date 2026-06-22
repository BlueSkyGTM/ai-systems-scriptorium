# PyTorch Operator Catalog: Weights and Measures M1 Reference Ingredient

Distilled 2026-06-21 from the named vault ore + live PyTorch / MS-Learn docs (Haiku fetch tier).
Dense; no prose polish. This is the **schema the M1 lesson authors fill**: author against this
ingredient, not the raw vault tree.

**Grounding rule (load-bearing):** M1 teaches the *real PyTorch framework*. The aefs Phase-03
from-scratch code (the `Value` autograd class, the hand-rolled `Adam`, the pure-Python mini-framework
`Linear`) is **conceptual scaffolding only**: use it to *explain what autograd/optimizers do
underneath*, never as the canonical code the reader writes. Canonical M1 code = real `torch`,
grounded in aefs `11-intro-to-pytorch`, `made-with-ml`'s production `train_step`/`eval_step`, and the
PyTorch doc anchors below. Every canonical code block is CONDUCTOR-FROZEN (authored + run on a
torch-CPU env, pasted byte-identical into author briefs); the marker `[FREEZE]` flags a block the
conductor must verify before Round 2.

**Doc version:** PyTorch 2.x (Azure ML curated env: PyTorch 2.8 + CUDA 12.6). APIs below are stable
in torch 2.x. `torch.compile` exists but is out of M1 scope (it lands in M4).

---

## Doc anchors (cite these; real URLs from the docs fetch)

| Topic | Canonical URL | Load-bearing facts |
|---|---|---|
| Tensor | https://docs.pytorch.org/docs/stable/tensors.html | `.shape` / `.dtype` / `.device` / `.requires_grad`; `.to(device)` is explicit; CPU↔CUDA op raises `RuntimeError`. |
| Autograd | https://docs.pytorch.org/docs/stable/autograd.html | runtime DAG; `.backward()` reverse-traverses; `.grad` only on leaf tensors with `requires_grad=True`; `torch.no_grad()` / `inference_mode()` for eval. |
| nn.Module | https://docs.pytorch.org/docs/stable/generated/torch.nn.Module.html | contract = `__init__` (register params via attribute assignment) + `forward`; `parameters()`, `state_dict()`, `train()`/`eval()`. |
| DataLoader | https://docs.pytorch.org/docs/stable/data.html | `batch_size` / `shuffle` / `num_workers` / `pin_memory` / `collate_fn`; yields batches; `pin_memory=True` speeds GPU transfer. |
| optim + schedulers | https://docs.pytorch.org/docs/stable/optim.html | `optimizer.step()` after `backward()`; `zero_grad()` before; `StepLR`/`CosineAnnealingLR`; call `scheduler.step()` per epoch. |
| save/load | https://docs.pytorch.org/docs/stable/generated/torch.save.html | save the **state_dict**, not the model object; `load_state_dict(strict=...)`; checkpoint = dict of epoch+model+optimizer state. |
| Azure ML PyTorch job | https://learn.microsoft.com/azure/machine-learning/how-to-train-pytorch?view=azureml-api-2 | device/compute config: `AmlCompute` size/min/max; curated `AzureML-acpt-pytorch-2.8-cuda12.6`; `command()` job with `${{inputs.*}}`. |

---

## L1: `tensors-and-autograd`

**Thesis:** a tensor is an array plus `device` and `requires_grad`; autograd is the bookkeeping you
do not write. The through-line question begins here: *check `shape`/`dtype`/`device` before you trust
any tensor entering a model.*

**Canonical code (real torch) [FREEZE]:**
```python
import torch

x = torch.tensor([[1., 2.], [3., 4.]])      # cpu, float32
print(x.shape, x.dtype, x.device)            # torch.Size([2, 2]) torch.float32 cpu

w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(0.5, requires_grad=True)
y_pred = w * 3.0 + b                          # 6.5
loss = (y_pred - 7.0) ** 2                    # 0.25
loss.backward()
print(w.grad, b.grad)                         # tensor(-3.) tensor(-1.)
```
Hand-derivation to show: d(loss)/dw = 2(y_pred−y_true)·x = 2(−0.5)(3) = −3.0; d/db = −1.0. **Expected
output is conductor-verified, not asserted.**

**Conceptual scaffold (aefs from-scratch; explain, do NOT have reader write):** the `Value` class
with `_backward` closures + reverse-topological `backward()` shows the DAG autograd builds.
Source: `vault/ai-engineering-from-scratch/phases/03-deep-learning-core/03-backpropagation/code/main.py`.

**Verify discipline:** verify gradients by hand on a 2-parameter toy before trusting the engine on a
large model. `zero_grad` before each step (grads accumulate by default).

**Facts:** `requires_grad` only on leaves; float labels into `CrossEntropyLoss` raises (labels are
`torch.long`); integer dtype into a linear layer raises.

---

## L2: `the-module-and-the-loop`

**Thesis:** `nn.Module` is the model contract; the loop is five steps in order. The
trainable-vs-total parameter check is the precondition for the M4 LoRA freeze.

**Canonical code (real torch) [FREEZE]** (adapted from aefs `11-intro-to-pytorch`):
```python
import torch.nn as nn

class TinyClassifier(nn.Module):
    def __init__(self, in_dim: int, n_classes: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, n_classes)
    def forward(self, x):
        return self.linear(x)                 # [batch, n_classes]

model = TinyClassifier(128, 4)
total = sum(p.numel() for p in model.parameters())
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(total, trainable)                       # 516 516  (all trainable until a freeze)
```

**Canonical loop [FREEZE]** (the five labeled steps; ground in made-with-ml `train_step`):
```python
def train_one_epoch(model, loader, optimizer, loss_fn, device):
    model.train()
    running = 0.0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)  # 1 device
        optimizer.zero_grad()                                  # 2 zero
        logits = model(inputs)                                 # 3 forward
        loss = loss_fn(logits, labels)                         # 4 loss
        loss.backward()                                        # 5 backward
        optimizer.step()                                       # 6 update
        running += loss.item()
    return running / len(loader)
```

**Real production reference (made-with-ml):** `train_step` uses
`loss += (J.detach().item() - loss) / (i + 1)` (running-mean loss); `eval_step` uses
`torch.inference_mode()` + `model.eval()`.
Source: `vault/made-with-ml/madewithml/train.py`.

**Verify discipline:** log `loss.item()`, lr, step every batch (a loop with no per-batch logging is a
black box). Param-count check: `trainable` must equal what you intend to train.

---

## L3: `data-optimizers-checkpoints`

**Thesis:** `DataLoader` batches/shuffles/parallelizes; the optimizer + one schedule drive updates;
`state_dict` is the checkpoint artifact.

**Canonical code (real torch) [FREEZE]:**
```python
from torch.utils.data import DataLoader

train_loader = DataLoader(train_ds, batch_size=64, shuffle=True,  num_workers=2, pin_memory=True)
val_loader   = DataLoader(val_ds,   batch_size=256, shuffle=False)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
# ... per epoch: train, validate, scheduler.step()

torch.save({"epoch": ep, "model": model.state_dict(), "optimizer": optimizer.state_dict()}, "ckpt.pt")
ckpt = torch.load("ckpt.pt", weights_only=True)
model.load_state_dict(ckpt["model"])
```

**Facts:** Adam defaults lr=1e-3, betas=(0.9, 0.999), eps=1e-8; fine for most problems untuned.
`shuffle=True` train only, never val. `num_workers` is set from the profiler (M4), not a blog post.
made-with-ml uses `ReduceLROnPlateau(mode="min")` stepped on `val_loss`; a real alternative to show.

**Verify discipline:** save state_dict (not the model object) for portability; reload and confirm a
forward pass matches before trusting a checkpoint.

---

## L4: `reading-a-real-train-py`

**Thesis:** the payoff: read an unfamiliar `train.py`, name what each section asserts, run the
two-batch smoke test before scaling. Debugging is verification, not vibes.

**Canonical verify snippet [FREEZE]** (the two-batch smoke test):
```python
def smoke_two_batches(model, loader, optimizer, loss_fn, device):
    model.train()
    losses = []
    for i, (x, y) in enumerate(loader):
        if i == 2: break
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
    assert losses[1] < losses[0], "loss did not decrease over two batches"
    assert sum(p.requires_grad for p in model.parameters()) > 0, "no trainable params"
    return losses
```

**The verify checklist the lesson teaches (from aefs `13-debugging-neural-networks`):**
1. Overfit-one-batch: train on 8 to 32 samples for 100+ iters; loss → ~0. Catches a broken
   loss/backward/optimizer hookup.
2. Common silent failures: missing `zero_grad` (grads accumulate); missing `eval()` at test
   (dropout/BN wrong); CPU/CUDA device mismatch; missing `no_grad`/`inference_mode` at inference.
3. NaN/Inf: lr too high; `log(0)` in cross-entropy; div-by-zero in BatchNorm.
Source: `.../13-debugging-neural-networks/code/debug_neural_nets.py` (the `NetworkDebugger` hooks).

**Verify discipline:** the two-batch smoke (loss decreases, right params trainable, shapes match)
runs in under a minute and catches the majority of bugs that otherwise surface after an hour of GPU.

---

## Throughline hook (M1 segment of `trainer.py` + `check_loop.py`)

- `trainer.py` M1 = the bare verified loop above (`train_one_epoch` + `smoke_two_batches`), extended
  in place by later modules (M2 train/val + early stop, M4 LoRA, M5 eval gate).
- `check_loop.py` = stdlib validator (NO torch import) that statically confirms a loop file has the
  five steps in the right order + the trainable-param check present. The rubric IS the schema; the
  pass/fail score is the handoff. (Conductor-frozen; see `build-log/weights-and-measures/m1/`.)

## Expected-value provenance (verify before publishing)

- L1 grads (−3.0, −1.0): hand-derivable; conductor confirms on torch-CPU.
- L2 param count 516 = 128·4 + 4 (Linear bias); conductor confirms.
- aefs `11-intro-to-pytorch` MNIST MLP (784→256→128→10) = 235,146 params, ~97.8% test acc after 10
  epochs: label "what you should see (approx)", not a hard assertion; reader confirms on own run.
