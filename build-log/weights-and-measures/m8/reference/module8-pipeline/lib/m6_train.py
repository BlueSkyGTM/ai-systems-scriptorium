"""m6_train.py — the classifier model and its training (M6's artifact).

Holds the support-ticket classifier (embedding -> mean-pool -> MLP), the vocab, and the
encoder, plus build_and_train(), which calls the m4_tune.fit loop and saves a
self-contained checkpoint. m5_eval and m7_regress import the model from here, so the
architecture can never drift across the pipeline.
"""
from __future__ import annotations

import random
from collections import Counter
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

import m4_tune

SEED = 42
MAX_LEN = 12
CLASS_NAMES = ["billing", "bug", "feature", "praise", "security"]
NUM_CLASSES = len(CLASS_NAMES)


# ---------------------------------------------------------------------------
# Tokenizer + vocab
# ---------------------------------------------------------------------------
def tokenize(text: str) -> List[str]:
    return text.lower().split()


class Vocab:
    PAD, UNK = "<pad>", "<unk>"

    def __init__(self, stoi: Dict[str, int] | None = None) -> None:
        self.stoi = dict(stoi) if stoi else {self.PAD: 0, self.UNK: 1}

    @classmethod
    def build(cls, texts: List[str]) -> "Vocab":
        v = cls()
        for text in texts:
            for tok in tokenize(text):
                v.stoi.setdefault(tok, len(v.stoi))
        return v

    def __len__(self) -> int:
        return len(self.stoi)

    def encode(self, text: str, max_len: int = MAX_LEN) -> Tuple[List[int], int]:
        ids = [self.stoi.get(t, self.stoi[self.UNK]) for t in tokenize(text)][:max_len]
        length = max(len(ids), 1)
        ids = ids + [self.stoi[self.PAD]] * (max_len - len(ids))
        return ids, length


def encode_batch(rows: List[dict], vocab: Vocab) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    ids, lengths, labels = [], [], []
    for r in rows:
        i, ln = vocab.encode(r["text"])
        ids.append(i)
        lengths.append(ln)
        labels.append(CLASS_NAMES.index(r["label"]))
    return (torch.tensor(ids), torch.tensor(lengths), torch.tensor(labels))


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class TextClassifier(nn.Module):
    def __init__(self, vocab_size: int, num_classes: int = NUM_CLASSES,
                 embed_dim: int = 32, hidden_dim: int = 64, pad_idx: int = 0) -> None:
        super().__init__()
        self.pad_idx = pad_idx
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_idx)
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, token_ids: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        emb = self.embed(token_ids)
        mask = (token_ids != self.pad_idx).unsqueeze(-1)
        pooled = (emb * mask).sum(1) / lengths.clamp(min=1).unsqueeze(-1).float()
        return self.fc2(F.relu(self.fc1(pooled)))


def majority_class(rows: List[dict]) -> int:
    counts = Counter(CLASS_NAMES.index(r["label"]) for r in rows)
    return counts.most_common(1)[0][0]


def build_and_train(curated: dict, epochs: int = 30, lr: float = 0.01) -> dict:
    """Train the classifier on curated['train'] using the m4_tune loop. Returns a
    checkpoint dict (in memory) plus the training summary."""
    torch.manual_seed(SEED)
    random.seed(SEED)
    train = curated["train"]
    vocab = Vocab.build([r["text"] for r in train])
    x, lengths, y = encode_batch(train, vocab)

    model = TextClassifier(len(vocab))
    loss_fn = nn.CrossEntropyLoss()
    final_loss = m4_tune.fit(model.parameters(), lambda: loss_fn(model(x, lengths), y), epochs, lr)

    model.eval()
    with torch.no_grad():
        train_acc = float((model(x, lengths).argmax(1) == y).float().mean())

    checkpoint = {
        "state_dict": model.state_dict(),
        "vocab": vocab.stoi,
        "class_names": CLASS_NAMES,
        "config": {"embed_dim": 32, "hidden_dim": 64, "max_len": MAX_LEN,
                   "num_classes": NUM_CLASSES},
        "train_majority_class": majority_class(train),
    }
    return {"checkpoint": checkpoint, "final_loss": final_loss, "train_acc": train_acc}


def load_model(checkpoint: dict) -> Tuple[TextClassifier, Vocab]:
    vocab = Vocab(checkpoint["vocab"])
    cfg = checkpoint["config"]
    model = TextClassifier(len(vocab), cfg["num_classes"], cfg["embed_dim"], cfg["hidden_dim"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, vocab


def predict(checkpoint: dict, text: str) -> str:
    model, vocab = load_model(checkpoint)
    ids, length = vocab.encode(text)
    with torch.no_grad():
        logits = model(torch.tensor([ids]), torch.tensor([length]))
    return CLASS_NAMES[int(logits.argmax(1).item())]
