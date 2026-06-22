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
