"""train.py — Module 6: Tuned Classifier with Eval Gate.

Fine-tunes a tiny text classifier on a synthetic 5-class sentiment/topic dataset.
Pure PyTorch (no HuggingFace). Runs on CPU in < 60 seconds on a modern laptop.
Saves a self-contained checkpoint to outputs/checkpoint.pt for eval.py to consume.

Design notes:
  - The synthetic dataset has per-class signal words so a small mean-pooled
    embedding model can reliably beat a majority-class baseline by >= 5pp.
  - All randomness is seeded (SEED = 42) so eval.py's held-out test set
    (seed = SEED + 1000) is deterministic and disjoint from training.
  - The checkpoint stores the model state, vocab, class names, and the
    training-set majority class so eval.py can build the baseline without
    re-parsing train.jsonl.
"""
from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn as nn

# ---------------------------------------------------------------------------
# Reproducibility — must come before any RNG use.
# ---------------------------------------------------------------------------
SEED = 42
os.environ.setdefault("PYTHONHASHSEED", str(SEED))
random.seed(SEED)
torch.manual_seed(SEED)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)
CHECKPOINT_PATH = OUTPUTS_DIR / "checkpoint.pt"
TRAIN_JSONL = OUTPUTS_DIR / "train.jsonl"

# ---------------------------------------------------------------------------
# Synthetic 5-class dataset.
# Each class owns a small set of signal words. We sample a few signal tokens
# plus some filler and shuffle — giving the model clear lexical signal that
# a tiny bag-of-embeddings classifier can learn in a few epochs.
# ---------------------------------------------------------------------------
CLASS_NAMES: List[str] = ["positive", "negative", "neutral", "tech", "sports"]
NUM_CLASSES: int = len(CLASS_NAMES)

SIGNAL_WORDS: Dict[int, List[str]] = {
    0: ["great", "love", "amazing", "wonderful", "excellent", "happy", "perfect", "good"],
    1: ["terrible", "hate", "awful", "bad", "horrible", "sad", "worst", "poor"],
    2: ["okay", "fine", "average", "decent", "normal", "mediocre", "fair", "standard"],
    3: ["code", "software", "tech", "computer", "digital", "program", "server", "cloud"],
    4: ["game", "team", "sport", "play", "win", "score", "league", "match"],
}

FILLER: List[str] = [
    "the", "a", "this", "that", "is", "was", "really", "very",
    "today", "again", "i", "you", "we", "they", "it",
]


def make_example(rng: random.Random) -> Tuple[str, int]:
    cls = rng.randrange(NUM_CLASSES)
    n_signal = rng.randint(2, 3)
    signal = [rng.choice(SIGNAL_WORDS[cls]) for _ in range(n_signal)]
    n_filler = rng.randint(1, 2)
    fillers = [rng.choice(FILLER) for _ in range(n_filler)]
    tokens = signal + fillers
    rng.shuffle(tokens)
    return " ".join(tokens), cls


def make_dataset(n: int, seed: int = SEED) -> List[Tuple[str, int]]:
    """Deterministic synthetic dataset. Train uses SEED; eval uses SEED + 1000."""
    rng = random.Random(seed)
    return [make_example(rng) for _ in range(n)]


# ---------------------------------------------------------------------------
# Tokenization + vocab
# ---------------------------------------------------------------------------
def tokenize(text: str) -> List[str]:
    return text.lower().split()


class Vocab:
    PAD = "<pad>"
    UNK = "<unk>"

    def __init__(self) -> None:
        self.itos: List[str] = [self.PAD, self.UNK]
        self.stoi: Dict[str, int] = {self.PAD: 0