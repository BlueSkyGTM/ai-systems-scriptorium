"""eval.py — M6 Eval Gate for the tuned skill classifier.

Loads a fine-tuned checkpoint and a held-out JSONL test set, then evaluates
the tuned model against a majority-class baseline on two metrics:

  * exact-match accuracy
  * macro-F1

The GATE passes (exit code 0) iff the tuned model beats the baseline by
≥ 5 percentage points on BOTH metrics. Otherwise the gate BLOCKS (exit 1).

Logging goes to MLflow with an offline sqlite backend.

Checkpoint contract (produced by train.py):
    {
        "vocab":   Dict[str, int],         # word -> id; must contain <pad>, <unk>
        "label_map": Dict[str, int],       # label string -> id (5 classes)
        "config":  {embed_dim, hidden_dim, max_len, ...},
        "state_dict": OrderedDict,         # TextClassifier weights
    }

Test JSONL row contract:
    {"text": "...", "label": "..."}
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import mlflow  # optional; gated by --mlflow-off flag for CI
    HAS_MLFLOW = True
except ImportError:  # pragma: no cover
    HAS_MLFLOW = False

# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------
torch.manual_seed(42)
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CHECKPOINT = REPO_ROOT / "outputs" / "skill_classifier.pt"
DEFAULT_TEST = REPO_ROOT / "data" / "test.jsonl"
DEFAULT_OUTPUTS_DIR = REPO_ROOT / "outputs"

MARGIN_PP = 5.0  # gate requires >= 5 percentage points on BOTH metrics


# ---------------------------------------------------------------------------
# Model — must mirror train.py exactly so state_dict loads cleanly
# ---------------------------------------------------------------------------
class TextClassifier(nn.Module):
    """Embedding -> mean-pool -> MLP classifier (CPU-friendly)."""

    def __init__(
        self,
        vocab_size: int,
        num_classes: int,
        embed_dim: int = 32,
        hidden_dim: int = 64,
        pad_idx: int = 0,
    ) -> None:
        super().__init__()
        self.pad_idx = pad_idx
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(
        self, token_ids: torch.Tensor, lengths: torch.Tensor
    )