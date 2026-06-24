"""train.py — Module 6: Tuned Classifier with Eval Gate.

Fine-tunes a tiny text classifier on a synthetic 5-class dataset. Pure PyTorch
(no HuggingFace). Runs on CPU in under 60 seconds. Saves a self-contained
checkpoint to outputs/checkpoint.pt that eval.py consumes.

Design:
  - The synthetic dataset gives each class its own signal words, so a small
    mean-pooled bag-of-embeddings model beats a majority-class baseline by a
    wide margin. That margin is what the M6 eval gate checks.
  - All randomness is seeded (SEED = 42). The held-out test set uses a disjoint
    seed (SEED + 1000), so train and test never overlap.
  - The checkpoint carries everything eval.py needs to rebuild the model and the
    baseline: the state_dict, the vocab, the class names, the model config, and
    the training-set majority class.

The model, vocab, and tokenizer defined here are imported by eval.py, so the two
scripts can never drift apart on the architecture.
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
import torch.nn.functional as F

# ---------------------------------------------------------------------------
# Reproducibility — before any RNG use.
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
CHECKPOINT_PATH = OUTPUTS_DIR / "checkpoint.pt"
TRAIN_JSONL = OUTPUTS_DIR / "train.jsonl"
TEST_JSONL = OUTPUTS_DIR / "test.jsonl"

# ---------------------------------------------------------------------------
# Synthetic 5-class dataset. Each class owns a set of signal words; an example
# is a few signal words plus filler, shuffled. Clear lexical signal, learnable
# in a few epochs by a tiny model.
# ---------------------------------------------------------------------------
# Support-ticket routing: the artifact's portfolio framing. Five intent classes,
# each with its own signal vocabulary.
CLASS_NAMES: List[str] = ["billing", "bug", "feature", "praise", "security"]
NUM_CLASSES: int = len(CLASS_NAMES)
MAX_LEN: int = 12

SIGNAL_WORDS: Dict[int, List[str]] = {
    0: ["invoice", "charge", "payment", "refund", "billing", "subscription", "price", "receipt"],
    1: ["crash", "error", "broken", "bug", "fails", "exception", "freeze", "glitch"],
    2: ["request", "add", "feature", "integrate", "enhancement", "support", "option", "ability"],
    3: ["great", "love", "amazing", "thanks", "excellent", "awesome", "perfect", "helpful"],
    4: ["password", "breach", "security", "hacked", "vulnerability", "leak", "phishing", "unauthorized"],
}

FILLER: List[str] = [
    "the", "a", "this", "that", "is", "was", "please", "could",
    "today", "again", "i", "you", "we", "they", "it",
]


def make_example(rng: random.Random) -> Tuple[str, str]:
    cls = rng.randrange(NUM_CLASSES)
    signal = [rng.choice(SIGNAL_WORDS[cls]) for _ in range(rng.randint(2, 3))]
    fillers = [rng.choice(FILLER) for _ in range(rng.randint(1, 2))]
    tokens = signal + fillers
    rng.shuffle(tokens)
    return " ".join(tokens), CLASS_NAMES[cls]


def make_dataset(n: int, seed: int) -> List[Tuple[str, str]]:
    """Deterministic synthetic dataset. Train seed=SEED, test seed=SEED+1000."""
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

    def __init__(self, stoi: Dict[str, int] | None = None) -> None:
        if stoi is None:
            self.stoi: Dict[str, int] = {self.PAD: 0, self.UNK: 1}
        else:
            self.stoi = dict(stoi)
        self.itos: List[str] = [w for w, _ in sorted(self.stoi.items(), key=lambda kv: kv[1])]

    @classmethod
    def build(cls, examples: List[Tuple[str, str]]) -> "Vocab":
        v = cls()
        for text, _ in examples:
            for tok in tokenize(text):
                if tok not in v.stoi:
                    v.stoi[tok] = len(v.stoi)
        v.itos = [w for w, _ in sorted(v.stoi.items(), key=lambda kv: kv[1])]
        return v

    def __len__(self) -> int:
        return len(self.stoi)

    def encode(self, text: str, max_len: int = MAX_LEN) -> Tuple[List[int], int]:
        ids = [self.stoi.get(tok, self.stoi[self.UNK]) for tok in tokenize(text)][:max_len]
        length = max(len(ids), 1)
        if len(ids) < max_len:
            ids = ids + [self.stoi[self.PAD]] * (max_len - len(ids))
        return ids, length


def encode_batch(
    examples: List[Tuple[str, str]], vocab: Vocab, max_len: int = MAX_LEN
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    token_ids, lengths, labels = [], [], []
    for text, label in examples:
        ids, length = vocab.encode(text, max_len)
        token_ids.append(ids)
        lengths.append(length)
        labels.append(CLASS_NAMES.index(label))
    return (
        torch.tensor(token_ids, dtype=torch.long),
        torch.tensor(lengths, dtype=torch.long),
        torch.tensor(labels, dtype=torch.long),
    )


# ---------------------------------------------------------------------------
# Model — Embedding -> masked mean-pool -> MLP. Imported by eval.py.
# ---------------------------------------------------------------------------
class TextClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        num_classes: int = NUM_CLASSES,
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

    def forward(self, token_ids: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        emb = self.embed(token_ids)                      # (B, L, E)
        mask = (token_ids != self.pad_idx).unsqueeze(-1)  # (B, L, 1)
        summed = (emb * mask).sum(dim=1)                  # (B, E)
        denom = lengths.clamp(min=1).unsqueeze(-1).float()
        pooled = summed / denom                           # masked mean
        h = F.relu(self.fc1(pooled))
        h = self.dropout(h)
        return self.fc2(h)


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
def majority_class(examples: List[Tuple[str, str]]) -> int:
    from collections import Counter
    counts = Counter(CLASS_NAMES.index(label) for _, label in examples)
    return counts.most_common(1)[0][0]


def write_jsonl(path: Path, examples: List[Tuple[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for text, label in examples:
            f.write(json.dumps({"text": text, "label": label}) + "\n")


def train_model(
    n_train: int = 600,
    n_test: int = 200,
    epochs: int = 25,
    embed_dim: int = 32,
    hidden_dim: int = 64,
    lr: float = 0.01,
    checkpoint_path: Path = CHECKPOINT_PATH,
    write_data: bool = True,
) -> dict:
    """Train the classifier, save the checkpoint, optionally write JSONL data.

    Returns a summary dict (final loss, train accuracy, paths).
    """
    torch.manual_seed(SEED)
    random.seed(SEED)

    train_data = make_dataset(n_train, seed=SEED)
    test_data = make_dataset(n_test, seed=SEED + 1000)
    vocab = Vocab.build(train_data)

    x, lengths, y = encode_batch(train_data, vocab)

    model = TextClassifier(len(vocab), NUM_CLASSES, embed_dim, hidden_dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    model.train()
    final_loss = 0.0
    for _ in range(epochs):
        opt.zero_grad()
        logits = model(x, lengths)
        loss = loss_fn(logits, y)
        loss.backward()
        opt.step()
        final_loss = float(loss.item())

    model.eval()
    with torch.no_grad():
        train_acc = float((model(x, lengths).argmax(dim=1) == y).float().mean().item())

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "state_dict": model.state_dict(),
        "vocab": vocab.stoi,
        "class_names": CLASS_NAMES,
        "config": {
            "embed_dim": embed_dim,
            "hidden_dim": hidden_dim,
            "max_len": MAX_LEN,
            "num_classes": NUM_CLASSES,
        },
        "train_majority_class": majority_class(train_data),
    }
    torch.save(checkpoint, checkpoint_path)

    if write_data:
        write_jsonl(TRAIN_JSONL, train_data)
        write_jsonl(TEST_JSONL, test_data)

    return {
        "final_loss": final_loss,
        "train_acc": train_acc,
        "checkpoint": str(checkpoint_path),
        "train_jsonl": str(TRAIN_JSONL),
        "test_jsonl": str(TEST_JSONL),
        "vocab_size": len(vocab),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the M6 skill classifier.")
    parser.add_argument("--n-train", type=int, default=600)
    parser.add_argument("--n-test", type=int, default=200)
    parser.add_argument("--epochs", type=int, default=25)
    args = parser.parse_args()

    summary = train_model(n_train=args.n_train, n_test=args.n_test, epochs=args.epochs)
    print(
        f"[train] loss={summary['final_loss']:.4f} "
        f"train_acc={summary['train_acc']:.3f} "
        f"vocab={summary['vocab_size']} -> {summary['checkpoint']}"
    )


if __name__ == "__main__":
    main()
