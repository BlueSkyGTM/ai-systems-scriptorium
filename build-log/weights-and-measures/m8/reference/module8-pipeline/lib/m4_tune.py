"""m4_tune.py — the reusable fine-tune loop (M4's technique).

The one training primitive every other stage borrows: given the trainable parameters and
a no-argument loss closure, run a fixed number of Adam steps and return the final loss.
Keeping the loop in one place is what lets m6_train stay about the model and the pipeline
stay about composition.
"""
from __future__ import annotations

from typing import Callable, Iterable

import torch


def fit(params: Iterable[torch.nn.Parameter], loss_fn: Callable[[], torch.Tensor],
        epochs: int, lr: float) -> float:
    """Run `epochs` Adam steps on `params`, minimising `loss_fn()`. Returns final loss."""
    params = list(params)
    opt = torch.optim.Adam(params, lr=lr)
    final = 0.0
    for _ in range(epochs):
        opt.zero_grad()
        loss = loss_fn()
        loss.backward()
        opt.step()
        final = float(loss.item())
    return final
