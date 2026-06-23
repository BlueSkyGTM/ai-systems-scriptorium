"""trainer.py - Weights and Measures M1: The PyTorch Operator

The M1 segment of the book's runnable spine. Authors paste from this file verbatim.
Every function here is conductor-verified on torch 2.x CPU.

Extended in place each module:
  M1  (this file): bare verified loop + two-batch smoke test
  M2: train/val split + early-stopping hook
  M3: dataset contract
  M4: LoRA adapter insertion
  M5: eval gate
  M6: portfolio train.py

The five-step loop order (canonical contract, gated by check_loop.py):
  1. zero_grad  2. forward  3. loss  4. backward  5. step
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---------------------------------------------------------------------------
# Model: used by the self-demo and referenced in the catalog L2 block
# ---------------------------------------------------------------------------

class TinyClassifier(nn.Module):
    """Single linear layer: (batch, in_dim) -> (batch, n_classes).

    Minimal nn.Module for verifying the loop contract. Not a "real" architecture;
    it exists so every M1 code path runs without a heavyweight model.
    """

    def __init__(self, in_dim: int, n_classes: int) -> None:
        super().__init__()
        self.linear = nn.Linear(in_dim, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear(x)  # [batch, n_classes]


# ---------------------------------------------------------------------------
# L2: train_one_epoch: the canonical five-step loop
# ---------------------------------------------------------------------------

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device | str,
) -> float:
    """Run one full pass over the training DataLoader.

    Returns the mean loss per batch (running accumulator / number of batches).

    The five steps (in order; do not rearrange):
      1. device:        move inputs and labels to the target device
      2. zero:          zero gradients before the forward pass
      3. forward:       call the model to get logits
      4. loss:          compute scalar loss from logits + labels
      5. backward+step: backpropagate, then update weights
    """
    model.train()
    running = 0.0

    for inputs, labels in loader:
        # 1. device: explicit .to(); a CPU tensor going into a CUDA model raises RuntimeError
        inputs, labels = inputs.to(device), labels.to(device)

        # 2. zero: grads accumulate by default; clear before each batch
        optimizer.zero_grad()

        # 3. forward
        logits = model(inputs)

        # 4. loss
        loss = loss_fn(logits, labels)

        # 5. backward + step
        loss.backward()
        optimizer.step()

        running += loss.item()

    return running / len(loader)


# ---------------------------------------------------------------------------
# L4: smoke_two_batches: the two-batch verify before you scale
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# M2: evaluate (the validation loop, catalog L1 FREEZE block)
# ---------------------------------------------------------------------------

def evaluate(
    model: nn.Module,
    loader: DataLoader,
    loss_fn: nn.Module,
    device: torch.device | str,
) -> tuple[float, float]:
    """Run a full validation pass with gradients disabled.

    Both conditions are required (catalog L1):
      - model.eval(): disables Dropout and switches BatchNorm to running stats
      - torch.no_grad(): disables gradient tracking (saves memory; speeds forward pass)
    Omitting either produces validation numbers that do not match inference-time behavior.

    Returns:
        (avg_loss, token_acc) where avg_loss is mean loss per batch and token_acc is
        the fraction of correctly predicted tokens across the full loader.
    """
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


# ---------------------------------------------------------------------------
# M2: EpochRecord (typed record for one epoch's result)
# ---------------------------------------------------------------------------

@dataclass
class EpochRecord:
    """Per-epoch result stored in the history list returned by fit()."""
    epoch: int
    train_loss: float
    valid_loss: float


# ---------------------------------------------------------------------------
# M2: FitResult (the return value of fit())
# ---------------------------------------------------------------------------

@dataclass
class FitResult:
    """Summary of a fit() run.

    Attributes:
        best_epoch:      epoch number (1-indexed) of the best valid_loss checkpoint.
        best_valid_loss: the best valid_loss seen during training.
        history:         per-epoch records in chronological order.
        checkpoint_path: path where the best checkpoint was saved.
    """
    best_epoch: int
    best_valid_loss: float
    history: list[EpochRecord] = field(default_factory=list)
    checkpoint_path: str = ""


# ---------------------------------------------------------------------------
# M2: fit (per-epoch train + validate with early stopping, catalog L3)
# ---------------------------------------------------------------------------

def fit(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    device: torch.device | str,
    max_epochs: int = 20,
    patience: int = 3,
    checkpoint_dir: str | None = None,
) -> FitResult:
    """Train for up to max_epochs with validation-loss early stopping.

    Policy (catalog L3): "save the checkpoint with best valid_loss; if no
    improvement for patience epochs, stop and promote the best."

    The checkpoint dict (catalog L3 FREEZE block) includes:
        epoch, model_state_dict, optimizer_state_dict, valid_loss
    Optimizer state is mandatory: restoring weights without it resets momentum
    and adaptive estimates, causing learning dynamics to diverge on resume.

    Args:
        model:          nn.Module to train (must have requires_grad params).
        train_loader:   DataLoader for training batches.
        val_loader:     DataLoader for validation batches (held-out, no overlap).
        optimizer:      optimizer already bound to model.parameters().
        loss_fn:        loss function (same for train and val).
        device:         target device string or torch.device.
        max_epochs:     hard ceiling on training epochs.
        patience:       stop after this many epochs without valid_loss improvement.
        checkpoint_dir: directory to write checkpoints; uses a temp dir if None.

    Returns:
        FitResult with best_epoch, best_valid_loss, full history, checkpoint_path.
        The model's state is restored to the best checkpoint before returning.
    """
    if checkpoint_dir is None:
        checkpoint_dir = tempfile.mkdtemp(prefix="wm_fit_")
    os.makedirs(checkpoint_dir, exist_ok=True)

    best_valid_loss = float("inf")
    best_epoch = -1
    best_ckpt_path = ""
    epochs_without_improvement = 0
    history: list[EpochRecord] = []

    for epoch in range(1, max_epochs + 1):
        # --- training pass (five-step loop via train_one_epoch) ---
        train_loss = train_one_epoch(model, train_loader, optimizer, loss_fn, device)

        # --- validation pass (model.eval() + no_grad, both required) ---
        valid_loss, _acc = evaluate(model, val_loader, loss_fn, device)

        history.append(EpochRecord(epoch=epoch, train_loss=train_loss, valid_loss=valid_loss))

        # --- checkpoint promotion: save if this epoch has the best valid_loss ---
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            best_epoch = epoch
            epochs_without_improvement = 0

            # Catalog L3 FREEZE block: save a dict with epoch, state_dicts, valid_loss
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
            break  # best checkpoint already saved; restore below

    # --- restore best checkpoint before returning ---
    if best_ckpt_path and os.path.isfile(best_ckpt_path):
        ckpt = torch.load(best_ckpt_path, weights_only=True)
        model.load_state_dict(ckpt["model_state_dict"])

    return FitResult(
        best_epoch=best_epoch,
        best_valid_loss=best_valid_loss,
        history=history,
        checkpoint_path=best_ckpt_path,
    )


# ---------------------------------------------------------------------------
# Self-demo (run as a script): pure torch, CPU, synthetic data, < 30 s
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    torch.manual_seed(42)
    device = torch.device("cpu")

    # --- synthetic classification dataset (no downloads) ---
    # Build a linearly-separable task: each class is centred on a distinct axis.
    # Centre magnitude 5 gives enough margin that a single gradient step on one batch
    # reliably decreases the loss on the next batch (required by smoke_two_batches).
    IN_DIM, N_CLASSES = 128, 4
    N_HALF = 64  # samples per "copy" of the dataset

    chunks = []
    for cls in range(N_CLASSES):
        centre = torch.zeros(IN_DIM)
        centre[cls] = 5.0  # clear per-class signal along one dim
        chunks.append(torch.randn(N_HALF // N_CLASSES, IN_DIM) + centre)
    X_half = torch.cat(chunks, dim=0)
    y_half = torch.repeat_interleave(torch.arange(N_CLASSES), N_HALF // N_CLASSES)  # torch.long

    # smoke dataset: two identical copies of X_half so both batches see the same data.
    # This makes the loss-decrease assertion deterministic: the gradient from batch 1
    # on data D will decrease the loss on the same data D in batch 2.
    X_smoke = torch.cat([X_half, X_half], dim=0)
    y_smoke = torch.cat([y_half, y_half], dim=0)
    smoke_dataset = TensorDataset(X_smoke, y_smoke)
    smoke_loader = DataLoader(smoke_dataset, batch_size=N_HALF, shuffle=False)

    # training dataset: 512 samples with shuffle
    N_TRAIN = 512
    chunks_train = []
    for cls in range(N_CLASSES):
        centre = torch.zeros(IN_DIM)
        centre[cls] = 5.0
        chunks_train.append(torch.randn(N_TRAIN // N_CLASSES, IN_DIM) + centre)
    X_train = torch.cat(chunks_train, dim=0)
    y_train = torch.repeat_interleave(torch.arange(N_CLASSES), N_TRAIN // N_CLASSES)
    train_dataset = TensorDataset(X_train, y_train)
    loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

    # --- model, optimizer, loss ---
    model = TinyClassifier(IN_DIM, N_CLASSES).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
    loss_fn = nn.CrossEntropyLoss()

    # --- param-count check (catalog L2) ---
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"params: total={total}, trainable={trainable}")

    # --- two-batch smoke test (catalog L4) ---
    smoke_losses = smoke_two_batches(model, smoke_loader, optimizer, loss_fn, device)
    print(f"smoke_two_batches: {smoke_losses[0]:.4f} -> {smoke_losses[1]:.4f}  [PASS]")

    # reset for clean training run (smoke test consumed 2 optimizer steps)
    model = TinyClassifier(IN_DIM, N_CLASSES).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)

    # --- training run: 10 epochs, print real loss trajectory ---
    print("\nepoch  mean_loss")
    print("-----  ---------")
    for ep in range(1, 11):
        mean_loss = train_one_epoch(model, loader, optimizer, loss_fn, device)
        print(f"  {ep:2d}   {mean_loss:.4f}")

    print("\ntrainer.py self-demo complete.")

    # -----------------------------------------------------------------------
    # M2: OVERFIT demo: deliberately induce divergence, then early-stop
    # -----------------------------------------------------------------------
    # Strategy: use a small training set (16 samples) with tight centres so the
    # model memorises it after a few epochs. Val set (128 samples) uses much
    # higher noise (std=2.5) so it tracks train down for a couple of epochs then
    # diverges. patience=3 means early stopping triggers well before max_epochs.
    # Seed chosen so best epoch lands in the 3-6 range for a clear table story.
    print("\n" + "=" * 60)
    print("M2 OVERFIT DEMO: inducing train/val divergence")
    print("=" * 60)

    torch.manual_seed(7)

    # Small training set: 16 samples, 4 per class; memorisable within ~5-8 epochs
    N_TINY = 16
    chunks_tiny = []
    for cls in range(N_CLASSES):
        centre = torch.zeros(IN_DIM)
        centre[cls] = 5.0
        chunks_tiny.append(torch.randn(N_TINY // N_CLASSES, IN_DIM) + centre)
    X_tiny = torch.cat(chunks_tiny, dim=0)
    y_tiny = torch.repeat_interleave(torch.arange(N_CLASSES), N_TINY // N_CLASSES)
    tiny_train_ds = TensorDataset(X_tiny, y_tiny)
    tiny_train_loader = DataLoader(tiny_train_ds, batch_size=4, shuffle=False)  # smaller batch = more steps/epoch

    # Val set with moderate noise: loss tracks down for 3-5 epochs then rises
    # as the model memorises the training examples.
    N_VAL = 128
    chunks_val = []
    for cls in range(N_CLASSES):
        centre = torch.zeros(IN_DIM)
        centre[cls] = 5.0
        # std=1.5 noise: meaningful but not so hard that val degrades from epoch 1
        chunks_val.append(torch.randn(N_VAL // N_CLASSES, IN_DIM) * 1.5 + centre)
    X_val = torch.cat(chunks_val, dim=0)
    y_val = torch.repeat_interleave(torch.arange(N_CLASSES), N_VAL // N_CLASSES)
    val_ds = TensorDataset(X_val, y_val)
    val_loader_overfit = DataLoader(val_ds, batch_size=32, shuffle=False)

    # Conservative LR: val loss improves for several epochs before diverging
    model_overfit = TinyClassifier(IN_DIM, N_CLASSES).to(device)
    opt_overfit = torch.optim.Adam(model_overfit.parameters(), lr=5e-3)

    result = fit(
        model_overfit,
        tiny_train_loader,
        val_loader_overfit,
        opt_overfit,
        loss_fn,
        device,
        max_epochs=30,
        patience=3,
    )

    print(f"\n{'epoch':>5}  {'train_loss':>10}  {'valid_loss':>10}")
    print(f"{'-----':>5}  {'----------':>10}  {'----------':>10}")
    for rec in result.history:
        marker = "  <-- BEST" if rec.epoch == result.best_epoch else ""
        print(f"  {rec.epoch:3d}   {rec.train_loss:10.4f}   {rec.valid_loss:10.4f}{marker}")

    total_ran = len(result.history)
    print(
        f"\nEarly stop after epoch {total_ran}  "
        f"(patience=3, no improvement since epoch {result.best_epoch})"
    )
    print(f"Best epoch : {result.best_epoch}  (valid_loss={result.best_valid_loss:.4f})")
    print(f"Final epoch: {total_ran}")
    assert result.best_epoch < total_ran, (
        f"best_epoch ({result.best_epoch}) must be BEFORE final epoch ({total_ran}); "
        "overfit demo did not induce divergence; check dataset setup"
    )
    print("[PASS] best epoch is before final epoch; divergence confirmed.")
    print("\ntrainer.py M2 overfit demo complete.")
